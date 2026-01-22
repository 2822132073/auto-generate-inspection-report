"""
巡检数据管理 API 路由
"""

import json
from functools import wraps
from flask import Blueprint, request, jsonify
from services.inspection_service import InspectionService
from services.project_service import ProjectService
from models.database import get_db_connection
from config import PAGE_SIZE_DEFAULT, PAGE_SIZE_MAX
from utils.logger import get_logger

logger = get_logger('api.inspection')

inspection_bp = Blueprint('inspections', __name__)


def handle_api_error(func):
    """统一 API 异常处理装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            logger.warning(f"操作失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 400
        except Exception as e:
            logger.exception(f"操作异常: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    return wrapper


@inspection_bp.route('/inspections', methods=['POST'])
@handle_api_error
def create_inspection():
    """提交巡检数据"""
    # 先尝试正常解析 JSON
    try:
        body = request.get_json()
    except Exception:
        # 如果失败（如包含控制字符），读取原始数据使用 strict=False 解析
        raw_data = request.get_data(as_text=True)
        try:
            body = json.loads(raw_data, strict=False)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON 解析失败: {e}")
            return jsonify({
                'success': False,
                'error': f'JSON 格式错误: {str(e)}'
            }), 400

    if not body:
        return jsonify({'success': False, 'error': '请求体不能为空'}), 400

    data = body.get('data', {})
    metadata = body.get('metadata', {})
    options = body.get('options', {})

    # 验证必需字段
    if not metadata.get('hostname'):
        return jsonify({'success': False, 'error': '缺少必需字段: metadata.hostname'}), 400

    if not metadata.get('timestamp'):
        return jsonify({'success': False, 'error': '缺少必需字段: metadata.timestamp'}), 400

    # 验证项目ID是否存在
    project_id = metadata.get('project_id')
    if project_id:
        resolved_id, resolved_code = ProjectService.resolve_project_id(project_id)

        if not resolved_id:
            return jsonify({
                'success': False,
                'error': f'项目不存在: {project_id}。请先创建项目或检查项目标识是否正确。'
            }), 400

        metadata['project_id'] = resolved_code

    # 创建记录
    result = InspectionService.create_inspection(data, metadata, options)

    logger.info(f"创建巡检记录成功: id={result['id']}, hostname={metadata.get('hostname')}")
    return jsonify({
        'success': True,
        'data': result,
        'message': '巡检数据保存成功'
    }), 201


@inspection_bp.route('/inspections', methods=['GET'])
@handle_api_error
def get_inspections():
    """查询巡检记录"""
    # 获取分页参数
    page = int(request.args.get('page', 1))
    page_size = min(int(request.args.get('page_size', PAGE_SIZE_DEFAULT)), PAGE_SIZE_MAX)

    # 获取筛选条件
    filters = {
        k: v for k, v in [
            ('hostname', request.args.get('hostname')),
            ('project_id', request.args.get('project_id')),
            ('start_date', request.args.get('start_date')),
            ('end_date', request.args.get('end_date'))
        ] if v
    }

    # 排序
    sort_by = request.args.get('sort_by', 'timestamp')
    sort_order = request.args.get('sort_order', 'desc')

    # 查询数据
    result = InspectionService.get_inspections(filters, page, page_size, sort_by, sort_order)

    return jsonify({'success': True, 'data': result}), 200


@inspection_bp.route('/inspections/<int:record_id>', methods=['GET'])
@handle_api_error
def get_inspection_detail(record_id):
    """获取巡检记录详情"""
    result = InspectionService.get_inspection_detail(record_id)

    if not result:
        return jsonify({'success': False, 'error': '记录不存在'}), 404

    return jsonify({'success': True, 'data': result}), 200


@inspection_bp.route('/inspections/<int:record_id>', methods=['DELETE'])
@handle_api_error
def delete_inspection(record_id):
    """删除巡检记录"""
    success = InspectionService.delete_inspection(record_id)

    if not success:
        return jsonify({'success': False, 'error': '记录不存在'}), 404

    logger.info(f"删除巡检记录成功: id={record_id}")
    return jsonify({'success': True, 'message': '删除成功'}), 200


@inspection_bp.route('/inspections/<int:record_id>/screenshot-status', methods=['GET'])
@handle_api_error
def get_screenshot_status(record_id):
    """查询截图生成状态"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT screenshot_status, COUNT(*) as count
            FROM command_executions
            WHERE record_id = ?
            GROUP BY screenshot_status
        ''', (record_id,))

        status = {row['screenshot_status']: row['count'] for row in cursor.fetchall()}

    # 统一构建所有状态
    all_statuses = ['pending', 'processing', 'completed', 'failed', 'skipped']
    status_data = {s: status.get(s, 0) for s in all_statuses}

    return jsonify({'success': True, 'data': status_data}), 200


@inspection_bp.route('/inspections/<int:record_id>/regenerate-screenshots', methods=['POST'])
@handle_api_error
def regenerate_screenshots(record_id):
    """重新生成截图（将状态改为 pending）"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE command_executions
            SET screenshot_status = 'pending', screenshot_path = NULL
            WHERE record_id = ?
        ''', (record_id,))
        updated = cursor.rowcount

    if updated == 0:
        return jsonify({'success': False, 'error': '记录不存在或无命令'}), 404

    logger.info(f"重置截图状态: record_id={record_id}, count={updated}")
    return jsonify({
        'success': True,
        'message': f'已将 {updated} 个命令的截图状态重置为待生成'
    }), 200
