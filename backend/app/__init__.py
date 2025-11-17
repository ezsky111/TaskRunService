from flask import Flask
from flask_cors import CORS
from app.core.config import Config
import os

def create_app():
    """应用工厂函数"""
    # 初始化目录
    Config.init_directories()
    
    # 初始化日志（在目录创建后）
    from app.utils.logger import setup_logger
    logger = setup_logger(__name__)
    
    app = Flask(__name__, static_folder='../../frontend/dist', static_url_path='/')
    
    # 配置应用
    app.config.from_object(Config)
    
    # 启用CORS
    CORS(app)
    
    # 初始化数据库
    from app.models.db import init_db
    init_db()

    # 初始化服务
    from app.core.task_manager import TaskManager
    from app.core.process_manager import ProcessManager
    app.task_manager = TaskManager()
    app.process_manager = ProcessManager()
    
    # 注册路由
    from app.routes import task_routes, log_routes, system_routes
    app.register_blueprint(task_routes.bp)
    app.register_blueprint(log_routes.bp)
    app.register_blueprint(system_routes.bp)
    
    # 前端路由 - SPA支持
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            return app.send_static_file(path)
        return app.send_static_file('index.html')
    
    logger.info("应用初始化完成")
    return app
