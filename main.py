#!/usr/bin/env python3
"""
AI资讯微信公众号智能体 - 命令行入口

Author: zengzhengtx
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agent.config import load_config
from src.utils.logger import init_logging
from src.agent.ai_news_agent import AINewsAgent


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="AI资讯微信公众号智能体")
    
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="配置文件路径"
    )
    
    parser.add_argument(
        "--max-articles",
        type=int,
        default=None,
        help="最大文章数量"
    )
    
    parser.add_argument(
        "--web",
        action="store_true",
        help="启动Web界面"
    )
    
    return parser.parse_args()


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_args()
    
    # 初始化日志
    logger = init_logging()
    logger.info("启动AI资讯微信公众号智能体...")
    
    # 加载配置
    config = load_config(args.config)
    
    # 如果指定了最大文章数，覆盖配置
    if args.max_articles is not None:
        config.agent.max_articles_per_run = args.max_articles
    
    # 如果指定了启动Web界面，则启动Web界面
    if args.web:
        from app import main as web_main
        web_main()
        return
    
    # 创建智能体
    agent = AINewsAgent(args.config)
    
    # 运行智能体
    logger.info("开始运行智能体...")
    articles = agent.run_news_collection()
    
    # 输出结果
    logger.info(f"智能体运行完成，生成了 {len(articles)} 篇文章")
    for i, article in enumerate(articles, 1):
        logger.info(f"{i}. {article.title}")
    
    logger.info("完成")


if __name__ == "__main__":
    main()
