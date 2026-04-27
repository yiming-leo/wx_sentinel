"""
日志管理模块
统一管理控制台输出和文件日志
"""
import logging
import os
from datetime import datetime


def setup_logger(
        name: str = "wx_sentinel",
        log_dir: str = None,
        level: int = logging.INFO,
        console_output: bool = True
) -> logging.Logger:
    """
    配置并返回一个 logger 实例

    Args:
        name: 日志器名称
        log_dir: 日志文件存放目录，默认为脚本所在目录下的 log/
        level: 日志级别
        console_output: 是否同时输出到控制台

    Returns:
        logging.Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 文件 handler
    if log_dir is None:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "log")
    os.makedirs(log_dir, exist_ok=True)

    log_filename = f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    log_path = os.path.join(log_dir, log_filename)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 控制台 handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    logger.info(f"日志文件: {log_path}")
    return logger


def get_logger(name: str = "wx_sentinel") -> logging.Logger:
    """获取已配置的 logger，如果不存在则创建"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger