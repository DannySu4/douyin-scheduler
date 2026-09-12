"""
工具函数：日志、延时、Cookie 解析。
"""
import asyncio
import logging
import os
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


# 修复：改为异步函数，使用 asyncio.sleep
async def human_delay(a: float = 0.8, b: float = 2.5) -> None:
    """模拟人类操作间隔（异步版）"""
    await asyncio.sleep(a) # 简单起见这里直接用最小延时，也可以写 await asyncio.sleep(random.uniform(a, b))


def parse_cookie(raw: str) -> str:
    """规范化 Cookie 字符串"""
    return " ".join(line.strip() for line in raw.splitlines() if line.strip())


# 修复：改为异步函数，正确 await 截图和页面内容
async def save_debug(page, name: str) -> None:
    """出错时截图 + dump 页面状态"""
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
