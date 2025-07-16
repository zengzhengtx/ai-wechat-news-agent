"""
数据模型定义
定义数据库表结构和数据模型

Author: zengzhengtx
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from pathlib import Path

from src.utils.logger import get_logger


@dataclass
class Article:
    """文章数据模型"""
    title: str
    content: str
    summary: str
    source_url: str
    source_type: str
    status: str = 'draft'  # draft, published, archived
    quality_score: float = 0.0
    tags: str = ''  # JSON字符串存储标签列表
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    id: Optional[int] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Article':
        """从字典创建实例"""
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


@dataclass
class NewsSource:
    """资讯源数据模型"""
    url: str
    title: str
    content: str
    source_type: str
    processed: bool = False
    fetched_at: Optional[datetime] = None
    id: Optional[int] = None
    
    def __post_init__(self):
        if self.fetched_at is None:
            self.fetched_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        if self.fetched_at:
            data['fetched_at'] = self.fetched_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NewsSource':
        """从字典创建实例"""
        if 'fetched_at' in data and isinstance(data['fetched_at'], str):
            data['fetched_at'] = datetime.fromisoformat(data['fetched_at'])
        return cls(**data)


@dataclass
class Config:
    """配置数据模型"""
    key: str
    value: str
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """从字典创建实例"""
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


class DatabaseSchema:
    """数据库模式定义"""
    
    # 文章表
    CREATE_ARTICLES_TABLE = """
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        summary TEXT,
        source_url TEXT,
        source_type TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'draft',
        quality_score REAL DEFAULT 0.0,
        tags TEXT DEFAULT ''
    )
    """
    
    # 资讯源表
    CREATE_NEWS_SOURCES_TABLE = """
    CREATE TABLE IF NOT EXISTS news_sources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE NOT NULL,
        title TEXT,
        content TEXT,
        source_type TEXT,
        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        processed BOOLEAN DEFAULT FALSE
    )
    """
    
    # 配置表
    CREATE_CONFIG_TABLE = """
    CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY,
        value TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    # 索引
    CREATE_INDEXES = [
        "CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status)",
        "CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_articles_quality_score ON articles(quality_score)",
        "CREATE INDEX IF NOT EXISTS idx_news_sources_source_type ON news_sources(source_type)",
        "CREATE INDEX IF NOT EXISTS idx_news_sources_processed ON news_sources(processed)",
        "CREATE INDEX IF NOT EXISTS idx_news_sources_fetched_at ON news_sources(fetched_at)"
    ]
    
    @classmethod
    def get_all_tables(cls) -> List[str]:
        """获取所有建表语句"""
        return [
            cls.CREATE_ARTICLES_TABLE,
            cls.CREATE_NEWS_SOURCES_TABLE,
            cls.CREATE_CONFIG_TABLE
        ]
    
    @classmethod
    def get_all_indexes(cls) -> List[str]:
        """获取所有索引语句"""
        return cls.CREATE_INDEXES


def init_database(db_path: str) -> None:
    """
    初始化数据库
    
    Args:
        db_path: 数据库文件路径
    """
    logger = get_logger()
    
    try:
        # 确保数据库目录存在
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 创建表
        for table_sql in DatabaseSchema.get_all_tables():
            cursor.execute(table_sql)
        
        # 创建索引
        for index_sql in DatabaseSchema.get_all_indexes():
            cursor.execute(index_sql)
        
        # 提交更改
        conn.commit()
        conn.close()
        
        logger.info(f"数据库初始化完成: {db_path}")
    
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise


def check_database_version(db_path: str) -> str:
    """
    检查数据库版本
    
    Args:
        db_path: 数据库文件路径
        
    Returns:
        str: 数据库版本
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM config WHERE key = 'db_version'")
        result = cursor.fetchone()
        
        conn.close()
        
        return result[0] if result else "1.0.0"
    
    except Exception:
        return "1.0.0"


def update_database_version(db_path: str, version: str) -> None:
    """
    更新数据库版本
    
    Args:
        db_path: 数据库文件路径
        version: 新版本号
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT OR REPLACE INTO config (key, value, updated_at) VALUES (?, ?, ?)",
            ('db_version', version, datetime.now().isoformat())
        )
        
        conn.commit()
        conn.close()
    
    except Exception as e:
        logger = get_logger()
        logger.error(f"更新数据库版本失败: {e}")


def migrate_database(db_path: str) -> None:
    """
    数据库迁移
    
    Args:
        db_path: 数据库文件路径
    """
    logger = get_logger()
    current_version = check_database_version(db_path)
    target_version = "1.0.0"
    
    if current_version == target_version:
        logger.info(f"数据库版本已是最新: {current_version}")
        return
    
    logger.info(f"开始数据库迁移: {current_version} -> {target_version}")
    
    # 这里可以添加具体的迁移逻辑
    # 例如：添加新字段、修改表结构等
    
    # 更新版本号
    update_database_version(db_path, target_version)
    logger.info("数据库迁移完成")
