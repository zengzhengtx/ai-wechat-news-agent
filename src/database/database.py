"""
数据库操作模块
提供数据库的增删改查操作

Author: zengzhengtx
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from contextlib import contextmanager

from src.database.models import Article, NewsSource, Config, init_database, migrate_database
from src.utils.logger import get_logger


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = get_logger()
        
        # 初始化数据库
        init_database(db_path)
        migrate_database(db_path)
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接（上下文管理器）"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 使结果可以按列名访问
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    # ==================== 文章操作 ====================
    
    def save_article(self, article: Article) -> int:
        """
        保存文章
        
        Args:
            article: 文章对象
            
        Returns:
            int: 文章ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if article.id is None:
                # 新增文章
                cursor.execute("""
                    INSERT INTO articles (
                        title, content, summary, source_url, source_type,
                        status, quality_score, tags, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article.title, article.content, article.summary,
                    article.source_url, article.source_type, article.status,
                    article.quality_score, article.tags,
                    article.created_at.isoformat(), article.updated_at.isoformat()
                ))
                article.id = cursor.lastrowid
            else:
                # 更新文章
                article.updated_at = datetime.now()
                cursor.execute("""
                    UPDATE articles SET
                        title=?, content=?, summary=?, source_url=?, source_type=?,
                        status=?, quality_score=?, tags=?, updated_at=?
                    WHERE id=?
                """, (
                    article.title, article.content, article.summary,
                    article.source_url, article.source_type, article.status,
                    article.quality_score, article.tags,
                    article.updated_at.isoformat(), article.id
                ))
            
            conn.commit()
            self.logger.info(f"文章已保存: ID={article.id}, 标题='{article.title[:50]}...'")
            return article.id
    
    def get_article(self, article_id: int) -> Optional[Article]:
        """
        获取文章
        
        Args:
            article_id: 文章ID
            
        Returns:
            Optional[Article]: 文章对象
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_article(row)
            return None
    
    def get_articles(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        order_by: str = "created_at DESC"
    ) -> List[Article]:
        """
        获取文章列表
        
        Args:
            status: 文章状态过滤
            limit: 限制数量
            offset: 偏移量
            order_by: 排序方式
            
        Returns:
            List[Article]: 文章列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            sql = "SELECT * FROM articles"
            params = []
            
            if status:
                sql += " WHERE status = ?"
                params.append(status)
            
            sql += f" ORDER BY {order_by} LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            return [self._row_to_article(row) for row in rows]
    
    def delete_article(self, article_id: int) -> bool:
        """
        删除文章
        
        Args:
            article_id: 文章ID
            
        Returns:
            bool: 是否删除成功
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM articles WHERE id = ?", (article_id,))
            conn.commit()
            
            success = cursor.rowcount > 0
            if success:
                self.logger.info(f"文章已删除: ID={article_id}")
            return success
    
    def search_articles(self, keyword: str, limit: int = 20) -> List[Article]:
        """
        搜索文章
        
        Args:
            keyword: 搜索关键词
            limit: 限制数量
            
        Returns:
            List[Article]: 文章列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM articles 
                WHERE title LIKE ? OR content LIKE ? OR summary LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", limit))
            
            rows = cursor.fetchall()
            return [self._row_to_article(row) for row in rows]
    
    def get_articles_stats(self) -> Dict[str, int]:
        """
        获取文章统计信息

        Returns:
            Dict[str, int]: 统计信息
        """
        try:
            with self.get_connection() as conn:
                conn.execute("PRAGMA busy_timeout = 10000")  # 10秒超时
                cursor = conn.cursor()

                stats = {}

                # 总文章数
                cursor.execute("SELECT COUNT(*) FROM articles")
                result = cursor.fetchone()
                stats['total'] = result[0] if result else 0

                # 按状态统计
                cursor.execute("""
                    SELECT status, COUNT(*) FROM articles GROUP BY status
                """)
                for row in cursor.fetchall():
                    if row and len(row) >= 2:
                        stats[f"status_{row[0]}"] = row[1]

                # 今日新增
                cursor.execute("""
                    SELECT COUNT(*) FROM articles
                    WHERE DATE(created_at) = DATE('now')
                """)
                result = cursor.fetchone()
                stats['today'] = result[0] if result else 0

                self.logger.info(f"数据库统计查询成功: {stats}")
                return stats

        except Exception as e:
            self.logger.error(f"获取统计信息失败: {e}")
            return {
                'total': 0,
                'status_draft': 0,
                'status_published': 0,
                'status_archived': 0,
                'today': 0
            }
    
    def _row_to_article(self, row: sqlite3.Row) -> Article:
        """将数据库行转换为Article对象"""
        return Article(
            id=row['id'],
            title=row['title'],
            content=row['content'],
            summary=row['summary'],
            source_url=row['source_url'],
            source_type=row['source_type'],
            status=row['status'],
            quality_score=row['quality_score'],
            tags=row['tags'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )
    
    # ==================== 资讯源操作 ====================
    
    def save_news_source(self, news_source: NewsSource) -> int:
        """
        保存资讯源
        
        Args:
            news_source: 资讯源对象
            
        Returns:
            int: 资讯源ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO news_sources (
                        url, title, content, source_type, processed, fetched_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    news_source.url, news_source.title, news_source.content,
                    news_source.source_type, news_source.processed,
                    news_source.fetched_at.isoformat()
                ))
                news_source.id = cursor.lastrowid
                conn.commit()
                return news_source.id
            
            except sqlite3.IntegrityError:
                # URL已存在，更新记录
                cursor.execute("""
                    UPDATE news_sources SET
                        title=?, content=?, source_type=?, processed=?, fetched_at=?
                    WHERE url=?
                """, (
                    news_source.title, news_source.content, news_source.source_type,
                    news_source.processed, news_source.fetched_at.isoformat(),
                    news_source.url
                ))
                conn.commit()
                
                # 获取更新后的ID
                cursor.execute("SELECT id FROM news_sources WHERE url=?", (news_source.url,))
                news_source.id = cursor.fetchone()[0]
                return news_source.id
    
    def get_unprocessed_news_sources(self, source_type: Optional[str] = None) -> List[NewsSource]:
        """
        获取未处理的资讯源
        
        Args:
            source_type: 资讯源类型过滤
            
        Returns:
            List[NewsSource]: 资讯源列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            sql = "SELECT * FROM news_sources WHERE processed = FALSE"
            params = []
            
            if source_type:
                sql += " AND source_type = ?"
                params.append(source_type)
            
            sql += " ORDER BY fetched_at DESC"
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            return [self._row_to_news_source(row) for row in rows]
    
    def mark_news_source_processed(self, news_source_id: int) -> None:
        """
        标记资讯源为已处理
        
        Args:
            news_source_id: 资讯源ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE news_sources SET processed = TRUE WHERE id = ?",
                (news_source_id,)
            )
            conn.commit()
    
    def _row_to_news_source(self, row: sqlite3.Row) -> NewsSource:
        """将数据库行转换为NewsSource对象"""
        return NewsSource(
            id=row['id'],
            url=row['url'],
            title=row['title'],
            content=row['content'],
            source_type=row['source_type'],
            processed=bool(row['processed']),
            fetched_at=datetime.fromisoformat(row['fetched_at'])
        )
    
    # ==================== 配置操作 ====================
    
    def get_config(self, key: str) -> Optional[str]:
        """
        获取配置值
        
        Args:
            key: 配置键
            
        Returns:
            Optional[str]: 配置值
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else None
    
    def set_config(self, key: str, value: str) -> None:
        """
        设置配置值
        
        Args:
            key: 配置键
            value: 配置值
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO config (key, value, updated_at)
                VALUES (?, ?, ?)
            """, (key, value, datetime.now().isoformat()))
            conn.commit()
    
    def get_all_configs(self) -> Dict[str, str]:
        """
        获取所有配置
        
        Returns:
            Dict[str, str]: 配置字典
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM config")
            rows = cursor.fetchall()
            return {row[0]: row[1] for row in rows}
