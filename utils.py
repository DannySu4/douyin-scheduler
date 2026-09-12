"""
工具函数：日志、延时、Cookie 解析。
"""
import json
import logging
import os
import random
import time
from typing import Optional


def get_logger(name: str = "douyin") -> logging.Logger:
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        fh = logging.FileHandler("logs/run.log", encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(sh)
        logger.addHandler(fh)
    return logger


def human_delay(a: float = 0.8, b: float = 2.5) -> None:
    time.sleep(random.uniform(a, b))


def parse_cookie(raw: str) -> str:
    return " ".join(line.strip() for line in raw.splitlines() if line.strip())


async def save_debug(page, name: str) -> None:
    """出错时截图 + dump 页面状态（修复协程等待问题）"""
    logger = get_logger()
    try:
        await page.screenshot(path=f"logs/{name}.png")
    except Exception as e:
        logger.warning("截图失败: %s", e)
    try:
        content = await page.content()
        with open(f"logs/{name}.html", "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        logger.warning("dump HTML 失败: %s", e)
