import logging
import os
from app.core.config import Config

def setup_logger(name):
    """配置日志记录器"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(getattr(logging, Config.LOG_LEVEL))
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
        
        # 文件处理器
        log_dir = Config.LOGS_DIR
        # 确保日志目录存在
        try:
            os.makedirs(log_dir, exist_ok=True)
        except (PermissionError, OSError):
            # 如果无法创建目标目录，使用相对路径
            log_dir = './logs'
            os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, 'app.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
        
        # 格式化器
        formatter = logging.Formatter(Config.LOG_FORMAT)
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger
