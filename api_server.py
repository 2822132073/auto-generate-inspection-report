#!/usr/bin/env python3
"""
HTTP API 服务器
提供终端截图生成和巡检报告管理服务
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO
import sys
import os
from pathlib import Path
from generate_terminal_screenshot import generate_screenshot_bytes
from models.database import init_database, get_db_connection
from api.inspection_routes import inspection_bp
from api.report_routes import report_bp
from api.template_routes import template_bp
from api.project_routes import project_bp
from services.template_service import TemplateService
from config import SCREENSHOTS_DIR

app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 默认字体文件
DEFAULT_FONT_FILE = 'OperatorMono-Medium.otf'
DEFAULT_SCALE_FACTOR = 3

# 初始化数据库
print("正在初始化数据库...")
init_database()
print("数据库初始化完成！")

# 初始化默认模板
print("正在初始化默认报告模板...")
TemplateService.init_default_templates()
print("默认模板初始化完成！")

# 注册蓝图
app.register_blueprint(inspection_bp, url_prefix='/api/v1')
app.register_blueprint(report_bp, url_prefix='/api/v1')
app.register_blueprint(template_bp, url_prefix='/api/v1')
app.register_blueprint(project_bp, url_prefix='/api/v1')


# ========== 健康检查 ==========
@app.route('/health', methods=['GET'])
def health():
    """健康检查端点"""
    return jsonify({"status": "ok"}), 200


@app.route('/api/v1/stats', methods=['GET'])
def stats():
    """系统统计信息"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # 统计巡检记录数
            cursor.execute('SELECT COUNT(*) FROM inspection_records')
            total_records = cursor.fetchone()[0]

            # 统计命令执行数
            cursor.execute('SELECT COUNT(*) FROM command_executions')
            total_commands = cursor.fetchone()[0]

            # 统计报告数
            cursor.execute('SELECT COUNT(*) FROM report_generations')
            total_reports = cursor.fetchone()[0]

            # 统计项目数
            cursor.execute('SELECT COUNT(DISTINCT project_id) FROM inspection_records WHERE project_id IS NOT NULL')
            total_projects = cursor.fetchone()[0]

            # 统计主机数
            cursor.execute('SELECT COUNT(DISTINCT hostname) FROM inspection_records')
            total_hosts = cursor.fetchone()[0]

            return jsonify({
                'success': True,
                'data': {
                    'total_inspections': total_records,
                    'total_commands': total_commands,
                    'total_reports': total_reports,
                    'total_projects': total_projects,
                    'total_hosts': total_hosts
                }
            }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ========== 截图访问端点 ==========
@app.route('/api/v1/screenshots/<path:screenshot_path>', methods=['GET'])
def get_screenshot(screenshot_path):
    """
    获取截图文件
    
    路径格式: /api/v1/screenshots/2026-01/18_01_free_-h.png
    """
    try:
        # 构建完整文件路径
        file_path = SCREENSHOTS_DIR / screenshot_path
        
        # 检查文件是否存在
        if not file_path.exists():
            return jsonify({'success': False, 'error': '截图不存在'}), 404
        
        # 检查文件是否在允许的目录内（安全性检查）
        try:
            file_path.resolve().relative_to(SCREENSHOTS_DIR.resolve())
        except ValueError:
            return jsonify({'success': False, 'error': '无效的文件路径'}), 403
        
        # 返回图片文件
        return send_file(
            file_path,
            mimetype='image/png',
            as_attachment=False,
            download_name=file_path.name
        )
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500


# ========== 保留原有截图生成端点 ==========
@app.route('/generate', methods=['POST'])
def generate():
    """
    生成终端截图（保留原有功能）

    请求体格式:
    {
        "env": {
            "USER": "root",
            "PWD": "/root",
            "HOSTNAME": "node-1",
            "PS1": "..."
        },
        "command": {
            "command": "free -h",
            "output": "...",
            "return_code": 0
        },
        "font_file": "OperatorMono-Medium.otf",  // 可选
        "scale_factor": 3  // 可选，默认 3
    }

    响应: PNG 图片（Content-Type: image/png）
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "请求体不能为空"}), 400

        if 'env' not in data:
            return jsonify({"error": "缺少必需字段: env"}), 400

        if 'command' not in data:
            return jsonify({"error": "缺少必需字段: command"}), 400

        env = data['env']
        command_data = data['command']

        if not isinstance(command_data, dict):
            return jsonify({"error": "command 必须是对象"}), 400

        if 'command' not in command_data:
            return jsonify({"error": "command 对象中缺少 'command' 字段"}), 400

        command = command_data.get('command', '')
        output = command_data.get('output', '')
        return_code = command_data.get('return_code', 0)

        font_file = data.get('font_file', DEFAULT_FONT_FILE)
        scale_factor = data.get('scale_factor', DEFAULT_SCALE_FACTOR)

        if font_file != DEFAULT_FONT_FILE:
            script_dir = Path(__file__).parent
            font_path = script_dir / font_file
            if not font_path.exists():
                return jsonify({"error": f"字体文件不存在: {font_file}"}), 400

        try:
            screenshot_bytes = generate_screenshot_bytes(
                env=env,
                command=command,
                output=output,
                return_code=return_code,
                font_file=font_file,
                scale_factor=scale_factor
            )
        except FileNotFoundError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": f"生成截图时出错: {str(e)}"}), 500

        return send_file(
            BytesIO(screenshot_bytes),
            mimetype='image/png',
            as_attachment=False
        )

    except Exception as e:
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    print(f"正在启动服务器，监听 {host}:{port}...")
    app.run(host=host, port=port, debug=False)
