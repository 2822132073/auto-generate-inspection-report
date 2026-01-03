"""
项目配置文件
定义路径、常量和配置参数
"""

import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent

# 数据目录
DATA_DIR = BASE_DIR / 'data'
SCREENSHOTS_DIR = DATA_DIR / 'screenshots'
REPORTS_DIR = DATA_DIR / 'reports'

# 数据库配置
DATABASE_PATH = DATA_DIR / 'inspections.db'

# 字体配置
DEFAULT_FONT_FILE = 'OperatorMono-Medium.otf'
DEFAULT_SCALE_FACTOR = 3

# API 配置
API_VERSION = 'v1'
PAGE_SIZE_DEFAULT = 20
PAGE_SIZE_MAX = 100

# 报告配置
REPORT_TITLE_DEFAULT = '服务器巡检报告'
REPORT_SCREENSHOT_WIDTH = 6  # inches

# 确保目录存在
def init_directories():
    """初始化必要的目录"""
    for dir_path in [DATA_DIR, SCREENSHOTS_DIR, REPORTS_DIR]:
        dir_path.mkdir(exist_ok=True, parents=True)

# 在导入时自动创建目录
init_directories()
