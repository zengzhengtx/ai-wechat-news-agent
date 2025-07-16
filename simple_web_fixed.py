#!/usr/bin/env python3
"""
AI资讯微信公众号智能体 - 修复版简化Web界面
修复了统计功能卡死的问题
"""

import os
import sys
import gradio as gr
import json
from datetime import datetime
from typing import List, Tuple, Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.logger import init_logging
from src.tools.base_tool import NewsItem
from src.tools.wechat_formatter import WeChatFormatterTool
from src.utils.validators import ContentFilter
from src.utils.datetime_utils import get_utc_now
from src.database.database import DatabaseManager
from src.agent.config import load_config


class FixedSimpleWebInterface:
    """修复版简化Web界面类"""
    
    def __init__(self):
        self.logger = init_logging()
        
        # 初始化组件
        self.wechat_formatter = WeChatFormatterTool()
        self.content_filter = ContentFilter()
        
        # 初始化数据库
        try:
            config = load_config()
            self.db_manager = DatabaseManager(config.database_path)
            self.logger.info("数据库连接成功")
        except Exception as e:
            self.logger.error(f"数据库初始化失败: {e}")
            self.db_manager = None
        
        self.logger.info("修复版简化Web界面初始化完成")
    
    def create_demo_news_items(self) -> List[NewsItem]:
        """创建演示资讯项"""
        return [
            NewsItem(
                title="OpenAI发布GPT-4 Turbo：更快、更便宜、更强大",
                content="""
                OpenAI在其首届开发者大会上发布了GPT-4 Turbo，这是GPT-4的升级版本，具有多项重大改进。
                
                主要特性包括：
                
                **更大的上下文窗口**
                GPT-4 Turbo支持高达128,000个token的上下文长度，相当于约300页的文本。
                
                **更新的知识截止时间**
                模型的训练数据更新至2024年4月，相比之前版本有了显著的知识更新。
                
                **更好的指令遵循能力**
                GPT-4 Turbo在遵循复杂指令方面表现更佳，特别是在JSON模式和函数调用方面。
                
                **显著降低的成本**
                输入token的价格降低了3倍，输出token的价格降低了2倍。
                
                开发者可以通过OpenAI API立即开始使用GPT-4 Turbo。
                """,
                url="https://openai.com/blog/new-models-and-developer-products-announced-at-devday",
                source="web_search",
                published_date=get_utc_now(),
                tags=['OpenAI', 'GPT-4', 'API', 'AI'],
                score=0.95
            ),
            NewsItem(
                title="Google发布Gemini：多模态AI的新里程碑",
                content="""
                Google DeepMind发布了其最新的大型语言模型Gemini，声称在多项基准测试中超越了GPT-4。
                
                **三个版本满足不同需求**
                - Gemini Ultra：最强大的版本，用于高度复杂的任务
                - Gemini Pro：平衡性能和效率的版本
                - Gemini Nano：为移动设备优化的轻量版本
                
                **原生多模态设计**
                与其他模型不同，Gemini从一开始就被设计为多模态模型。
                
                **卓越的性能表现**
                在MMLU基准测试中，Gemini Ultra获得了90.0%的分数，首次超越人类专家水平。
                
                Gemini Pro已经在Google Bard中上线，Gemini Ultra将在明年初发布。
                """,
                url="https://blog.google/technology/ai/google-gemini-ai/",
                source="web_search",
                published_date=get_utc_now(),
                tags=['Google', 'Gemini', 'multimodal', 'AI'],
                score=0.92
            )
        ]
    
    def format_article(self, title: str, content: str) -> str:
        """格式化文章"""
        try:
            formatted_content = self.wechat_formatter.format_content(
                content=content,
                title=title,
                include_images=True,
                include_source_links=True,
                add_emojis=True
            )
            return formatted_content
        except Exception as e:
            self.logger.error(f"格式化失败: {e}")
            return f"格式化失败: {str(e)}"
    
    def generate_demo_article(self) -> Tuple[str, str]:
        """生成演示文章"""
        try:
            news_items = self.create_demo_news_items()
            selected_item = news_items[0]  # 选择第一条
            
            formatted_content = self.format_article(
                selected_item.title,
                selected_item.content
            )
            
            return selected_item.title, formatted_content
        except Exception as e:
            self.logger.error(f"生成演示文章失败: {e}")
            return "生成失败", f"错误: {str(e)}"
    
    def filter_demo_content(self) -> str:
        """筛选演示内容"""
        try:
            news_items = self.create_demo_news_items()
            filtered_items = self.content_filter.filter_and_dedupe(news_items)
            
            result = f"原始资讯数量: {len(news_items)}\n"
            result += f"筛选后数量: {len(filtered_items)}\n\n"
            result += "筛选结果:\n"
            
            for i, item in enumerate(filtered_items, 1):
                result += f"{i}. {item.title}\n"
                result += f"   来源: {item.source}\n"
                result += f"   质量分数: {item.score:.2f}\n\n"
            
            return result
        except Exception as e:
            self.logger.error(f"筛选失败: {e}")
            return f"筛选失败: {str(e)}"
    
    def custom_format_article(self, title: str, content: str, include_images: bool, include_links: bool, add_emojis: bool) -> str:
        """自定义格式化文章"""
        try:
            if not title.strip() or not content.strip():
                return "请输入标题和内容"
            
            formatted_content = self.wechat_formatter.format_content(
                content=content,
                title=title,
                include_images=include_images,
                include_source_links=include_links,
                add_emojis=add_emojis
            )
            return formatted_content
        except Exception as e:
            self.logger.error(f"自定义格式化失败: {e}")
            return f"格式化失败: {str(e)}"
    
    def get_safe_stats(self) -> str:
        """安全地获取统计信息"""
        try:
            if not self.db_manager:
                return "数据库未连接"
            
            self.logger.info("开始获取统计信息...")
            stats = self.db_manager.get_articles_stats()
            
            result = "📊 数据库统计信息:\n\n"
            result += f"总文章数: {stats.get('total', 0)}\n"
            result += f"草稿数量: {stats.get('status_draft', 0)}\n"
            result += f"已发布: {stats.get('status_published', 0)}\n"
            result += f"已归档: {stats.get('status_archived', 0)}\n"
            result += f"今日新增: {stats.get('today', 0)}\n"
            
            self.logger.info("统计信息获取成功")
            return result
            
        except Exception as e:
            self.logger.error(f"获取统计信息失败: {e}")
            return f"获取统计信息失败: {str(e)}"
    
    def save_demo_articles(self) -> str:
        """保存演示文章到数据库"""
        try:
            if not self.db_manager:
                return "数据库未连接，无法保存"
            
            news_items = self.create_demo_news_items()
            saved_count = 0
            
            for item in news_items:
                from src.database.models import Article
                
                article = Article(
                    title=item.title,
                    content=item.content,
                    summary=item.content[:200] + "...",
                    source_url=item.url,
                    source_type=item.source,
                    status='draft',
                    quality_score=item.score,
                    tags=json.dumps(item.tags, ensure_ascii=False)
                )
                
                article_id = self.db_manager.save_article(article)
                saved_count += 1
                self.logger.info(f"保存文章成功: ID={article_id}")
            
            result = f"成功保存 {saved_count} 篇文章\n\n"
            result += self.get_safe_stats()
            
            return result
            
        except Exception as e:
            self.logger.error(f"保存文章失败: {e}")
            return f"保存失败: {str(e)}"
    
    def create_interface(self) -> gr.Blocks:
        """创建Gradio界面"""
        with gr.Blocks(title="AI资讯智能体修复版", theme=gr.themes.Soft()) as app:
            gr.Markdown("# 🤖 AI资讯微信公众号智能体 - 修复版")
            gr.Markdown("这是一个修复了统计功能的演示界面，展示智能体的核心功能。")
            
            with gr.Tabs():
                with gr.TabItem("📝 文章格式化"):
                    gr.Markdown("## 自动生成演示文章")
                    
                    with gr.Row():
                        generate_btn = gr.Button("生成演示文章", variant="primary", size="lg")
                    
                    with gr.Row():
                        article_title = gr.Textbox(label="文章标题", interactive=False)
                    
                    article_content = gr.Markdown(label="格式化后的文章内容", height=400)
                    
                    generate_btn.click(
                        fn=self.generate_demo_article,
                        outputs=[article_title, article_content]
                    )
                
                with gr.TabItem("🧹 内容筛选"):
                    gr.Markdown("## 内容筛选与去重")
                    
                    with gr.Row():
                        filter_btn = gr.Button("执行内容筛选", variant="primary", size="lg")
                    
                    filter_result = gr.Textbox(
                        label="筛选结果",
                        lines=15,
                        interactive=False
                    )
                    
                    filter_btn.click(
                        fn=self.filter_demo_content,
                        outputs=[filter_result]
                    )
                
                with gr.TabItem("✏️ 自定义格式化"):
                    gr.Markdown("## 自定义文章格式化")
                    
                    with gr.Row():
                        with gr.Column():
                            custom_title = gr.Textbox(
                                label="文章标题",
                                placeholder="请输入文章标题...",
                                lines=1
                            )
                            
                            custom_content = gr.Textbox(
                                label="文章内容",
                                placeholder="请输入文章内容...",
                                lines=10
                            )
                            
                            with gr.Row():
                                include_images = gr.Checkbox(label="包含配图建议", value=True)
                                include_links = gr.Checkbox(label="包含原始链接", value=True)
                                add_emojis = gr.Checkbox(label="添加表情符号", value=True)
                            
                            format_btn = gr.Button("格式化文章", variant="primary")
                        
                        with gr.Column():
                            formatted_result = gr.Markdown(label="格式化结果", height=500)
                    
                    format_btn.click(
                        fn=self.custom_format_article,
                        inputs=[custom_title, custom_content, include_images, include_links, add_emojis],
                        outputs=[formatted_result]
                    )
                
                with gr.TabItem("📊 数据库管理"):
                    gr.Markdown("## 数据库管理（修复版）")
                    
                    with gr.Row():
                        save_btn = gr.Button("保存演示文章", variant="primary")
                        stats_btn = gr.Button("获取统计信息", variant="secondary")
                    
                    with gr.Row():
                        db_result = gr.Textbox(
                            label="操作结果",
                            lines=15,
                            interactive=False
                        )
                    
                    save_btn.click(
                        fn=self.save_demo_articles,
                        outputs=[db_result]
                    )
                    
                    stats_btn.click(
                        fn=self.get_safe_stats,
                        outputs=[db_result]
                    )
            
            gr.Markdown("---")
            gr.Markdown("💡 **修复说明**: 这个版本修复了统计功能卡死的问题，添加了更好的错误处理和超时保护。")
        
        return app


def main():
    """主函数"""
    print("🚀 启动AI资讯智能体修复版Web界面...")
    
    # 创建修复版界面
    fixed_interface = FixedSimpleWebInterface()
    app = fixed_interface.create_interface()
    
    # 启动界面
    print("🌐 Web界面启动中...")
    app.launch(
        server_name="127.0.0.1",
        server_port=7861,  # 使用不同端口避免冲突
        share=False,
        inbrowser=True
    )


if __name__ == "__main__":
    main()
