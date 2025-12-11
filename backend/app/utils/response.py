from flask import jsonify


def api_response(data=None, msg: str = '成功', code: int = 200):
    """统一 API 响应格式：
    返回 (jsonify(payload), http_status)

    payload: { code, msg, success, data }
    success: True for 2xx codes
    """
    success = 200 <= code < 300
    payload = {
        'code': code,
        'msg': msg,
        'success': success,
        'data': data
    }
    return jsonify(payload), code
