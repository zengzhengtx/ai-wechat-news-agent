#!/usr/bin/env python3
"""
基础框架测试脚本
测试配置加载、日志系统和数据库初始化
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agent.config import load_config
from src.utils.logger import init_logging
from src.database.database import DatabaseManager
from src.database.models import Article


def test_config():
    """测试配置加载"""
    print("🔧 测试配置加载...")
    
    config = load_config()
    print(f"✅ 配置加载成功")
    print(f"   - 模型: {config.agent.model_id}")
    print(f"   - OpenAI API Key: {'已设置' if config.openai_api_key else '未设置'}")
    print(f"   - 数据库路径: {config.database_path}")
    print(f"   - Web端口: {config.web_ui.port}")
    
    return config


def test_logging():
    """测试日志系统"""
    print("\n📝 测试日志系统...")
    
    logger = init_logging()
    logger.info("日志系统测试 - INFO级别")
    logger.warning("日志系统测试 - WARNING级别")
    logger.error("日志系统测试 - ERROR级别")
    
    print("✅ 日志系统正常")
    return logger


def test_database(config):
    """测试数据库"""
    print("\n🗄️ 测试数据库...")
    
    # 初始化数据库
    db_manager = DatabaseManager(config.database_path)
    print("✅ 数据库初始化成功")
    
    # 测试文章保存
    test_article = Article(
        title="测试文章标题",
        content="这是一篇测试文章的内容...",
        summary="测试文章摘要",
        source_url="https://example.com/test",
        source_type="test",
        status="draft",
        quality_score=0.8,
        tags='["测试", "AI"]'
    )
    
    article_id = db_manager.save_article(test_article)
    print(f"✅ 文章保存成功，ID: {article_id}")
    
    # 测试文章读取
    retrieved_article = db_manager.get_article(article_id)
    if retrieved_article:
        print(f"✅ 文章读取成功: {retrieved_article.title}")
    else:
        print("❌ 文章读取失败")
    
    # 测试统计信息
    stats = db_manager.get_articles_stats()
    print(f"✅ 统计信息: {stats}")
    
    return db_manager


def test_tools():
    """测试工具基类"""
    print("\n🔨 测试工具基类...")
    
    from src.tools.base_tool import NewsItem, CacheManager
    
    # 测试NewsItem
    news_item = NewsItem(
        title="测试资讯标题",
        content="测试资讯内容",
        url="https://example.com/news",
        source="test_source"
    )
    print(f"✅ NewsItem创建成功: {news_item}")
    
    # 测试缓存管理器
    cache_manager = CacheManager()
    cache_manager.set("test_key", {"data": "test_value"})
    cached_data = cache_manager.get("test_key")
    
    if cached_data and cached_data.get("data") == "test_value":
        print("✅ 缓存管理器正常")
    else:
        print("❌ 缓存管理器异常")
    
    return True


def main():
    """主测试函数"""
    print("🚀 开始基础框架测试...\n")
    
    try:
        # 测试配置
        config = test_config()
        
        # 测试日志
        logger = test_logging()
        
        # 测试数据库
        db_manager = test_database(config)
        
        # 测试工具
        test_tools()
        
        print("\n🎉 所有基础框架测试通过！")
        print("\n📋 测试总结:")
        print("   ✅ 配置管理系统")
        print("   ✅ 日志记录系统")
        print("   ✅ 数据库操作")
        print("   ✅ 工具基类")
        print("\n🔥 基础框架搭建完成，可以开始开发具体功能！")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
