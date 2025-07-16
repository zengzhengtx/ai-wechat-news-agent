"""
arXiv搜索工具
获取最新的AI相关学术论文

Author: zengzhengtx
"""

import arxiv
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.tools.base_tool import BaseNewsTool, NewsItem
from src.utils.logger import get_logger


class ArxivSearchTool(BaseNewsTool):
    """arXiv搜索工具"""
    
    name = "arxiv_search"
    description = "搜索arXiv上的最新AI学术论文"
    inputs = {
        "categories": {
            "type": "array",
            "description": "arXiv分类列表，如['cs.AI', 'cs.LG']"
        },
        "max_papers": {
            "type": "integer",
            "description": "最大论文数量",
            "nullable": True
        },
        "days_back": {
            "type": "integer",
            "description": "搜索多少天前的论文",
            "nullable": True
        }
    }
    output_type = "string"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = arxiv.Client()
        self.rate_limit_delay = 1.0  # arXiv API相对宽松
    
    def forward(self, categories: List[str], max_papers: int = 10, days_back: int = 7) -> str:
        """
        搜索arXiv论文
        
        Args:
            categories: arXiv分类列表
            max_papers: 最大论文数量
            days_back: 搜索多少天前的论文
            
        Returns:
            str: 论文结果的JSON字符串
        """
        try:
            papers = self.fetch_with_cache(
                categories=categories,
                max_papers=max_papers,
                days_back=days_back
            )
            
            # 转换为字符串格式返回
            results = []
            for paper in papers:
                results.append({
                    'title': paper.title,
                    'content': paper.content[:800] + '...' if len(paper.content) > 800 else paper.content,
                    'url': paper.url,
                    'source': paper.source,
                    'published_date': paper.published_date.isoformat(),
                    'tags': paper.tags,
                    'score': paper.score
                })
            
            import json
            return json.dumps(results, ensure_ascii=False, indent=2)
        
        except Exception as e:
            self.logger.error(f"arXiv搜索失败: {e}")
            return f"搜索失败: {str(e)}"
    
    def _fetch_news(self, categories: List[str], max_papers: int = 10, days_back: int = 7) -> List[NewsItem]:
        """
        获取arXiv论文
        
        Args:
            categories: arXiv分类列表
            max_papers: 最大论文数量
            days_back: 搜索多少天前的论文
            
        Returns:
            List[NewsItem]: 论文列表
        """
        all_papers = []
        
        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        for category in categories:
            self.logger.info(f"搜索arXiv分类: {category}")
            
            try:
                # 构建搜索查询
                query = f"cat:{category}"
                
                # 创建搜索对象
                search = arxiv.Search(
                    query=query,
                    max_results=max_papers,
                    sort_by=arxiv.SortCriterion.SubmittedDate,
                    sort_order=arxiv.SortOrder.Descending
                )
                
                # 执行搜索
                papers = list(self.client.results(search))
                
                for paper in papers:
                    # 检查发布日期
                    if paper.published < start_date:
                        continue
                    
                    # 创建NewsItem
                    news_item = NewsItem(
                        title=paper.title,
                        content=self._format_paper_content(paper),
                        url=paper.entry_id,
                        source=f'arxiv_{category}',
                        published_date=paper.published,
                        tags=self._extract_tags(paper, category)
                    )
                    
                    all_papers.append(news_item)
                
                # 速率限制
                self._rate_limit()
                
            except Exception as e:
                self.logger.error(f"搜索arXiv分类 '{category}' 失败: {e}")
                continue
        
        # 按发布时间排序
        all_papers.sort(key=lambda x: x.published_date, reverse=True)
        
        # 去重
        unique_papers = self.deduplicate(all_papers, threshold=0.9)
        
        # 按相关性过滤
        ai_keywords = [
            'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'transformer', 'attention', 'GPT', 'BERT',
            'computer vision', 'natural language processing', 'reinforcement learning',
            'generative model', 'diffusion', 'large language model'
        ]
        
        filtered_papers = self.filter_by_keywords(unique_papers, ai_keywords, min_score=0.1)
        
        return filtered_papers[:max_papers]
    
    def _format_paper_content(self, paper: arxiv.Result) -> str:
        """
        格式化论文内容
        
        Args:
            paper: arXiv论文对象
            
        Returns:
            str: 格式化后的内容
        """
        content_parts = []
        
        # 摘要
        if paper.summary:
            content_parts.append(f"摘要: {paper.summary}")
        
        # 作者
        if paper.authors:
            authors = ", ".join([author.name for author in paper.authors[:5]])
            if len(paper.authors) > 5:
                authors += f" 等 {len(paper.authors)} 位作者"
            content_parts.append(f"作者: {authors}")
        
        # 分类
        if paper.categories:
            categories = ", ".join(paper.categories)
            content_parts.append(f"分类: {categories}")
        
        # 发布日期
        content_parts.append(f"发布日期: {paper.published.strftime('%Y-%m-%d')}")
        
        # PDF链接
        if paper.pdf_url:
            content_parts.append(f"PDF链接: {paper.pdf_url}")
        
        return "\n\n".join(content_parts)
    
    def _extract_tags(self, paper: arxiv.Result, category: str) -> List[str]:
        """
        提取论文标签
        
        Args:
            paper: arXiv论文对象
            category: 主要分类
            
        Returns:
            List[str]: 标签列表
        """
        tags = ['arxiv', 'academic', 'research']
        
        # 添加分类标签
        if category:
            tags.append(category)
        
        # 根据分类添加更具体的标签
        category_mapping = {
            'cs.AI': ['artificial-intelligence', 'AI'],
            'cs.LG': ['machine-learning', 'ML'],
            'cs.CL': ['natural-language-processing', 'NLP'],
            'cs.CV': ['computer-vision', 'CV'],
            'cs.NE': ['neural-networks', 'neural-computing'],
            'cs.RO': ['robotics'],
            'stat.ML': ['statistics', 'machine-learning']
        }
        
        for cat in paper.categories:
            if cat in category_mapping:
                tags.extend(category_mapping[cat])
        
        # 从标题中提取关键词
        title_lower = paper.title.lower()
        keyword_mapping = {
            'transformer': ['transformer', 'attention'],
            'bert': ['BERT', 'language-model'],
            'gpt': ['GPT', 'generative'],
            'diffusion': ['diffusion', 'generative'],
            'reinforcement': ['reinforcement-learning', 'RL'],
            'gan': ['GAN', 'generative'],
            'cnn': ['CNN', 'convolutional'],
            'rnn': ['RNN', 'recurrent'],
            'lstm': ['LSTM', 'sequence'],
            'attention': ['attention', 'transformer']
        }
        
        for keyword, related_tags in keyword_mapping.items():
            if keyword in title_lower:
                tags.extend(related_tags)
        
        return list(set(tags))  # 去重
    
    def search_by_keywords(self, keywords: List[str], max_papers: int = 10) -> List[NewsItem]:
        """
        根据关键词搜索论文
        
        Args:
            keywords: 关键词列表
            max_papers: 最大论文数量
            
        Returns:
            List[NewsItem]: 论文列表
        """
        all_papers = []
        
        for keyword in keywords:
            self.logger.info(f"搜索关键词: {keyword}")
            
            try:
                # 构建搜索查询
                query = f'all:"{keyword}"'
                
                # 创建搜索对象
                search = arxiv.Search(
                    query=query,
                    max_results=max_papers // len(keywords) + 1,
                    sort_by=arxiv.SortCriterion.SubmittedDate,
                    sort_order=arxiv.SortOrder.Descending
                )
                
                # 执行搜索
                papers = list(self.client.results(search))
                
                for paper in papers:
                    # 只要最近30天的论文
                    if paper.published < datetime.now() - timedelta(days=30):
                        continue
                    
                    news_item = NewsItem(
                        title=paper.title,
                        content=self._format_paper_content(paper),
                        url=paper.entry_id,
                        source=f'arxiv_keyword_{keyword}',
                        published_date=paper.published,
                        tags=self._extract_tags(paper, '') + [keyword]
                    )
                    
                    all_papers.append(news_item)
                
                self._rate_limit()
                
            except Exception as e:
                self.logger.error(f"搜索关键词 '{keyword}' 失败: {e}")
                continue
        
        # 去重和排序
        unique_papers = self.deduplicate(all_papers, threshold=0.9)
        unique_papers.sort(key=lambda x: x.published_date, reverse=True)
        
        return unique_papers[:max_papers]
    
    def get_trending_categories(self) -> List[str]:
        """
        获取热门arXiv分类
        
        Returns:
            List[str]: 分类列表
        """
        return [
            'cs.AI',  # Artificial Intelligence
            'cs.LG',  # Machine Learning
            'cs.CL',  # Computation and Language
            'cs.CV',  # Computer Vision and Pattern Recognition
            'cs.NE',  # Neural and Evolutionary Computing
            'cs.RO',  # Robotics
            'stat.ML'  # Machine Learning (Statistics)
        ]
    
    def get_paper_details(self, arxiv_id: str) -> Dict[str, Any]:
        """
        获取论文详细信息
        
        Args:
            arxiv_id: arXiv论文ID
            
        Returns:
            Dict[str, Any]: 论文详细信息
        """
        try:
            search = arxiv.Search(id_list=[arxiv_id])
            paper = next(self.client.results(search))
            
            return {
                'id': paper.entry_id,
                'title': paper.title,
                'authors': [author.name for author in paper.authors],
                'summary': paper.summary,
                'categories': paper.categories,
                'published': paper.published.isoformat(),
                'updated': paper.updated.isoformat() if paper.updated else None,
                'pdf_url': paper.pdf_url,
                'comment': paper.comment,
                'journal_ref': paper.journal_ref,
                'doi': paper.doi
            }
        
        except Exception as e:
            self.logger.error(f"获取论文详情失败 {arxiv_id}: {e}")
            return {}
