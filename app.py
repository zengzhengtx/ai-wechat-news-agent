#!/usr/bin/env python3
"""
AI资讯微信公众号智能体 - Web应用入口
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
from src.web.interface import WebInterface


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="AI资讯微信公众号智能体")
    
    parser.add_argument(
        "--host",
        type=str,
        default=None,
        help="Web界面主机地址"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Web界面端口"
    )
    
    parser.add_argument(
        "--share",
        action="store_true",
        help="是否共享Web界面"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="配置文件路径"
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
    
    # 创建Web界面
    web_interface = WebInterface(args.config)
    app = web_interface.create_interface()
    
    # 确定主机和端口
    host = args.host or config.web_ui.host
    port = args.port or config.web_ui.port
    share = args.share or config.web_ui.share
    
    # 启动Web界面
    logger.info(f"启动Web界面: http://{host}:{port}")
    app.launch(
        server_name=host,
        server_port=port,
        share=share,
        inbrowser=True
    )


if __name__ == "__main__":
    main()
