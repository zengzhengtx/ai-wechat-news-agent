"""
内容验证和筛选工具
提供内容质量评估、去重和筛选功能

Author: zengzhengtx
"""

import re
import jieba
import jieba.analyse
from typing import List, Dict, Any, Set, Tuple
from collections import Counter
from datetime import datetime, timedelta
import textstat

from src.tools.base_tool import NewsItem
from src.utils.logger import get_logger
from src.utils.datetime_utils import normalize_datetime, safe_datetime_subtract, get_utc_now, days_since


class ContentFilter:
    """内容筛选器"""
    
    def __init__(self, duplicate_threshold: float = 0.8, min_quality_score: float = 0.6):
        self.duplicate_threshold = duplicate_threshold
        self.min_quality_score = min_quality_score
        self.logger = get_logger()
        
        # 加载停用词
        self.stopwords = self._load_stopwords()
        
        # 初始化jieba
        jieba.initialize()
    
    def filter_and_dedupe(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """
        过滤和去重处理
        
        Args:
            news_items: 资讯项列表
            
        Returns:
            List[NewsItem]: 处理后的资讯项列表
        """
        if not news_items:
            return []
        
        self.logger.info(f"开始内容筛选和去重，原始数量: {len(news_items)}")
        
        # 1. 质量评估
        quality_items = self.filter_by_quality(news_items)
        self.logger.info(f"质量筛选后数量: {len(quality_items)}")
        
        # 2. 去重处理
        unique_items = self.deduplicate(quality_items)
        self.logger.info(f"去重后数量: {len(unique_items)}")
        
        # 3. 按相关性和质量排序
        sorted_items = self.sort_by_relevance(unique_items)
        
        return sorted_items
    
    def filter_by_quality(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """
        按质量筛选
        
        Args:
            news_items: 资讯项列表
            
        Returns:
            List[NewsItem]: 高质量资讯项列表
        """
        quality_items = []
        
        for item in news_items:
            # 计算质量分数
            quality_score = self.assess_quality(item)
            item.score = max(item.score, quality_score)  # 取较高的分数
            
            if quality_score >= self.min_quality_score:
                quality_items.append(item)
        
        return quality_items
    
    def deduplicate(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """
        去重处理
        
        Args:
            news_items: 资讯项列表
            
        Returns:
            List[NewsItem]: 去重后的资讯项列表
        """
        if not news_items:
            return []
        
        unique_items = []
        seen_fingerprints = []

        for item in news_items:
            # 计算内容指纹
            fingerprint = self._calculate_fingerprint(item)

            # 检查是否重复
            is_duplicate = False
            for seen_fp in seen_fingerprints:
                similarity = self._calculate_fingerprint_similarity(fingerprint, seen_fp)
                if similarity >= self.duplicate_threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_items.append(item)
                seen_fingerprints.append(fingerprint)
        
        return unique_items
    
    def sort_by_relevance(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """
        按相关性和质量排序
        
        Args:
            news_items: 资讯项列表
            
        Returns:
            List[NewsItem]: 排序后的资讯项列表
        """
        # 按分数和发布时间排序
        sorted_items = sorted(
            news_items,
            key=lambda x: (x.score, x.published_date),
            reverse=True
        )
        
        return sorted_items
    
    def assess_quality(self, news_item: NewsItem) -> float:
        """
        评估内容质量
        
        Args:
            news_item: 资讯项
            
        Returns:
            float: 质量分数 (0-1)
        """
        score = 0.0
        
        # 1. 内容长度评估 (20%)
        content_length = len(news_item.content)
        if content_length < 100:
            length_score = 0.2
        elif content_length < 300:
            length_score = 0.5
        elif content_length < 1000:
            length_score = 0.8
        else:
            length_score = 1.0
        
        score += length_score * 0.2
        
        # 2. 标题质量评估 (20%)
        title_score = self._assess_title_quality(news_item.title)
        score += title_score * 0.2
        
        # 3. 内容丰富度评估 (30%)
        richness_score = self._assess_content_richness(news_item.content)
        score += richness_score * 0.3
        
        # 4. 时效性评估 (15%)
        recency_score = self._assess_recency(news_item.published_date)
        score += recency_score * 0.15
        
        # 5. 来源可靠性评估 (15%)
        source_score = self._assess_source_reliability(news_item.source)
        score += source_score * 0.15
        
        return min(score, 1.0)
    
    def _assess_title_quality(self, title: str) -> float:
        """
        评估标题质量
        
        Args:
            title: 标题文本
            
        Returns:
            float: 质量分数 (0-1)
        """
        if not title:
            return 0.0
        
        score = 0.0
        
        # 标题长度
        title_length = len(title)
        if 10 <= title_length <= 100:
            score += 0.5
        elif title_length > 100:
            score += 0.3
        else:
            score += 0.1
        
        # 标题关键词
        ai_keywords = ['AI', '人工智能', '机器学习', '深度学习', 'GPT', '大模型', 'LLM']
        for keyword in ai_keywords:
            if keyword in title:
                score += 0.3
                break
        
        # 标题格式
        if re.search(r'[:：]', title):  # 包含冒号，可能是格式化的标题
            score += 0.2
        
        return min(score, 1.0)
    
    def _assess_content_richness(self, content: str) -> float:
        """
        评估内容丰富度
        
        Args:
            content: 内容文本
            
        Returns:
            float: 丰富度分数 (0-1)
        """
        if not content:
            return 0.0
        
        score = 0.0
        
        # 1. 关键词密度
        keywords = jieba.analyse.extract_tags(content, topK=10)
        if len(keywords) >= 5:
            score += 0.3
        elif len(keywords) >= 3:
            score += 0.2
        else:
            score += 0.1
        
        # 2. 段落结构
        paragraphs = content.split('\n\n')
        if len(paragraphs) >= 3:
            score += 0.3
        elif len(paragraphs) >= 2:
            score += 0.2
        else:
            score += 0.1
        
        # 3. 句子复杂度
        try:
            # 使用textstat计算可读性
            readability = textstat.flesch_reading_ease(content)
            if 30 <= readability <= 70:  # 适中的可读性
                score += 0.2
            else:
                score += 0.1
        except:
            score += 0.1
        
        # 4. 特殊内容
        if re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content):
            score += 0.1  # 包含URL
        
        if re.search(r'\d+(?:\.\d+)?%', content):
            score += 0.1  # 包含百分比数据
        
        return min(score, 1.0)
    
    def _assess_recency(self, published_date: datetime) -> float:
        """
        评估时效性

        Args:
            published_date: 发布日期

        Returns:
            float: 时效性分数 (0-1)
        """
        if not published_date:
            return 0.5  # 默认中等时效性

        days_diff = days_since(published_date)
        if days_diff is None:
            return 0.5  # 如果无法计算，返回默认值

        if days_diff < 1:
            return 1.0  # 24小时内
        elif days_diff < 3:
            return 0.9  # 3天内
        elif days_diff < 7:
            return 0.8  # 1周内
        elif days_diff < 14:
            return 0.6  # 2周内
        elif days_diff < 30:
            return 0.4  # 1个月内
        elif days_diff < 90:
            return 0.2  # 3个月内
        else:
            return 0.1  # 更早
    
    def _assess_source_reliability(self, source: str) -> float:
        """
        评估来源可靠性
        
        Args:
            source: 来源标识
            
        Returns:
            float: 可靠性分数 (0-1)
        """
        # 预定义的可靠来源评分
        source_scores = {
            'arxiv': 0.9,
            'github': 0.8,
            'huggingface': 0.9,
            'web_search': 0.6,
        }
        
        # 检查来源前缀
        for prefix, score in source_scores.items():
            if source.startswith(prefix):
                return score
        
        return 0.5  # 默认中等可靠性
    
    def _calculate_fingerprint(self, news_item: NewsItem) -> str:
        """
        计算内容指纹

        Args:
            news_item: 资讯项

        Returns:
            str: 内容指纹字符串
        """
        # 提取标题关键词
        title_keywords = jieba.analyse.extract_tags(news_item.title, topK=10)

        # 提取内容关键词
        content_keywords = jieba.analyse.extract_tags(news_item.content, topK=30)

        # 创建指纹字符串
        fingerprint = f"{news_item.title}|{','.join(sorted(title_keywords))}|{','.join(sorted(content_keywords))}"

        return fingerprint
    
    def _calculate_fingerprint_similarity(
        self,
        fp1: str,
        fp2: str
    ) -> float:
        """
        计算指纹相似度

        Args:
            fp1: 指纹1
            fp2: 指纹2

        Returns:
            float: 相似度分数 (0-1)
        """
        # 分解指纹
        parts1 = fp1.split('|')
        parts2 = fp2.split('|')

        if len(parts1) != 3 or len(parts2) != 3:
            return 0.0

        title1, title_kw1, content_kw1 = parts1
        title2, title_kw2, content_kw2 = parts2

        # 标题相似度
        title_similarity = self._calculate_text_similarity(title1, title2)

        # 标题关键词相似度
        title_kw_set1 = set(title_kw1.split(',')) if title_kw1 else set()
        title_kw_set2 = set(title_kw2.split(',')) if title_kw2 else set()

        # 内容关键词相似度
        content_kw_set1 = set(content_kw1.split(',')) if content_kw1 else set()
        content_kw_set2 = set(content_kw2.split(',')) if content_kw2 else set()

        # 计算关键词相似度
        kw_similarity = 0.0
        if title_kw_set1 and title_kw_set2:
            intersection = title_kw_set1.intersection(title_kw_set2)
            union = title_kw_set1.union(title_kw_set2)
            kw_similarity += len(intersection) / len(union) * 0.4

        if content_kw_set1 and content_kw_set2:
            intersection = content_kw_set1.intersection(content_kw_set2)
            union = content_kw_set1.union(content_kw_set2)
            kw_similarity += len(intersection) / len(union) * 0.6

        # 综合相似度 (标题权重更高)
        return title_similarity * 0.6 + kw_similarity * 0.4
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        计算文本相似度
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            float: 相似度分数 (0-1)
        """
        if text1 == text2:
            return 1.0
        
        # 分词
        words1 = set(jieba.cut(text1))
        words2 = set(jieba.cut(text2))
        
        # 移除停用词
        words1 = words1 - self.stopwords
        words2 = words2 - self.stopwords
        
        if not words1 or not words2:
            return 0.0
        
        # 计算Jaccard相似度
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _load_stopwords(self) -> Set[str]:
        """
        加载停用词
        
        Returns:
            Set[str]: 停用词集合
        """
        # 常见中文停用词
        stopwords = {
            '的', '了', '和', '是', '就', '都', '而', '及', '与', '这', '那', '有', '在',
            '中', '为', '对', '到', '以', '等', '上', '下', '由', '于', '从', '之', '或',
            '也', '如', '但', '并', '很', '再', '已', '所', '然', '没', '去', '能', '好',
            '还', '只', '会', '多', '于是', '吧', '呢', '啊', '哦', '嗯', '这样', '那样'
        }
        
        # 常见英文停用词
        english_stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'if', 'because', 'as', 'what',
            'which', 'this', 'that', 'these', 'those', 'then', 'just', 'so', 'than',
            'such', 'both', 'through', 'about', 'for', 'is', 'of', 'while', 'during',
            'to', 'from', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'once',
            'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each'
        }
        
        stopwords.update(english_stopwords)
        return stopwords
