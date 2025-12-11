import os
from flask import Blueprint, request, current_app, send_file
from app.utils.response import api_response
from app.utils.logger import setup_logger
from app.core.config import Config

bp = Blueprint('logs', __name__, url_prefix='/api/logs')
logger = setup_logger(__name__)

@bp.route('', methods=['GET'])
def list_logs():
    """列出所有日志文件"""
    try:
        logs = []
        for file in os.listdir(Config.LOGS_DIR):
            if file.endswith('.log'):
                file_path = os.path.join(Config.LOGS_DIR, file)
                logs.append({
                    'filename': file,
                    'size': os.path.getsize(file_path),
                    'modified_at': os.path.getmtime(file_path)
                })
        return api_response(logs, '获取成功', 200)
    except Exception as e:
        logger.error(f"列出日志文件失败: {e}")
        return api_response(None, str(e), 500)

@bp.route('/<task_id>_<run_id>.log', methods=['GET'])
def get_log(task_id, run_id):
    """获取任务执行日志"""
    try:
        log_file = os.path.join(Config.LOGS_DIR, f"{task_id}_{run_id}.log")
        if not os.path.exists(log_file):
            return api_response(None, '日志文件不存在', 404)
        
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return api_response({'filename': f"{task_id}_{run_id}.log", 'content': content}, '获取成功', 200)
    except Exception as e:
        logger.error(f"获取日志失败: {e}")
        return api_response(None, str(e), 500)

@bp.route('/<task_id>_<run_id>.log/download', methods=['GET'])
def download_log(task_id, run_id):
    """下载任务执行日志"""
    try:
        log_file = os.path.join(Config.LOGS_DIR, f"{task_id}_{run_id}.log")
        if not os.path.exists(log_file):
            return api_response(None, '日志文件不存在', 404)
        
        return send_file(
            log_file,
            as_attachment=True,
            download_name=f"{task_id}_{run_id}.log"
        )
    except Exception as e:
        logger.error(f"下载日志失败: {e}")
        return api_response(None, str(e), 500)

@bp.route('/app.log', methods=['GET'])
def get_app_log():
    """获取应用日志"""
    try:
        app_log_file = os.path.join(Config.LOGS_DIR, 'app.log')
        if not os.path.exists(app_log_file):
            return api_response(None, '应用日志不存在', 404)
        
        # 获取最后N行
        lines = request.args.get('lines', 100, type=int)
        with open(app_log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            content = ''.join(all_lines[-lines:])
        
        return api_response({'filename': 'app.log', 'content': content, 'total_lines': len(all_lines)}, '获取成功', 200)
    except Exception as e:
        logger.error(f"获取应用日志失败: {e}")
        return api_response(None, str(e), 500)
