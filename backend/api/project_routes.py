"""
项目管理 API 路由
提供项目管理的 REST 接口
"""

from functools import wraps
from flask import Blueprint, request, jsonify
from services.project_service import ProjectService
from utils.logger import get_logger

logger = get_logger('api.project')

project_bp = Blueprint('projects', __name__)


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


def validate_required_fields(data, required_fields):
    """验证必需字段"""
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        raise ValueError(f'缺少必需字段: {", ".join(missing)}')


@project_bp.route('/projects', methods=['POST'])
@handle_api_error
def create_project():
    """
    创建新项目

    请求体:
    {
        "project_code": "PRJ001",
        "project_name": "生产环境监控",
        "description": "生产环境服务器巡检项目"
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': '请求体不能为空'}), 400

    validate_required_fields(data, ['project_code', 'project_name'])

    project = ProjectService.create_project(
        data['project_code'], data['project_name'], data.get('description')
    )

    logger.info(f"创建项目成功: code={data['project_code']}, name={data['project_name']}")
    return jsonify({
        'success': True,
        'message': '项目创建成功',
        'data': project
    }), 201


@project_bp.route('/projects', methods=['GET'])
@handle_api_error
def get_projects():
    """
    获取项目列表

    查询参数:
    - status: 项目状态 (active/archived/all, 默认 active)
    - page: 页码 (默认 1)
    - page_size: 每页数量 (默认 50)
    """
    status = request.args.get('status', 'active')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 50))

    result = ProjectService.get_projects(status=status, page=page, page_size=page_size)

    return jsonify({'success': True, 'data': result}), 200


@project_bp.route('/projects/<int:project_id>', methods=['GET'])
@handle_api_error
def get_project(project_id):
    """获取项目详情"""
    project = ProjectService.get_project(project_id)

    if not project:
        return jsonify({'success': False, 'error': '项目不存在'}), 404

    return jsonify({'success': True, 'data': project}), 200


@project_bp.route('/projects/by-code/<project_code>', methods=['GET'])
@handle_api_error
def get_project_by_code(project_code):
    """根据项目代码获取项目"""
    project = ProjectService.get_project_by_code(project_code)

    if not project:
        return jsonify({'success': False, 'error': '项目不存在'}), 404

    return jsonify({'success': True, 'data': project}), 200


@project_bp.route('/projects/search', methods=['GET'])
@handle_api_error
def search_projects():
    """
    搜索项目（按名称模糊查询）

    查询参数:
    - name: 项目名称关键字
    """
    name = request.args.get('name')
    if not name:
        return jsonify({'success': False, 'error': '缺少查询参数: name'}), 400

    projects = ProjectService.get_project_by_name(name)

    return jsonify({
        'success': True,
        'data': {'total': len(projects), 'projects': projects}
    }), 200


@project_bp.route('/projects/<int:project_id>', methods=['PUT'])
@handle_api_error
def update_project(project_id):
    """
    更新项目信息

    请求体:
    {
        "project_name": "新项目名称",  // 可选
        "description": "新描述",       // 可选
        "status": "archived"           // 可选
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': '请求体不能为空'}), 400

    success = ProjectService.update_project(
        project_id=project_id,
        project_name=data.get('project_name'),
        description=data.get('description'),
        status=data.get('status')
    )

    if not success:
        return jsonify({'success': False, 'error': '项目不存在'}), 404

    project = ProjectService.get_project(project_id)
    logger.info(f"更新项目成功: id={project_id}")

    return jsonify({
        'success': True,
        'message': '项目更新成功',
        'data': project
    }), 200


@project_bp.route('/projects/<int:project_id>', methods=['DELETE'])
@handle_api_error
def delete_project(project_id):
    """删除项目（软删除）"""
    success = ProjectService.delete_project(project_id)

    if not success:
        return jsonify({'success': False, 'error': '项目不存在'}), 404

    logger.info(f"删除项目成功: id={project_id}")
    return jsonify({'success': True, 'message': '项目已归档'}), 200


@project_bp.route('/projects/<int:project_id>/statistics', methods=['GET'])
@handle_api_error
def get_project_statistics(project_id):
    """获取项目统计信息"""
    stats = ProjectService.get_project_statistics(project_id)

    if not stats:
        return jsonify({'success': False, 'error': '项目不存在'}), 404

    return jsonify({'success': True, 'data': stats}), 200
