"""
报告模板 API 路由
提供模板管理的 REST 接口
"""

from flask import Blueprint, request, jsonify
from services.template_service import TemplateService

template_bp = Blueprint('templates', __name__)


@template_bp.route('/templates', methods=['POST'])
def create_template():
    """
    创建新模板
    
    请求体:
    {
        "name": "custom_template",
        "description": "自定义模板描述",
        "config": {
            "include_return_code": true,
            "include_output": true,
            "include_screenshots": true,
            "title_format": "巡检报告 - {project_id}",
            "section_organization": "by_host",
            "custom_fields": []
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': '请求体不能为空'}), 400
        
        name = data.get('name')
        description = data.get('description', '')
        config = data.get('config')
        
        if not name:
            return jsonify({'success': False, 'error': '缺少必需字段: name'}), 400
        
        if not config:
            return jsonify({'success': False, 'error': '缺少必需字段: config'}), 400
        
        template = TemplateService.create_template(name, description, config)
        
        return jsonify({
            'success': True,
            'message': '模板创建成功',
            'data': template
        }), 201
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500


@template_bp.route('/templates', methods=['GET'])
def get_templates():
    """
    获取模板列表
    
    查询参数:
    - include_config: 是否包含详细配置 (true/false, 默认 true)
    """
    try:
        include_config = request.args.get('include_config', 'true').lower() == 'true'
        
        templates = TemplateService.get_templates(include_config=include_config)
        
        return jsonify({
            'success': True,
            'data': {
                'total': len(templates),
                'templates': templates
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500


@template_bp.route('/templates/<int:template_id>', methods=['GET'])
def get_template(template_id):
    """获取模板详情"""
    try:
        template = TemplateService.get_template(template_id)
        
        if not template:
            return jsonify({'success': False, 'error': '模板不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': template
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500


@template_bp.route('/templates/by-name/<name>', methods=['GET'])
def get_template_by_name(name):
    """根据名称获取模板"""
    try:
        template = TemplateService.get_template_by_name(name)
        
        if not template:
            return jsonify({'success': False, 'error': '模板不存在'}), 404
        
        return jsonify({
            'success': True,
            'data': template
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500


@template_bp.route('/templates/default', methods=['GET'])
def get_default_template():
    """获取默认模板"""
    try:
        template = TemplateService.get_default_template()
        
        if not template:
            return jsonify({'success': False, 'error': '未设置默认模板'}), 404
        
        return jsonify({
            'success': True,
            'data': template
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500


@template_bp.route('/templates/<int:template_id>', methods=['PUT'])
def update_template(template_id):
    """
    更新模板
    
    请求体:
    {
        "name": "new_name",  // 可选
        "description": "new description",  // 可选
        "config": {...},  // 可选
        "is_default": true  // 可选
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': '请求体不能为空'}), 400
        
        name = data.get('name')
        description = data.get('description')
        config = data.get('config')
        is_default = data.get('is_default')
        
        success = TemplateService.update_template(
            template_id=template_id,
            name=name,
            description=description,
            config=config,
            is_default=is_default
        )
        
        if not success:
            return jsonify({'success': False, 'error': '模板不存在'}), 404
        
        # 返回更新后的模板
        template = TemplateService.get_template(template_id)
        
        return jsonify({
            'success': True,
            'message': '模板更新成功',
            'data': template
        }), 200
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500


@template_bp.route('/templates/<int:template_id>', methods=['DELETE'])
def delete_template(template_id):
    """删除模板"""
    try:
        success = TemplateService.delete_template(template_id)
        
        if not success:
            return jsonify({'success': False, 'error': '模板不存在'}), 404
        
        return jsonify({
            'success': True,
            'message': '模板删除成功'
        }), 200
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500
