"""
日志工具模块
提供统一的日志记录功能
"""

import os
import logging
import sys
from datetime import datetime
from typing import Optional
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    # 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
        'RESET': '\033[0m'      # 重置
    }
    
    def format(self, record):
        # 添加颜色
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


def setup_logger(
    name: str = "wechat_agent",
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    console_output: bool = True
) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        log_level: 日志级别
        log_file: 日志文件路径
        console_output: 是否输出到控制台
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 设置日志级别
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    colored_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(colored_formatter)
        logger.addHandler(console_handler)
    
    # 文件处理器
    if log_file:
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "wechat_agent") -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 日志记录器
    """
    return logging.getLogger(name)


class LogCapture:
    """日志捕获器，用于在Web界面中显示日志"""
    
    def __init__(self, max_lines: int = 1000):
        self.max_lines = max_lines
        self.logs = []
        self.handler = None
    
    def start_capture(self, logger_name: str = "wechat_agent"):
        """开始捕获日志"""
        logger = logging.getLogger(logger_name)
        
        # 创建自定义处理器
        self.handler = LogCaptureHandler(self)
        self.handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        self.handler.setFormatter(formatter)
        
        logger.addHandler(self.handler)
    
    def stop_capture(self, logger_name: str = "wechat_agent"):
        """停止捕获日志"""
        if self.handler:
            logger = logging.getLogger(logger_name)
            logger.removeHandler(self.handler)
            self.handler = None
    
    def add_log(self, message: str):
        """添加日志消息"""
        self.logs.append(f"{datetime.now().strftime('%H:%M:%S')} - {message}")
        
        # 保持最大行数限制
        if len(self.logs) > self.max_lines:
            self.logs = self.logs[-self.max_lines:]
    
    def get_logs(self) -> str:
        """获取所有日志"""
        return "\n".join(self.logs)
    
    def clear_logs(self):
        """清空日志"""
        self.logs.clear()


class LogCaptureHandler(logging.Handler):
    """日志捕获处理器"""
    
    def __init__(self, capture: LogCapture):
        super().__init__()
        self.capture = capture
    
    def emit(self, record):
        """发送日志记录"""
        try:
            message = self.format(record)
            self.capture.add_log(message)
        except Exception:
            self.handleError(record)


# 全局日志捕获器
log_capture = LogCapture()


def init_logging(config=None):
    """
    初始化日志系统
    
    Args:
        config: 配置对象
    """
    if config:
        log_level = config.log_level
        log_file = config.log_file
    else:
        log_level = os.getenv("LOG_LEVEL", "INFO")
        log_file = os.getenv("LOG_FILE", "logs/app.log")
    
    # 设置主日志记录器
    logger = setup_logger(
        name="wechat_agent",
        log_level=log_level,
        log_file=log_file,
        console_output=True
    )
    
    # 启动日志捕获
    log_capture.start_capture()
    
    logger.info("日志系统初始化完成")
    return logger
