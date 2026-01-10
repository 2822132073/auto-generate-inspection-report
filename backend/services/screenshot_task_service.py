"""
截图任务处理服务
异步处理截图生成任务
"""

import json
from models.database import get_db_connection
from services.screenshot_service import ScreenshotService
from utils.logger import get_logger

logger = get_logger('services.screenshot_task')


class ScreenshotTaskService:
    """截图任务处理服务"""

    @staticmethod
    def get_pending_tasks(limit=10):
        """获取待处理的截图任务"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT ce.id, ce.record_id, ce.command, ce.output, ce.return_code,
                       ce.execution_order, ir.env_data
                FROM command_executions ce
                JOIN inspection_records ir ON ce.record_id = ir.id
                WHERE ce.screenshot_status = 'pending'
                ORDER BY ce.created_at
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def process_task(task):
        """处理单个截图任务"""
        command_id = task['id']

        # 标记为处理中
        with get_db_connection() as conn:
            conn.execute(
                "UPDATE command_executions SET screenshot_status = 'processing' WHERE id = ?",
                (command_id,)
            )

        try:
            env = json.loads(task['env_data']) if task['env_data'] else {}
            screenshot_path = ScreenshotService.generate_and_save(
                record_id=task['record_id'],
                env=env,
                command=task['command'],
                output=task['output'],
                return_code=task['return_code'],
                order=task['execution_order']
            )

            # 更新为完成
            with get_db_connection() as conn:
                conn.execute('''
                    UPDATE command_executions
                    SET screenshot_path = ?, screenshot_status = 'completed'
                    WHERE id = ?
                ''', (screenshot_path, command_id))

        except Exception as e:
            logger.error(f"截图生成失败 [command_id={command_id}]: {e}")
            with get_db_connection() as conn:
                conn.execute(
                    "UPDATE command_executions SET screenshot_status = 'failed' WHERE id = ?",
                    (command_id,)
                )

    @staticmethod
    def process_all_pending():
        """处理所有待处理任务，返回处理数量"""
        processed = 0
        while True:
            tasks = ScreenshotTaskService.get_pending_tasks(limit=5)
            if not tasks:
                break
            logger.info(f"发现 {len(tasks)} 个待处理截图任务")
            for task in tasks:
                logger.debug(f"处理截图任务: command_id={task['id']}, command={task['command'][:30]}")
                ScreenshotTaskService.process_task(task)
                processed += 1
        return processed
