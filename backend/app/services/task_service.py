import os
import threading
import subprocess
import uuid
import re
import json
from datetime import datetime
from app.models.db import SessionLocal
from app.models.task_models import Task, Script, TaskRun, TaskRunLog, TaskRunContext
from app.core.config import Config

class TaskService:
    """数据库持久化任务编排与执行服务"""
    def __init__(self):
        self.tasks_dir = Config.TASKS_DIR
        self.max_workers = Config.MAX_TASK_WORKERS
        self.task_timeout = Config.TASK_TIMEOUT
        self.active_runs = {}
        self.lock = threading.RLock()

    def list_tasks(self):
        """获取所有编排任务"""
        session = SessionLocal()
        try:
            tasks = session.query(Task).all()
            result = []
            for task in tasks:
                scripts = session.query(Script).filter(Script.task_id == task.id).order_by(Script.order).all()
                result.append({
                    'id': task.id,
                    'name': task.name,
                    'description': task.description,
                    'scripts': [s.filename for s in scripts]
                })
            return result
        finally:
            session.close()

    def create_task(self, name, description, script_filenames):
        """创建任务并编排脚本顺序"""
        session = SessionLocal()
        try:
            task = Task(name=name, description=description)
            session.add(task)
            session.flush()  # 获取task.id
            for order, filename in enumerate(script_filenames):
                script = Script(task_id=task.id, filename=filename, order=order)
                session.add(script)
            session.commit()
            return task.id
        finally:
            session.close()

    def run_task(self, task_id, context=None):
        """执行任务，依次执行脚本，支持环境变量上下文"""
        session = SessionLocal()
        try:
            task = session.query(Task).filter(Task.id == task_id).first()
            if not task:
                return None, "任务不存在"
            initial_context = context or {}
            run = TaskRun(task_id=task.id, status='running', initial_context=initial_context, final_context=initial_context)
            session.add(run)
            session.commit()
            thread = threading.Thread(target=self._run_scripts, args=(run.id,))
            thread.daemon = False
            thread.start()
            self.active_runs[run.id] = thread
            return run.id, "任务已提交执行"
        finally:
            session.close()

    def _run_scripts(self, run_id):
        """执行脚本序列，环境变量完全隔离"""
        session = SessionLocal()
        try:
            run = session.query(TaskRun).filter(TaskRun.id == run_id).first()
            task = run.task
            context = dict(run.initial_context or {})  # 创建独立拷贝，完全隔离
            status = 'success'
            
            for script in sorted(task.scripts, key=lambda s: s.order):
                script_path = os.path.join(self.tasks_dir, script.filename)
                output, context = self._execute_script(script_path, context)
                
                # 保存脚本输出日志
                log = TaskRunLog(run_id=run.id, script_filename=script.filename, output=output)
                session.add(log)
                
                # 保存此脚本执行后的环境变量状态
                script_context = TaskRunContext(run_id=run.id, script_filename=script.filename, context=context)
                session.add(script_context)
                session.commit()
                
                if 'ERROR' in output:
                    status = 'failed'
                    break
            
            run.status = status
            run.finished_at = datetime.utcnow()
            run.final_context = context
            session.commit()
        finally:
            session.close()

    def _execute_script(self, script_path, context):
        """执行单个脚本，环境变量隔离"""
        # 完整隔离环境变量：创建干净的环境，只注入需要的变量
        env = os.environ.copy()
        # 清除可能的污染，注入当前任务的上下文
        for k, v in context.items():
            env[str(k)] = str(v)
        
        try:
            result = subprocess.run(
                ['python', script_path],
                capture_output=True,
                text=True,
                timeout=self.task_timeout,
                env=env,
                cwd=self.tasks_dir
            )
            output = result.stdout + result.stderr
            # 改进的 JSON 解析：支持多行和嵌套
            new_context = self._parse_context_from_output(output, context)
            return output, new_context
        except subprocess.TimeoutExpired:
            return f"ERROR: 脚本执行超时 ({self.task_timeout}s)", context
        except Exception as e:
            return f"ERROR: {str(e)}", context

    def _parse_context_from_output(self, output, context):
        """改进的上下文解析，支持多行JSON"""
        try:
            # 查找所有 __CONTEXT__ 标记
            lines = output.split('\n')
            for line in lines:
                if '__CONTEXT__' in line:
                    # 提取 __CONTEXT__ 后的内容
                    idx = line.find('__CONTEXT__')
                    if idx != -1:
                        json_str = line[idx + len('__CONTEXT__'):].strip()
                        try:
                            ctx = json.loads(json_str)
                            if isinstance(ctx, dict):
                                context.update(ctx)
                        except json.JSONDecodeError:
                            # 尝试多行解析
                            pass
        except Exception:
            pass
        return context

    def get_task_runs(self, task_id):
        """获取任务的所有运行记录"""
        session = SessionLocal()
        try:
            runs = session.query(TaskRun).filter(TaskRun.task_id == task_id).order_by(TaskRun.started_at.desc()).all()
            return runs
        finally:
            session.close()

    def get_run_logs(self, run_id):
        """获取运行的脚本日志"""
        session = SessionLocal()
        try:
            logs = session.query(TaskRunLog).filter(TaskRunLog.run_id == run_id).order_by(TaskRunLog.created_at.asc()).all()
            return logs
        finally:
            session.close()

    def get_run_contexts(self, run_id):
        """获取运行的环境变量历史"""
        session = SessionLocal()
        try:
            contexts = session.query(TaskRunContext).filter(TaskRunContext.run_id == run_id).order_by(TaskRunContext.created_at.asc()).all()
            return contexts
        finally:
            session.close()
