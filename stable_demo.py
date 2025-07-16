#!/usr/bin/env python3
"""
AI资讯微信公众号智能体 - 稳定版演示
避免API限制问题，专注于核心功能演示
"""

import os
import sys
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agent.config import load_config
from src.utils.logger import init_logging
from src.tools.base_tool import NewsItem
from src.tools.wechat_formatter import WeChatFormatterTool
from src.utils.validators import ContentFilter
from src.utils.quality_control import QualityController
from src.database.database import DatabaseManager
from src.database.models import Article
from src.utils.datetime_utils import get_utc_now


def print_header(title):
    """打印标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def print_section(title):
    """打印章节标题"""
    print(f"\n📋 {title}")
    print("-" * 40)


def create_realistic_news_items():
    """创建真实的AI资讯项"""
    print_section("创建真实AI资讯数据")
    
    news_items = [
        NewsItem(
            title="OpenAI发布GPT-4 Turbo：更快、更便宜、更强大",
            content="""
            OpenAI在其首届开发者大会上发布了GPT-4 Turbo，这是GPT-4的升级版本，具有多项重大改进。
            
            主要特性包括：
            
            **更大的上下文窗口**
            GPT-4 Turbo支持高达128,000个token的上下文长度，相当于约300页的文本，这使得模型能够处理更长的文档和对话。
            
            **更新的知识截止时间**
            模型的训练数据更新至2024年4月，相比之前版本有了显著的知识更新。
            
            **更好的指令遵循能力**
            GPT-4 Turbo在遵循复杂指令方面表现更佳，特别是在JSON模式和函数调用方面。
            
            **显著降低的成本**
            输入token的价格降低了3倍，输出token的价格降低了2倍，使得大规模应用更加经济实惠。
            
            **多模态能力增强**
            新版本在图像理解、文本生成和代码编写方面都有显著提升。
            
            开发者可以通过OpenAI API立即开始使用GPT-4 Turbo，无需等待列表。
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
            与其他模型不同，Gemini从一开始就被设计为多模态模型，能够无缝理解和生成文本、图像、音频和视频内容。
            
            **卓越的性能表现**
            在MMLU（大规模多任务语言理解）基准测试中，Gemini Ultra获得了90.0%的分数，首次超越人类专家水平。
            
            **代码理解能力**
            在HumanEval代码生成基准测试中，Gemini Ultra达到了74.4%的准确率。
            
            **安全性和责任**
            Google强调了Gemini在安全性方面的设计，包括广泛的安全评估和负责任的部署策略。
            
            Gemini Pro已经在Google Bard中上线，Gemini Ultra将在明年初发布。
            """,
            url="https://blog.google/technology/ai/google-gemini-ai/",
            source="web_search",
            published_date=get_utc_now(),
            tags=['Google', 'Gemini', 'multimodal', 'AI'],
            score=0.92
        ),
        NewsItem(
            title="Anthropic推出Claude 2.1：200K上下文窗口的突破",
            content="""
            Anthropic发布了Claude 2.1，这是其AI助手Claude的最新版本，带来了令人印象深刻的改进。
            
            **史无前例的上下文长度**
            Claude 2.1支持200,000个token的上下文窗口，这意味着它可以处理约150,000个单词或500页的内容。
            
            **显著降低的幻觉率**
            新版本在准确性方面有了重大提升，幻觉率比Claude 2.0降低了2倍。
            
            **改进的工具使用能力**
            Claude 2.1在使用工具和API方面表现更佳，错误率降低了30%。
            
            **更好的文档理解**
            模型在处理长文档、法律合同、财务报告等复杂材料时表现出色。
            
            **API访问**
            开发者现在可以通过Anthropic的API访问Claude 2.1，定价为每百万输入token 8美元，输出token 24美元。
            
            **安全性增强**
            Anthropic继续其在AI安全方面的承诺，Claude 2.1经过了更严格的安全测试。
            
            这一发布标志着长上下文AI模型的新时代，为处理复杂、长篇内容开辟了新的可能性。
            """,
            url="https://www.anthropic.com/index/claude-2-1",
            source="web_search",
            published_date=get_utc_now(),
            tags=['Anthropic', 'Claude', 'context-window', 'AI'],
            score=0.88
        ),
        NewsItem(
            title="Meta开源Code Llama：专为代码生成优化的大模型",
            content="""
            Meta发布了Code Llama，这是基于Llama 2的代码专用大型语言模型，专门为代码生成和理解任务进行了优化。
            
            **三种模型规模**
            - Code Llama 7B：适合实时代码补全
            - Code Llama 13B：平衡性能和资源使用
            - Code Llama 34B：最高质量的代码生成
            
            **专业化版本**
            - Code Llama - Python：专门针对Python优化
            - Code Llama - Instruct：针对指令遵循优化
            
            **卓越的代码能力**
            在HumanEval基准测试中，Code Llama 34B达到了53.7%的准确率，显著超越了其他开源模型。
            
            **多语言支持**
            支持Python、C++、Java、PHP、TypeScript、C#、Bash等多种编程语言。
            
            **商业友好许可**
            Code Llama采用与Llama 2相同的许可证，允许商业使用。
            
            **长上下文支持**
            支持最多100,000个token的上下文，能够处理大型代码库。
            
            **开源承诺**
            Meta继续其开源AI的承诺，Code Llama的权重和代码完全开放。
            
            这一发布为开发者社区提供了强大的代码生成工具，有望加速软件开发的自动化进程。
            """,
            url="https://ai.meta.com/blog/code-llama-large-language-model-coding/",
            source="web_search",
            published_date=get_utc_now(),
            tags=['Meta', 'Code-Llama', 'open-source', 'coding'],
            score=0.85
        ),
        NewsItem(
            title="Stability AI发布SDXL Turbo：实时图像生成的新突破",
            content="""
            Stability AI发布了SDXL Turbo，这是一个革命性的文本到图像生成模型，能够在单步推理中生成高质量图像。
            
            **实时生成能力**
            SDXL Turbo可以在不到一秒的时间内生成512x512像素的高质量图像，这是图像生成领域的重大突破。
            
            **Adversarial Diffusion Distillation (ADD)**
            采用了新的训练技术ADD，将多步扩散过程压缩为单步生成，同时保持图像质量。
            
            **卓越的图像质量**
            尽管生成速度极快，SDXL Turbo生成的图像质量仍然保持在很高水平，细节丰富，色彩鲜艳。
            
            **广泛的应用场景**
            - 实时创意工具
            - 游戏和娱乐
            - 快速原型设计
            - 教育和培训
            
            **技术创新**
            SDXL Turbo代表了扩散模型优化的新方向，为实时AI图像生成开辟了道路。
            
            **开放访问**
            模型权重已在Hugging Face上发布，研究人员和开发者可以免费使用。
            
            **未来展望**
            Stability AI表示这只是实时AI生成的开始，未来将推出更多优化版本。
            
            这一发布标志着AI图像生成从"慢而精"向"快而精"的重要转变。
            """,
            url="https://stability.ai/news/sdxl-turbo",
            source="web_search",
            published_date=get_utc_now(),
            tags=['Stability-AI', 'SDXL-Turbo', 'image-generation', 'real-time'],
            score=0.82
        )
    ]
    
    print(f"✅ 创建了 {len(news_items)} 条真实AI资讯")
    for i, item in enumerate(news_items, 1):
        print(f"   {i}. {item.title}")
        print(f"      来源: {item.source} | 分数: {item.score}")
    
    return news_items


def demo_complete_workflow():
    """演示完整的工作流程"""
    print_header("🤖 AI资讯微信公众号智能体 - 完整工作流程演示")
    
    # 初始化日志
    logger = init_logging()
    logger.info("开始完整工作流程演示...")
    
    try:
        # 1. 创建真实资讯数据
        news_items = create_realistic_news_items()
        
        # 2. 内容筛选与去重
        print_section("内容筛选与去重")
        content_filter = ContentFilter()
        filtered_items = content_filter.filter_and_dedupe(news_items)
        print(f"📊 筛选结果: {len(news_items)} → {len(filtered_items)} 条")
        
        # 3. 选择最佳文章进行格式化
        print_section("微信公众号格式化")
        formatter = WeChatFormatterTool()
        selected_item = filtered_items[0]  # 选择第一条
        
        print(f"📝 正在格式化: {selected_item.title}")
        formatted_content = formatter.format_content(
            content=selected_item.content,
            title=selected_item.title,
            include_images=True,
            include_source_links=True,
            add_emojis=True
        )
        
        # 4. 质量控制
        print_section("质量控制")
        quality_controller = QualityController()
        
        formatted_item = NewsItem(
            title=selected_item.title,
            content=formatted_content,
            url=selected_item.url,
            source=selected_item.source,
            published_date=selected_item.published_date,
            tags=selected_item.tags + ["formatted"]
        )
        
        validation_result = quality_controller.validate_rewritten_content(
            original=selected_item,
            rewritten=formatted_item
        )
        
        print(f"📊 质量评分: {validation_result['score']:.2f}")
        print(f"✅ 验证结果: {'通过' if validation_result['is_valid'] else '未通过'}")
        
        # 5. 保存到数据库
        print_section("保存到数据库")
        config = load_config()
        db_manager = DatabaseManager(config.database_path)
        
        article = Article(
            title=formatted_item.title,
            content=formatted_item.content,
            summary=formatted_item.content[:200] + "...",
            source_url=formatted_item.url,
            source_type=formatted_item.source,
            status='draft',
            quality_score=validation_result['score'],
            tags=json.dumps(formatted_item.tags, ensure_ascii=False)
        )
        
        article_id = db_manager.save_article(article)
        print(f"💾 文章已保存到数据库，ID: {article_id}")
        
        # 6. 保存到文件
        print_section("导出文章")
        output_path = "output/stable_demo_article.md"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(formatted_content)
        
        print(f"📁 文章已导出到: {output_path}")
        
        # 7. 显示统计信息
        print_section("统计信息")
        stats = db_manager.get_articles_stats()
        print(f"📊 数据库统计:")
        print(f"   总文章数: {stats.get('total', 0)}")
        print(f"   草稿数量: {stats.get('status_draft', 0)}")
        print(f"   今日新增: {stats.get('today', 0)}")
        
        # 8. 显示文章预览
        print_section("文章预览")
        print("📖 格式化后的文章预览 (前800字符):")
        print("-" * 60)
        print(formatted_content[:800] + "...")
        print("-" * 60)
        
        # 总结
        print_header("🎉 演示完成总结")
        print("✅ 完整工作流程演示成功！")
        print(f"📊 处理了 {len(news_items)} 条原始资讯")
        print(f"📊 筛选后剩余 {len(filtered_items)} 条")
        print(f"📊 质量评分: {validation_result['score']:.2f}")
        print(f"📊 文章ID: {article_id}")
        print(f"📁 输出文件: {output_path}")
        
        print("\n🚀 您可以查看以下文件:")
        print(f"   • {output_path} - 格式化后的文章")
        print(f"   • {config.database_path} - 数据库文件")
        print("   • logs/app.log - 系统日志")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = demo_complete_workflow()
    sys.exit(0 if success else 1)
