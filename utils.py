import asyncio
import logging
import os

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

async def human_delay(a: float = 0.8, b: float = 2.5) -> None:
    await asyncio.sleep(a)

async def save_debug(page, name: str) -> None:
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
