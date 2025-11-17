import os
import json
import uuid
import threading
import subprocess
from datetime import datetime
from pathlib import Path
from app.utils.logger import setup_logger
from app.core.config import Config
from app.utils.process_lock import ProcessLock

logger = setup_logger(__name__)

class TaskManager:
    """任务管理器 - 负责任务的编排和执行"""
    
    def __init__(self):
        self.tasks_dir = Config.TASKS_DIR
        self.logs_dir = Config.LOGS_DIR
        self.max_workers = Config.MAX_TASK_WORKERS
        self.task_timeout = Config.TASK_TIMEOUT
        self.active_tasks = {}
        self.lock = threading.RLock()
        self.process_lock = ProcessLock()
        from app.services.task_service import TaskService
        self.task_service = TaskService()
        logger.info("TaskManager 初始化完成")
    
    def list_tasks(self):
        """列出所有可用的Python任务文件"""
        tasks = []
        try:
            for file in os.listdir(self.tasks_dir):
                if file.endswith('.py'):
                    file_path = os.path.join(self.tasks_dir, file)
                    tasks.append({
                        'id': file[:-3],
                        'name': file[:-3],
                        'path': file_path,
                        'created_at': datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
                    })
        except Exception as e:
            logger.error(f"列出任务失败: {e}")
        return tasks
    
    def get_task_info(self, task_id):
        """获取任务详细信息"""
        task_path = os.path.join(self.tasks_dir, f"{task_id}.py")
        if not os.path.exists(task_path):
            return None
        
        try:
            with open(task_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'id': task_id,
                'name': task_id,
                'path': task_path,
                'content': content,
                'created_at': datetime.fromtimestamp(os.path.getctime(task_path)).isoformat(),
                'modified_at': datetime.fromtimestamp(os.path.getmtime(task_path)).isoformat()
            }
        except Exception as e:
            logger.error(f"获取任务信息失败: {e}")
            return None
    
    def create_db_task(self, name, description, script_filenames):
        """通过数据库创建任务并编排脚本"""
        try:
            task_id = self.task_service.create_task(name, description, script_filenames)
            logger.info(f"数据库任务创建成功: {task_id}")
            return True, task_id
        except Exception as e:
            logger.error(f"数据库任务创建失败: {e}")
            return False, str(e)
    
    def update_task(self, task_id, content):
        """更新任务内容"""
        task_path = os.path.join(self.tasks_dir, f"{task_id}.py")
        if not os.path.exists(task_path):
            return False, "任务不存在"
        
        try:
            with open(task_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"任务更新成功: {task_id}")
            return True, "任务更新成功"
        except Exception as e:
            logger.error(f"更新任务失败: {e}")
            return False, str(e)
    
    def delete_task(self, task_id):
        """删除任务"""
        task_path = os.path.join(self.tasks_dir, f"{task_id}.py")
        if not os.path.exists(task_path):
            return False, "任务不存在"
        
        try:
            os.remove(task_path)
            logger.info(f"任务删除成功: {task_id}")
            return True, "任务删除成功"
        except Exception as e:
            logger.error(f"删除任务失败: {e}")
            return False, str(e)
    
    def execute_db_task(self, task_id, context=None):
        """通过数据库任务编排执行任务"""
        try:
            run_id, msg = self.task_service.run_task(task_id, context)
            logger.info(f"数据库任务执行: {task_id}, run_id: {run_id}")
            return run_id, msg
        except Exception as e:
            logger.error(f"数据库任务执行失败: {e}")
            return None, str(e)
    
    def _execute_task_thread(self, task_id, run_id, task_path, params):
        """后台线程执行任务"""
        log_file = os.path.join(self.logs_dir, f"{task_id}_{run_id}.log")
        
        try:
            # 构建命令
            cmd = ['python', task_path]
            if params:
                cmd.extend([str(p) for p in params])
            
            # 执行任务
            with open(log_file, 'w', encoding='utf-8') as lf:
                result = subprocess.run(
                    cmd,
                    stdout=lf,
                    stderr=subprocess.STDOUT,
                    timeout=self.task_timeout,
                    cwd=self.tasks_dir
                )
            
            status = 'success' if result.returncode == 0 else 'failed'
            logger.info(f"任务执行完成: {task_id}, run_id: {run_id}, 状态: {status}")
            
        except subprocess.TimeoutExpired:
            with open(log_file, 'a', encoding='utf-8') as lf:
                lf.write(f"\n[ERROR] 任务执行超时 ({self.task_timeout}秒)")
            logger.error(f"任务执行超时: {task_id}, run_id: {run_id}")
            status = 'timeout'
        except Exception as e:
            with open(log_file, 'a', encoding='utf-8') as lf:
                lf.write(f"\n[ERROR] 执行错误: {str(e)}")
            logger.error(f"任务执行错误: {task_id}, run_id: {run_id}, {e}")
            status = 'error'
        finally:
            # 更新任务状态
            with self.lock:
                if run_id in self.active_tasks:
                    self.active_tasks[run_id]['status'] = status
                    self.active_tasks[run_id]['end_time'] = datetime.now().isoformat()
            
            # 释放进程锁
            self.process_lock.release_lock(task_id)
    
    def get_task_status(self, run_id):
        """获取任务执行状态"""
        with self.lock:
            if run_id in self.active_tasks:
                task = self.active_tasks[run_id]
                return {
                    'run_id': run_id,
                    'task_id': task['task_id'],
                    'status': task['status'],
                    'start_time': task['start_time'],
                    'end_time': task.get('end_time')
                }
        return None
    
    def get_active_tasks(self):
        """获取所有活跃任务"""
        with self.lock:
            return [
                {
                    'run_id': run_id,
                    'task_id': task['task_id'],
                    'status': task['status'],
                    'start_time': task['start_time']
                }
                for run_id, task in self.active_tasks.items()
            ]
    
    def cleanup_finished_tasks(self):
        """清理已完成的任务记录"""
        with self.lock:
            finished = [
                run_id for run_id, task in self.active_tasks.items()
                if task['status'] in ['success', 'failed', 'error', 'timeout']
            ]
            for run_id in finished:
                del self.active_tasks[run_id]
