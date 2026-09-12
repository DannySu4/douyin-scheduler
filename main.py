"""
抖音私信发送主程序（Playwright 异步版 - storage_state 稳定版）
"""
import asyncio
import os
from playwright.async_api import async_playwright
from utils import get_logger, human_delay, save_debug

logger = get_logger()

async def send_message(page):
    """核心发送逻辑"""
    mode = os.getenv("MODE", "web")
    target = os.getenv("TARGET_USER", "")
    text = os.getenv("MESSAGE_TEXT", "")

    if not os.path.exists("auth_state.json"):
        logger.error("auth_state.json 不存在，请先运行 inject_cookies.py！")
        return False

    logger.info("已加载登录状态，正在访问抖音网页版...")
    await page.goto("https://www.douyin.com/")
    await human_delay(2, 4)
    
    if mode == "web":
        logger.info(f"准备给 {target} 发送: {text}")
        # TODO: 这里需要补充真实的抖音网页版点击和发送逻辑（选择器）
        # 示例：await page.click("搜索框选择器")
        # 示例：await page.fill("输入框选择器", text)
        # 示例：await page.click("发送按钮选择器")
        
        await save_debug(page, "send_success")
        logger.info("✅ 发送流程执行完毕（请补充真实的 DOM 操作逻辑）")
        return True

async def main():
    ok = False
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 直接通过 storage_state 加载 Cookie，彻底避开 add_cookies 协议报错
        context = await browser.new_context(storage_state="auth_state.json")
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
