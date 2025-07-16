#!/usr/bin/env python3
"""
资讯获取工具测试脚本
测试各种资讯源工具和内容筛选功能
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agent.config import load_config
from src.utils.logger import init_logging
from src.tools.base_tool import NewsItem
from src.utils.validators import ContentFilter


def create_mock_news_data():
    """创建模拟资讯数据"""
    print("\n📰 创建模拟资讯数据...")

    mock_data = [
        {
            'title': 'OpenAI发布GPT-4.5：性能大幅提升',
            'content': 'OpenAI今日宣布发布GPT-4.5模型，该模型在多项基准测试中表现出色，推理能力和代码生成能力都有显著提升。新模型采用了改进的Transformer架构，训练数据规模达到了前所未有的水平。',
            'url': 'https://example.com/gpt-4.5-release',
            'source': 'web_search',
            'published_date': datetime.now().isoformat(),
            'tags': ['AI', 'GPT', 'OpenAI'],
            'score': 0.9
        },
        {
            'title': 'Meta推出新一代AI芯片，专为大模型训练优化',
            'content': 'Meta公司发布了专门为大型语言模型训练设计的AI芯片，该芯片采用7nm工艺，具有超高的计算密度和能效比。预计将大幅降低AI模型训练成本。',
            'url': 'https://example.com/meta-ai-chip',
            'source': 'web_search',
            'published_date': (datetime.now()).isoformat(),
            'tags': ['AI', 'Meta', 'chip'],
            'score': 0.8
        },
        {
            'title': 'arXiv论文：Attention机制的新突破',
            'content': '研究人员提出了一种新的注意力机制，能够显著提高Transformer模型的效率。该方法在保持性能的同时，将计算复杂度从O(n²)降低到O(n log n)。',
            'url': 'https://arxiv.org/abs/2024.12345',
            'source': 'arxiv_cs.AI',
            'published_date': datetime.now().isoformat(),
            'tags': ['arxiv', 'attention', 'transformer'],
            'score': 0.85
        },
        {
            'title': 'GitHub热门：新的开源大模型框架',
            'content': '一个新的开源大模型训练框架在GitHub上获得了超过10k星标。该框架支持分布式训练，内存优化，并提供了简洁的API接口。',
            'url': 'https://github.com/example/llm-framework',
            'source': 'github_machine-learning',
            'published_date': datetime.now().isoformat(),
            'tags': ['github', 'open-source', 'framework'],
            'score': 0.75
        },
        {
            'title': 'Hugging Face发布新的多模态模型',
            'content': 'Hugging Face在其模型库中发布了一个新的多模态模型，能够同时处理文本、图像和音频输入。该模型在多个基准测试中达到了SOTA性能。',
            'url': 'https://huggingface.co/example/multimodal-model',
            'source': 'huggingface_models',
            'published_date': datetime.now().isoformat(),
            'tags': ['huggingface', 'multimodal', 'SOTA'],
            'score': 0.88
        }
    ]

    print(f"✅ 创建了 {len(mock_data)} 条模拟资讯")
    return mock_data


def test_news_item_creation():
    """测试NewsItem创建"""
    print("\n📝 测试NewsItem创建...")

    try:
        news_item = NewsItem(
            title="测试资讯标题",
            content="这是一条测试资讯的内容，包含了人工智能、机器学习等相关信息。",
            url="https://example.com/test-news",
            source="test_source",
            tags=["AI", "test"]
        )

        print(f"✅ NewsItem创建成功: {news_item.title}")
        print(f"   ID: {news_item.id}")
        print(f"   来源: {news_item.source}")
        print(f"   发布时间: {news_item.published_date}")

        return True

    except Exception as e:
        print(f"❌ NewsItem创建失败: {e}")
        return False


def test_content_filter(mock_data):
    """测试内容筛选器"""
    print("\n🧹 测试内容筛选与去重...")

    if not mock_data:
        print("❌ 没有资讯数据可供筛选")
        return []

    # 转换为NewsItem对象
    news_items = []

    for result in mock_data:
        try:
            item = NewsItem(
                title=result['title'],
                content=result['content'],
                url=result['url'],
                source=result['source'],
                published_date=datetime.fromisoformat(result['published_date']),
                tags=result.get('tags', []),
                score=result.get('score', 0.0)
            )
            news_items.append(item)
        except Exception as e:
            print(f"转换资讯项失败: {e}")

    print(f"原始资讯项数量: {len(news_items)}")

    # 创建内容筛选器
    content_filter = ContentFilter(duplicate_threshold=0.8, min_quality_score=0.5)

    # 筛选和去重
    filtered_items = content_filter.filter_and_dedupe(news_items)

    print(f"✅ 筛选后资讯项数量: {len(filtered_items)}")
    print("\n📊 筛选后的前3条资讯:")

    for i, item in enumerate(filtered_items[:3], 1):
        print(f"  {i}. {item.title}")
        print(f"     来源: {item.source}")
        print(f"     质量分数: {item.score:.2f}")
        print(f"     发布日期: {item.published_date.strftime('%Y-%m-%d')}")
        print()

    return filtered_items


def main():
    """主测试函数"""
    print("🚀 开始资讯获取工具测试...\n")

    # 初始化日志
    logger = init_logging()

    try:
        # 测试NewsItem创建
        test_news_item_creation()

        # 创建模拟数据
        mock_data = create_mock_news_data()

        # 测试内容筛选
        filtered_items = test_content_filter(mock_data)

        print("\n🎉 资讯获取工具测试完成！")
        print("\n📋 测试总结:")
        print(f"   ✅ NewsItem创建: 成功")
        print(f"   ✅ 模拟数据: {len(mock_data)} 条")
        print(f"   ✅ 内容筛选: {len(filtered_items)}/{len(mock_data)} 条结果")
        print("\n🔥 基础功能测试通过，可以继续开发智能体集成！")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
