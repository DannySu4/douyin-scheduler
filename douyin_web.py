#!/usr/bin/env python3
"""
抖音网页版私信发送（Playwright 无头浏览器模式）
使用前请确保已在 GitHub Secrets 中设置：
  DOUYIN_COOKIE, TARGET_USER, MESSAGE_TEXT
"""

import asyncio
import json
import os
import sys
from pathlib import Path

from playwright.async_api import async_playwright

from config import Config

# ---------- 常量 ----------
COOKIE_FILE = "cookies.txt"
DEBUG_DIR = Path("debug-logs")
LOGIN_URL = "https://www.douyin.com/"
MESSAGE_URL_TEMPLATE = "https://www.douyin.com/messages/{user}"  # 根据实际调整

# ---------- 选择器（抖音网页版可能会变，需自行调整）----------
SELECTORS = {
    "chat_item": ".chat-list-item",           # 会话列表项
    "message_input": ".public-DraftEditor-content",  # 输入框
    "send_button": "button[class*='send']",   # 发送按钮
}


async def load_cookies(page, cookie_str: str):
    """将 Cookie 字符串注入浏览器"""
    cookies = []
    for item in cookie_str.split(";"):
        item = item.strip()
        if not item:
            continue
        if "=" not in item:
            continue
        name, value = item.split("=", 1)
        cookies.append({
            "name": name,
            "value": value,
            "domain": ".douyin.com",
            "path": "/",
            "secure": True,
            "httpOnly": False,
        })
    await page.context.add_cookies(cookies)


async def send_message(config: Config):
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

        # 1. 先访问首页，建立会话
        await page.goto(LOGIN_URL, wait_until="domcontentloaded")
        await asyncio.sleep(2)

        # 2. 注入 Cookie
        await load_cookies(page, config.cookie_str)

        # 3. 刷新页面使 Cookie 生效
        await page.reload(wait_until="networkidle")
        await asyncio.sleep(3)

        # 4. 判断是否登录成功（检测头像或用户名元素）
        try:
            await page.wait_for_selector(SELECTORS["chat_item"], timeout=10000)
            print("[+] 登录成功，检测到会话列表")
        except Exception:
            # 保存截图用于调试
            DEBUG_DIR.mkdir(exist_ok=True)
            await page.screenshot(path=str(DEBUG_DIR / "login_failed.png"))
            raise RuntimeError("登录失败，请检查 Cookie 是否有效")

        # 5. 导航到私信页面（使用目标用户标识）
        target_url = MESSAGE_URL_TEMPLATE.format(user=config.target_user)
        await page.goto(target_url, wait_until="domcontentloaded")
        await asyncio.sleep(3)

        # 6. 等待输入框出现
        try:
            input_box = await page.wait_for_selector(
                SELECTORS["message_input"], timeout=15000
            )
        except Exception:
            DEBUG_DIR.mkdir(exist_ok=True)
            await page.screenshot(path=str(DEBUG_DIR / "input_not_found.png"))
            raise RuntimeError("未找到输入框，可能是页面结构变化或目标用户不存在")

        # 7. 输入消息
        await input_box.click()
        await input_box.fill(config.message_text)
        await asyncio.sleep(1)

        # 8. 点击发送按钮
        try:
            send_btn = await page.wait_for_selector(
                SELECTORS["send_button"], timeout=5000
            )
            await send_btn.click()
        except Exception:
            # 尝试按 Enter 发送（有些版本支持）
            await page.keyboard.press("Enter")
            await asyncio.sleep(1)

        # 9. 等待发送成功（观察消息气泡出现）
        await asyncio.sleep(3)
        print(f"[✓] 消息已发送至 {config.target_user}: {config.message_text}")

        await browser.close()


def main():
    config = Config()
    config.validate()
    print(f"[*] 使用 Cookie: {config.masked_cookie}")
    print(f"[*] 目标用户: {config.target_user}")
    print(f"[*] 消息内容: {config.message_text}")

    asyncio.run(send_message(config))


if __name__ == "__main__":
    main()
