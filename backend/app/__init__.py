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
    
    # 使用运行时解析的绝对路径来定位前端构建产物，避免在不同工作目录下路径解析错误
    base_dir = os.path.dirname(__file__)
    static_dir = os.path.abspath(os.path.join(base_dir, '../../frontend/dist'))
    # 禁用 Flask 自动注册的静态路由（static_url_path=None），使用自定义回退逻辑
    app = Flask(__name__, static_folder=static_dir, static_url_path=None)

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
    from flask import request
    from app.utils.response import api_response
    from app.routes import task_routes, log_routes, system_routes, auth_routes
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(task_routes.bp)
    app.register_blueprint(log_routes.bp)
    app.register_blueprint(system_routes.bp)

    # 全局鉴权：对 /api/* 接口进行 token 校验，白名单可包含无需鉴权的接口
    @app.before_request
    def global_auth_check():
        # 仅拦截 /api 开头的接口
        path = request.path
        if not path.startswith('/api'):
            return None

        # 白名单，不需要鉴权的接口
        whitelist = ['/api/auth/login', '/api/system/health']
        if path in whitelist:
            return None

        auth = request.headers.get('Authorization', '')
        if not auth:
            return api_response(None, 'Unauthorized', 401)

        # 支持两种形式："Bearer <token>" 或 直接把 token 放在 Authorization 头里
        if auth.startswith('Bearer '):
            token = auth.split(' ', 1)[1].strip()
        else:
            token = auth.strip()
        from app.utils.auth import verify_token
        if not verify_token(token):
            return api_response(None, 'Invalid or expired token', 401)
    
    # 前端路由 - SPA支持
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        # 如果请求的是静态资源且存在，直接返回；否则返回 SPA 的 index.html 以支持前端路由
        requested_path = os.path.join(app.static_folder, path)
        if path and os.path.exists(requested_path):
            return app.send_static_file(path)
        # 若 index.html 丢失，显式抛出 404 以便更快定位问题
        index_file = os.path.join(app.static_folder, 'index.html')
        if not os.path.exists(index_file):
            logger.error(f"前端静态文件未找到: {index_file}")
            return ("Frontend build not found", 404)
        return app.send_static_file('index.html')
    
    logger.info("应用初始化完成")
    return app
