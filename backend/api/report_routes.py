"""
报告生成和下载 API 路由
"""

from functools import wraps
from flask import Blueprint, request, jsonify, send_file
from services.report_service import ReportService
from services.inspection_service import InspectionService
from services.project_service import ProjectService
from config import REPORTS_DIR
from utils.logger import get_logger

logger = get_logger('api.report')

report_bp = Blueprint('reports', __name__)


def resolve_query_project_id(project_identifier):
    """
    解析并返回用于查询的项目ID
    优先使用解析后的项目代码，否则使用原始标识符（向后兼容）
    """
    _, project_code = ProjectService.resolve_project_id(project_identifier)
    return project_code if project_code else project_identifier


@report_bp.route('/projects/<project_id>/hosts', methods=['GET'])
def get_project_hosts(project_id):
    """
    获取项目下所有主机列表及最新巡检时间
    支持通过项目 ID、项目代码或项目名称查询
    """
    try:
        query_project_id = resolve_query_project_id(project_id)
        records = InspectionService.get_project_latest_hosts(query_project_id)

        # 提取主机信息
        hosts = [
            {
                'hostname': r['hostname'],
                'ip': r.get('ip'),
                'os': r.get('os'),
                'kernel': r.get('kernel'),
                'arch': r.get('arch'),
                'timestamp': r['timestamp'],
                'latest_timestamp': r['timestamp'],
                'record_id': r['id']
            }
            for r in records
        ]

        return jsonify({
            'success': True,
            'data': {
                'project_id': project_id,
                'host_count': len(hosts),
                'hosts': hosts
            }
        }), 200

    except Exception as e:
        logger.exception(f"获取项目主机列表异常: project_id={project_id}, {e}")
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
        template_id = body.get('template_id')

        project_db_id, project_code = ProjectService.resolve_project_id(project_id)
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
        logger.warning(f"生成项目报告失败: project_id={project_id}, {e}")
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        logger.exception(f"生成项目报告异常: project_id={project_id}, {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@report_bp.route('/projects/<project_id>/report', methods=['GET'])
def download_project_report(project_id):
    """
    下载项目最新报告
    支持通过项目 ID、项目代码或项目名称查询
    """
    try:
        query_project_id = resolve_query_project_id(project_id)
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
        logger.exception(f"下载项目报告异常: project_id={project_id}, {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
