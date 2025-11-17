import psutil
import os
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class ProcessManager:
    """进程管理器 - 监控和管理系统进程"""
    
    def __init__(self):
        self.current_process = psutil.Process(os.getpid())
        logger.info("ProcessManager 初始化完成")
    
    def get_system_info(self):
        """获取系统信息"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                }
            }
        except Exception as e:
            logger.error(f"获取系统信息失败: {e}")
            return {}
    
    def get_process_info(self):
        """获取当前进程信息"""
        try:
            return {
                'pid': self.current_process.pid,
                'name': self.current_process.name(),
                'status': self.current_process.status(),
                'memory_info': {
                    'rss': self.current_process.memory_info().rss,
                    'vms': self.current_process.memory_info().vms
                },
                'cpu_percent': self.current_process.cpu_percent(interval=1),
                'num_threads': self.current_process.num_threads()
            }
        except Exception as e:
            logger.error(f"获取进程信息失败: {e}")
            return {}
    
    def get_all_processes(self):
        """获取所有Python进程"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'status', 'memory_info']):
                try:
                    if 'python' in proc.name().lower():
                        processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'status': proc.info['status'],
                            'memory_rss': proc.info['memory_info'].rss if proc.info['memory_info'] else 0
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return processes
        except Exception as e:
            logger.error(f"获取进程列表失败: {e}")
            return []
