"""
数据库初始化和连接管理
"""

import sqlite3
from contextlib import contextmanager
from config import DATABASE_PATH


def init_database():
    """初始化数据库表和索引"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # 创建 inspection_records 表（巡检记录）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inspection_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id VARCHAR(100),
            hostname VARCHAR(100) NOT NULL,
            ip VARCHAR(50),
            os VARCHAR(50),
            kernel VARCHAR(100),
            arch VARCHAR(20),
            timestamp DATETIME NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) DEFAULT 'completed',
            env_data TEXT,
            notes TEXT
        )
    ''')

    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON inspection_records(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_hostname ON inspection_records(hostname)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_project_id ON inspection_records(project_id)')

    # 创建 command_executions 表（命令执行记录）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS command_executions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id INTEGER NOT NULL,
            command VARCHAR(500) NOT NULL,
            output TEXT,
            return_code INTEGER DEFAULT 0,
            screenshot_path VARCHAR(500),
            screenshot_status VARCHAR(20) DEFAULT 'pending',
            execution_order INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (record_id) REFERENCES inspection_records(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_record_id ON command_executions(record_id)')

    # 迁移：为旧表添加 screenshot_status 字段
    cursor.execute("PRAGMA table_info(command_executions)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'screenshot_status' not in columns:
        cursor.execute("ALTER TABLE command_executions ADD COLUMN screenshot_status VARCHAR(20) DEFAULT 'pending'")
        # 已有截图的设为 completed，没有的设为 skipped
        cursor.execute("UPDATE command_executions SET screenshot_status = 'completed' WHERE screenshot_path IS NOT NULL")
        cursor.execute("UPDATE command_executions SET screenshot_status = 'skipped' WHERE screenshot_path IS NULL")

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_screenshot_status ON command_executions(screenshot_status)')

    # 迁移：为旧表添加 name 字段
    cursor.execute("PRAGMA table_info(command_executions)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'name' not in columns:
        cursor.execute("ALTER TABLE command_executions ADD COLUMN name VARCHAR(200)")
        # 旧数据：将 command 复制到 name 作为默认值
        cursor.execute("UPDATE command_executions SET name = command WHERE name IS NULL")

    # 创建 report_generations 表（报告生成记录）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS report_generations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id VARCHAR(100) NOT NULL,
            report_path VARCHAR(500),
            format VARCHAR(20) DEFAULT 'docx',
            generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            file_size INTEGER,
            host_count INTEGER
        )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_project_report ON report_generations(project_id)')

    # 创建 report_templates 表（报告模板）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS report_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL UNIQUE,
            description TEXT,
            config TEXT NOT NULL,
            is_default INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_template_name ON report_templates(name)')

    # 创建 projects 表（项目管理）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_code VARCHAR(50) NOT NULL UNIQUE,
            project_name VARCHAR(200) NOT NULL,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) DEFAULT 'active'
        )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_project_code ON projects(project_code)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_project_name ON projects(project_name)')

    conn.commit()
    conn.close()


@contextmanager
def get_db_connection():
    """
    获取数据库连接的上下文管理器

    用法:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(...)
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # 返回字典格式
    # 启用外键约束
    conn.execute('PRAGMA foreign_keys = ON')
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
