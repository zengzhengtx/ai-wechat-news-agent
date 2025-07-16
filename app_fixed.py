#!/usr/bin/env python3
"""
AI资讯微信公众号智能体 - 修复版Web应用入口
修复了时区问题的版本

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


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="AI资讯微信公众号智能体")
    
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Web界面主机地址"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
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
    
    parser.add_argument(
        "--simple",
        action="store_true",
        help="使用简化版界面（避免API问题）"
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
    
    # 根据参数选择界面类型
    if args.simple:
        logger.info("使用简化版Web界面")
        try:
            from simple_web import SimpleWebInterface
            web_interface = SimpleWebInterface()
            app = web_interface.create_interface()
        except ImportError as e:
            logger.error(f"导入简化版界面失败: {e}")
            logger.info("尝试运行: python simple_web.py")
            return
    else:
        logger.info("尝试使用完整版Web界面")
        try:
            # 尝试导入完整版界面
            from src.web.interface import WebInterface
            web_interface = WebInterface(args.config)
            app = web_interface.create_interface()
        except Exception as e:
            logger.error(f"完整版界面初始化失败: {e}")
            logger.info("回退到简化版界面")
            try:
                from simple_web import SimpleWebInterface
                web_interface = SimpleWebInterface()
                app = web_interface.create_interface()
            except ImportError as e2:
                logger.error(f"简化版界面也无法加载: {e2}")
                print("\n❌ 无法启动Web界面")
                print("请尝试以下解决方案:")
                print("1. 运行简化版: python simple_web.py")
                print("2. 运行稳定版演示: python stable_demo.py")
                print("3. 检查依赖安装: pip install -r requirements.txt")
                return
    
    # 启动Web界面
    logger.info(f"启动Web界面: http://{args.host}:{args.port}")
    print(f"\n🌐 Web界面启动中...")
    print(f"📍 访问地址: http://{args.host}:{args.port}")
    
    try:
        app.launch(
            server_name=args.host,
            server_port=args.port,
            share=args.share,
            inbrowser=True
        )
    except Exception as e:
        logger.error(f"Web界面启动失败: {e}")
        print(f"\n❌ Web界面启动失败: {e}")
        print("\n🔧 故障排除建议:")
        print("1. 检查端口是否被占用")
        print("2. 尝试不同的端口: --port 8080")
        print("3. 使用简化版: --simple")
        print("4. 直接运行演示: python stable_demo.py")


if __name__ == "__main__":
    main()
