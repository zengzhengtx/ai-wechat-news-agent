#!/usr/bin/env python3
"""
AI资讯微信公众号智能体 - 简化版Web演示
提供基本的Web界面演示功能

Author: zengzhengtx
"""

import os
import sys
import gradio as gr
import json
from datetime import datetime
from typing import List, Tuple, Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agent.config import load_config
from src.utils.logger import init_logging, log_capture
from src.tools.base_tool import NewsItem
from src.tools.wechat_formatter import WeChatFormatterTool
from src.utils.validators import ContentFilter
from src.utils.quality_control import QualityController
from src.database.database import DatabaseManager
from src.database.models import Article


class DemoWebInterface:
    """演示Web界面类"""
    
    def __init__(self):
        self.config = load_config()
        self.logger = init_logging()
        
        # 初始化组件
        self.db_manager = DatabaseManager(self.config.database_path)
        self.wechat_formatter = WeChatFormatterTool()
        self.content_filter = ContentFilter()
        self.quality_controller = QualityController()
        
        self.logger.info("演示Web界面初始化完成")
    
    def create_demo_news_items(self) -> List[NewsItem]:
        """创建演示资讯项"""
        return [
            NewsItem(
                title="OpenAI发布GPT-4.5：性能大幅提升",
                content="""
                OpenAI今日宣布发布GPT-4.5模型，该模型在多项基准测试中表现出色，推理能力和代码生成能力都有显著提升。
                
                新模型采用了改进的Transformer架构，训练数据规模达到了前所未有的水平。GPT-4.5在数学推理、编程和多语言理解方面都有巨大突破。
                
                主要改进包括：
                1. 上下文窗口扩展到128K tokens
                2. 推理速度提升3倍
                3. 幻觉现象显著减少
                4. 多模态能力增强
                
                OpenAI表示，GPT-4.5将首先向付费用户开放，随后逐步向开发者和企业用户推广。
                """,
                url="https://example.com/gpt-4.5-release",
                source="web_search",
                published_date=datetime.now(),
                tags=['AI', 'GPT', 'OpenAI'],
                score=0.9
            ),
            NewsItem(
                title="Meta推出新一代AI芯片，专为大模型训练优化",
                content="""
                Meta公司今日发布了专门为大型语言模型训练设计的AI芯片MTIA-2，该芯片采用7nm工艺，具有超高的计算密度和能效比。
                
                MTIA-2芯片的主要特点：
                - 每秒可执行400万亿次AI运算
                - 能效比较上一代提升60%
                - 支持混合精度计算
                - 内置大容量HBM3内存
                
                Meta表示，使用MTIA-2芯片集群训练大型语言模型，成本可降低40%，训练时间缩短50%。
                """,
                url="https://example.com/meta-ai-chip",
                source="web_search",
                published_date=datetime.now(),
                tags=['AI', 'Meta', 'chip'],
                score=0.8
            ),
            NewsItem(
                title="研究人员发布RLHF新方法，大幅提升AI模型安全性",
                content="""
                来自斯坦福大学和UC Berkeley的研究人员发布了一种名为"多层次RLHF"的新方法，可以大幅提升大型语言模型的安全性和对齐性。
                
                新提出的多层次RLHF方法引入了价值观层次结构，允许模型在不同情境下灵活应用不同的价值观权重。
                
                研究团队在多个开源模型上测试了这一方法，结果表明：
                - 有害输出减少了78%
                - 模型能力几乎没有损失
                - 价值观冲突情况下的表现更加平衡
                """,
                url="https://example.com/rlhf-new-method",
                source="arxiv_cs.AI",
                published_date=datetime.now(),
                tags=['AI', 'RLHF', 'alignment', 'safety'],
                score=0.85
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
            return f"筛选失败: {str(e)}"
    
    def save_demo_articles(self) -> str:
        """保存演示文章到数据库"""
        try:
            news_items = self.create_demo_news_items()
            saved_count = 0
            
            for item in news_items:
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
            
            stats = self.db_manager.get_articles_stats()
            
            result = f"成功保存 {saved_count} 篇文章\n\n"
            result += "数据库统计:\n"
            result += f"总文章数: {stats.get('total', 0)}\n"
            result += f"草稿数量: {stats.get('status_draft', 0)}\n"
            result += f"今日新增: {stats.get('today', 0)}\n"
            
            return result
        except Exception as e:
            return f"保存失败: {str(e)}"
    
    def get_article_list(self) -> List[List[Any]]:
        """获取文章列表"""
        try:
            articles = self.db_manager.get_articles(limit=20)
            
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
        except Exception as e:
            return [["错误", str(e), "", "", "", 0]]
    
    def load_article_content(self, article_id: int) -> Tuple[str, str]:
        """加载文章内容"""
        try:
            if article_id <= 0:
                return "", "请选择一篇文章"
            
            article = self.db_manager.get_article(article_id)
            if article:
                return article.title, article.content
            else:
                return "", "文章不存在"
        except Exception as e:
            return "", f"加载失败: {str(e)}"
    
    def create_interface(self) -> gr.Blocks:
        """创建Gradio界面"""
        with gr.Blocks(title="AI资讯智能体演示", theme=gr.themes.Soft()) as app:
            gr.Markdown("# 🤖 AI资讯微信公众号智能体演示")
            gr.Markdown("这是一个简化版的演示界面，展示智能体的核心功能。")
            
            with gr.Tabs():
                with gr.TabItem("文章格式化"):
                    gr.Markdown("## 📝 文章格式化演示")
                    gr.Markdown("点击按钮生成一篇格式化的微信公众号文章")
                    
                    with gr.Row():
                        generate_btn = gr.Button("生成演示文章", variant="primary")
                    
                    with gr.Row():
                        with gr.Column():
                            article_title = gr.Textbox(label="文章标题", interactive=False)
                        
                    article_content = gr.Markdown(label="格式化后的文章内容")
                    
                    generate_btn.click(
                        fn=self.generate_demo_article,
                        outputs=[article_title, article_content]
                    )
                
                with gr.TabItem("内容筛选"):
                    gr.Markdown("## 🧹 内容筛选演示")
                    gr.Markdown("演示智能体如何筛选和去重资讯内容")
                    
                    with gr.Row():
                        filter_btn = gr.Button("执行内容筛选", variant="primary")
                    
                    filter_result = gr.Textbox(
                        label="筛选结果",
                        lines=15,
                        interactive=False
                    )
                    
                    filter_btn.click(
                        fn=self.filter_demo_content,
                        outputs=[filter_result]
                    )
                
                with gr.TabItem("数据库管理"):
                    gr.Markdown("## 💾 数据库管理演示")
                    
                    with gr.Row():
                        with gr.Column():
                            save_btn = gr.Button("保存演示文章", variant="primary")
                            refresh_btn = gr.Button("刷新文章列表")
                            
                            save_result = gr.Textbox(
                                label="保存结果",
                                lines=8,
                                interactive=False
                            )
                        
                        with gr.Column():
                            article_list = gr.Dataframe(
                                headers=["ID", "标题", "状态", "来源", "创建时间", "质量分数"],
                                label="文章列表",
                                interactive=False
                            )
                    
                    with gr.Row():
                        article_id_input = gr.Number(
                            label="文章ID",
                            value=0,
                            precision=0
                        )
                        load_btn = gr.Button("加载文章")
                    
                    with gr.Row():
                        loaded_title = gr.Textbox(label="文章标题", interactive=False)
                    
                    loaded_content = gr.Markdown(label="文章内容")
                    
                    # 绑定事件
                    save_btn.click(
                        fn=self.save_demo_articles,
                        outputs=[save_result]
                    )
                    
                    refresh_btn.click(
                        fn=self.get_article_list,
                        outputs=[article_list]
                    )
                    
                    load_btn.click(
                        fn=self.load_article_content,
                        inputs=[article_id_input],
                        outputs=[loaded_title, loaded_content]
                    )
                    
                    # 页面加载时自动刷新文章列表
                    app.load(
                        fn=self.get_article_list,
                        outputs=[article_list]
                    )
            
            gr.Markdown("---")
            gr.Markdown("💡 **提示**: 这是一个演示版本，展示了智能体的核心功能。完整版本支持实时资讯获取和OpenAI API集成。")
        
        return app


def main():
    """主函数"""
    print("🚀 启动AI资讯智能体演示Web界面...")
    
    # 创建演示界面
    demo_interface = DemoWebInterface()
    app = demo_interface.create_interface()
    
    # 启动界面
    print("🌐 Web界面启动中...")
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        inbrowser=True
    )


if __name__ == "__main__":
    main()
