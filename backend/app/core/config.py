import os
from datetime import timedelta

class Config:
    """应用配置"""
    # Flask配置
    DEBUG = os.getenv('FLASK_DEBUG', False)
    TESTING = os.getenv('FLASK_TESTING', False)
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # 任务配置
    TASKS_DIR = os.getenv('TASKS_DIR', '/workspaces/TaskRunService/tasks')
    LOGS_DIR = os.getenv('LOGS_DIR', '/workspaces/TaskRunService/logs')
    MAX_TASK_WORKERS = int(os.getenv('MAX_TASK_WORKERS', '5'))
    TASK_TIMEOUT = int(os.getenv('TASK_TIMEOUT', '3600'))  # 1小时
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 进程管理配置
    PROCESS_CHECK_INTERVAL = int(os.getenv('PROCESS_CHECK_INTERVAL', '10'))
    
    @staticmethod
    def init_directories():
        """初始化所需的目录"""
        try:
            os.makedirs(Config.TASKS_DIR, exist_ok=True)
            os.makedirs(Config.LOGS_DIR, exist_ok=True)
        except (PermissionError, OSError) as e:
            print(f"警告: 无法创建目录 {e}")
            # 在开发环境中，使用相对路径
            Config.TASKS_DIR = './tasks'
            Config.LOGS_DIR = './logs'
            os.makedirs(Config.TASKS_DIR, exist_ok=True)
            os.makedirs(Config.LOGS_DIR, exist_ok=True)
