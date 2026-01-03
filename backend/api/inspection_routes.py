"""
巡检数据管理 API 路由
"""

from flask import Blueprint, request, jsonify
from services.inspection_service import InspectionService
from services.project_service import ProjectService
from config import PAGE_SIZE_DEFAULT, PAGE_SIZE_MAX

inspection_bp = Blueprint('inspections', __name__)


@inspection_bp.route('/inspections', methods=['POST'])
def create_inspection():
    """提交巡检数据"""
    try:
        body = request.get_json()

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
            # 使用 resolve_project_id 支持多种格式（ID/代码/名称）
            resolved_id, resolved_code = ProjectService.resolve_project_id(project_id)
            
            if not resolved_id:
                return jsonify({
                    'success': False, 
                    'error': f'项目不存在: {project_id}。请先创建项目或检查项目标识是否正确。'
                }), 400
            
            # 使用解析后的项目代码（统一使用 project_code）
            metadata['project_id'] = resolved_code

        # 创建记录
        result = InspectionService.create_inspection(data, metadata, options)

        return jsonify({
            'success': True,
            'data': result,
            'message': '巡检数据保存成功'
        }), 201

    except ValueError as e:
        # 业务逻辑错误
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        # 服务器内部错误
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500


@inspection_bp.route('/inspections', methods=['GET'])
def get_inspections():
    """查询巡检记录"""
    try:
        # 获取分页参数
        page = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('page_size', PAGE_SIZE_DEFAULT)), PAGE_SIZE_MAX)

        # 获取筛选条件
        filters = {}
        if request.args.get('hostname'):
            filters['hostname'] = request.args.get('hostname')
        if request.args.get('project_id'):
            filters['project_id'] = request.args.get('project_id')
        if request.args.get('start_date'):
            filters['start_date'] = request.args.get('start_date')
        if request.args.get('end_date'):
            filters['end_date'] = request.args.get('end_date')

        # 排序
        sort_by = request.args.get('sort_by', 'timestamp')
        sort_order = request.args.get('sort_order', 'desc')

        # 查询数据
        result = InspectionService.get_inspections(filters, page, page_size, sort_by, sort_order)

        return jsonify({'success': True, 'data': result}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@inspection_bp.route('/inspections/<int:record_id>', methods=['GET'])
def get_inspection_detail(record_id):
    """获取巡检记录详情"""
    try:
        result = InspectionService.get_inspection_detail(record_id)

        if not result:
            return jsonify({'success': False, 'error': '记录不存在'}), 404

        return jsonify({'success': True, 'data': result}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@inspection_bp.route('/inspections/<int:record_id>', methods=['DELETE'])
def delete_inspection(record_id):
    """删除巡检记录"""
    try:
        success = InspectionService.delete_inspection(record_id)

        if not success:
            return jsonify({'success': False, 'error': '记录不存在'}), 404

        return jsonify({'success': True, 'message': '删除成功'}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
