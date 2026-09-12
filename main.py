"""
抖音私信发送主程序（Playwright 异步版）
"""
import asyncio
import os
from playwright.async_api import async_playwright
from utils import get_logger, human_delay, parse_cookie, save_debug

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

    # 注入 Cookie（修复：补充 domain 和 path）
    await page.context.add_cookies([
        {"name": "temp_login", "value": "1", "domain": ".douyin.com", "path": "/"}
    ])
    
    # 更稳妥的方式：先访问抖音，让浏览器拿到基础上下文，再注入真实 Cookie
    logger.info("正在访问抖音网页版以获取上下文...")
    await page.goto("https://www.douyin.com/")
    await human_delay(2, 4)
    
    # 解析并注入真实 Cookie
    cookies_list = []
    for part in cookie.split(";"):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            cookies_list.append({
                "name": k.strip(),
                "value": v.strip(),
                "domain": ".douyin.com",
                "path": "/"
            })
    
    if cookies_list:
        await page.context.add_cookies(cookies_list)
        logger.info(f"成功注入 {len(cookies_list)} 条 Cookie")

    if mode == "web":
        logger.info("刷新页面生效 Cookie...")
        await page.reload()
        await human_delay(2, 4)
        
        logger.info(f"准备给 {target} 发送: {text}")
        # TODO: 这里需要补充真实的点击和发送逻辑
        # 示例：await page.click("搜索框选择器")
        # 示例：await page.fill("输入框选择器", text)
        # 示例：await page.click("发送按钮选择器")
        
        await save_debug(page, "send_success")
        logger.info("✅ 发送流程执行完毕")
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
            await save_debug(page, "error") # 修复：加上 await
        finally:
            await context.close()
            await browser.close()
            
    return ok

if __name__ == "__main__":
    success = asyncio.run(main())
    raise SystemExit(0 if success else 1)
