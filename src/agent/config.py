"""
配置管理模块
负责加载和管理应用程序配置
"""

import os
import yaml
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class SourceConfig(BaseModel):
    """资讯源配置基类"""
    enabled: bool = True
    max_items: int = 10


class ArxivConfig(SourceConfig):
    """arXiv配置"""
    categories: List[str] = ["cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.NE"]
    days_back: int = 7


class WebSearchConfig(SourceConfig):
    """网络搜索配置"""
    queries: List[str] = [
        "AI news today",
        "artificial intelligence breakthrough",
        "machine learning research",
        "deep learning advances"
    ]
    max_results_per_query: int = 5


class HuggingFaceConfig(SourceConfig):
    """Hugging Face配置"""
    trending_period: str = "daily"


class GitHubConfig(SourceConfig):
    """GitHub配置"""
    topics: List[str] = [
        "artificial-intelligence",
        "machine-learning", 
        "deep-learning",
        "nlp"
    ]
    max_repos: int = 10
    min_stars: int = 100


class SourcesConfig(BaseModel):
    """所有资讯源配置"""
    arxiv: ArxivConfig = ArxivConfig()
    web_search: WebSearchConfig = WebSearchConfig()
    huggingface: HuggingFaceConfig = HuggingFaceConfig()
    github: GitHubConfig = GitHubConfig()


class AgentConfig(BaseModel):
    """智能体配置"""
    model_type: str = "openai"
    model_id: str = "gpt-4o"
    max_steps: int = 20
    max_articles_per_run: int = 5


class ContentConfig(BaseModel):
    """内容处理配置"""
    min_quality_score: float = 0.6
    max_article_length: int = 3000
    min_article_length: int = 800
    duplicate_threshold: float = 0.8


class OutputConfig(BaseModel):
    """输出配置"""
    format: str = "wechat"
    include_images: bool = True
    include_source_links: bool = True
    add_emojis: bool = True


class ScheduleConfig(BaseModel):
    """定时任务配置"""
    enabled: bool = False
    interval: str = "daily"
    time: str = "09:00"


class WebUIConfig(BaseModel):
    """Web界面配置"""
    host: str = "127.0.0.1"
    port: int = 7860
    share: bool = False
    theme: str = "default"


class AppConfig(BaseModel):
    """应用程序主配置"""
    agent: AgentConfig = AgentConfig()
    sources: SourcesConfig = SourcesConfig()
    content: ContentConfig = ContentConfig()
    output: OutputConfig = OutputConfig()
    schedule: ScheduleConfig = ScheduleConfig()
    web_ui: WebUIConfig = WebUIConfig()
    
    # 从环境变量获取的配置
    openai_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    github_token: Optional[str] = Field(default_factory=lambda: os.getenv("GITHUB_TOKEN"))
    database_path: str = Field(default_factory=lambda: os.getenv("DATABASE_PATH", "data/articles.db"))
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    log_file: str = Field(default_factory=lambda: os.getenv("LOG_FILE", "logs/app.log"))
    cache_dir: str = Field(default_factory=lambda: os.getenv("CACHE_DIR", "data/cache"))
    cache_expire_hours: int = Field(default_factory=lambda: int(os.getenv("CACHE_EXPIRE_HOURS", "24")))


def load_config(config_path: str = "config.yaml") -> AppConfig:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        AppConfig: 应用程序配置对象
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        return AppConfig(**config_data)
    except FileNotFoundError:
        print(f"配置文件 {config_path} 未找到，使用默认配置")
        return AppConfig()
    except Exception as e:
        print(f"加载配置文件失败: {e}，使用默认配置")
        return AppConfig()


def save_config(config: AppConfig, config_path: str = "config.yaml") -> None:
    """
    保存配置到文件
    
    Args:
        config: 应用程序配置对象
        config_path: 配置文件路径
    """
    try:
        # 排除环境变量字段
        config_dict = config.model_dump(exclude={
            'openai_api_key', 'github_token', 'database_path', 
            'log_level', 'log_file', 'cache_dir', 'cache_expire_hours'
        })
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
        
        print(f"配置已保存到 {config_path}")
    except Exception as e:
        print(f"保存配置文件失败: {e}")


# 全局配置实例
config = load_config()
