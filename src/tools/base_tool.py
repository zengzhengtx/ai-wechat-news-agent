"""
工具基类模块
定义所有工具的基础接口和通用功能

Author: zengzhengtx
"""

import time
import hashlib
import pickle
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path

from smolagents import Tool
from src.utils.logger import get_logger
from src.utils.datetime_utils import normalize_datetime, get_utc_now


class NewsItem:
    """资讯项数据类"""
    
    def __init__(
        self,
        title: str,
        content: str,
        url: str,
        source: str,
        published_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        score: float = 0.0
    ):
        self.title = title
        self.content = content
        self.url = url
        self.source = source
        self.published_date = normalize_datetime(published_date) or get_utc_now()
        self.tags = tags or []
        self.score = score
        self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """生成唯一ID"""
        content_hash = hashlib.md5(
            f"{self.title}{self.url}".encode('utf-8')
        ).hexdigest()
        return content_hash[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'url': self.url,
            'source': self.source,
            'published_date': self.published_date.isoformat(),
            'tags': self.tags,
            'score': self.score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NewsItem':
        """从字典创建实例"""
        published_date = None
        if data.get('published_date'):
            published_date = datetime.fromisoformat(data['published_date'])
        
        return cls(
            title=data['title'],
            content=data['content'],
            url=data['url'],
            source=data['source'],
            published_date=published_date,
            tags=data.get('tags', []),
            score=data.get('score', 0.0)
        )
    
    def __str__(self) -> str:
        return f"NewsItem(title='{self.title[:50]}...', source='{self.source}')"
    
    def __repr__(self) -> str:
        return self.__str__()


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_dir: str = "data/cache", expire_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.expire_hours = expire_hours
        self.logger = get_logger()
    
    def _get_cache_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        safe_key = hashlib.md5(key.encode('utf-8')).hexdigest()
        return self.cache_dir / f"{safe_key}.cache"
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            # 检查缓存是否过期
            cache_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
            if datetime.now() - cache_time > timedelta(hours=self.expire_hours):
                cache_path.unlink()  # 删除过期缓存
                return None
            
            # 读取缓存数据
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
            
            self.logger.debug(f"缓存命中: {key}")
            return data
        
        except Exception as e:
            self.logger.warning(f"读取缓存失败: {e}")
            return None
    
    def set(self, key: str, data: Any) -> None:
        """设置缓存数据"""
        cache_path = self._get_cache_path(key)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            
            self.logger.debug(f"缓存已保存: {key}")
        
        except Exception as e:
            self.logger.warning(f"保存缓存失败: {e}")
    
    def clear_expired(self) -> None:
        """清理过期缓存"""
        try:
            current_time = datetime.now()
            expired_count = 0
            
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if current_time - cache_time > timedelta(hours=self.expire_hours):
                    cache_file.unlink()
                    expired_count += 1
            
            if expired_count > 0:
                self.logger.info(f"清理了 {expired_count} 个过期缓存文件")
        
        except Exception as e:
            self.logger.warning(f"清理缓存失败: {e}")


class BaseNewsTool(Tool, ABC):
    """资讯工具基类"""
    
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self.cache_manager = cache_manager or CacheManager()
        self.logger = get_logger()
        self.rate_limit_delay = 1.0  # 请求间隔（秒）
        self.last_request_time = 0
    
    def _rate_limit(self) -> None:
        """实施速率限制"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _get_cache_key(self, **kwargs) -> str:
        """生成缓存键"""
        key_parts = [self.__class__.__name__]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
        return "_".join(key_parts)
    
    @abstractmethod
    def _fetch_news(self, **kwargs) -> List[NewsItem]:
        """
        获取资讯数据（子类必须实现）
        
        Returns:
            List[NewsItem]: 资讯项列表
        """
        pass
    
    def fetch_with_cache(self, **kwargs) -> List[NewsItem]:
        """
        带缓存的获取资讯数据
        
        Returns:
            List[NewsItem]: 资讯项列表
        """
        cache_key = self._get_cache_key(**kwargs)
        
        # 尝试从缓存获取
        cached_data = self.cache_manager.get(cache_key)
        if cached_data is not None:
            self.logger.info(f"{self.__class__.__name__} 使用缓存数据")
            return [NewsItem.from_dict(item) for item in cached_data]
        
        # 缓存未命中，获取新数据
        try:
            self.logger.info(f"{self.__class__.__name__} 开始获取资讯...")
            news_items = self._fetch_news(**kwargs)
            
            # 保存到缓存
            cache_data = [item.to_dict() for item in news_items]
            self.cache_manager.set(cache_key, cache_data)
            
            self.logger.info(f"{self.__class__.__name__} 获取到 {len(news_items)} 条资讯")
            return news_items
        
        except Exception as e:
            self.logger.error(f"{self.__class__.__name__} 获取资讯失败: {e}")
            return []
    
    def filter_by_keywords(
        self, 
        news_items: List[NewsItem], 
        keywords: List[str],
        min_score: float = 0.1
    ) -> List[NewsItem]:
        """
        根据关键词过滤资讯
        
        Args:
            news_items: 资讯项列表
            keywords: 关键词列表
            min_score: 最小分数阈值
            
        Returns:
            List[NewsItem]: 过滤后的资讯项列表
        """
        filtered_items = []
        
        for item in news_items:
            score = 0.0
            text = f"{item.title} {item.content}".lower()
            
            for keyword in keywords:
                if keyword.lower() in text:
                    score += 1.0
            
            # 标题中的关键词权重更高
            title_text = item.title.lower()
            for keyword in keywords:
                if keyword.lower() in title_text:
                    score += 0.5
            
            # 归一化分数
            item.score = score / len(keywords) if keywords else 0.0
            
            if item.score >= min_score:
                filtered_items.append(item)
        
        # 按分数排序
        filtered_items.sort(key=lambda x: x.score, reverse=True)
        return filtered_items
    
    def deduplicate(self, news_items: List[NewsItem], threshold: float = 0.8) -> List[NewsItem]:
        """
        去重处理
        
        Args:
            news_items: 资讯项列表
            threshold: 相似度阈值
            
        Returns:
            List[NewsItem]: 去重后的资讯项列表
        """
        if not news_items:
            return []
        
        unique_items = []
        seen_titles = set()
        
        for item in news_items:
            # 简单的标题去重
            title_lower = item.title.lower().strip()
            
            # 检查是否已存在相似标题
            is_duplicate = False
            for seen_title in seen_titles:
                similarity = self._calculate_similarity(title_lower, seen_title)
                if similarity >= threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_items.append(item)
                seen_titles.add(title_lower)
        
        self.logger.info(f"去重前: {len(news_items)} 条，去重后: {len(unique_items)} 条")
        return unique_items
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算文本相似度（简单实现）
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            float: 相似度分数 (0-1)
        """
        if text1 == text2:
            return 1.0
        
        # 简单的词汇重叠度计算
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
