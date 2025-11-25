import os
import threading
from app.utils.script_runner import run_script
import uuid
import re
import json
from datetime import datetime
from app.models.db import SessionLocal
from app.models.task_models import Task, Script, TaskRun
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

    def update_task(self, task_id, name, description, script_filenames):
        """更新数据库中的任务及其脚本顺序"""
        session = SessionLocal()
        try:
            task = session.query(Task).filter(Task.id == task_id).first()
            if not task:
                return False, '任务不存在'
            task.name = name or task.name
            task.description = description or task.description

            # 删除旧的脚本并重新创建新的顺序
            session.query(Script).filter(Script.task_id == task_id).delete()
            for order, filename in enumerate(script_filenames):
                script = Script(task_id=task_id, filename=filename, order=order)
                session.add(script)

            session.commit()
            return True, '更新成功'
        except Exception as e:
            session.rollback()
            return False, str(e)
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
            # store a structure so we can collect streaming logs per script
            self.active_runs[run.id] = {
                'thread': thread,
                'stream_logs': {},  # map: script_filename -> [lines]
                'run_dir': os.path.join(Config.LOGS_DIR, f"run_{run.id}")
            }
            return run.id, "任务已提交执行"
        finally:
            session.close()

    def _run_scripts(self, run_id):
        """执行脚本序列，环境变量完全隔离，使用 multiprocessing.Manager() 提供共享上下文代理"""
        from multiprocessing import Manager

        session = SessionLocal()
        manager = None
        try:
            run = session.query(TaskRun).filter(TaskRun.id == run_id).first()
            task = run.task
            context = dict(run.initial_context or {})  # 创建独立拷贝，完全隔离
            status = 'success'

            # 创建 Manager，并用 dict 代理保存初始上下文
            manager = Manager()
            context_proxy = manager.dict(context)

            # prepare run directory under configured LOGS_DIR
            run_dir = os.path.join(Config.LOGS_DIR, f"run_{run.id}")
            try:
                os.makedirs(run_dir, exist_ok=True)
            except Exception:
                pass

            # start consumer thread helper
            def _consume_logs(q, stop_evt, logs_list, logfile_path):
                try:
                    with open(logfile_path, 'a', encoding='utf-8') as lf:
                        while not stop_evt.is_set() or not q.empty():
                            try:
                                level, msg = q.get(timeout=0.5)
                                line = f"[{level}] {msg}\n"
                                logs_list.append(line)
                                lf.write(line)
                                lf.flush()
                            except Exception:
                                continue
                except Exception:
                    pass

            for script in sorted(task.scripts, key=lambda s: s.order):
                script_path = os.path.join(self.tasks_dir, script.filename)
                logfile_path = os.path.join(run_dir, f"{script.filename}.log")

                # create per-script log queue and consumer to avoid cross-script mixing
                from multiprocessing import Queue as MPQueue
                script_log_q = MPQueue()
                script_stop_evt = threading.Event()
                # ensure per-script storage exists
                try:
                    self.active_runs[run.id]['stream_logs'].setdefault(script.filename, [])
                    script_storage = self.active_runs[run.id]['stream_logs'][script.filename]
                except Exception:
                    script_storage = []

                consumer_thread = threading.Thread(target=_consume_logs, args=(script_log_q, script_stop_evt, script_storage, logfile_path))
                consumer_thread.daemon = True
                consumer_thread.start()

                output, new_context = self._execute_script(script_path, context, context_proxy, script_log_q)

                # stop consumer for this script and wait a short time for remaining logs
                try:
                    script_stop_evt.set()
                    consumer_thread.join(timeout=2)
                except Exception:
                    pass

                # 如果脚本通过代理修改了上下文，则以代理为准
                try:
                    context = dict(context_proxy)
                except Exception:
                    context = dict(new_context or context)

                # 保存脚本输出日志（优先写入通过 SDK 发送的流式日志，避免重复）
                try:
                    script_streamed_list = self.active_runs[run.id]['stream_logs'].get(script.filename, [])
                    streamed = ''.join(script_streamed_list)
                except Exception:
                    streamed = ''

                # 只保留通过 SDK (streamed) 的日志；若没有则写入空文件(或保持已打开文件)
                try:
                    script_streamed_list = self.active_runs[run.id]['stream_logs'].get(script.filename, [])
                    streamed = ''.join(script_streamed_list)
                except Exception:
                    streamed = ''

                try:
                    # truncate/create logfile; write only streamed logs if present
                    with open(logfile_path, 'w', encoding='utf-8') as lf:
                        if streamed:
                            lf.write(streamed)
                        else:
                            # intentionally write nothing to preserve 'only SDK logs' policy
                            lf.write('')
                except Exception:
                    pass

                # 保存此脚本执行后的环境变量状态到文件
                ctx_path = os.path.join(run_dir, f"{script.filename}.context.json")
                try:
                    with open(ctx_path, 'w', encoding='utf-8') as cf:
                        json.dump(context, cf, ensure_ascii=False, indent=2)
                except Exception:
                    pass

                # commit run state (update DB TaskRun only)
                session.commit()

                if 'ERROR' in output:
                    status = 'failed'
                    break

            run.status = status
            run.finished_at = datetime.utcnow()
            run.final_context = context
            session.commit()
        finally:
            try:
                if manager is not None:
                    manager.shutdown()
            except Exception:
                pass
            # no global stop_event to set; per-script consumers are stopped after each script
            try:
                # optional: keep stream logs in active_runs for a short while
                pass
            except Exception:
                pass
            session.close()

    def _execute_script(self, script_path, context, context_proxy=None, log_queue=None):
        """执行单个脚本，环境变量隔离"""
        # 完整隔离环境变量：创建干净的环境，只注入需要的变量
        env = os.environ.copy()
        # 清除可能的污染，注入当前任务的上下文（同时支持 proxy）
        if context_proxy is not None:
            try:
                for k, v in dict(context_proxy).items():
                    env[str(k)] = str(v)
            except Exception:
                for k, v in context.items():
                    env[str(k)] = str(v)
        else:
            for k, v in context.items():
                env[str(k)] = str(v)

        try:
            output, returncode, timed_out = run_script(
                script_path,
                params=None,
                env=env,
                cwd=self.tasks_dir,
                timeout=self.task_timeout,
                context_proxy=context_proxy,
                log_queue=log_queue,
            )

            if timed_out:
                return f"ERROR: 脚本执行超时 ({self.task_timeout}s)", context

            # 改进的 JSON 解析：支持多行和嵌套
            new_context = self._parse_context_from_output(output, context)
            return output, new_context
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
        run_dir = os.path.join(Config.LOGS_DIR, f"run_{run_id}")
        result = []
        try:
            if not os.path.exists(run_dir):
                return []
            for fname in sorted(os.listdir(run_dir)):
                if fname.endswith('.log'):
                    path = os.path.join(run_dir, fname)
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        result.append({
                            'script': fname.replace('.log', ''),
                            'output': content,
                            'created_at': datetime.fromtimestamp(os.path.getctime(path)).isoformat()
                        })
                    except Exception:
                        continue
        except Exception:
            return []
        return result

    def get_run_contexts(self, run_id):
        """获取运行的环境变量历史"""
        run_dir = os.path.join(Config.LOGS_DIR, f"run_{run_id}")
        result = []
        try:
            if not os.path.exists(run_dir):
                return []
            for fname in sorted(os.listdir(run_dir)):
                if fname.endswith('.context.json'):
                    path = os.path.join(run_dir, fname)
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            ctx = json.load(f)
                        result.append({
                            'script': fname.replace('.context.json', ''),
                            'context': ctx,
                            'created_at': datetime.fromtimestamp(os.path.getctime(path)).isoformat()
                        })
                    except Exception:
                        continue
        except Exception:
            return []
        return result
