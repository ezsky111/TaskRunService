import time
from typing import Optional
import jwt
from flask import current_app


def generate_token(username: str, expire_seconds: int = 3600 * 24) -> str:
    """生成 JWT token，默认有效期 1 天。"""
    secret = current_app.config.get('SECRET_KEY')
    now = int(time.time())
    payload = {
        'sub': username,
        'iat': now,
        'exp': now + expire_seconds
    }
    token = jwt.encode(payload, secret, algorithm='HS256')
    # PyJWT v2 返回 str
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token


def verify_token(token: str) -> Optional[dict]:
    """验证 token，成功返回 payload（dict），失败返回 None。"""
    secret = current_app.config.get('SECRET_KEY')
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload
    except Exception:
        return None


def get_username_from_token(token: str) -> Optional[str]:
    payload = verify_token(token)
    if not payload:
        return None
    return payload.get('sub')
