#!/usr/bin/env python3
"""
抖音网页版私信发送（Playwright 无头浏览器模式）
支持 Cookie-Editor 导出的 JSON 数组格式 或 传统字符串格式。
"""

import asyncio
import os
import sys
from pathlib import Path

from playwright.async_api import async_playwright

from config import config as cfg  # 避免与参数名冲突

# ---------- 常量 ----------
LOGIN_URL = "https://www.douyin.com/"
MESSAGE_URL_TEMPLATE = "https://www.douyin.com/messages/{user}"
DEBUG_DIR = Path("debug-logs")

# ---------- 选择器（抖音网页版可能变化，需自行调整）----------
SELECTORS = {
    "chat_item": ".chat-list-item",
    "message_input": ".public-DraftEditor-content",
    "send_button": "button[class*='send']",
}


async def send_message(config_obj=None) -> bool:
    """
    发送私信的主函数。
    参数 config_obj：Config 实例，若不传则使用全局 config。
    返回 True 表示成功，False 表示失败。
    """
    if config_obj is None:
        from config import config as config_obj

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        try:
            # 1. 访问首页
            await page.goto(LOGIN_URL, wait_until="domcontentloaded")
            await asyncio.sleep(2)

            # 2. 注入 Cookie（自动识别格式）
            cookies = config_obj.get_cookies_list()
            await context.add_cookies(cookies)

            # 3. 刷新使 Cookie 生效
            await page.reload(wait_until="networkidle")
            await asyncio.sleep(3)

            # 4. 检查登录状态
            await page.wait_for_selector(SELECTORS["chat_item"], timeout=10000)
            print("[✓] 登录成功，检测到会话列表")

            # 5. 导航到目标用户私信页
            target_url = MESSAGE_URL_TEMPLATE.format(user=config_obj.target_user)
            await page.goto(target_url, wait_until="domcontentloaded")
            await asyncio.sleep(3)

            # 6. 等待输入框
            input_box = await page.wait_for_selector(
                SELECTORS["message_input"], timeout=15000
            )

            # 7. 输入消息
            await input_box.click()
            await input_box.fill(config_obj.message_text)
            await asyncio.sleep(1)

            # 8. 发送
            try:
                send_btn = await page.wait_for_selector(
                    SELECTORS["send_button"], timeout=5000
                )
                await send_btn.click()
            except Exception:
                await page.keyboard.press("Enter")
                await asyncio.sleep(1)

            await asyncio.sleep(3)
            print(f"[✓] 消息已发送至 {config_obj.target_user}: {config_obj.message_text}")
            return True

        except Exception as e:
            DEBUG_DIR.mkdir(exist_ok=True)
            await page.screenshot(path=str(DEBUG_DIR / "error.png"))
            print(f"[✗] 发送失败: {e}")
            return False

        finally:
            await browser.close()


def main():
    from config import config
    config.validate()
    print(f"[*] 使用 Cookie: {config.masked_cookie}")
    print(f"[*] 目标用户: {config.target_user}")
    print(f"[*] 消息内容: {config.message_text}")

    success = asyncio.run(send_message(config))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
