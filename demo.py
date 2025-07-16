#!/usr/bin/env python3
"""
AI资讯微信公众号智能体 - 演示脚本
提供简单的演示功能，无需完整的API调用

Author: zengzhengtx
"""

import os
import sys
import argparse
from datetime import datetime
import time
import json

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


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="AI资讯微信公众号智能体演示")
    
    parser.add_argument(
        "--mode",
        type=str,
        choices=["format", "filter", "save", "web"],
        default="format",
        help="演示模式: format=格式化示例文章, filter=内容筛选, save=保存到数据库, web=启动Web界面"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="output/demo_article.md",
        help="输出文件路径"
    )
    
    return parser.parse_args()


def create_demo_news_items():
    """创建演示资讯项"""
    print("\n📰 创建演示资讯项...")
    
    news_items = [
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
            
            传统的RLHF（基于人类反馈的强化学习）方法在提升模型安全性方面取得了显著成效，但仍存在一些局限性，如过度优化单一目标、难以平衡多种价值观等问题。
            
            新提出的多层次RLHF方法引入了价值观层次结构，允许模型在不同情境下灵活应用不同的价值观权重，从而实现更加细致的对齐调整。
            
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
    
    print(f"✅ 创建了 {len(news_items)} 条演示资讯")
    return news_items


def demo_format_article():
    """演示文章格式化"""
    print("\n📝 演示文章格式化...")
    
    # 创建演示资讯项
    news_items = create_demo_news_items()
    
    # 选择第一条资讯
    news_item = news_items[0]
    
    # 创建格式化工具
    formatter = WeChatFormatterTool()
    
    # 格式化内容
    print("开始格式化内容...")
    formatted_content = formatter.format_content(
        content=news_item.content,
        title=news_item.title,
        include_images=True,
        include_source_links=True,
        add_emojis=True
    )
    
    print(f"✅ 内容格式化成功，长度: {len(formatted_content)} 字符")
    
    # 保存到文件
    output_path = "output/demo_article.md"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(formatted_content)
    
    print(f"✅ 格式化后的文章已保存到: {output_path}")
    
    return formatted_content


def demo_filter_content():
    """演示内容筛选"""
    print("\n🧹 演示内容筛选...")
    
    # 创建演示资讯项
    news_items = create_demo_news_items()
    
    # 创建内容筛选器
    content_filter = ContentFilter()
    
    # 筛选内容
    print("开始筛选内容...")
    filtered_items = content_filter.filter_and_dedupe(news_items)
    
    print(f"✅ 内容筛选成功，原始数量: {len(news_items)}，筛选后数量: {len(filtered_items)}")
    
    # 显示筛选结果
    print("\n📊 筛选结果:")
    for i, item in enumerate(filtered_items, 1):
        print(f"  {i}. {item.title}")
        print(f"     来源: {item.source}")
        print(f"     质量分数: {item.score:.2f}")
        print()
    
    return filtered_items


def demo_save_to_database():
    """演示保存到数据库"""
    print("\n💾 演示保存到数据库...")
    
    # 创建演示资讯项
    news_items = create_demo_news_items()
    
    # 创建数据库管理器
    config = load_config()
    db_manager = DatabaseManager(config.database_path)
    
    # 保存到数据库
    print("开始保存到数据库...")
    articles = []
    
    for item in news_items:
        # 创建文章对象
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
        
        # 保存到数据库
        article_id = db_manager.save_article(article)
        article.id = article_id
        articles.append(article)
        
        print(f"✅ 文章已保存: ID={article_id}, 标题='{item.title[:30]}...'")
    
    # 获取文章统计信息
    stats = db_manager.get_articles_stats()
    print(f"\n📊 数据库统计信息:")
    print(f"  总文章数: {stats.get('total', 0)}")
    print(f"  草稿数量: {stats.get('status_draft', 0)}")
    print(f"  今日新增: {stats.get('today', 0)}")
    
    return articles


def demo_web_interface():
    """演示Web界面"""
    print("\n🌐 启动Web界面...")
    
    try:
        from app import main as web_main
        web_main()
        return True
    except Exception as e:
        print(f"❌ 启动Web界面失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 开始AI资讯智能体演示...\n")
    
    # 解析命令行参数
    args = parse_args()
    
    # 初始化日志
    logger = init_logging()
    
    try:
        # 根据模式执行不同的演示
        if args.mode == "format":
            demo_format_article()
        elif args.mode == "filter":
            demo_filter_content()
        elif args.mode == "save":
            demo_save_to_database()
        elif args.mode == "web":
            demo_web_interface()
        
        print("\n🎉 演示完成！")
        return True
        
    except Exception as e:
        print(f"\n❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
