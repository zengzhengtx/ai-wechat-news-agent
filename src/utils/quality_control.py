"""
质量控制模块
提供内容质量评估和验证功能
"""

import re
import jieba
import jieba.analyse
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.tools.base_tool import NewsItem
from src.utils.logger import get_logger


class QualityController:
    """质量控制器"""
    
    def __init__(self, min_quality_score: float = 0.6):
        self.min_quality_score = min_quality_score
        self.logger = get_logger()
    
    def validate_rewritten_content(self, original: NewsItem, rewritten: NewsItem) -> Dict[str, Any]:
        """
        验证改写后的内容质量
        
        Args:
            original: 原始资讯项
            rewritten: 改写后的资讯项
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            'is_valid': True,
            'score': 0.0,
            'issues': [],
            'suggestions': []
        }
        
        # 1. 长度检查
        length_check = self._check_length(rewritten.content)
        result['score'] += length_check['score'] * 0.2
        if length_check['issues']:
            result['issues'].extend(length_check['issues'])
        
        # 2. 内容完整性检查
        completeness_check = self._check_completeness(original, rewritten)
        result['score'] += completeness_check['score'] * 0.3
        if completeness_check['issues']:
            result['issues'].extend(completeness_check['issues'])
        
        # 3. 可读性检查
        readability_check = self._check_readability(rewritten.content)
        result['score'] += readability_check['score'] * 0.3
        if readability_check['issues']:
            result['issues'].extend(readability_check['issues'])
        
        # 4. 格式检查
        format_check = self._check_format(rewritten.content)
        result['score'] += format_check['score'] * 0.2
        if format_check['issues']:
            result['issues'].extend(format_check['issues'])
        
        # 判断是否通过验证
        result['is_valid'] = result['score'] >= self.min_quality_score and len(result['issues']) <= 1
        
        # 生成改进建议
        result['suggestions'] = self._generate_suggestions(result['issues'])
        
        return result
    
    def _check_length(self, content: str) -> Dict[str, Any]:
        """
        检查内容长度
        
        Args:
            content: 内容
            
        Returns:
            Dict[str, Any]: 检查结果
        """
        result = {'score': 0.0, 'issues': []}
        
        length = len(content)
        
        if length < 500:
            result['issues'].append("内容过短，可能信息不够完整")
            result['score'] = 0.3
        elif length < 800:
            result['score'] = 0.6
        elif length <= 3000:
            result['score'] = 1.0
        else:
            result['issues'].append("内容过长，可能影响阅读体验")
            result['score'] = 0.7
        
        return result
    
    def _check_completeness(self, original: NewsItem, rewritten: NewsItem) -> Dict[str, Any]:
        """
        检查内容完整性
        
        Args:
            original: 原始资讯项
            rewritten: 改写后的资讯项
            
        Returns:
            Dict[str, Any]: 检查结果
        """
        result = {'score': 0.0, 'issues': []}
        
        # 检查关键信息是否保留
        original_keywords = set(jieba.analyse.extract_tags(original.content, topK=20))
        rewritten_keywords = set(jieba.analyse.extract_tags(rewritten.content, topK=20))
        
        # 计算关键词保留率
        if original_keywords:
            retention_rate = len(original_keywords.intersection(rewritten_keywords)) / len(original_keywords)
            
            if retention_rate >= 0.7:
                result['score'] = 1.0
            elif retention_rate >= 0.5:
                result['score'] = 0.8
            elif retention_rate >= 0.3:
                result['score'] = 0.6
                result['issues'].append("部分关键信息可能丢失")
            else:
                result['score'] = 0.3
                result['issues'].append("大量关键信息丢失")
        else:
            result['score'] = 0.5
        
        # 检查URL是否保留
        if original.url and original.url not in rewritten.content:
            result['issues'].append("原始来源URL丢失")
            result['score'] *= 0.9
        
        return result
    
    def _check_readability(self, content: str) -> Dict[str, Any]:
        """
        检查可读性
        
        Args:
            content: 内容
            
        Returns:
            Dict[str, Any]: 检查结果
        """
        result = {'score': 0.0, 'issues': []}
        
        # 检查段落结构
        paragraphs = content.split('\n\n')
        if len(paragraphs) < 2:
            result['issues'].append("缺少段落分隔，影响阅读体验")
            result['score'] = 0.5
        else:
            result['score'] = 0.8
        
        # 检查句子长度
        sentences = re.split(r'[。！？]', content)
        avg_sentence_length = sum(len(s) for s in sentences if s.strip()) / max(len(sentences), 1)
        
        if avg_sentence_length > 50:
            result['issues'].append("句子过长，建议适当分句")
            result['score'] *= 0.8
        
        # 检查是否有标题结构
        if '##' in content or '**' in content:
            result['score'] = min(result['score'] + 0.2, 1.0)
        
        return result
    
    def _check_format(self, content: str) -> Dict[str, Any]:
        """
        检查格式
        
        Args:
            content: 内容
            
        Returns:
            Dict[str, Any]: 检查结果
        """
        result = {'score': 0.0, 'issues': []}
        
        score = 0.0
        
        # 检查是否有标题
        if content.startswith('#'):
            score += 0.3
        else:
            result['issues'].append("缺少标题格式")
        
        # 检查是否有emoji
        emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]'
        if re.search(emoji_pattern, content):
            score += 0.2
        
        # 检查是否有小标题
        if '##' in content:
            score += 0.3
        
        # 检查是否有强调格式
        if '**' in content or '*' in content:
            score += 0.2
        
        result['score'] = min(score, 1.0)
        
        return result
    
    def _generate_suggestions(self, issues: List[str]) -> List[str]:
        """
        生成改进建议
        
        Args:
            issues: 问题列表
            
        Returns:
            List[str]: 建议列表
        """
        suggestions = []
        
        issue_to_suggestion = {
            "内容过短": "增加更多相关信息，丰富内容",
            "内容过长": "精简内容，保留核心信息",
            "部分关键信息可能丢失": "确保保留原文的关键信息和术语",
            "大量关键信息丢失": "重新改写，确保包含原文的主要信息点",
            "原始来源URL丢失": "添加原始来源链接",
            "缺少段落分隔": "增加段落分隔，提高可读性",
            "句子过长": "将长句拆分为短句，提高可读性",
            "缺少标题格式": "添加标题格式，使用'#'标记"
        }
        
        for issue in issues:
            for key, suggestion in issue_to_suggestion.items():
                if key in issue:
                    suggestions.append(suggestion)
                    break
            else:
                # 如果没有匹配到预定义建议，添加通用建议
                suggestions.append(f"解决问题: {issue}")
        
        return suggestions
    
    def batch_validate(self, originals: List[NewsItem], rewrittens: List[NewsItem]) -> List[Dict[str, Any]]:
        """
        批量验证内容质量
        
        Args:
            originals: 原始资讯项列表
            rewrittens: 改写后的资讯项列表
            
        Returns:
            List[Dict[str, Any]]: 验证结果列表
        """
        results = []
        
        for original, rewritten in zip(originals, rewrittens):
            result = self.validate_rewritten_content(original, rewritten)
            results.append({
                'id': rewritten.id,
                'title': rewritten.title,
                'is_valid': result['is_valid'],
                'score': result['score'],
                'issues': result['issues'],
                'suggestions': result['suggestions']
            })
        
        return results
    
    def get_quality_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        获取质量统计信息
        
        Args:
            results: 验证结果列表
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        stats = {
            'total': len(results),
            'valid': sum(1 for r in results if r['is_valid']),
            'invalid': sum(1 for r in results if not r['is_valid']),
            'avg_score': sum(r['score'] for r in results) / max(len(results), 1),
            'common_issues': {}
        }
        
        # 统计常见问题
        all_issues = []
        for result in results:
            all_issues.extend(result['issues'])
        
        for issue in all_issues:
            if issue in stats['common_issues']:
                stats['common_issues'][issue] += 1
            else:
                stats['common_issues'][issue] = 1
        
        # 按出现频率排序
        stats['common_issues'] = dict(
            sorted(stats['common_issues'].items(), key=lambda x: x[1], reverse=True)
        )
        
        return stats
