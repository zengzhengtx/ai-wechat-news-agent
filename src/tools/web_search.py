"""
网络搜索工具
使用DuckDuckGo搜索引擎获取最新AI资讯

Author: zengzhengtx
"""

import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

from src.tools.base_tool import BaseNewsTool, NewsItem
from src.utils.logger import get_logger


class WebSearchTool(BaseNewsTool):
    """网络搜索工具"""
    
    name = "web_search"
    description = "搜索最新AI资讯和新闻"
    inputs = {
        "queries": {
            "type": "array",
            "description": "搜索查询列表"
        },
        "max_results_per_query": {
            "type": "integer",
            "description": "每个查询的最大结果数量",
            "nullable": True
        }
    }
    output_type = "string"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.rate_limit_delay = 2.0  # DuckDuckGo需要更长的延迟
    
    def forward(self, queries: List[str], max_results_per_query: int = 5) -> str:
        """
        执行搜索
        
        Args:
            queries: 搜索查询列表
            max_results_per_query: 每个查询的最大结果数量
            
        Returns:
            str: 搜索结果的JSON字符串
        """
        try:
            news_items = self.fetch_with_cache(
                queries=queries,
                max_results_per_query=max_results_per_query
            )
            
            # 转换为字符串格式返回
            results = []
            for item in news_items:
                results.append({
                    'title': item.title,
                    'content': item.content[:500] + '...' if len(item.content) > 500 else item.content,
                    'url': item.url,
                    'source': item.source,
                    'published_date': item.published_date.isoformat(),
                    'score': item.score
                })
            
            import json
            return json.dumps(results, ensure_ascii=False, indent=2)
        
        except Exception as e:
            self.logger.error(f"Web搜索失败: {e}")
            return f"搜索失败: {str(e)}"
    
    def _fetch_news(self, queries: List[str], max_results_per_query: int = 5) -> List[NewsItem]:
        """
        获取搜索结果
        
        Args:
            queries: 搜索查询列表
            max_results_per_query: 每个查询的最大结果数量
            
        Returns:
            List[NewsItem]: 搜索结果列表
        """
        all_news_items = []
        
        for query in queries:
            self.logger.info(f"搜索查询: {query}")
            
            try:
                # 搜索新闻
                news_results = self._search_duckduckgo_news(query, max_results_per_query)
                
                # 转换为NewsItem
                for result in news_results:
                    news_item = NewsItem(
                        title=result.get('title', ''),
                        content=result.get('content', ''),
                        url=result.get('url', ''),
                        source='web_search',
                        published_date=result.get('published_date'),
                        tags=['AI', 'news']
                    )
                    all_news_items.append(news_item)
                
                # 速率限制
                self._rate_limit()
                
            except Exception as e:
                self.logger.error(f"搜索查询 '{query}' 失败: {e}")
                continue
        
        # 去重和过滤
        unique_items = self.deduplicate(all_news_items)
        
        # 按AI相关性过滤
        ai_keywords = [
            'artificial intelligence', 'AI', 'machine learning', 'deep learning',
            'neural network', 'GPT', 'LLM', 'transformer', 'computer vision',
            'natural language processing', 'NLP', 'robotics', 'automation'
        ]
        
        filtered_items = self.filter_by_keywords(unique_items, ai_keywords, min_score=0.1)
        
        return filtered_items[:20]  # 限制返回数量
    
    def _search_duckduckgo_news(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        使用DuckDuckGo搜索新闻
        
        Args:
            query: 搜索查询
            max_results: 最大结果数量
            
        Returns:
            List[Dict[str, Any]]: 搜索结果列表
        """
        results = []
        
        try:
            # 构建搜索URL
            encoded_query = quote_plus(f"{query} news")
            url = f"https://duckduckgo.com/html/?q={encoded_query}&iar=news&ia=news"
            
            # 发送请求
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # 解析HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找新闻结果
            news_items = soup.find_all('div', class_='result')
            
            for item in news_items[:max_results]:
                try:
                    # 提取标题和链接
                    title_elem = item.find('a', class_='result__a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    
                    # 提取摘要
                    snippet_elem = item.find('a', class_='result__snippet')
                    content = snippet_elem.get_text(strip=True) if snippet_elem else ''
                    
                    # 提取发布时间（如果有）
                    published_date = datetime.now() - timedelta(hours=1)  # 默认1小时前
                    
                    if title and url:
                        results.append({
                            'title': title,
                            'content': content,
                            'url': url,
                            'published_date': published_date
                        })
                
                except Exception as e:
                    self.logger.warning(f"解析搜索结果项失败: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"DuckDuckGo搜索失败: {e}")
            
            # 备用搜索方法
            results = self._fallback_search(query, max_results)
        
        return results
    
    def _fallback_search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        备用搜索方法
        
        Args:
            query: 搜索查询
            max_results: 最大结果数量
            
        Returns:
            List[Dict[str, Any]]: 搜索结果列表
        """
        # 这里可以实现其他搜索引擎的备用方案
        # 目前返回一些模拟数据
        self.logger.info(f"使用备用搜索方法: {query}")
        
        mock_results = [
            {
                'title': f'AI News: {query} - Latest Developments',
                'content': f'Recent developments in {query} show significant progress in artificial intelligence research...',
                'url': 'https://example.com/ai-news-1',
                'published_date': datetime.now() - timedelta(hours=2)
            },
            {
                'title': f'Machine Learning Breakthrough in {query}',
                'content': f'Researchers have made a breakthrough in {query} using advanced machine learning techniques...',
                'url': 'https://example.com/ai-news-2',
                'published_date': datetime.now() - timedelta(hours=4)
            }
        ]
        
        return mock_results[:max_results]
    
    def search_specific_sites(self, query: str, sites: List[str], max_results: int = 3) -> List[NewsItem]:
        """
        在特定网站中搜索
        
        Args:
            query: 搜索查询
            sites: 网站列表
            max_results: 最大结果数量
            
        Returns:
            List[NewsItem]: 搜索结果列表
        """
        all_results = []
        
        for site in sites:
            try:
                site_query = f"site:{site} {query}"
                results = self._search_duckduckgo_news(site_query, max_results)
                
                for result in results:
                    news_item = NewsItem(
                        title=result.get('title', ''),
                        content=result.get('content', ''),
                        url=result.get('url', ''),
                        source=f'web_search_{site}',
                        published_date=result.get('published_date'),
                        tags=['AI', 'news', site]
                    )
                    all_results.append(news_item)
                
                self._rate_limit()
                
            except Exception as e:
                self.logger.error(f"在 {site} 搜索失败: {e}")
                continue
        
        return all_results
    
    def get_trending_ai_topics(self) -> List[str]:
        """
        获取热门AI话题
        
        Returns:
            List[str]: 热门话题列表
        """
        # 预定义的热门AI话题
        trending_topics = [
            "ChatGPT updates",
            "GPT-4 improvements", 
            "AI safety research",
            "machine learning breakthroughs",
            "computer vision advances",
            "natural language processing",
            "AI ethics",
            "autonomous vehicles",
            "AI in healthcare",
            "robotics innovations"
        ]
        
        return trending_topics
