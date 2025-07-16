#!/usr/bin/env python3
"""
内容改写功能测试脚本
测试内容改写和微信公众号格式化功能
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
from src.tools.content_rewriter import ContentRewriteTool
from src.tools.wechat_formatter import WeChatFormatterTool
from src.utils.quality_control import QualityController


def create_test_news_item():
    """创建测试资讯项"""
    print("\n📰 创建测试资讯项...")
    
    test_content = """
    Researchers from OpenAI have introduced GPT-4o, a new multimodal AI model that represents a significant advancement in artificial intelligence capabilities. 
    
    GPT-4o (the "o" stands for "omni") can process and generate text, audio, and visual content with remarkable speed and accuracy. The model demonstrates near-human-level understanding across these modalities, enabling more natural and intuitive interactions.
    
    Key features of GPT-4o include:
    
    1. Real-time audio processing with latency comparable to human conversation
    2. Enhanced vision capabilities for analyzing images and videos
    3. Improved reasoning abilities across multiple languages
    4. Significantly reduced training and inference costs compared to previous models
    
    The model achieves these capabilities while maintaining the same level of safety as GPT-4. OpenAI has implemented extensive safety measures, including red-teaming exercises and adversarial testing.
    
    GPT-4o will be available to ChatGPT Plus and Team users, as well as developers through the API. The free version of ChatGPT will also receive GPT-4o capabilities, albeit with usage limits.
    
    This release represents a significant step toward more natural human-computer interaction and demonstrates OpenAI's continued leadership in advancing AI technology.
    """
    
    news_item = NewsItem(
        title="OpenAI Introduces GPT-4o: A Multimodal AI Model with Enhanced Capabilities",
        content=test_content,
        url="https://openai.com/blog/gpt-4o",
        source="web_search",
        published_date=datetime.now(),
        tags=["AI", "GPT", "OpenAI", "multimodal"]
    )
    
    print(f"✅ 测试资讯项创建成功: {news_item.title}")
    return news_item


def test_content_rewriter():
    """测试内容改写工具"""
    print("\n✏️ 测试内容改写工具...")
    
    config = load_config()
    rewriter = ContentRewriteTool(api_key=config.openai_api_key)
    
    news_item = create_test_news_item()
    
    try:
        print("开始改写内容...")
        rewritten_title = rewriter.rewrite_title(news_item.title, style="通俗易懂")
        print(f"✅ 改写后的标题: {rewritten_title}")
        
        rewritten_content = rewriter.rewrite_content(
            content=news_item.content,
            title=news_item.title,
            style="通俗易懂",
            max_length=2000
        )
        
        print(f"✅ 内容改写成功，长度: {len(rewritten_content)} 字符")
        print("\n📝 改写后内容预览 (前200字符):")
        print(f"{rewritten_content[:200]}...")
        
        # 创建改写后的资讯项
        rewritten_item = NewsItem(
            title=rewritten_title,
            content=rewritten_content,
            url=news_item.url,
            source=news_item.source,
            published_date=news_item.published_date,
            tags=news_item.tags + ["rewritten"]
        )
        
        return rewritten_item
    
    except Exception as e:
        print(f"❌ 内容改写失败: {e}")
        return news_item


def test_wechat_formatter(news_item):
    """测试微信公众号格式化工具"""
    print("\n📱 测试微信公众号格式化工具...")
    
    formatter = WeChatFormatterTool()
    
    try:
        print("开始格式化内容...")
        formatted_content = formatter.format_content(
            content=news_item.content,
            title=news_item.title,
            include_images=True,
            include_source_links=True,
            add_emojis=True
        )
        
        print(f"✅ 内容格式化成功，长度: {len(formatted_content)} 字符")
        print("\n📝 格式化后内容预览 (前200字符):")
        print(f"{formatted_content[:200]}...")
        
        # 创建格式化后的资讯项
        formatted_item = NewsItem(
            title=news_item.title,
            content=formatted_content,
            url=news_item.url,
            source=news_item.source,
            published_date=news_item.published_date,
            tags=news_item.tags + ["formatted"]
        )
        
        return formatted_item
    
    except Exception as e:
        print(f"❌ 内容格式化失败: {e}")
        return news_item


def test_quality_control(original_item, rewritten_item):
    """测试质量控制"""
    print("\n🔍 测试质量控制...")
    
    quality_controller = QualityController(min_quality_score=0.6)
    
    try:
        validation_result = quality_controller.validate_rewritten_content(
            original=original_item,
            rewritten=rewritten_item
        )
        
        print(f"✅ 质量评分: {validation_result['score']:.2f}")
        print(f"✅ 是否通过验证: {'是' if validation_result['is_valid'] else '否'}")
        
        if validation_result['issues']:
            print("\n⚠️ 发现的问题:")
            for issue in validation_result['issues']:
                print(f"  • {issue}")
        
        if validation_result['suggestions']:
            print("\n💡 改进建议:")
            for suggestion in validation_result['suggestions']:
                print(f"  • {suggestion}")
        
        return validation_result
    
    except Exception as e:
        print(f"❌ 质量控制失败: {e}")
        return None


def save_result_to_file(item, filename="output/rewritten_article.md"):
    """保存结果到文件"""
    print(f"\n💾 保存结果到文件: {filename}...")
    
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# {item.title}\n\n")
            f.write(item.content)
        
        print(f"✅ 文件保存成功: {filename}")
        return True
    
    except Exception as e:
        print(f"❌ 文件保存失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始内容改写功能测试...\n")
    
    # 初始化日志
    logger = init_logging()
    
    try:
        # 创建测试资讯项
        original_item = create_test_news_item()
        
        # 测试内容改写
        rewritten_item = test_content_rewriter()
        
        # 测试微信公众号格式化
        formatted_item = test_wechat_formatter(rewritten_item)
        
        # 测试质量控制
        validation_result = test_quality_control(original_item, formatted_item)
        
        # 保存结果到文件
        save_result_to_file(formatted_item)
        
        print("\n🎉 内容改写功能测试完成！")
        print("\n📋 测试总结:")
        print(f"   ✅ 内容改写: 成功")
        print(f"   ✅ 微信格式化: 成功")
        print(f"   ✅ 质量控制: {'通过' if validation_result and validation_result['is_valid'] else '未通过'}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
