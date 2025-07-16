"""
Hugging Face资讯工具
获取Hugging Face Hub上的最新模型、数据集和热门项目

Author: zengzhengtx
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from huggingface_hub import HfApi

from src.tools.base_tool import BaseNewsTool, NewsItem
from src.utils.logger import get_logger
from src.utils.datetime_utils import normalize_datetime, safe_datetime_compare, get_utc_now, is_recent


class HuggingFaceNewsTool(BaseNewsTool):
    """Hugging Face资讯工具"""
    
    name = "huggingface_news"
    description = "获取Hugging Face Hub上的最新模型和数据集信息"
    inputs = {
        "max_items": {
            "type": "integer",
            "description": "最大项目数量",
            "nullable": True
        },
        "trending_period": {
            "type": "string",
            "description": "热门时间段：daily, weekly, monthly",
            "nullable": True
        }
    }
    output_type = "string"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api = HfApi()
        self.rate_limit_delay = 1.0
    
    def forward(self, max_items: int = 15, trending_period: str = "daily") -> str:
        """
        获取Hugging Face资讯
        
        Args:
            max_items: 最大项目数量
            trending_period: 热门时间段
            
        Returns:
            str: 资讯结果的JSON字符串
        """
        try:
            news_items = self.fetch_with_cache(
                max_items=max_items,
                trending_period=trending_period
            )
            
            # 转换为字符串格式返回
            results = []
            for item in news_items:
                results.append({
                    'title': item.title,
                    'content': item.content[:600] + '...' if len(item.content) > 600 else item.content,
                    'url': item.url,
                    'source': item.source,
                    'published_date': item.published_date.isoformat(),
                    'tags': item.tags,
                    'score': item.score
                })
            
            import json
            return json.dumps(results, ensure_ascii=False, indent=2)
        
        except Exception as e:
            self.logger.error(f"Hugging Face资讯获取失败: {e}")
            return f"获取失败: {str(e)}"
    
    def _fetch_news(self, max_items: int = 15, trending_period: str = "daily") -> List[NewsItem]:
        """
        获取Hugging Face资讯
        
        Args:
            max_items: 最大项目数量
            trending_period: 热门时间段
            
        Returns:
            List[NewsItem]: 资讯项列表
        """
        all_items = []
        
        try:
            # 获取热门模型
            models = self._get_trending_models(max_items // 2)
            all_items.extend(models)
            
            # 获取热门数据集
            datasets = self._get_trending_datasets(max_items // 4)
            all_items.extend(datasets)
            
            # 获取最新模型
            recent_models = self._get_recent_models(max_items // 4)
            all_items.extend(recent_models)
            
        except Exception as e:
            self.logger.error(f"获取Hugging Face数据失败: {e}")
        
        # 去重和排序
        unique_items = self.deduplicate(all_items, threshold=0.9)
        unique_items.sort(key=lambda x: x.published_date, reverse=True)
        
        return unique_items[:max_items]
    
    def _get_trending_models(self, max_models: int = 10) -> List[NewsItem]:
        """
        获取热门模型
        
        Args:
            max_models: 最大模型数量
            
        Returns:
            List[NewsItem]: 模型资讯列表
        """
        models = []
        
        try:
            # 获取热门模型（按下载量排序）
            model_list = list(self.api.list_models(
                sort="downloads",
                direction=-1,
                limit=max_models * 2  # 获取更多以便筛选
            ))
            
            for model in model_list[:max_models]:
                try:
                    # 获取模型详细信息
                    model_info = self._get_model_info(model.modelId)
                    
                    if model_info:
                        news_item = NewsItem(
                            title=f"热门模型: {model.modelId}",
                            content=self._format_model_content(model_info),
                            url=f"https://huggingface.co/{model.modelId}",
                            source="huggingface_models",
                            published_date=model_info.get('created_at', datetime.now()),
                            tags=self._extract_model_tags(model_info)
                        )
                        models.append(news_item)
                
                except Exception as e:
                    self.logger.warning(f"获取模型信息失败 {model.modelId}: {e}")
                    continue
                
                self._rate_limit()
        
        except Exception as e:
            self.logger.error(f"获取热门模型失败: {e}")
        
        return models
    
    def _get_trending_datasets(self, max_datasets: int = 5) -> List[NewsItem]:
        """
        获取热门数据集
        
        Args:
            max_datasets: 最大数据集数量
            
        Returns:
            List[NewsItem]: 数据集资讯列表
        """
        datasets = []
        
        try:
            # 获取热门数据集
            dataset_list = list(self.api.list_datasets(
                sort="downloads",
                direction=-1,
                limit=max_datasets * 2
            ))
            
            for dataset in dataset_list[:max_datasets]:
                try:
                    # 获取数据集详细信息
                    dataset_info = self._get_dataset_info(dataset.id)
                    
                    if dataset_info:
                        news_item = NewsItem(
                            title=f"热门数据集: {dataset.id}",
                            content=self._format_dataset_content(dataset_info),
                            url=f"https://huggingface.co/datasets/{dataset.id}",
                            source="huggingface_datasets",
                            published_date=dataset_info.get('created_at', datetime.now()),
                            tags=self._extract_dataset_tags(dataset_info)
                        )
                        datasets.append(news_item)
                
                except Exception as e:
                    self.logger.warning(f"获取数据集信息失败 {dataset.id}: {e}")
                    continue
                
                self._rate_limit()
        
        except Exception as e:
            self.logger.error(f"获取热门数据集失败: {e}")
        
        return datasets
    
    def _get_recent_models(self, max_models: int = 5) -> List[NewsItem]:
        """
        获取最新模型
        
        Args:
            max_models: 最大模型数量
            
        Returns:
            List[NewsItem]: 模型资讯列表
        """
        models = []
        
        try:
            # 获取最新模型（按创建时间排序）
            model_list = list(self.api.list_models(
                sort="createdAt",
                direction=-1,
                limit=max_models * 2
            ))
            
            # 过滤最近7天的模型
            recent_date = get_utc_now() - timedelta(days=7)
            
            for model in model_list:
                try:
                    model_info = self._get_model_info(model.modelId)
                    
                    # 安全的日期比较
                    if model_info and is_recent(model_info.get('created_at'), days=30):
                        news_item = NewsItem(
                            title=f"新发布模型: {model.modelId}",
                            content=self._format_model_content(model_info),
                            url=f"https://huggingface.co/{model.modelId}",
                            source="huggingface_new_models",
                            published_date=model_info.get('created_at', datetime.now()),
                            tags=self._extract_model_tags(model_info) + ['new-release']
                        )
                        models.append(news_item)
                        
                        if len(models) >= max_models:
                            break
                
                except Exception as e:
                    self.logger.warning(f"获取新模型信息失败 {model.modelId}: {e}")
                    continue
                
                self._rate_limit()
        
        except Exception as e:
            self.logger.error(f"获取最新模型失败: {e}")
        
        return models
    
    def _get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        获取模型详细信息
        
        Args:
            model_id: 模型ID
            
        Returns:
            Optional[Dict[str, Any]]: 模型信息
        """
        try:
            model_info = self.api.model_info(model_id)
            
            return {
                'id': model_info.modelId,
                'author': getattr(model_info, 'author', ''),
                'downloads': getattr(model_info, 'downloads', 0),
                'likes': getattr(model_info, 'likes', 0),
                'tags': getattr(model_info, 'tags', []),
                'pipeline_tag': getattr(model_info, 'pipeline_tag', ''),
                'library_name': getattr(model_info, 'library_name', ''),
                'created_at': getattr(model_info, 'created_at', datetime.now()),
                'last_modified': getattr(model_info, 'last_modified', datetime.now()),
                'card_data': getattr(model_info, 'card_data', {}),
                'siblings': getattr(model_info, 'siblings', [])
            }
        
        except Exception as e:
            self.logger.warning(f"获取模型信息失败 {model_id}: {e}")
            return None
    
    def _get_dataset_info(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """
        获取数据集详细信息
        
        Args:
            dataset_id: 数据集ID
            
        Returns:
            Optional[Dict[str, Any]]: 数据集信息
        """
        try:
            dataset_info = self.api.dataset_info(dataset_id)
            
            return {
                'id': dataset_info.id,
                'author': getattr(dataset_info, 'author', ''),
                'downloads': getattr(dataset_info, 'downloads', 0),
                'likes': getattr(dataset_info, 'likes', 0),
                'tags': getattr(dataset_info, 'tags', []),
                'created_at': getattr(dataset_info, 'created_at', datetime.now()),
                'last_modified': getattr(dataset_info, 'last_modified', datetime.now()),
                'card_data': getattr(dataset_info, 'card_data', {}),
                'siblings': getattr(dataset_info, 'siblings', [])
            }
        
        except Exception as e:
            self.logger.warning(f"获取数据集信息失败 {dataset_id}: {e}")
            return None
    
    def _format_model_content(self, model_info: Dict[str, Any]) -> str:
        """
        格式化模型内容
        
        Args:
            model_info: 模型信息
            
        Returns:
            str: 格式化后的内容
        """
        content_parts = []
        
        content_parts.append(f"模型ID: {model_info['id']}")
        
        if model_info.get('author'):
            content_parts.append(f"作者: {model_info['author']}")
        
        if model_info.get('pipeline_tag'):
            content_parts.append(f"任务类型: {model_info['pipeline_tag']}")
        
        if model_info.get('library_name'):
            content_parts.append(f"框架: {model_info['library_name']}")
        
        content_parts.append(f"下载量: {model_info.get('downloads', 0):,}")
        content_parts.append(f"点赞数: {model_info.get('likes', 0):,}")
        
        if model_info.get('tags'):
            tags = ", ".join(model_info['tags'][:10])
            content_parts.append(f"标签: {tags}")
        
        if model_info.get('created_at'):
            content_parts.append(f"创建时间: {model_info['created_at'].strftime('%Y-%m-%d')}")
        
        return "\n".join(content_parts)
    
    def _format_dataset_content(self, dataset_info: Dict[str, Any]) -> str:
        """
        格式化数据集内容
        
        Args:
            dataset_info: 数据集信息
            
        Returns:
            str: 格式化后的内容
        """
        content_parts = []
        
        content_parts.append(f"数据集ID: {dataset_info['id']}")
        
        if dataset_info.get('author'):
            content_parts.append(f"作者: {dataset_info['author']}")
        
        content_parts.append(f"下载量: {dataset_info.get('downloads', 0):,}")
        content_parts.append(f"点赞数: {dataset_info.get('likes', 0):,}")
        
        if dataset_info.get('tags'):
            tags = ", ".join(dataset_info['tags'][:10])
            content_parts.append(f"标签: {tags}")
        
        if dataset_info.get('created_at'):
            content_parts.append(f"创建时间: {dataset_info['created_at'].strftime('%Y-%m-%d')}")
        
        return "\n".join(content_parts)
    
    def _extract_model_tags(self, model_info: Dict[str, Any]) -> List[str]:
        """
        提取模型标签
        
        Args:
            model_info: 模型信息
            
        Returns:
            List[str]: 标签列表
        """
        tags = ['huggingface', 'model']
        
        if model_info.get('pipeline_tag'):
            tags.append(model_info['pipeline_tag'])
        
        if model_info.get('library_name'):
            tags.append(model_info['library_name'])
        
        if model_info.get('tags'):
            tags.extend(model_info['tags'][:5])  # 限制标签数量
        
        return list(set(tags))
    
    def _extract_dataset_tags(self, dataset_info: Dict[str, Any]) -> List[str]:
        """
        提取数据集标签
        
        Args:
            dataset_info: 数据集信息
            
        Returns:
            List[str]: 标签列表
        """
        tags = ['huggingface', 'dataset']
        
        if dataset_info.get('tags'):
            tags.extend(dataset_info['tags'][:5])
        
        return list(set(tags))

    def _safe_date_compare(self, date1, date2):
        """
        安全的日期比较，处理timezone-aware和naive datetime的混合情况

        Args:
            date1: 第一个日期
            date2: 第二个日期

        Returns:
            bool: date1 > date2
        """
        try:
            if date1 is None:
                return False

            # 如果date1是datetime.min，返回False
            if date1 == datetime.min:
                return False

            # 处理timezone问题
            from datetime import timezone

            # 如果date1有timezone信息而date2没有
            if date1.tzinfo is not None and date2.tzinfo is None:
                # 将date2转换为UTC
                date2 = date2.replace(tzinfo=timezone.utc)
            # 如果date2有timezone信息而date1没有
            elif date1.tzinfo is None and date2.tzinfo is not None:
                # 将date1转换为UTC
                date1 = date1.replace(tzinfo=timezone.utc)

            return date1 > date2

        except Exception as e:
            self.logger.warning(f"日期比较失败: {e}")
            return False
