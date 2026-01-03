#!/usr/bin/env python3
"""
数据库初始化脚本
用于手动初始化或重置数据库
"""

from models.database import init_database

if __name__ == '__main__':
    print("正在初始化数据库...")
    init_database()
    print("数据库初始化完成！")
    print("数据库文件位置: data/inspections.db")
