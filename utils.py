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
    """模拟人类操作间隔，避免机器级连续动作。"""
    time.sleep(random.uniform(a, b))


def parse_cookie(raw: str) -> str:
    """规范化 Cookie 字符串（去除换行/多余空格）。"""
    return " ".join(line.strip() for line in raw.splitlines() if line.strip())


def cookie_to_dict(raw: str) -> dict:
    """把 Cookie 字符串转成 dict，方便 playwright 注入。"""
    out = {}
    for part in raw.split(";"):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def save_debug(page, name: str) -> None:
    """出错时截图 + dump 页面状态，便于在 Artifact 里排查。"""
    logger = get_logger()
    try:
        page.screenshot(path=f"logs/{name}.png")
    except Exception as e:
        logger.warning("截图失败: %s", e)
    try:
        with open(f"logs/{name}.html", "w", encoding="utf-8") as f:
            f.write(page.content())
    except Exception as e:
        logger.warning("dump HTML 失败: %s", e)


def mask_cookie(cookie: str) -> str:
    """日志中脱敏 Cookie，只保留首尾。"""
    if len(cookie) <= 16:
        return "***"
    return cookie[:8] + "..." + cookie[-6:]
