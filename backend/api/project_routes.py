"""
项目管理 API 路由
提供项目管理的 REST 接口
"""

from flask import Blueprint, request, jsonify
from services.project_service import ProjectService

project_bp = Blueprint('projects', __name__)


@project_bp.route('/projects', methods=['POST'])
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
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': '请求体不能为空'}), 400
        
        project_code = data.get('project_code')
        project_name = data.get('project_name')
        description = data.get('description')
        
        if not project_code:
            return jsonify({'success': False, 'error': '缺少必需字段: project_code'}), 400
        
        if not project_name:
            return jsonify({'success': False, 'error': '缺少必需字段: project_name'}), 400
        
        project = ProjectService.create_project(project_code, project_name, description)
        
        return jsonify({
            'success': True,
            'message': '项目创建成功',
            'data': project
        }), 201
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500


@project_bp.route('/projects', methods=['GET'])
def get_projects():
    """
    获取项目列表
    
    查询参数:
    - status: 项目状态 (active/archived/all, 默认 active)
    - page: 页码 (默认 1)
    - page_size: 每页数量 (默认 50)
    """
    try:
        status = request.args.get('status', 'active')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 50))
        
        result = ProjectService.get_projects(status=status, page=page, page_size=page_size)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500


@project_bp.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """获取项目详情"""
    try:
        project = ProjectService.get_project(project_id)
        
        if not project:
            return jsonify({'success': False, 'error': '项目不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': project
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500


@project_bp.route('/projects/by-code/<project_code>', methods=['GET'])
def get_project_by_code(project_code):
    """根据项目代码获取项目"""
    try:
        project = ProjectService.get_project_by_code(project_code)
        
        if not project:
            return jsonify({'success': False, 'error': '项目不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': project
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500


@project_bp.route('/projects/search', methods=['GET'])
def search_projects():
    """
    搜索项目（按名称模糊查询）
    
    查询参数:
    - name: 项目名称关键字
    """
    try:
        name = request.args.get('name')
        
        if not name:
            return jsonify({'success': False, 'error': '缺少查询参数: name'}), 400
        
        projects = ProjectService.get_project_by_name(name)
        
        return jsonify({
            'success': True,
            'data': {
                'total': len(projects),
                'projects': projects
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500


@project_bp.route('/projects/<int:project_id>', methods=['PUT'])
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
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': '请求体不能为空'}), 400
        
        project_name = data.get('project_name')
        description = data.get('description')
        status = data.get('status')
        
        success = ProjectService.update_project(
            project_id=project_id,
            project_name=project_name,
            description=description,
            status=status
        )
        
        if not success:
            return jsonify({'success': False, 'error': '项目不存在'}), 404
        
        # 返回更新后的项目
        project = ProjectService.get_project(project_id)
        
        return jsonify({
            'success': True,
            'message': '项目更新成功',
            'data': project
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500


@project_bp.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """删除项目（软删除）"""
    try:
        success = ProjectService.delete_project(project_id)
        
        if not success:
            return jsonify({'success': False, 'error': '项目不存在'}), 404
        
        return jsonify({
            'success': True,
            'message': '项目已归档'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500


@project_bp.route('/projects/<int:project_id>/statistics', methods=['GET'])
def get_project_statistics(project_id):
    """获取项目统计信息"""
    try:
        stats = ProjectService.get_project_statistics(project_id)
        
        if not stats:
            return jsonify({'success': False, 'error': '项目不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500
