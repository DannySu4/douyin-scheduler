"""
抖音私信发送主程序（Playwright 异步版）
"""
import asyncio
import os
from playwright.async_api import async_playwright
from utils import get_logger, human_delay, parse_cookie, cookie_to_dict, save_debug

logger = get_logger()

async def send_message(page):
    """核心发送逻辑"""
    mode = os.getenv("MODE", "web")
    target = os.getenv("TARGET_USER", "")
    text = os.getenv("MESSAGE_TEXT", "")
    cookie = parse_cookie(os.getenv("DOUYIN_COOKIE", ""))

    if not cookie:
        logger.error("Cookie 为空，请检查 Secrets 配置！")
        return False

    # 注入 Cookie
    cookie_dict = cookie_to_dict(cookie)
    await page.context.add_cookies([
        {"name": k, "value": v, "domain": ".douyin.com", "path": "/"} 
        for k, v in cookie_dict.items()
    ])
    
    if mode == "web":
        logger.info("进入抖音网页版...")
        await page.goto("https://www.douyin.com/")
        await human_delay(2, 4)
        
        # TODO: 这里需要根据抖音网页版实际的 DOM 结构补充：
        # 1. 点击消息/私信图标
        # 2. 搜索 target 用户
        # 3. 找到输入框并输入 text
        # 4. 点击发送按钮
        logger.info(f"准备给 {target} 发送: {text}")
        # 示例：await page.fill('input[placeholder="输入私信内容"]', text)
        # 示例：await page.click('button:has-text("发送")')
        
        save_debug(page, "send_success")
        logger.info("✅ 发送流程执行完毕（请检查上方 TODO 是否已补充实际点击逻辑）")
        return True

async def main():
    ok = False
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        try:
            ok = await send_message(page)
        except Exception as e:
            logger.exception("发送失败: %s", e)
            save_debug(page, "error")
        finally:
            await context.close()
            await browser.close()
            
    return ok

if __name__ == "__main__":
    # 正确运行异步主函数并等待结果
    success = asyncio.run(main())
    raise SystemExit(0 if success else 1)
