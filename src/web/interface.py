"""
Web界面模块
提供基于Gradio的用户界面

Author: zengzhengtx
"""

import os
import gradio as gr
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from src.agent.config import load_config, AppConfig
from src.agent.ai_news_agent import AINewsAgent
from src.database.database import DatabaseManager
from src.database.models import Article
from src.utils.logger import get_logger, log_capture


class WebInterface:
    """Web界面类"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = load_config(config_path)
        self.logger = get_logger()
        
        # 初始化数据库
        self.db_manager = DatabaseManager(self.config.database_path)
        
        # 初始化智能体
        self.agent = AINewsAgent(config_path)
        
        # 运行状态
        self.is_running = False
        self.start_time = None
        
        self.logger.info("Web界面初始化完成")
    
    def create_interface(self) -> gr.Blocks:
        """
        创建Gradio界面
        
        Returns:
            gr.Blocks: Gradio界面
        """
        with gr.Blocks(title="AI资讯微信公众号智能体", theme=gr.themes.Soft()) as app:
            gr.Markdown("# 🤖 AI资讯微信公众号智能体")
            
            with gr.Tabs() as tabs:
                with gr.TabItem("控制台", id=0):
                    self._create_control_panel()
                
                with gr.TabItem("文章管理", id=1):
                    self._create_article_manager()
                
                with gr.TabItem("配置", id=2):
                    self._create_config_panel()
                
                with gr.TabItem("统计", id=3):
                    self._create_stats_panel()
            
            # 页面加载时自动刷新文章列表
            app.load(self._refresh_article_list)
        
        return app
    
    def _create_control_panel(self):
        """创建控制面板"""
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("## 智能体控制")
                
                with gr.Row():
                    self.start_btn = gr.Button("启动智能体", variant="primary")
                    self.stop_btn = gr.Button("停止智能体", variant="stop")
                
                self.status_text = gr.Textbox(
                    label="状态",
                    value="就绪",
                    interactive=False
                )
                
                self.progress_bar = gr.Progress()
                
                self.log_output = gr.Textbox(
                    label="日志输出",
                    value="",
                    lines=15,
                    max_lines=100,
                    interactive=False,
                    autoscroll=True
                )
                
                self.clear_log_btn = gr.Button("清空日志")
            
            with gr.Column(scale=1):
                gr.Markdown("## 运行信息")
                
                self.run_info = gr.JSON(
                    label="运行信息",
                    value=self._get_run_info()
                )
                
                self.refresh_info_btn = gr.Button("刷新信息")
                
                gr.Markdown("## 快速操作")
                
                with gr.Row():
                    self.collect_one_btn = gr.Button("获取单篇文章")
                    self.view_latest_btn = gr.Button("查看最新文章")
        
        # 绑定事件
        self.start_btn.click(
            fn=self._start_agent,
            outputs=[self.status_text, self.log_output, self.run_info]
        )
        
        self.stop_btn.click(
            fn=self._stop_agent,
            outputs=[self.status_text, self.log_output, self.run_info]
        )
        
        self.clear_log_btn.click(
            fn=self._clear_logs,
            outputs=[self.log_output]
        )
        
        self.refresh_info_btn.click(
            fn=self._get_run_info,
            outputs=[self.run_info]
        )
        
        self.collect_one_btn.click(
            fn=self._collect_one_article,
            outputs=[self.status_text, self.log_output, self.run_info]
        )
    
    def _create_article_manager(self):
        """创建文章管理界面"""
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## 文章列表")
                
                self.article_filter = gr.Dropdown(
                    label="状态过滤",
                    choices=["全部", "草稿", "已发布", "已归档"],
                    value="全部"
                )
                
                self.article_list = gr.Dataframe(
                    headers=["ID", "标题", "状态", "来源", "创建时间", "质量分数"],
                    datatype=["number", "str", "str", "str", "str", "number"],
                    label="文章列表",
                    interactive=False,
                    wrap=True
                )
                
                self.refresh_articles_btn = gr.Button("刷新列表")
            
            with gr.Column(scale=2):
                gr.Markdown("## 文章预览")
                
                self.article_id_input = gr.Number(
                    label="文章ID",
                    value=0,
                    precision=0
                )
                
                self.article_title = gr.Textbox(
                    label="标题",
                    interactive=True
                )
                
                self.article_content = gr.Markdown(
                    label="内容",
                    value="选择文章以查看内容"
                )
                
                with gr.Row():
                    self.load_article_btn = gr.Button("加载文章")
                    self.save_article_btn = gr.Button("保存修改")
                    self.export_article_btn = gr.Button("导出文章")
        
        # 绑定事件
        self.article_filter.change(
            fn=self._filter_articles,
            inputs=[self.article_filter],
            outputs=[self.article_list]
        )
        
        self.refresh_articles_btn.click(
            fn=self._refresh_article_list,
            outputs=[self.article_list]
        )
        
        self.article_list.select(
            fn=self._select_article,
            outputs=[self.article_id_input, self.article_title, self.article_content]
        )
        
        self.load_article_btn.click(
            fn=self._load_article,
            inputs=[self.article_id_input],
            outputs=[self.article_title, self.article_content]
        )
        
        self.save_article_btn.click(
            fn=self._save_article_changes,
            inputs=[self.article_id_input, self.article_title, self.article_content],
            outputs=[self.article_list]
        )
        
        self.export_article_btn.click(
            fn=self._export_article,
            inputs=[self.article_id_input]
        )
    
    def _create_config_panel(self):
        """创建配置面板"""
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 基本配置")
                
                self.openai_api_key = gr.Textbox(
                    label="OpenAI API密钥",
                    value=self.config.openai_api_key or "",
                    type="password"
                )
                
                self.model_id = gr.Dropdown(
                    label="模型",
                    choices=["gpt-4o", "gpt-4", "gpt-3.5-turbo"],
                    value=self.config.agent.model_id
                )
                
                self.max_articles = gr.Slider(
                    label="每次运行最大文章数",
                    minimum=1,
                    maximum=10,
                    value=self.config.agent.max_articles_per_run,
                    step=1
                )
                
                self.save_config_btn = gr.Button("保存配置")
            
            with gr.Column():
                gr.Markdown("## 资讯源配置")
                
                with gr.Row():
                    self.enable_web_search = gr.Checkbox(
                        label="启用网络搜索",
                        value=self.config.sources.web_search.enabled
                    )
                    
                    self.enable_arxiv = gr.Checkbox(
                        label="启用arXiv",
                        value=self.config.sources.arxiv.enabled
                    )
                
                with gr.Row():
                    self.enable_huggingface = gr.Checkbox(
                        label="启用Hugging Face",
                        value=self.config.sources.huggingface.enabled
                    )
                    
                    self.enable_github = gr.Checkbox(
                        label="启用GitHub",
                        value=self.config.sources.github.enabled
                    )
                
                gr.Markdown("## 输出配置")
                
                with gr.Row():
                    self.include_images = gr.Checkbox(
                        label="包含配图建议",
                        value=self.config.output.include_images
                    )
                    
                    self.include_source_links = gr.Checkbox(
                        label="包含原始链接",
                        value=self.config.output.include_source_links
                    )
                    
                    self.add_emojis = gr.Checkbox(
                        label="添加表情符号",
                        value=self.config.output.add_emojis
                    )
        
        # 绑定事件
        self.save_config_btn.click(
            fn=self._save_config,
            inputs=[
                self.openai_api_key,
                self.model_id,
                self.max_articles,
                self.enable_web_search,
                self.enable_arxiv,
                self.enable_huggingface,
                self.enable_github,
                self.include_images,
                self.include_source_links,
                self.add_emojis
            ],
            outputs=[self.status_text]
        )
    
    def _create_stats_panel(self):
        """创建统计面板"""
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 文章统计")
                
                self.article_stats = gr.JSON(
                    label="文章统计",
                    value=self._get_article_stats()
                )
                
                self.refresh_stats_btn = gr.Button("刷新统计")
            
            with gr.Column():
                gr.Markdown("## 来源分布")
                
                self.source_chart = gr.BarPlot(
                    x="来源",
                    y="数量",
                    title="资讯来源分布",
                    tooltip=["来源", "数量"],
                    height=300,
                    width=500
                )
        
        # 绑定事件
        self.refresh_stats_btn.click(
            fn=self._refresh_stats,
            outputs=[self.article_stats, self.source_chart]
        )
    
    def _start_agent(self) -> Tuple[str, str, Dict[str, Any]]:
        """
        启动智能体
        
        Returns:
            Tuple[str, str, Dict[str, Any]]: 状态文本、日志输出、运行信息
        """
        if self.is_running:
            return "智能体已在运行中", log_capture.get_logs(), self._get_run_info()
        
        self.is_running = True
        self.start_time = datetime.now()
        
        self.logger.info("启动智能体...")
        
        try:
            # 清空日志
            log_capture.clear_logs()
            
            # 启动智能体
            self.agent.run_news_collection()
            
            self.is_running = False
            
            return "运行完成", log_capture.get_logs(), self._get_run_info()
            
        except Exception as e:
            self.logger.error(f"智能体运行失败: {e}")
            self.is_running = False
            return f"运行失败: {str(e)}", log_capture.get_logs(), self._get_run_info()
    
    def _stop_agent(self) -> Tuple[str, str, Dict[str, Any]]:
        """
        停止智能体
        
        Returns:
            Tuple[str, str, Dict[str, Any]]: 状态文本、日志输出、运行信息
        """
        if not self.is_running:
            return "智能体未在运行", log_capture.get_logs(), self._get_run_info()
        
        self.logger.info("停止智能体...")
        self.is_running = False
        
        return "已停止", log_capture.get_logs(), self._get_run_info()
    
    def _clear_logs(self) -> str:
        """
        清空日志
        
        Returns:
            str: 空日志
        """
        log_capture.clear_logs()
        return ""
    
    def _get_run_info(self) -> Dict[str, Any]:
        """
        获取运行信息
        
        Returns:
            Dict[str, Any]: 运行信息
        """
        info = {
            "状态": "运行中" if self.is_running else "就绪",
            "开始时间": self.start_time.strftime("%Y-%m-%d %H:%M:%S") if self.start_time else "无",
            "运行时长": str(datetime.now() - self.start_time).split('.')[0] if self.start_time else "0",
            "文章总数": self.db_manager.get_articles_stats().get('total', 0),
            "今日新增": self.db_manager.get_articles_stats().get('today', 0)
        }
        
        return info
    
    def _collect_one_article(self) -> Tuple[str, str, Dict[str, Any]]:
        """
        获取单篇文章
        
        Returns:
            Tuple[str, str, Dict[str, Any]]: 状态文本、日志输出、运行信息
        """
        if self.is_running:
            return "智能体已在运行中", log_capture.get_logs(), self._get_run_info()
        
        self.is_running = True
        self.start_time = datetime.now()
        
        self.logger.info("开始获取单篇文章...")
        
        try:
            # 清空日志
            log_capture.clear_logs()
            
            # 设置最大文章数为1
            original_max = self.config.agent.max_articles_per_run
            self.config.agent.max_articles_per_run = 1
            
            # 运行智能体
            self.agent.run_news_collection()
            
            # 恢复设置
            self.config.agent.max_articles_per_run = original_max
            
            self.is_running = False
            
            return "获取完成", log_capture.get_logs(), self._get_run_info()
            
        except Exception as e:
            self.logger.error(f"获取单篇文章失败: {e}")
            self.is_running = False
            return f"获取失败: {str(e)}", log_capture.get_logs(), self._get_run_info()
    
    def _refresh_article_list(self) -> List[List[Any]]:
        """
        刷新文章列表
        
        Returns:
            List[List[Any]]: 文章列表数据
        """
        articles = self.db_manager.get_articles(limit=50)
        
        data = []
        for article in articles:
            data.append([
                article.id,
                article.title,
                article.status,
                article.source_type,
                article.created_at.strftime("%Y-%m-%d %H:%M"),
                round(article.quality_score, 2)
            ])
        
        return data
    
    def _filter_articles(self, filter_value: str) -> List[List[Any]]:
        """
        过滤文章列表
        
        Args:
            filter_value: 过滤值
            
        Returns:
            List[List[Any]]: 过滤后的文章列表
        """
        status_map = {
            "全部": None,
            "草稿": "draft",
            "已发布": "published",
            "已归档": "archived"
        }
        
        status = status_map.get(filter_value)
        
        articles = self.db_manager.get_articles(status=status, limit=50)
        
        data = []
        for article in articles:
            data.append([
                article.id,
                article.title,
                article.status,
                article.source_type,
                article.created_at.strftime("%Y-%m-%d %H:%M"),
                round(article.quality_score, 2)
            ])
        
        return data
    
    def _select_article(self, evt: gr.SelectData) -> Tuple[int, str, str]:
        """
        选择文章
        
        Args:
            evt: 选择事件
            
        Returns:
            Tuple[int, str, str]: 文章ID、标题、内容
        """
        row_index = evt.index[0]
        article_id = self.article_list.value[row_index][0]
        
        article = self.db_manager.get_article(article_id)
        
        if article:
            return article.id, article.title, article.content
        else:
            return 0, "", "文章不存在"
    
    def _load_article(self, article_id: int) -> Tuple[str, str]:
        """
        加载文章
        
        Args:
            article_id: 文章ID
            
        Returns:
            Tuple[str, str]: 标题、内容
        """
        article = self.db_manager.get_article(article_id)
        
        if article:
            return article.title, article.content
        else:
            return "", "文章不存在"
    
    def _save_article_changes(
        self, 
        article_id: int, 
        title: str, 
        content: str
    ) -> List[List[Any]]:
        """
        保存文章修改
        
        Args:
            article_id: 文章ID
            title: 标题
            content: 内容
            
        Returns:
            List[List[Any]]: 更新后的文章列表
        """
        article = self.db_manager.get_article(article_id)
        
        if article:
            article.title = title
            article.content = content
            article.updated_at = datetime.now()
            
            self.db_manager.save_article(article)
            
            self.logger.info(f"文章已更新: ID={article_id}")
        
        return self._refresh_article_list()
    
    def _export_article(self, article_id: int) -> Optional[str]:
        """
        导出文章
        
        Args:
            article_id: 文章ID
            
        Returns:
            Optional[str]: 导出路径
        """
        article = self.db_manager.get_article(article_id)
        
        if not article:
            return None
        
        # 创建导出目录
        export_dir = "output/exports"
        os.makedirs(export_dir, exist_ok=True)
        
        # 生成文件名
        filename = f"{export_dir}/article_{article_id}_{int(time.time())}.md"
        
        # 写入文件
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(article.content)
        
        self.logger.info(f"文章已导出: {filename}")
        
        return filename
    
    def _save_config(
        self,
        api_key: str,
        model_id: str,
        max_articles: int,
        enable_web_search: bool,
        enable_arxiv: bool,
        enable_huggingface: bool,
        enable_github: bool,
        include_images: bool,
        include_source_links: bool,
        add_emojis: bool
    ) -> str:
        """
        保存配置
        
        Returns:
            str: 状态消息
        """
        try:
            # 更新配置
            self.config.openai_api_key = api_key
            self.config.agent.model_id = model_id
            self.config.agent.max_articles_per_run = int(max_articles)
            
            self.config.sources.web_search.enabled = enable_web_search
            self.config.sources.arxiv.enabled = enable_arxiv
            self.config.sources.huggingface.enabled = enable_huggingface
            self.config.sources.github.enabled = enable_github
            
            self.config.output.include_images = include_images
            self.config.output.include_source_links = include_source_links
            self.config.output.add_emojis = add_emojis
            
            # 保存到环境变量
            os.environ["OPENAI_API_KEY"] = api_key
            
            # 重新初始化智能体
            self.agent = AINewsAgent()
            
            self.logger.info("配置已更新")
            
            return "配置已保存"
            
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}")
            return f"保存失败: {str(e)}"
    
    def _get_article_stats(self) -> Dict[str, Any]:
        """
        获取文章统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            self.logger.info("开始获取文章统计信息...")
            stats = self.db_manager.get_articles_stats()

            result = {
                "总文章数": stats.get('total', 0),
                "草稿": stats.get('status_draft', 0),
                "已发布": stats.get('status_published', 0),
                "已归档": stats.get('status_archived', 0),
                "今日新增": stats.get('today', 0)
            }

            self.logger.info(f"文章统计信息获取成功: {result}")
            return result

        except Exception as e:
            self.logger.error(f"获取文章统计信息失败: {e}")
            return {
                "总文章数": 0,
                "草稿": 0,
                "已发布": 0,
                "已归档": 0,
                "今日新增": 0,
                "错误": str(e)
            }
    
    def _get_source_distribution(self) -> Dict[str, List[Any]]:
        """
        获取来源分布

        Returns:
            Dict[str, List[Any]]: 来源分布数据
        """
        try:
            self.logger.info("开始获取来源分布数据...")
            articles = self.db_manager.get_articles(limit=100)

            source_counts = {}
            for article in articles:
                source = article.source_type or "未知来源"
                if source in source_counts:
                    source_counts[source] += 1
                else:
                    source_counts[source] = 1

            # 如果没有数据，返回默认数据
            if not source_counts:
                source_counts = {"暂无数据": 0}

            data = {
                "来源": list(source_counts.keys()),
                "数量": list(source_counts.values())
            }

            self.logger.info(f"来源分布数据获取成功: {data}")
            return data

        except Exception as e:
            self.logger.error(f"获取来源分布数据失败: {e}")
            return {
                "来源": ["错误"],
                "数量": [0]
            }
    
    def _refresh_stats(self) -> Tuple[Dict[str, Any], Dict[str, List[Any]]]:
        """
        刷新统计信息

        Returns:
            Tuple[Dict[str, Any], Dict[str, List[Any]]]: 文章统计和来源分布
        """
        try:
            self.logger.info("开始刷新统计信息...")

            # 获取文章统计
            article_stats = self._get_article_stats()

            # 获取来源分布
            source_distribution = self._get_source_distribution()

            self.logger.info("统计信息刷新完成")
            return article_stats, source_distribution

        except Exception as e:
            self.logger.error(f"刷新统计信息失败: {e}")

            # 返回错误信息
            error_stats = {
                "错误": f"刷新失败: {str(e)}",
                "总文章数": 0,
                "草稿": 0,
                "已发布": 0,
                "已归档": 0,
                "今日新增": 0
            }

            error_distribution = {
                "来源": ["错误"],
                "数量": [0]
            }

            return error_stats, error_distribution
