
import os
from flask import Blueprint, jsonify, request, current_app
from app.utils.logger import setup_logger

bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')
logger = setup_logger(__name__)

@bp.route('', methods=['GET'])
def list_tasks():
    """获取所有任务列表"""
    try:
        tasks = current_app.task_manager.list_tasks()
        return jsonify({
            'success': True,
            'data': tasks
        })
    except Exception as e:
        logger.error(f"获取任务列表失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/<task_id>', methods=['GET'])
def get_task(task_id):
    """获取任务详细信息"""
    try:
        task = current_app.task_manager.get_task_info(task_id)
        if not task:
            return jsonify({
                'success': False,
                'message': '任务不存在'
            }), 404
        return jsonify({
            'success': True,
            'data': task
        })
    except Exception as e:
        logger.error(f"获取任务失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('', methods=['POST'])
def create_task():
    """创建新任务"""
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        content = data.get('content', '')
        
        if not task_id:
            return jsonify({
                'success': False,
                'message': '缺少task_id'
            }), 400
        
        success, message = current_app.task_manager.create_task(task_id, content)
        
        return jsonify({
            'success': success,
            'message': message
        }), 201 if success else 400
    except Exception as e:
        logger.error(f"创建任务失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/<task_id>', methods=['PUT'])
def update_task(task_id):
    """更新任务"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        
        success, message = current_app.task_manager.update_task(task_id, content)
        
        return jsonify({
            'success': success,
            'message': message
        }), 200 if success else 400
    except Exception as e:
        logger.error(f"更新任务失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """删除任务"""
    try:
        success, message = current_app.task_manager.delete_task(task_id)
        
        return jsonify({
            'success': success,
            'message': message
        }), 200 if success else 400
    except Exception as e:
        logger.error(f"删除任务失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/<task_id>/execute', methods=['POST'])
def execute_task(task_id):
    """执行任务"""
    try:
        data = request.get_json() or {}
        params = data.get('params', None)
        
        run_id, message = current_app.task_manager.execute_task(task_id, params)
        
        if run_id:
            return jsonify({
                'success': True,
                'message': message,
                'run_id': run_id
            }), 202
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
    except Exception as e:
        logger.error(f"执行任务失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/runs/<run_id>', methods=['GET'])
def get_task_status(run_id):
    """获取任务执行状态"""
    try:
        status = current_app.task_manager.get_task_status(run_id)
        if not status:
            return jsonify({
                'success': False,
                'message': '执行记录不存在'
            }), 404
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        logger.error(f"获取任务状态失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/runs', methods=['GET'])
def get_active_tasks():
    """获取所有活跃任务"""
    try:
        tasks = current_app.task_manager.get_active_tasks()
        return jsonify({
            'success': True,
            'data': tasks
        })
    except Exception as e:
        logger.error(f"获取活跃任务失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/db', methods=['GET'])
def list_db_tasks():
    """获取所有编排任务"""
    try:
        tasks = current_app.task_manager.task_service.list_tasks()
        return jsonify({'success': True, 'data': tasks}), 200
    except Exception as e:
        logger.error(f"获取编排任务列表失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/db', methods=['POST'])
def create_db_task():
    """通过数据库创建任务（含脚本顺序）"""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        script_filenames = data.get('scripts', [])
        if not name or not script_filenames:
            return jsonify({'success': False, 'message': '缺少name或scripts'}), 400
        success, result = current_app.task_manager.create_db_task(name, description, script_filenames)
        return jsonify({'success': success, 'task_id': result if success else None, 'message': result}), 201 if success else 400
    except Exception as e:
        logger.error(f"数据库任务创建失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/db/<int:task_id>', methods=['PUT'])
def update_db_task(task_id):
    """更新数据库任务（名称/描述/脚本顺序）"""
    try:
        data = request.get_json() or {}
        name = data.get('name')
        description = data.get('description', '')
        script_filenames = data.get('scripts', [])

        success, message = current_app.task_manager.task_service.update_task(task_id, name, description, script_filenames)
        return jsonify({'success': success, 'message': message}), 200 if success else 400
    except Exception as e:
        logger.error(f"更新数据库任务失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/db/<int:task_id>/execute', methods=['POST'])
def execute_db_task(task_id):
    """通过数据库任务编排执行任务"""
    try:
        data = request.get_json() or {}
        context = data.get('context', {})
        run_id, message = current_app.task_manager.execute_db_task(task_id, context)
        if run_id:
            return jsonify({'success': True, 'message': message, 'run_id': run_id}), 202
        else:
            return jsonify({'success': False, 'message': message}), 400
    except Exception as e:
        logger.error(f"数据库任务执行失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/db/<int:task_id>/runs', methods=['GET'])
def get_db_task_runs(task_id):
    """获取数据库任务的所有运行记录"""
    try:
        runs = current_app.task_manager.task_service.get_task_runs(task_id)
        return jsonify({'success': True, 'data': [
            {
                'run_id': r.id,
                'status': r.status,
                'started_at': r.started_at,
                'finished_at': r.finished_at,
                'initial_context': r.initial_context,
                'final_context': r.final_context
            } for r in runs
        ]})
    except Exception as e:
        logger.error(f"获取数据库任务运行记录失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/db/runs/<int:run_id>/logs', methods=['GET'])
def get_db_run_logs(run_id):
    """获取某次数据库任务运行的所有脚本日志"""
    try:
        logs = current_app.task_manager.task_service.get_run_logs(run_id)
        # logs now returned as list of dicts with keys: script, output, created_at
        return jsonify({'success': True, 'data': logs})
    except Exception as e:
        logger.error(f"获取数据库任务日志失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/db/runs/<int:run_id>/contexts', methods=['GET'])
def get_db_run_contexts(run_id):
    """获取某次数据库任务运行的环境变量历史"""
    try:
        contexts = current_app.task_manager.task_service.get_run_contexts(run_id)
        # contexts returned as list of dicts with keys: script, context, created_at
        return jsonify({'success': True, 'data': contexts})
    except Exception as e:
        logger.error(f"获取数据库任务环境变量历史失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
