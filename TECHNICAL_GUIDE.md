# 技术实现指南

## 核心技术栈

### 主要依赖
```
smolagents>=1.20.0
openai>=1.0.0
gradio>=4.0.0
sqlite3 (内置)
requests>=2.28.0
beautifulsoup4>=4.11.0
feedparser>=6.0.0
arxiv>=1.4.0
PyGithub>=1.58.0
pydantic>=2.0.0
pyyaml>=6.0
python-dotenv>=1.0.0
schedule>=1.2.0
```

## 关键实现细节

### 1. smolagents集成方案

#### 模型配置
```python
from smolagents import CodeAgent, LiteLLMModel

# OpenAI模型初始化
model = LiteLLMModel(
    model_id="gpt-4",
    api_key=os.getenv("OPENAI_API_KEY")
)

# 智能体初始化
agent = CodeAgent(
    tools=[
        web_search_tool,
        arxiv_tool,
        huggingface_tool,
        github_tool,
        content_rewriter,
        wechat_formatter
    ],
    model=model,
    max_steps=20,
    add_base_tools=True
)
```

#### 工具开发模式
```python
from smolagents import Tool

class WebSearchTool(Tool):
    name = "web_search"
    description = "搜索最新AI资讯和新闻"
    inputs = {
        "query": {
            "type": "string",
            "description": "搜索关键词"
        },
        "max_results": {
            "type": "integer", 
            "description": "最大结果数量"
        }
    }
    output_type = "string"
    
    def forward(self, query: str, max_results: int = 10):
        # 实现搜索逻辑
        pass
```

### 2. 数据库设计

#### SQLite表结构
```sql
-- 文章表
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    source_url TEXT,
    source_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'draft',
    quality_score REAL,
    tags TEXT
);

-- 资讯源表
CREATE TABLE news_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    title TEXT,
    content TEXT,
    source_type TEXT,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE
);

-- 配置表
CREATE TABLE config (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. 工作流程实现

#### 主要工作流程
```python
async def run_news_collection_workflow():
    """主要的资讯收集工作流程"""
    
    # 1. 获取资讯
    news_items = []
    if config.sources.arxiv.enabled:
        arxiv_papers = await arxiv_tool.search_papers()
        news_items.extend(arxiv_papers)
    
    if config.sources.web_search.enabled:
        web_results = await web_search_tool.search()
        news_items.extend(web_results)
    
    # 2. 内容筛选和去重
    filtered_items = content_filter.filter_and_dedupe(news_items)
    
    # 3. 内容改写
    articles = []
    for item in filtered_items[:config.max_articles]:
        rewritten = await content_rewriter.rewrite(item)
        formatted = await wechat_formatter.format(rewritten)
        articles.append(formatted)
    
    # 4. 保存到数据库
    for article in articles:
        db.save_article(article)
    
    return articles
```

### 4. Gradio界面架构

#### 主界面结构
```python
import gradio as gr

def create_main_interface():
    with gr.Blocks(title="AI资讯智能体") as app:
        with gr.Tabs():
            with gr.Tab("控制台"):
                create_control_panel()
            
            with gr.Tab("文章管理"):
                create_article_manager()
            
            with gr.Tab("配置"):
                create_config_panel()
            
            with gr.Tab("统计"):
                create_stats_panel()
    
    return app

def create_control_panel():
    with gr.Row():
        start_btn = gr.Button("启动智能体", variant="primary")
        stop_btn = gr.Button("停止智能体", variant="secondary")
        status = gr.Textbox(label="状态", interactive=False)
    
    with gr.Row():
        progress = gr.Progress()
        logs = gr.Textbox(label="实时日志", lines=20, max_lines=50)
    
    # 绑定事件处理
    start_btn.click(
        fn=start_agent,
        outputs=[status, logs]
    )
```

### 5. 异步处理和状态管理

#### 异步任务管理
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AgentManager:
    def __init__(self):
        self.agent = None
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def start_collection(self, progress_callback=None):
        self.running = True
        
        try:
            while self.running:
                if progress_callback:
                    progress_callback("开始收集资讯...")
                
                # 异步执行智能体任务
                result = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self.agent.run,
                    "收集最新AI资讯并改写为微信公众号文章"
                )
                
                if progress_callback:
                    progress_callback(f"完成，生成了{len(result)}篇文章")
                
                # 等待下次执行
                await asyncio.sleep(config.collection_interval)
                
        except Exception as e:
            logger.error(f"智能体执行错误: {e}")
            raise
    
    def stop_collection(self):
        self.running = False
```

### 6. 配置管理系统

#### 配置类设计
```python
from pydantic import BaseModel
from typing import Optional
import yaml

class SourceConfig(BaseModel):
    enabled: bool = True
    max_items: int = 10

class ArxivConfig(SourceConfig):
    categories: list[str] = ["cs.AI", "cs.LG", "cs.CL"]

class OutputConfig(BaseModel):
    format: str = "wechat"
    max_length: int = 3000
    include_images: bool = True

class AgentConfig(BaseModel):
    model_type: str = "openai"
    model_id: str = "gpt-4"
    api_key: Optional[str] = None
    max_steps: int = 20

class AppConfig(BaseModel):
    agent: AgentConfig
    sources: dict
    output: OutputConfig
    web_ui: dict

def load_config(config_path: str = "config.yaml") -> AppConfig:
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)
    return AppConfig(**config_data)
```

### 7. 错误处理和重试机制

#### 重试装饰器
```python
import functools
import time
from typing import Callable, Any

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))  # 指数退避
                        continue
                    break
            
            raise last_exception
        return wrapper
    return decorator

# 使用示例
@retry_on_failure(max_retries=3, delay=1.0)
def call_openai_api(prompt: str) -> str:
    # OpenAI API调用逻辑
    pass
```

### 8. 内容质量控制

#### 质量评估算法
```python
class ContentQualityAssessor:
    def __init__(self):
        self.min_length = 500
        self.max_length = 5000
        self.required_keywords = ["AI", "人工智能", "机器学习"]
    
    def assess_quality(self, content: str) -> float:
        score = 0.0
        
        # 长度检查
        if self.min_length <= len(content) <= self.max_length:
            score += 0.3
        
        # 关键词检查
        keyword_count = sum(1 for kw in self.required_keywords if kw in content)
        score += (keyword_count / len(self.required_keywords)) * 0.3
        
        # 结构检查（标题、段落等）
        if self._has_good_structure(content):
            score += 0.2
        
        # 可读性检查
        readability_score = self._calculate_readability(content)
        score += readability_score * 0.2
        
        return min(score, 1.0)
    
    def _has_good_structure(self, content: str) -> bool:
        # 检查是否有标题、段落分隔等
        return "##" in content and "\n\n" in content
    
    def _calculate_readability(self, content: str) -> float:
        # 简单的可读性评估
        sentences = content.split('。')
        avg_sentence_length = sum(len(s) for s in sentences) / len(sentences)
        
        # 理想句子长度为20-40字符
        if 20 <= avg_sentence_length <= 40:
            return 1.0
        else:
            return max(0.0, 1.0 - abs(avg_sentence_length - 30) / 30)
```

### 9. 部署和运行

#### 启动脚本
```python
# main.py
import asyncio
import os
from src.agent.ai_news_agent import AINewsAgent
from src.web.interface import create_web_interface
from src.utils.logger import setup_logger

def main():
    # 设置日志
    logger = setup_logger()
    
    # 检查环境变量
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("请设置OPENAI_API_KEY环境变量")
    
    # 初始化智能体
    agent = AINewsAgent()
    
    # 启动Web界面
    app = create_web_interface(agent)
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )

if __name__ == "__main__":
    main()
```

### 10. 测试策略

#### 单元测试示例
```python
import pytest
from src.tools.web_search import WebSearchTool

class TestWebSearchTool:
    def setup_method(self):
        self.tool = WebSearchTool()
    
    def test_search_basic(self):
        results = self.tool.forward("AI news", max_results=5)
        assert len(results) <= 5
        assert all("AI" in result.lower() for result in results)
    
    @pytest.mark.asyncio
    async def test_search_async(self):
        results = await self.tool.async_search("machine learning")
        assert isinstance(results, list)
        assert len(results) > 0
```

这个技术实现指南提供了项目的核心技术细节和实现方案。现在请确认这些开发任务和技术方案是否符合您的需求，我将开始执行全自动开发。
