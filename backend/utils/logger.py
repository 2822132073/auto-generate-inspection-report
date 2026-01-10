"""
统一日志配置模块
"""

import logging
import sys

# 日志格式
LOG_FORMAT = '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def setup_logging(level=logging.INFO):
    """配置根日志"""
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        stream=sys.stdout
    )
    # 降低第三方库日志级别
    logging.getLogger('werkzeug').setLevel(logging.WARNING)


def get_logger(name):
    """获取指定名称的 logger"""
    return logging.getLogger(name)
