from flask import Blueprint, jsonify, current_app
from app.utils.logger import setup_logger

bp = Blueprint('system', __name__, url_prefix='/api/system')
logger = setup_logger(__name__)

@bp.route('/info', methods=['GET'])
def get_system_info():
    """获取系统信息"""
    try:
        info = current_app.process_manager.get_system_info()
        return jsonify({
            'success': True,
            'data': info
        })
    except Exception as e:
        logger.error(f"获取系统信息失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/process', methods=['GET'])
def get_process_info():
    """获取当前进程信息"""
    try:
        info = current_app.process_manager.get_process_info()
        return jsonify({
            'success': True,
            'data': info
        })
    except Exception as e:
        logger.error(f"获取进程信息失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/processes', methods=['GET'])
def get_all_processes():
    """获取所有Python进程"""
    try:
        processes = current_app.process_manager.get_all_processes()
        return jsonify({
            'success': True,
            'data': processes
        })
    except Exception as e:
        logger.error(f"获取进程列表失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'success': True,
        'message': 'Service is running'
    })
