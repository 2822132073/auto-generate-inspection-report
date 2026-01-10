"""
巡检数据处理服务
处理巡检记录的增删改查
"""

import json
from models.database import get_db_connection
from config import SCREENSHOTS_DIR


class InspectionService:
    """巡检数据处理服务"""

    @staticmethod
    def create_inspection(data, metadata, options=None):
        """
        创建巡检记录

        Args:
            data: 包含 env 和 commands 的字典
            metadata: 元数据（hostname, ip, timestamp 等）
            options: 可选配置（generate_screenshots, notes）

        Returns:
            dict: 创建的记录信息
        """
        options = options or {}
        generate_screenshots = options.get('generate_screenshots', True)

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # 插入主记录
            cursor.execute('''
                INSERT INTO inspection_records
                (project_id, hostname, ip, os, kernel, arch, timestamp, env_data, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metadata.get('project_id'),
                metadata.get('hostname'),
                metadata.get('ip'),
                metadata.get('os'),
                metadata.get('kernel'),
                metadata.get('arch'),
                metadata.get('timestamp'),
                json.dumps(data.get('env', {}), ensure_ascii=False),
                options.get('notes')
            ))

            record_id = cursor.lastrowid

            # 插入命令执行记录
            commands = data.get('commands', {})
            screenshot_status = 'pending' if generate_screenshots else 'skipped'

            for idx, (cmd_key, cmd_data) in enumerate(commands.items(), 1):
                command = cmd_data.get('command', '')
                output = cmd_data.get('output', '')
                return_code = cmd_data.get('return_code', 0)

                cursor.execute('''
                    INSERT INTO command_executions
                    (record_id, command, output, return_code, screenshot_path, screenshot_status, execution_order)
                    VALUES (?, ?, ?, ?, NULL, ?, ?)
                ''', (record_id, command, output, return_code, screenshot_status, idx))

            return {
                'id': record_id,
                'hostname': metadata.get('hostname'),
                'timestamp': metadata.get('timestamp'),
                'commands_count': len(commands),
                'screenshots_pending': len(commands) if generate_screenshots else 0
            }

    @staticmethod
    def get_inspections(filters=None, page=1, page_size=20, sort_by='timestamp', sort_order='desc'):
        """
        查询巡检记录（支持分页和筛选）

        Args:
            filters: 筛选条件字典 (hostname, project_id, start_date, end_date)
            page: 页码
            page_size: 每页数量
            sort_by: 排序字段
            sort_order: 排序方向 (asc/desc)

        Returns:
            dict: 分页数据
        """
        filters = filters or {}

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # 构建查询条件
            where_clauses = []
            params = []

            if filters.get('hostname'):
                where_clauses.append('hostname = ?')
                params.append(filters['hostname'])

            if filters.get('project_id'):
                where_clauses.append('project_id = ?')
                params.append(filters['project_id'])

            if filters.get('start_date'):
                where_clauses.append('timestamp >= ?')
                params.append(filters['start_date'])

            if filters.get('end_date'):
                where_clauses.append('timestamp <= ?')
                params.append(filters['end_date'])

            where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

            # 查询总数
            count_query = f"SELECT COUNT(*) FROM inspection_records {where_sql}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]

            # 查询数据
            offset = (page - 1) * page_size
            order_sql = f"ORDER BY {sort_by} {sort_order.upper()}"

            data_query = f'''
                SELECT id, project_id, hostname, ip, os, kernel, arch,
                       timestamp, created_at, status, notes,
                       (SELECT COUNT(*) FROM command_executions WHERE record_id = inspection_records.id) as commands_count
                FROM inspection_records
                {where_sql}
                {order_sql}
                LIMIT ? OFFSET ?
            '''

            cursor.execute(data_query, params + [page_size, offset])
            records = [dict(row) for row in cursor.fetchall()]

            return {
                'total': total,
                'page': page,
                'page_size': page_size,
                'records': records
            }

    @staticmethod
    def get_inspection_detail(record_id):
        """获取巡检记录详情（包含所有命令）"""
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # 查询主记录
            cursor.execute('SELECT * FROM inspection_records WHERE id = ?', (record_id,))
            record = cursor.fetchone()

            if not record:
                return None

            # 查询命令记录
            cursor.execute('''
                SELECT * FROM command_executions
                WHERE record_id = ?
                ORDER BY execution_order
            ''', (record_id,))
            commands = [dict(row) for row in cursor.fetchall()]

            result = dict(record)
            result['commands'] = commands
            result['env'] = json.loads(result.get('env_data', '{}'))

            return result

    @staticmethod
    def delete_inspection(record_id):
        """删除巡检记录（级联删除命令和截图）"""
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # 获取截图路径
            cursor.execute('''
                SELECT screenshot_path FROM command_executions
                WHERE record_id = ? AND screenshot_path IS NOT NULL
            ''', (record_id,))

            screenshot_paths = [row[0] for row in cursor.fetchall()]

            # 删除截图文件
            for path in screenshot_paths:
                file_path = SCREENSHOTS_DIR / path
                if file_path.exists():
                    file_path.unlink()

            # 删除数据库记录（级联删除命令）
            cursor.execute('DELETE FROM inspection_records WHERE id = ?', (record_id,))

            return cursor.rowcount > 0

    @staticmethod
    def get_project_latest_hosts(project_id):
        """
        获取项目下所有主机及其最新巡检记录

        Args:
            project_id: 项目ID

        Returns:
            list: 每个主机的最新巡检记录列表
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # 使用子查询获取每个主机的最新记录
            query = '''
                SELECT ir.*
                FROM inspection_records ir
                INNER JOIN (
                    SELECT hostname, MAX(timestamp) as max_timestamp
                    FROM inspection_records
                    WHERE project_id = ?
                    GROUP BY hostname
                ) latest ON ir.hostname = latest.hostname
                          AND ir.timestamp = latest.max_timestamp
                WHERE ir.project_id = ?
                ORDER BY ir.hostname
            '''

            cursor.execute(query, (project_id, project_id))
            records = [dict(row) for row in cursor.fetchall()]

            return records
