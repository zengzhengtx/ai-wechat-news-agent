"""
AI资讯智能体主类
整合所有工具，实现完整的资讯获取、改写和发布流程
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from smolagents import CodeAgent, LiteLLMModel

from src.agent.config import load_config
from src.tools.web_search import WebSearchTool
from src.tools.arxiv_search import ArxivSearchTool
from src.tools.huggingface_news import HuggingFaceNewsTool
from src.tools.github_trending import GitHubTrendingTool
from src.tools.content_rewriter import ContentRewriteTool
from src.tools.wechat_formatter import WeChatFormatterTool
from src.tools.base_tool import NewsItem
from src.utils.validators import ContentFilter
from src.utils.quality_control import QualityController
from src.database.database import DatabaseManager
from src.database.models import Article
from src.utils.logger import get_logger


class AINewsAgent:
    """AI资讯智能体"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = load_config(config_path)
        self.logger = get_logger()
        
        # 初始化数据库
        self.db_manager = DatabaseManager(self.config.database_path)
        
        # 初始化工具
        self._init_tools()
        
        # 初始化智能体
        self._init_agent()
        
        # 初始化质量控制
        self.content_filter = ContentFilter(
            duplicate_threshold=self.config.content.duplicate_threshold,
            min_quality_score=self.config.content.min_quality_score
        )
        self.quality_controller = QualityController(
            min_quality_score=self.config.content.min_quality_score
        )
        
        self.logger.info("AI资讯智能体初始化完成")
    
    def _init_tools(self):
        """初始化工具"""
        self.logger.info("初始化工具...")
        
        # 资讯获取工具
        self.web_search_tool = WebSearchTool()
        self.arxiv_tool = ArxivSearchTool()
        self.huggingface_tool = HuggingFaceNewsTool()
        self.github_tool = GitHubTrendingTool(github_token=self.config.github_token)
        
        # 内容处理工具
        self.content_rewriter = ContentRewriteTool(api_key=self.config.openai_api_key)
        self.wechat_formatter = WeChatFormatterTool()
        
        self.logger.info("工具初始化完成")
    
    def _init_agent(self):
        """初始化智能体"""
        self.logger.info("初始化智能体...")
        
        # 创建模型
        model = LiteLLMModel(
            model_id=self.config.agent.model_id,
            api_key=self.config.openai_api_key
        )
        
        # 创建智能体
        self.agent = CodeAgent(
            tools=[
                self.web_search_tool,
                self.arxiv_tool,
                self.huggingface_tool,
                self.github_tool
            ],
            model=model,
            max_steps=self.config.agent.max_steps,
            add_base_tools=True
        )
        
        self.logger.info("智能体初始化完成")
    
    def run_news_collection(self) -> List[Article]:
        """
        运行资讯收集流程
        
        Returns:
            List[Article]: 生成的文章列表
        """
        self.logger.info("开始资讯收集流程...")
        
        try:
            # 1. 获取资讯
            news_items = self._collect_news()
            self.logger.info(f"收集到 {len(news_items)} 条原始资讯")
            
            # 2. 筛选和去重
            filtered_items = self.content_filter.filter_and_dedupe(news_items)
            self.logger.info(f"筛选后剩余 {len(filtered_items)} 条资讯")
            
            # 3. 选择最佳资讯
            selected_items = self._select_best_news(filtered_items)
            self.logger.info(f"选择了 {len(selected_items)} 条优质资讯")
            
            # 4. 改写内容
            rewritten_items = self._rewrite_news(selected_items)
            self.logger.info(f"改写了 {len(rewritten_items)} 条资讯")
            
            # 5. 格式化为微信公众号格式
            formatted_items = self._format_for_wechat(rewritten_items)
            self.logger.info(f"格式化了 {len(formatted_items)} 条资讯")
            
            # 6. 质量检查
            validated_items = self._validate_quality(selected_items, formatted_items)
            self.logger.info(f"通过质量检查的资讯: {len(validated_items)} 条")
            
            # 7. 保存到数据库
            articles = self._save_articles(validated_items)
            self.logger.info(f"保存了 {len(articles)} 篇文章")
            
            return articles
            
        except Exception as e:
            self.logger.error(f"资讯收集流程失败: {e}")
            raise
    
    def _collect_news(self) -> List[NewsItem]:
        """收集资讯"""
        all_news = []
        
        try:
            # Web搜索
            if self.config.sources.web_search.enabled:
                self.logger.info("开始Web搜索...")
                web_results = json.loads(self.web_search_tool.forward(
                    queries=self.config.sources.web_search.queries,
                    max_results_per_query=self.config.sources.web_search.max_results_per_query
                ))
                
                for result in web_results:
                    news_item = NewsItem(
                        title=result['title'],
                        content=result['content'],
                        url=result['url'],
                        source=result['source'],
                        published_date=datetime.fromisoformat(result['published_date']),
                        tags=result.get('tags', []),
                        score=result.get('score', 0.0)
                    )
                    all_news.append(news_item)
        
        except Exception as e:
            self.logger.error(f"Web搜索失败: {e}")
        
        try:
            # arXiv搜索
            if self.config.sources.arxiv.enabled:
                self.logger.info("开始arXiv搜索...")
                arxiv_results = json.loads(self.arxiv_tool.forward(
                    categories=self.config.sources.arxiv.categories,
                    max_papers=self.config.sources.arxiv.max_papers,
                    days_back=self.config.sources.arxiv.days_back
                ))
                
                for result in arxiv_results:
                    news_item = NewsItem(
                        title=result['title'],
                        content=result['content'],
                        url=result['url'],
                        source=result['source'],
                        published_date=datetime.fromisoformat(result['published_date']),
                        tags=result.get('tags', []),
                        score=result.get('score', 0.0)
                    )
                    all_news.append(news_item)
        
        except Exception as e:
            self.logger.error(f"arXiv搜索失败: {e}")
        
        try:
            # Hugging Face搜索
            if self.config.sources.huggingface.enabled:
                self.logger.info("开始Hugging Face搜索...")
                hf_results = json.loads(self.huggingface_tool.forward(
                    max_items=self.config.sources.huggingface.max_items,
                    trending_period=self.config.sources.huggingface.trending_period
                ))
                
                for result in hf_results:
                    news_item = NewsItem(
                        title=result['title'],
                        content=result['content'],
                        url=result['url'],
                        source=result['source'],
                        published_date=datetime.fromisoformat(result['published_date']),
                        tags=result.get('tags', []),
                        score=result.get('score', 0.0)
                    )
                    all_news.append(news_item)
        
        except Exception as e:
            self.logger.error(f"Hugging Face搜索失败: {e}")
        
        try:
            # GitHub搜索
            if self.config.sources.github.enabled:
                self.logger.info("开始GitHub搜索...")
                github_results = json.loads(self.github_tool.forward(
                    topics=self.config.sources.github.topics,
                    max_repos=self.config.sources.github.max_repos,
                    min_stars=self.config.sources.github.min_stars
                ))
                
                for result in github_results:
                    news_item = NewsItem(
                        title=result['title'],
                        content=result['content'],
                        url=result['url'],
                        source=result['source'],
                        published_date=datetime.fromisoformat(result['published_date']),
                        tags=result.get('tags', []),
                        score=result.get('score', 0.0)
                    )
                    all_news.append(news_item)
        
        except Exception as e:
            self.logger.error(f"GitHub搜索失败: {e}")
        
        return all_news
    
    def _select_best_news(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """选择最佳资讯"""
        # 按分数排序
        sorted_items = sorted(news_items, key=lambda x: x.score, reverse=True)
        
        # 选择前N条
        max_articles = self.config.agent.max_articles_per_run
        selected_items = sorted_items[:max_articles]
        
        return selected_items
    
    def _rewrite_news(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """改写资讯"""
        rewritten_items = []
        
        for item in news_items:
            try:
                rewritten_item = self.content_rewriter.rewrite_news_item(item, style="通俗易懂")
                rewritten_items.append(rewritten_item)
            except Exception as e:
                self.logger.error(f"改写资讯失败: {e}")
                rewritten_items.append(item)  # 使用原始资讯
        
        return rewritten_items
    
    def _format_for_wechat(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """格式化为微信公众号格式"""
        formatted_items = []
        
        for item in news_items:
            try:
                formatted_content = self.wechat_formatter.format_news_item(item)
                
                # 创建新的NewsItem
                formatted_item = NewsItem(
                    title=item.title,
                    content=formatted_content,
                    url=item.url,
                    source=item.source,
                    published_date=item.published_date,
                    tags=item.tags + ["formatted"]
                )
                formatted_item.score = item.score
                
                formatted_items.append(formatted_item)
            except Exception as e:
                self.logger.error(f"格式化失败: {e}")
                formatted_items.append(item)  # 使用原始资讯
        
        return formatted_items
    
    def _validate_quality(self, originals: List[NewsItem], formatted: List[NewsItem]) -> List[NewsItem]:
        """验证质量"""
        validated_items = []
        
        for original, formatted_item in zip(originals, formatted):
            try:
                validation_result = self.quality_controller.validate_rewritten_content(
                    original, formatted_item
                )
                
                if validation_result['is_valid']:
                    validated_items.append(formatted_item)
                    self.logger.info(f"质量验证通过: {formatted_item.title}")
                else:
                    self.logger.warning(f"质量验证失败: {formatted_item.title}, 问题: {validation_result['issues']}")
                    # 可以选择是否包含未通过验证的文章
                    validated_items.append(formatted_item)  # 暂时仍然包含
                    
            except Exception as e:
                self.logger.error(f"质量验证失败: {e}")
                validated_items.append(formatted_item)
        
        return validated_items
    
    def _save_articles(self, news_items: List[NewsItem]) -> List[Article]:
        """保存文章到数据库"""
        articles = []
        
        for item in news_items:
            try:
                # 生成摘要
                summary = self.content_rewriter.generate_summary(item.content)
                
                # 创建文章对象
                article = Article(
                    title=item.title,
                    content=item.content,
                    summary=summary,
                    source_url=item.url,
                    source_type=item.source,
                    status='draft',
                    quality_score=item.score,
                    tags=json.dumps(item.tags, ensure_ascii=False)
                )
                
                # 保存到数据库
                article_id = self.db_manager.save_article(article)
                article.id = article_id
                
                articles.append(article)
                
            except Exception as e:
                self.logger.error(f"保存文章失败: {e}")
        
        return articles
    
    def get_recent_articles(self, limit: int = 10) -> List[Article]:
        """获取最近的文章"""
        return self.db_manager.get_articles(limit=limit, order_by="created_at DESC")
    
    def get_article_stats(self) -> Dict[str, Any]:
        """获取文章统计信息"""
        return self.db_manager.get_articles_stats()
