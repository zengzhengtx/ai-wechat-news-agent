#!/usr/bin/env python3
"""
AI资讯微信公众号智能体 - 简化演示
不依赖Web界面，直接在命令行中演示所有功能

Author: zengzhengtx
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


def print_header(title):
    """打印标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def print_section(title):
    """打印章节标题"""
    print(f"\n📋 {title}")
    print("-" * 40)


def create_demo_news_items():
    """创建演示资讯项"""
    print_section("创建演示资讯数据")
    
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
    
    print(f"✅ 成功创建 {len(news_items)} 条演示资讯")
    for i, item in enumerate(news_items, 1):
        print(f"   {i}. {item.title}")
        print(f"      来源: {item.source} | 分数: {item.score}")
    
    return news_items


def demo_content_filtering(news_items):
    """演示内容筛选功能"""
    print_section("内容筛选与去重演示")
    
    content_filter = ContentFilter()
    
    print(f"📊 原始资讯数量: {len(news_items)}")
    
    # 执行筛选
    filtered_items = content_filter.filter_and_dedupe(news_items)
    
    print(f"📊 筛选后数量: {len(filtered_items)}")
    print("\n筛选结果:")
    
    for i, item in enumerate(filtered_items, 1):
        print(f"   {i}. {item.title}")
        print(f"      质量分数: {item.score:.2f}")
        print(f"      来源: {item.source}")
    
    return filtered_items


def demo_wechat_formatting(news_items):
    """演示微信公众号格式化"""
    print_section("微信公众号格式化演示")
    
    formatter = WeChatFormatterTool()
    
    # 选择第一条资讯进行格式化
    selected_item = news_items[0]
    print(f"📝 正在格式化文章: {selected_item.title}")
    
    # 执行格式化
    formatted_content = formatter.format_content(
        content=selected_item.content,
        title=selected_item.title,
        include_images=True,
        include_source_links=True,
        add_emojis=True
    )
    
    print(f"✅ 格式化完成，内容长度: {len(formatted_content)} 字符")
    
    # 保存到文件
    output_path = "output/simple_demo_article.md"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(formatted_content)
    
    print(f"💾 格式化后的文章已保存到: {output_path}")
    
    # 显示前500字符预览
    print("\n📖 文章预览 (前500字符):")
    print("-" * 40)
    print(formatted_content[:500] + "...")
    print("-" * 40)
    
    return formatted_content


def demo_quality_control(original_items, formatted_items):
    """演示质量控制"""
    print_section("质量控制演示")
    
    quality_controller = QualityController()
    
    # 创建格式化后的NewsItem用于质量检查
    formatted_news_item = NewsItem(
        title=original_items[0].title,
        content=formatted_items,
        url=original_items[0].url,
        source=original_items[0].source,
        published_date=original_items[0].published_date,
        tags=original_items[0].tags + ["formatted"]
    )
    
    # 执行质量验证
    validation_result = quality_controller.validate_rewritten_content(
        original=original_items[0],
        rewritten=formatted_news_item
    )
    
    print(f"📊 质量评分: {validation_result['score']:.2f}")
    print(f"✅ 验证结果: {'通过' if validation_result['is_valid'] else '未通过'}")
    
    if validation_result['issues']:
        print("\n⚠️ 发现的问题:")
        for issue in validation_result['issues']:
            print(f"   • {issue}")
    
    if validation_result['suggestions']:
        print("\n💡 改进建议:")
        for suggestion in validation_result['suggestions']:
            print(f"   • {suggestion}")
    
    return validation_result


def demo_database_operations(news_items):
    """演示数据库操作"""
    print_section("数据库操作演示")
    
    config = load_config()
    db_manager = DatabaseManager(config.database_path)
    
    print(f"📂 数据库路径: {config.database_path}")
    
    # 保存文章到数据库
    saved_articles = []
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
        
        article_id = db_manager.save_article(article)
        article.id = article_id
        saved_articles.append(article)
        
        print(f"💾 已保存文章: ID={article_id}, 标题='{item.title[:30]}...'")
    
    # 获取统计信息
    stats = db_manager.get_articles_stats()
    print(f"\n📊 数据库统计信息:")
    print(f"   总文章数: {stats.get('total', 0)}")
    print(f"   草稿数量: {stats.get('status_draft', 0)}")
    print(f"   今日新增: {stats.get('today', 0)}")
    
    # 获取最近的文章
    recent_articles = db_manager.get_articles(limit=5)
    print(f"\n📚 最近的 {len(recent_articles)} 篇文章:")
    for article in recent_articles:
        print(f"   • {article.title[:50]}... (ID: {article.id})")
    
    return saved_articles


def main():
    """主演示函数"""
    print_header("🤖 AI资讯微信公众号智能体 - 完整功能演示")
    
    # 初始化日志
    logger = init_logging()
    logger.info("开始简化演示...")
    
    try:
        # 1. 创建演示数据
        news_items = create_demo_news_items()
        
        # 2. 演示内容筛选
        filtered_items = demo_content_filtering(news_items)
        
        # 3. 演示微信格式化
        formatted_content = demo_wechat_formatting(filtered_items)
        
        # 4. 演示质量控制
        quality_result = demo_quality_control(filtered_items, formatted_content)
        
        # 5. 演示数据库操作
        saved_articles = demo_database_operations(filtered_items)
        
        # 总结
        print_header("🎉 演示完成总结")
        print("✅ 所有功能演示成功完成！")
        print(f"📊 处理了 {len(news_items)} 条原始资讯")
        print(f"📊 筛选后剩余 {len(filtered_items)} 条")
        print(f"📊 质量评分: {quality_result['score']:.2f}")
        print(f"📊 保存了 {len(saved_articles)} 篇文章到数据库")
        print(f"📁 格式化文章已保存到: output/simple_demo_article.md")
        
        print("\n🚀 您可以查看以下文件:")
        print("   • output/simple_demo_article.md - 格式化后的文章")
        print("   • data/articles.db - 数据库文件")
        print("   • logs/app.log - 系统日志")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
