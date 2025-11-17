import os
import threading
import time
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class ProcessLock:
    """进程锁 - 确保同一任务不被并发执行"""
    
    def __init__(self):
        self.locks = {}
        self.global_lock = threading.Lock()
    
    def acquire_lock(self, task_id, timeout=5):
        """获取任务锁"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            with self.global_lock:
                if task_id not in self.locks:
                    self.locks[task_id] = threading.Lock()
                    return self.locks[task_id].acquire(blocking=False)
            time.sleep(0.1)
        
        logger.warning(f"无法在 {timeout}s 内获取任务锁: {task_id}")
        return False
    
    def release_lock(self, task_id):
        """释放任务锁"""
        with self.global_lock:
            if task_id in self.locks:
                try:
                    self.locks[task_id].release()
                    # 清理锁对象
                    del self.locks[task_id]
                except RuntimeError:
                    pass
    
    def is_task_running(self, task_id):
        """检查任务是否正在运行"""
        with self.global_lock:
            if task_id in self.locks:
                # 尝试无阻塞获取锁
                acquired = self.locks[task_id].acquire(blocking=False)
                if acquired:
                    self.locks[task_id].release()
                    return False
                else:
                    return True
            return False
