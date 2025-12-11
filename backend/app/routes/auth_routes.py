from flask import Blueprint, request, current_app
from app.utils.response import api_response
from app.utils.auth import generate_token, get_username_from_token
from app.models.db import SessionLocal
from app.models.task_models import User
from werkzeug.security import check_password_hash
from app.utils.logger import setup_logger

bp = Blueprint('auth', __name__, url_prefix='/api')
logger = setup_logger(__name__)


@bp.route('/auth/login', methods=['POST'])
def login():
    """简单登录实现：接受 JSON {userName, password}。示例中使用非常简单的密码校验（仅示例）。"""
    try:
        data = request.get_json() or {}
        # 支持前端两种命名：userName 或 username
        username = data.get('userName') or data.get('username')
        password = data.get('password')

        if not username or not password:
            return api_response(None, '缺少用户名或密码', 400)

        session = SessionLocal()
        try:
            user = session.query(User).filter_by(username=username).first()
        finally:
            session.close()

        if not user or not check_password_hash(user.password_hash, password):
            return api_response(None, '用户名或密码错误', 401)

        token = generate_token(username)
        # 返回 token 与 refreshToken 字段以匹配前端类型定义
        return api_response({'token': token, 'refreshToken': ''}, '登录成功', 200)
    except Exception as e:
        logger.error(f"登录失败: {e}")
        return api_response(None, str(e), 500)


@bp.route('/user/info', methods=['GET'])
def get_user_info():
    """根据请求头 Authorization: Bearer <token> 返回用户信息。"""
    try:
        auth = request.headers.get('Authorization', '')
        if not auth:
            return api_response(None, '无效或已过期的 token', 401)

        # 支持两种形式："Bearer <token>" 或 直接把 token 放在 Authorization 头里
        if auth.startswith('Bearer '):
            token = auth.split(' ', 1)[1].strip()
        else:
            token = auth.strip()
        username = get_username_from_token(token)
        if not username:
            return api_response(None, '无效或已过期的 token', 401)

        session = SessionLocal()
        try:
            user = session.query(User).filter_by(username=username).first()
        finally:
            session.close()

        if not user:
            return api_response(None, '用户不存在', 404)

        roles = user.roles.split(',') if user.roles else ['user']
        user_info = {
            'buttons': [],
            'roles': roles,
            'userId': user.id,
            'userName': user.username,
            'email': '',
            'avatar': ''
        }
        return api_response(user_info, '获取成功', 200)
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        return api_response(None, str(e), 500)
