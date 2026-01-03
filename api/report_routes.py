"""
报告生成和下载 API 路由
"""

from flask import Blueprint, request, jsonify, send_file
from services.report_service import ReportService
from services.inspection_service import InspectionService
from services.project_service import ProjectService
from config import REPORTS_DIR

report_bp = Blueprint('reports', __name__)


@report_bp.route('/projects/<project_id>/hosts', methods=['GET'])
def get_project_hosts(project_id):
    """
    获取项目下所有主机列表及最新巡检时间
    支持通过项目 ID、项目代码或项目名称查询
    """
    try:
        # 解析项目标识符，获取项目代码
        _, project_code = ProjectService.resolve_project_id(project_id)
        
        # 如果解析失败，尝试直接使用原始 project_id（向后兼容）
        query_project_id = project_code if project_code else project_id
        
        records = InspectionService.get_project_latest_hosts(query_project_id)

        # 提取主机信息
        hosts = []
        for record in records:
            hosts.append({
                'hostname': record['hostname'],
                'ip': record.get('ip'),
                'os': record.get('os'),
                'kernel': record.get('kernel'),
                'arch': record.get('arch'),
                'timestamp': record['timestamp'],
                'latest_timestamp': record['timestamp'],
                'record_id': record['id']
            })

        return jsonify({
            'success': True,
            'data': {
                'project_id': project_id,
                'host_count': len(hosts),
                'hosts': hosts
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@report_bp.route('/projects/<project_id>/report', methods=['POST'])
def generate_project_report(project_id):
    """
    生成项目巡检报告
    支持通过项目 ID、项目代码或项目名称查询
    
    请求体:
    {
        "options": {
            "title": "自定义标题",
            "include_screenshots": true
        },
        "template_id": 1  // 可选，指定使用的模板ID，不指定则使用默认模板
    }
    """
    try:
        body = request.get_json() or {}
        options = body.get('options', {})
        template_id = body.get('template_id')  # 支持模板ID

        # 解析项目标识符，获取项目代码
        project_db_id, project_code = ProjectService.resolve_project_id(project_id)
        
        # 如果解析成功，使用项目代码；否则使用原始 project_id（向后兼容）
        query_project_id = project_code if project_code else project_id
        
        # 如果解析到了项目信息，将项目名称添加到 options 中
        if project_db_id:
            project_info = ProjectService.get_project(project_db_id)
            if project_info and 'title' not in options:
                options['title'] = project_info['project_name']

        # 生成报告
        result = ReportService.generate_project_report(
            project_id=query_project_id,
            options=options,
            template_id=template_id
        )

        return jsonify({
            'success': True,
            'data': {
                'report_id': result['report_id'],
                'download_url': f'/api/v1/projects/{project_id}/report',
                'file_size': result['file_size'],
                'host_count': result['host_count'],
                'generated_at': result['generated_at'],
                'template_id': template_id
            },
            'message': '报告生成成功'
        }), 201

    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@report_bp.route('/projects/<project_id>/report', methods=['GET'])
def download_project_report(project_id):
    """
    下载项目最新报告
    支持通过项目 ID、项目代码或项目名称查询
    """
    try:
        # 解析项目标识符
        _, project_code = ProjectService.resolve_project_id(project_id)
        query_project_id = project_code if project_code else project_id
        
        # 获取最新报告路径
        report_path = ReportService.get_latest_project_report(query_project_id)

        if not report_path:
            return jsonify({'success': False, 'error': '项目报告不存在'}), 404

        file_path = REPORTS_DIR / report_path

        if not file_path.exists():
            return jsonify({'success': False, 'error': '报告文件不存在'}), 404

        return send_file(
            file_path,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=f'inspection_report_{project_id}.docx'
        )

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
