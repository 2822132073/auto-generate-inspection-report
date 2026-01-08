"""
截图生成服务
封装现有截图生成功能，保存到文件系统
"""

from pathlib import Path
from datetime import datetime
from utils.screenshot_generator import generate_screenshot_bytes, sanitize_filename
from config import SCREENSHOTS_DIR, DEFAULT_FONT_FILE, DEFAULT_SCALE_FACTOR


class ScreenshotService:
    """截图生成服务（封装现有功能）"""

    @staticmethod
    def generate_and_save(record_id, env, command, output, return_code, order):
        """
        生成截图并保存到文件系统

        Args:
            record_id: 巡检记录ID
            env: 环境变量字典
            command: 命令字符串
            output: 命令输出
            return_code: 返回码
            order: 执行顺序

        Returns:
            str: 相对路径（用于存储到数据库）
        """
        # 生成截图字节流
        screenshot_bytes = generate_screenshot_bytes(
            env=env,
            command=command,
            output=output,
            return_code=return_code,
            font_file=DEFAULT_FONT_FILE,
            scale_factor=DEFAULT_SCALE_FACTOR
        )

        # 构建文件路径（按月份组织）
        month_dir = datetime.now().strftime('%Y-%m')
        save_dir = SCREENSHOTS_DIR / month_dir
        save_dir.mkdir(exist_ok=True, parents=True)

        # 文件名：记录ID_顺序_命令名.png
        safe_command = sanitize_filename(command)
        if not safe_command:
            safe_command = f"command_{order}"

        filename = f"{record_id}_{order:02d}_{safe_command}.png"
        file_path = save_dir / filename

        # 保存文件
        with open(file_path, 'wb') as f:
            f.write(screenshot_bytes)
        print(f"截图已保存: {file_path}")

        # 返回相对路径
        return f"{month_dir}/{filename}"
