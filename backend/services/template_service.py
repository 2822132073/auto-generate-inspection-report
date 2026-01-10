"""
报告模板服务
管理报告模板的增删改查和默认模板初始化
"""

import json
from datetime import datetime
from models.database import get_db_connection


class TemplateService:
    """报告模板服务"""

    # 默认模板配置
    DEFAULT_TEMPLATES = [
        {
            'name': 'standard',
            'description': '标准模板 - 包含所有信息（返回码、执行结果、截图）',
            'config': {
                'include_return_code': True,
                'include_output': True,
                'include_screenshots': True,
                'title_format': '服务器巡检报告 - {project_id}',
                'section_organization': 'by_host',  # by_host 或 by_command
                'custom_fields': []
            },
            'is_default': False
        },
        {
            'name': 'simplified',
            'description': '简化模板 - 只显示命令和截图，不显示返回码和文本输出',
            'config': {
                'include_return_code': False,
                'include_output': False,
                'include_screenshots': True,
                'title_format': '服务器巡检报告（简化版） - {project_id}',
                'section_organization': 'by_host',
                'custom_fields': []
            },
            'is_default': True
        },
        {
            'name': 'screenshot_only',
            'description': '纯截图模板 - 只包含截图，不包含任何文本信息',
            'config': {
                'include_return_code': False,
                'include_output': False,
                'include_screenshots': True,
                'show_command_title': False,
                'title_format': '{project_id} 巡检截图',
                'section_organization': 'by_host',
                'custom_fields': []
            },
            'is_default': False
        }
    ]

    @staticmethod
    def init_default_templates():
        """初始化默认模板（如果不存在）"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            for template_def in TemplateService.DEFAULT_TEMPLATES:
                # 检查模板是否已存在
                cursor.execute('SELECT id FROM report_templates WHERE name = ?', (template_def['name'],))
                if cursor.fetchone():
                    continue
                
                # 插入默认模板
                cursor.execute('''
                    INSERT INTO report_templates (name, description, config, is_default)
                    VALUES (?, ?, ?, ?)
                ''', (
                    template_def['name'],
                    template_def['description'],
                    json.dumps(template_def['config'], ensure_ascii=False),
                    1 if template_def['is_default'] else 0
                ))

    @staticmethod
    def create_template(name, description, config):
        """
        创建新模板
        
        Args:
            name: 模板名称（唯一）
            description: 模板描述
            config: 模板配置字典
            
        Returns:
            dict: 创建的模板信息
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 验证配置
            TemplateService._validate_config(config)
            
            try:
                cursor.execute('''
                    INSERT INTO report_templates (name, description, config)
                    VALUES (?, ?, ?)
                ''', (name, description, json.dumps(config, ensure_ascii=False)))
                
                template_id = cursor.lastrowid
                
                return {
                    'id': template_id,
                    'name': name,
                    'description': description,
                    'config': config,
                    'is_default': False
                }
            except Exception as e:
                if 'UNIQUE constraint failed' in str(e):
                    raise ValueError(f"模板名称 '{name}' 已存在")
                raise

    @staticmethod
    def get_templates(include_config=True):
        """
        获取所有模板列表
        
        Args:
            include_config: 是否包含详细配置
            
        Returns:
            list: 模板列表
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if include_config:
                cursor.execute('''
                    SELECT id, name, description, config, is_default, created_at, updated_at
                    FROM report_templates
                    ORDER BY is_default DESC, created_at DESC
                ''')
            else:
                cursor.execute('''
                    SELECT id, name, description, is_default, created_at
                    FROM report_templates
                    ORDER BY is_default DESC, created_at DESC
                ''')
            
            templates = []
            for row in cursor.fetchall():
                template = dict(row)
                if include_config and 'config' in template:
                    template['config'] = json.loads(template['config'])
                templates.append(template)
            
            return templates

    @staticmethod
    def _fetch_and_parse_template(where_clause, params):
        """
        通用模板查询和解析方法

        Args:
            where_clause: WHERE 子句
            params: 查询参数

        Returns:
            dict: 模板信息，不存在返回 None
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT id, name, description, config, is_default, created_at, updated_at
                FROM report_templates
                WHERE {where_clause}
            ''', params)
            row = cursor.fetchone()

            if not row:
                return None

            template = dict(row)
            template['config'] = json.loads(template['config'])
            return template

    @staticmethod
    def get_template(template_id):
        """获取模板详情"""
        return TemplateService._fetch_and_parse_template('id = ?', (template_id,))

    @staticmethod
    def get_template_by_name(name):
        """根据名称获取模板"""
        return TemplateService._fetch_and_parse_template('name = ?', (name,))

    @staticmethod
    def get_default_template():
        """获取默认模板"""
        return TemplateService._fetch_and_parse_template('is_default = 1 LIMIT 1', ())

    @staticmethod
    def update_template(template_id, name=None, description=None, config=None, is_default=None):
        """
        更新模板
        
        Args:
            template_id: 模板ID
            name: 新名称（可选）
            description: 新描述（可选）
            config: 新配置（可选）
            is_default: 是否设为默认（可选）
            
        Returns:
            bool: 是否更新成功
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 检查模板是否存在
            cursor.execute('SELECT id FROM report_templates WHERE id = ?', (template_id,))
            if not cursor.fetchone():
                return False
            
            updates = []
            params = []
            
            if name is not None:
                updates.append('name = ?')
                params.append(name)
            
            if description is not None:
                updates.append('description = ?')
                params.append(description)
            
            if config is not None:
                TemplateService._validate_config(config)
                updates.append('config = ?')
                params.append(json.dumps(config, ensure_ascii=False))
            
            if is_default is not None:
                # 如果设为默认，先取消其他模板的默认状态
                if is_default:
                    cursor.execute('UPDATE report_templates SET is_default = 0')
                updates.append('is_default = ?')
                params.append(1 if is_default else 0)
            
            if updates:
                updates.append('updated_at = ?')
                params.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                params.append(template_id)
                
                query = f"UPDATE report_templates SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
            
            return True

    @staticmethod
    def delete_template(template_id):
        """删除模板"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 检查是否为默认模板
            cursor.execute('SELECT is_default FROM report_templates WHERE id = ?', (template_id,))
            row = cursor.fetchone()
            
            if not row:
                return False
            
            if row['is_default']:
                raise ValueError("不能删除默认模板")
            
            cursor.execute('DELETE FROM report_templates WHERE id = ?', (template_id,))
            
            return cursor.rowcount > 0

    @staticmethod
    def _validate_config(config):
        """验证模板配置格式"""
        required_fields = [
            'include_return_code',
            'include_output',
            'include_screenshots',
            'title_format',
            'section_organization'
        ]
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"配置缺少必需字段: {field}")
        
        # 验证布尔值字段
        bool_fields = ['include_return_code', 'include_output', 'include_screenshots']
        for field in bool_fields:
            if not isinstance(config[field], bool):
                raise ValueError(f"字段 {field} 必须是布尔值")
        
        # 验证字符串字段
        if not isinstance(config['title_format'], str):
            raise ValueError("title_format 必须是字符串")
        
        # 验证 section_organization
        valid_orgs = ['by_host', 'by_command']
        if config['section_organization'] not in valid_orgs:
            raise ValueError(f"section_organization 必须是 {valid_orgs} 之一")
