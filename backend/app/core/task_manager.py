import os
import json
import uuid
import threading
from app.utils.script_runner import run_script
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
        manager = None
        try:
            # 构建命令
            cmd = ['python', task_path]
            if params:
                cmd.extend([str(p) for p in params])

            # 使用 Manager 提供共享上下文代理，方便脚本通过 SDK 读取/写入
            from multiprocessing import Manager
            manager = Manager()
            context_proxy = manager.dict()

            # create a log queue and start consumer to capture streaming logs
            from multiprocessing import Queue as MPQueue
            log_queue = MPQueue()

            stop_evt = threading.Event()
            stream_logs = []
            def _consume(q, stop_event, storage, logfile_path):
                try:
                    with open(logfile_path, 'a', encoding='utf-8') as lf:
                        while not stop_event.is_set() or not q.empty():
                            try:
                                level, msg = q.get(timeout=0.5)
                                line = f"[{level}] {msg}\n"
                                storage.append(line)
                                lf.write(line)
                                lf.flush()
                            except Exception:
                                continue
                except Exception:
                    pass

            logfile_path = os.path.join(self.logs_dir, f"{task_id}_{run_id}.log")
            consumer_th = threading.Thread(target=_consume, args=(log_queue, stop_evt, stream_logs, logfile_path))
            consumer_th.daemon = True
            consumer_th.start()

            # 调用运行器
            params_for_run = cmd[1:] if len(cmd) > 1 else None
            output, returncode, timed_out = run_script(
                task_path,
                params=params_for_run,
                env=None,
                cwd=self.tasks_dir,
                timeout=self.task_timeout,
                context_proxy=context_proxy,
                log_queue=log_queue,
            )

            with open(log_file, 'w', encoding='utf-8') as lf:
                lf.write(output or '')

            if timed_out:
                status = 'timeout'
            else:
                status = 'success' if returncode == 0 else 'failed'

            # stop consumer and attach stream logs to active_tasks if present
            try:
                stop_evt.set()
                consumer_th.join(timeout=1)
            except Exception:
                pass
            try:
                if run_id in self.active_tasks:
                    self.active_tasks[run_id].setdefault('stream_logs', []).extend(stream_logs)
            except Exception:
                pass

            logger.info(f"任务执行完成: {task_id}, run_id: {run_id}, 状态: {status}")

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

            # 关闭 manager（如果存在）并释放进程锁
            try:
                if manager is not None:
                    manager.shutdown()
            except Exception:
                pass

            try:
                self.process_lock.release_lock(task_id)
            except Exception:
                pass
    
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
