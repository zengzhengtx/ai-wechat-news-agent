#!/usr/bin/env python3
"""
AI资讯微信公众号智能体 - 简化版Web界面
不依赖LiteLLM，提供基本的Web演示功能

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

from src.utils.logger import init_logging
from src.tools.base_tool import NewsItem
from src.tools.wechat_formatter import WeChatFormatterTool
from src.utils.validators import ContentFilter


class SimpleWebInterface:
    """简化版Web界面类"""
    
    def __init__(self):
        self.logger = init_logging()
        
        # 初始化组件
        self.wechat_formatter = WeChatFormatterTool()
        self.content_filter = ContentFilter()
        
        self.logger.info("简化版Web界面初始化完成")
    
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
                
                业内专家认为，GPT-4.5的发布将进一步推动AI技术在各行业的应用，特别是在科研、教育和软件开发领域。
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
                
                Meta表示，使用MTIA-2芯片集群训练大型语言模型，成本可降低40%，训练时间缩短50%。这将大幅降低AI模型训练的门槛。
                
                Meta计划在自家数据中心大规模部署MTIA-2芯片，并考虑向其他AI研究机构提供云服务。
                
                这一举措被视为Meta对抗NVIDIA在AI芯片领域主导地位的重要一步。
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
                
                传统的RLHF（基于人类反馈的强化学习）方法在提升模型安全性方面取得了显著成效，但仍存在一些局限性。
                
                新提出的多层次RLHF方法引入了价值观层次结构，允许模型在不同情境下灵活应用不同的价值观权重。
                
                研究团队在多个开源模型上测试了这一方法，结果表明：
                - 有害输出减少了78%
                - 模型能力几乎没有损失
                - 价值观冲突情况下的表现更加平衡
                
                该研究已在arXiv上发布预印本，并计划在下个月的NeurIPS会议上正式发表。
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
            return f"格式化失败: {str(e)}"
    
    def create_interface(self) -> gr.Blocks:
        """创建Gradio界面"""
        with gr.Blocks(title="AI资讯智能体简化演示", theme=gr.themes.Soft()) as app:
            gr.Markdown("# 🤖 AI资讯微信公众号智能体 - 简化演示")
            gr.Markdown("这是一个简化版的演示界面，展示智能体的核心功能。")
            
            with gr.Tabs():
                with gr.TabItem("📝 文章格式化演示"):
                    gr.Markdown("## 自动生成演示文章")
                    gr.Markdown("点击按钮生成一篇格式化的微信公众号文章")
                    
                    with gr.Row():
                        generate_btn = gr.Button("生成演示文章", variant="primary", size="lg")
                    
                    with gr.Row():
                        article_title = gr.Textbox(label="文章标题", interactive=False)
                    
                    article_content = gr.Markdown(label="格式化后的文章内容", height=400)
                    
                    generate_btn.click(
                        fn=self.generate_demo_article,
                        outputs=[article_title, article_content]
                    )
                
                with gr.TabItem("🧹 内容筛选演示"):
                    gr.Markdown("## 内容筛选与去重")
                    gr.Markdown("演示智能体如何筛选和去重资讯内容")
                    
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
                    gr.Markdown("输入您自己的内容，体验格式化功能")
                    
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
            
            gr.Markdown("---")
            gr.Markdown("💡 **提示**: 这是一个简化版演示，展示了智能体的核心格式化功能。完整版本支持实时资讯获取和OpenAI API集成。")
        
        return app


def main():
    """主函数"""
    print("🚀 启动AI资讯智能体简化版Web界面...")
    
    # 创建简化界面
    simple_interface = SimpleWebInterface()
    app = simple_interface.create_interface()
    
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
