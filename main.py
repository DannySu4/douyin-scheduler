"""
抖音私信发送主程序（Playwright 异步版）
"""
import asyncio
import os
import json
from playwright.async_api import async_playwright
from utils import get_logger, human_delay, save_debug

logger = get_logger()

async def send_message(page):
    """核心发送逻辑"""
    mode = os.getenv("MODE", "web")
    target = os.getenv("TARGET_USER", "")
    text = os.getenv("MESSAGE_TEXT", "")

    # 检查 auth_state.json 是否存在且合法
    if not os.path.exists("auth_state.json"):
        logger.error("auth_state.json 不存在，请先运行 inject_cookies.py！")
        return False
        
    try:
        with open("auth_state.json", "r") as f:
            state = json.load(f)
            if not state.get("cookies"):
                logger.error("auth_state.json 中没有有效的 Cookie 数据！")
                return False
    except Exception as e:
        logger.error(f"读取 auth_state.json 失败: {e}")
        return False

    logger.info("已加载登录状态，正在访问抖音网页版...")
    await page.goto("https://www.douyin.com/")
    await human_delay(2, 4)
    
    if mode == "web":
        logger.info(f"准备给 {target} 发送: {text}")
        # TODO: 这里需要补充真实的抖音网页版点击和发送逻辑（选择器）
        
        await save_debug(page, "send_success")
        logger.info("✅ 发送流程执行完毕（请补充真实的 DOM 操作逻辑）")
        return True

async def main():
    ok = False
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            # 尝试加载 storage_state
            context = await browser.new_context(storage_state="auth_state.json")
        except Exception as e:
            logger.exception(f"加载 auth_state.json 失败（Cookie格式仍有误）: {e}")
            # 兜底方案：创建空上下文（虽然没法登录，但防止流程直接崩溃）
            context = await browser.new_context()
            
        page = await context.new_page()
        try:
            ok = await send_message(page)
        except Exception as e:
            logger.exception("发送失败: %s", e)
            await save_debug(page, "error")
        finally:
            await context.close()
            await browser.close()
            
    return ok

if __name__ == "__main__":
    success = asyncio.run(main())
    raise SystemExit(0 if success else 1)
