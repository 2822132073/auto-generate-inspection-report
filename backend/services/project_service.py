"""
项目管理服务
管理项目的增删改查
"""

from datetime import datetime
from models.database import get_db_connection


class ProjectService:
    """项目管理服务"""

    @staticmethod
    def create_project(project_code, project_name, description=None):
        """
        创建新项目
        
        Args:
            project_code: 项目代码（唯一标识，如 "PRJ001"）
            project_name: 项目名称
            description: 项目描述（可选）
            
        Returns:
            dict: 创建的项目信息
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO projects (project_code, project_name, description)
                    VALUES (?, ?, ?)
                ''', (project_code, project_name, description))
                
                project_id = cursor.lastrowid
                
                return {
                    'id': project_id,
                    'project_code': project_code,
                    'project_name': project_name,
                    'description': description,
                    'status': 'active'
                }
            except Exception as e:
                if 'UNIQUE constraint failed' in str(e):
                    raise ValueError(f"项目代码 '{project_code}' 已存在")
                raise

    @staticmethod
    def get_projects(status='active', page=1, page_size=50):
        """
        获取项目列表
        
        Args:
            status: 项目状态筛选 ('active', 'archived', 'all')
            page: 页码
            page_size: 每页数量
            
        Returns:
            dict: 分页数据
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 构建查询条件
            where_clause = ""
            params = []
            
            if status != 'all':
                where_clause = "WHERE status = ?"
                params.append(status)
            
            # 查询总数
            count_query = f"SELECT COUNT(*) FROM projects {where_clause}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]
            
            # 查询数据
            offset = (page - 1) * page_size
            data_query = f'''
                SELECT id, project_code, project_name, description, 
                       created_at, updated_at, status
                FROM projects
                {where_clause}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            '''
            
            cursor.execute(data_query, params + [page_size, offset])
            projects = [dict(row) for row in cursor.fetchall()]
            
            return {
                'total': total,
                'page': page,
                'page_size': page_size,
                'projects': projects
            }

    @staticmethod
    def _get_project_by_field(field_name, field_value, single=True):
        """
        通用项目查询方法

        Args:
            field_name: 字段名 (id, project_code, project_name)
            field_value: 字段值
            single: 是否返回单个结果（True）或列表（False，仅用于模糊查询）

        Returns:
            dict 或 list: 项目信息
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()

            if field_name == 'project_name' and not single:
                # 模糊查询
                cursor.execute('''
                    SELECT id, project_code, project_name, description,
                           created_at, updated_at, status
                    FROM projects
                    WHERE project_name LIKE ?
                    ORDER BY created_at DESC
                ''', (f'%{field_value}%',))
                return [dict(row) for row in cursor.fetchall()]

            # 精确查询
            cursor.execute(f'''
                SELECT id, project_code, project_name, description,
                       created_at, updated_at, status
                FROM projects
                WHERE {field_name} = ?
            ''', (field_value,))

            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_project(project_id):
        """
        获取项目详情（通过ID）

        Args:
            project_id: 项目ID

        Returns:
            dict: 项目信息，不存在返回 None
        """
        return ProjectService._get_project_by_field('id', project_id)

    @staticmethod
    def get_project_by_code(project_code):
        """
        根据项目代码获取项目

        Args:
            project_code: 项目代码

        Returns:
            dict: 项目信息，不存在返回 None
        """
        return ProjectService._get_project_by_field('project_code', project_code)

    @staticmethod
    def get_project_by_name(project_name):
        """
        根据项目名称获取项目（支持模糊查询）

        Args:
            project_name: 项目名称

        Returns:
            list: 匹配的项目列表
        """
        return ProjectService._get_project_by_field('project_name', project_name, single=False)

    @staticmethod
    def resolve_project_id(project_identifier):
        """
        解析项目标识符，返回项目ID
        支持输入：项目ID（整数/数字字符串）、项目代码（字符串）、项目名称（字符串）
        
        Args:
            project_identifier: 项目标识符（ID/代码/名称）
            
        Returns:
            tuple: (project_id, project_code) 或 (None, None)
        """
        # 1. 尝试作为整数ID（支持 int 和数字字符串）
        try:
            pid = int(project_identifier)
            project = ProjectService.get_project(pid)
            if project:
                return project['id'], project['project_code']
        except (ValueError, TypeError):
            pass
        
        # 2. 作为字符串处理
        if isinstance(project_identifier, str):
            # 2.1 尝试按项目代码查询
            project = ProjectService.get_project_by_code(project_identifier)
            if project:
                return project['id'], project['project_code']
            
            # 2.2 尝试按项目名称查询
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, project_code FROM projects WHERE project_name = ?
                ''', (project_identifier,))
                row = cursor.fetchone()
                if row:
                    return row['id'], row['project_code']
        
        return None, None

    @staticmethod
    def update_project(project_id, project_name=None, description=None, status=None):
        """
        更新项目信息
        
        Args:
            project_id: 项目ID
            project_name: 新项目名称（可选）
            description: 新描述（可选）
            status: 新状态（可选）
            
        Returns:
            bool: 是否更新成功
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 检查项目是否存在
            cursor.execute('SELECT id FROM projects WHERE id = ?', (project_id,))
            if not cursor.fetchone():
                return False
            
            updates = []
            params = []
            
            if project_name is not None:
                updates.append('project_name = ?')
                params.append(project_name)
            
            if description is not None:
                updates.append('description = ?')
                params.append(description)
            
            if status is not None:
                updates.append('status = ?')
                params.append(status)
            
            if updates:
                updates.append('updated_at = ?')
                params.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                params.append(project_id)
                
                query = f"UPDATE projects SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
            
            return True

    @staticmethod
    def delete_project(project_id):
        """
        删除项目（软删除，标记为 archived）
        
        Args:
            project_id: 项目ID
            
        Returns:
            bool: 是否删除成功
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 软删除：将状态设置为 archived
            cursor.execute('''
                UPDATE projects 
                SET status = 'archived', updated_at = ?
                WHERE id = ?
            ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), project_id))
            
            return cursor.rowcount > 0

    @staticmethod
    def get_project_statistics(project_id):
        """
        获取项目统计信息
        
        Args:
            project_id: 项目ID
            
        Returns:
            dict: 统计信息
        """
        project = ProjectService.get_project(project_id)
        if not project:
            return None
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            project_code = project['project_code']
            
            # 统计巡检记录数
            cursor.execute('''
                SELECT COUNT(*) FROM inspection_records WHERE project_id = ?
            ''', (project_code,))
            total_inspections = cursor.fetchone()[0]
            
            # 统计主机数
            cursor.execute('''
                SELECT COUNT(DISTINCT hostname) FROM inspection_records WHERE project_id = ?
            ''', (project_code,))
            total_hosts = cursor.fetchone()[0]
            
            # 统计报告数
            cursor.execute('''
                SELECT COUNT(*) FROM report_generations WHERE project_id = ?
            ''', (project_code,))
            total_reports = cursor.fetchone()[0]
            
            # 获取最新巡检时间
            cursor.execute('''
                SELECT MAX(timestamp) FROM inspection_records WHERE project_id = ?
            ''', (project_code,))
            latest_inspection = cursor.fetchone()[0]
            
            return {
                'project': project,
                'statistics': {
                    'total_inspections': total_inspections,
                    'total_hosts': total_hosts,
                    'total_reports': total_reports,
                    'latest_inspection': latest_inspection
                }
            }
