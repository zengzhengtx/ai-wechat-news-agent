"""
GitHub热门项目工具
获取GitHub上热门的AI相关项目和仓库
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from github import Github, GithubException

from src.tools.base_tool import BaseNewsTool, NewsItem
from src.utils.logger import get_logger
from src.utils.datetime_utils import normalize_datetime, safe_datetime_subtract, get_utc_now, days_since


class GitHubTrendingTool(BaseNewsTool):
    """GitHub热门项目工具"""
    
    name = "github_trending"
    description = "获取GitHub上热门的AI相关项目"
    inputs = {
        "topics": {
            "type": "array",
            "description": "GitHub主题列表，如['artificial-intelligence', 'machine-learning']"
        },
        "max_repos": {
            "type": "integer",
            "description": "最大仓库数量",
            "nullable": True
        },
        "min_stars": {
            "type": "integer",
            "description": "最小星标数量",
            "nullable": True
        }
    }
    output_type = "string"
    
    def __init__(self, github_token: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.github_token = github_token
        self.github = Github(github_token) if github_token else Github()
        self.rate_limit_delay = 3.0  # GitHub API有严格的速率限制
        self.max_retries = 3  # 最大重试次数
    
    def forward(self, topics: List[str], max_repos: int = 10, min_stars: int = 100) -> str:
        """
        获取GitHub热门项目
        
        Args:
            topics: GitHub主题列表
            max_repos: 最大仓库数量
            min_stars: 最小星标数量
            
        Returns:
            str: 项目结果的JSON字符串
        """
        try:
            repos = self.fetch_with_cache(
                topics=topics,
                max_repos=max_repos,
                min_stars=min_stars
            )
            
            # 转换为字符串格式返回
            results = []
            for repo in repos:
                results.append({
                    'title': repo.title,
                    'content': repo.content[:700] + '...' if len(repo.content) > 700 else repo.content,
                    'url': repo.url,
                    'source': repo.source,
                    'published_date': repo.published_date.isoformat(),
                    'tags': repo.tags,
                    'score': repo.score
                })
            
            import json
            return json.dumps(results, ensure_ascii=False, indent=2)
        
        except Exception as e:
            self.logger.error(f"GitHub热门项目获取失败: {e}")
            return f"获取失败: {str(e)}"
    
    def _fetch_news(self, topics: List[str], max_repos: int = 10, min_stars: int = 100) -> List[NewsItem]:
        """
        获取GitHub热门项目
        
        Args:
            topics: GitHub主题列表
            max_repos: 最大仓库数量
            min_stars: 最小星标数量
            
        Returns:
            List[NewsItem]: 项目列表
        """
        all_repos = []
        
        try:
            # 获取热门仓库
            trending_repos = self._get_trending_repos(topics, max_repos, min_stars)
            all_repos.extend(trending_repos)
            
            # 获取最近更新的仓库
            recent_repos = self._get_recent_repos(topics, max_repos // 2, min_stars)
            all_repos.extend(recent_repos)
            
        except Exception as e:
            self.logger.error(f"获取GitHub数据失败: {e}")
        
        # 去重和排序
        unique_repos = self.deduplicate(all_repos, threshold=0.9)
        unique_repos.sort(key=lambda x: x.score, reverse=True)
        
        return unique_repos[:max_repos]
    
    def _get_trending_repos(self, topics: List[str], max_repos: int, min_stars: int) -> List[NewsItem]:
        """
        获取热门仓库
        
        Args:
            topics: 主题列表
            max_repos: 最大仓库数量
            min_stars: 最小星标数量
            
        Returns:
            List[NewsItem]: 仓库列表
        """
        repos = []
        
        for topic in topics:
            self.logger.info(f"搜索GitHub主题: {topic}")
            
            try:
                # 构建搜索查询
                query = f"topic:{topic} stars:>={min_stars}"
                
                # 搜索仓库（按星标数排序）
                search_result = self.github.search_repositories(
                    query=query,
                    sort="stars",
                    order="desc"
                )
                
                # 处理搜索结果
                count = 0
                for repo in search_result:
                    if count >= max_repos // len(topics):
                        break
                    
                    try:
                        repo_info = self._get_repo_info(repo)
                        if repo_info:
                            news_item = NewsItem(
                                title=f"热门项目: {repo.full_name}",
                                content=self._format_repo_content(repo_info),
                                url=repo.html_url,
                                source=f"github_{topic}",
                                published_date=repo.created_at,
                                tags=self._extract_repo_tags(repo_info, topic)
                            )
                            
                            # 计算热度分数
                            news_item.score = self._calculate_repo_score(repo_info)
                            repos.append(news_item)
                            count += 1
                    
                    except Exception as e:
                        self.logger.warning(f"处理仓库失败 {repo.full_name}: {e}")
                        continue
                
                self._rate_limit()
                
            except GithubException as e:
                self.logger.error(f"搜索GitHub主题 '{topic}' 失败: {e}")
                continue
            except Exception as e:
                self.logger.error(f"处理GitHub主题 '{topic}' 失败: {e}")
                continue
        
        return repos
    
    def _get_recent_repos(self, topics: List[str], max_repos: int, min_stars: int) -> List[NewsItem]:
        """
        获取最近更新的仓库
        
        Args:
            topics: 主题列表
            max_repos: 最大仓库数量
            min_stars: 最小星标数量
            
        Returns:
            List[NewsItem]: 仓库列表
        """
        repos = []
        
        # 搜索最近30天更新的仓库
        recent_date = get_utc_now() - timedelta(days=30)
        date_str = recent_date.strftime("%Y-%m-%d")
        
        for topic in topics:
            try:
                query = f"topic:{topic} stars:>={min_stars} pushed:>{date_str}"
                
                search_result = self.github.search_repositories(
                    query=query,
                    sort="updated",
                    order="desc"
                )
                
                count = 0
                for repo in search_result:
                    if count >= max_repos // len(topics):
                        break
                    
                    try:
                        repo_info = self._get_repo_info(repo)
                        if repo_info:
                            news_item = NewsItem(
                                title=f"最近更新: {repo.full_name}",
                                content=self._format_repo_content(repo_info),
                                url=repo.html_url,
                                source=f"github_recent_{topic}",
                                published_date=repo.updated_at,
                                tags=self._extract_repo_tags(repo_info, topic) + ['recent-update']
                            )
                            
                            news_item.score = self._calculate_repo_score(repo_info) * 0.8  # 稍微降低分数
                            repos.append(news_item)
                            count += 1
                    
                    except Exception as e:
                        self.logger.warning(f"处理最近仓库失败 {repo.full_name}: {e}")
                        continue
                
                self._rate_limit()
                
            except Exception as e:
                self.logger.error(f"搜索最近更新仓库失败 '{topic}': {e}")
                continue
        
        return repos
    
    def _get_repo_info(self, repo) -> Optional[Dict[str, Any]]:
        """
        获取仓库详细信息
        
        Args:
            repo: GitHub仓库对象
            
        Returns:
            Optional[Dict[str, Any]]: 仓库信息
        """
        try:
            return {
                'full_name': repo.full_name,
                'name': repo.name,
                'owner': repo.owner.login,
                'description': repo.description or '',
                'stars': repo.stargazers_count,
                'forks': repo.forks_count,
                'watchers': repo.watchers_count,
                'language': repo.language,
                'topics': repo.get_topics(),
                'created_at': repo.created_at,
                'updated_at': repo.updated_at,
                'pushed_at': repo.pushed_at,
                'size': repo.size,
                'open_issues': repo.open_issues_count,
                'license': repo.license.name if repo.license else None,
                'html_url': repo.html_url,
                'clone_url': repo.clone_url,
                'homepage': repo.homepage
            }
        
        except Exception as e:
            self.logger.warning(f"获取仓库信息失败: {e}")
            return None
    
    def _format_repo_content(self, repo_info: Dict[str, Any]) -> str:
        """
        格式化仓库内容
        
        Args:
            repo_info: 仓库信息
            
        Returns:
            str: 格式化后的内容
        """
        content_parts = []
        
        content_parts.append(f"仓库: {repo_info['full_name']}")
        
        if repo_info.get('description'):
            content_parts.append(f"描述: {repo_info['description']}")
        
        content_parts.append(f"⭐ 星标: {repo_info['stars']:,}")
        content_parts.append(f"🍴 分叉: {repo_info['forks']:,}")
        content_parts.append(f"👀 关注: {repo_info['watchers']:,}")
        
        if repo_info.get('language'):
            content_parts.append(f"主要语言: {repo_info['language']}")
        
        if repo_info.get('topics'):
            topics = ", ".join(repo_info['topics'][:8])
            content_parts.append(f"主题: {topics}")
        
        if repo_info.get('license'):
            content_parts.append(f"许可证: {repo_info['license']}")
        
        content_parts.append(f"创建时间: {repo_info['created_at'].strftime('%Y-%m-%d')}")
        content_parts.append(f"最后更新: {repo_info['updated_at'].strftime('%Y-%m-%d')}")
        
        if repo_info.get('homepage'):
            content_parts.append(f"主页: {repo_info['homepage']}")
        
        return "\n".join(content_parts)
    
    def _extract_repo_tags(self, repo_info: Dict[str, Any], topic: str) -> List[str]:
        """
        提取仓库标签
        
        Args:
            repo_info: 仓库信息
            topic: 主题
            
        Returns:
            List[str]: 标签列表
        """
        tags = ['github', 'repository', topic]
        
        if repo_info.get('language'):
            tags.append(repo_info['language'].lower())
        
        if repo_info.get('topics'):
            tags.extend(repo_info['topics'][:5])
        
        # 根据星标数添加热度标签
        stars = repo_info.get('stars', 0)
        if stars > 10000:
            tags.append('super-popular')
        elif stars > 5000:
            tags.append('very-popular')
        elif stars > 1000:
            tags.append('popular')
        
        return list(set(tags))
    
    def _calculate_repo_score(self, repo_info: Dict[str, Any]) -> float:
        """
        计算仓库热度分数
        
        Args:
            repo_info: 仓库信息
            
        Returns:
            float: 热度分数
        """
        score = 0.0
        
        # 星标数权重
        stars = repo_info.get('stars', 0)
        score += min(stars / 1000, 10.0) * 0.4
        
        # 分叉数权重
        forks = repo_info.get('forks', 0)
        score += min(forks / 100, 5.0) * 0.2
        
        # 最近活跃度权重
        if repo_info.get('updated_at'):
            try:
                days_since_update = days_since(repo_info['updated_at'])
                if days_since_update is not None:
                    if days_since_update < 7:
                        score += 2.0
                    elif days_since_update < 30:
                        score += 1.0
                    elif days_since_update < 90:
                        score += 0.5
                else:
                    score += 0.5
            except Exception as e:
                self.logger.warning(f"计算活跃度时出错: {e}")
                score += 0.5
        
        # 问题数量（反向权重）
        open_issues = repo_info.get('open_issues', 0)
        if open_issues < 10:
            score += 0.5
        elif open_issues > 100:
            score -= 0.5
        
        # 语言权重
        popular_languages = ['Python', 'JavaScript', 'TypeScript', 'Go', 'Rust', 'C++']
        if repo_info.get('language') in popular_languages:
            score += 0.3
        
        return max(score, 0.0)
    
    def get_trending_topics(self) -> List[str]:
        """
        获取热门AI相关主题
        
        Returns:
            List[str]: 主题列表
        """
        return [
            'artificial-intelligence',
            'machine-learning',
            'deep-learning',
            'neural-networks',
            'computer-vision',
            'natural-language-processing',
            'reinforcement-learning',
            'generative-ai',
            'large-language-models',
            'transformers',
            'pytorch',
            'tensorflow',
            'huggingface',
            'openai',
            'chatgpt'
        ]
