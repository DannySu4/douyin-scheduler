"""
抖音网页版私信发送（无头浏览器方案，主方案）

原理：用 Playwright 打开已登录的抖音网页版，进入私信会话，输入文本并发送。
登录态通过 Cookie 注入实现，无需手动扫码。

⚠️ 说明：
- 抖音页面 DOM / 类名经常变化，选择器需按实际情况调整（见 README "排查" 一节）
- 此脚本仅供本人账号、低频、合规场景使用，勿用于营销群发
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from config import config
from utils import get_logger, human_delay, save_debug, mask_cookie

if TYPE_CHECKING:
    from playwright.sync_api import Page, BrowserContext

log = get_logger()

IM_URL = "https://www.douyin.com/im/"
LOGIN_URL = "https://www.douyin.com/login"


def _import_playwright():
    """延迟导入 playwright，便于无浏览器环境跑离线测试。"""
    from playwright.sync_api import sync_playwright  # type: ignore
    return sync_playwright


def _import_cookie_to_dict():
    from utils import cookie_to_dict
    return cookie_to_dict


def _inject_cookie(context, cookie_raw: str) -> None:
    """把 Cookie 字符串注入到当前 context。"""
    cookie_to_dict = _import_cookie_to_dict()
    cookies = []
    for k, v in cookie_to_dict(cookie_raw).items():
        cookies.append(
            {
                "name": k,
                "value": v,
                "domain": ".douyin.com",
                "path": "/",
            }
        )
    if cookies:
        context.add_cookies(cookies)


def _is_logged_in(page: Page) -> bool:
    """通过跳转后 URL 或页面特征判断登录态是否生效。"""
    # 简单判定：不在登录页即视为已登录
    return LOGIN_URL not in page.url


def _open_conversation(page: Page) -> None:
    """
    进入与目标用户的私信会话。
    支持两种 TARGET_USER：
    1) 完整会话 URL（含 conversation_id）-> 直接访问
    2) 用户主页 / sec_uid -> 先访问主页再点"发私信"
    """
    target = config.TARGET_USER
    log.info("目标: %s", target)

    if "conversation_id" in target or target.startswith("https://www.douyin.com/im/"):
        # 方式 A：直接打开已有会话
        page.goto(target, wait_until="domcontentloaded", timeout=config.NAV_TIMEOUT_MS)
        human_delay()
        return

    # 方式 B：从用户主页进入
    page.goto(target, wait_until="domcontentloaded", timeout=config.NAV_TIMEOUT_MS)
    human_delay(1.5, 3.0)
    # 点击"发私信"按钮（选择器需按实际页面调整）
    send_btn = page.locator("text=发私信").first
    send_btn.wait_for(state="visible", timeout=config.NAV_TIMEOUT_MS)
    send_btn.click()
    human_delay()
    # 点击后通常会跳转到 im 页面并打开对应会话


def _send_text(page: Page, text: str) -> None:
    """在输入框中输入文本并发送。"""
    # 输入框选择器：抖音网页版私信输入框，通常 contenteditable 或 textarea
    # ⚠️ 实际类名会变，失败时看 logs/*.png 截图手动修正
    editor = page.locator(
        "div[contenteditable='true'], textarea[placeholder*='消息'], "
        "textarea[placeholder*='message'], div.input_area"
    ).first
    editor.wait_for(state="visible", timeout=config.NAV_TIMEOUT_MS)

    # 聚焦 -> 清空 -> 逐段输入（更像真人）
    editor.click()
    human_delay()
    editor.fill("")  # 清空残留
    for chunk in _split_for_typing(text):
        editor.type(chunk, delay=random_delay_ms())
        human_delay(0.3, 0.9)

    # 按 Enter 发送（抖音私信默认 Enter 发送）
    editor.press("Enter")
    human_delay(1.0, 2.0)
    log.info("已发送: %s", text[:30])


def _split_for_typing(text: str, size: int = 10) -> list:
    return [text[i : i + size] for i in range(0, len(text), size)]


def random_delay_ms() -> int:
    return random.randint(50, 150)


def send_message(text: str = None) -> bool:
    """
    完整流程：启动浏览器 -> 注入 Cookie -> 进入会话 -> 发消息 -> 关闭。
    返回是否成功。
    """
    message = text or config.MESSAGE_TEXT
    sync_playwright = _import_playwright()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=config.HEADLESS)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="zh-CN",
        )
        _inject_cookie(context, config.COOKIE)
        page = context.new_page()
        page.set_default_timeout(config.NAV_TIMEOUT_MS)

        try:
            log.info("打开 IM 页面 ...")
            page.goto(IM_URL, wait_until="domcontentloaded", timeout=config.NAV_TIMEOUT_MS)
            human_delay()

            if not _is_logged_in(page):
                log.error("Cookie 登录态失效，被重定向到登录页: %s", page.url)
                save_debug(page, "not_logged_in")
                return False

            log.info("登录态 OK，打开会话 ...")
            _open_conversation(page)

            log.info("发送消息 ...")
            _send_text(page, message)

            # 留一点时间让请求真正发出
            human_delay(1.5, 3.0)
            return True

        except Exception as e:
            log.exception("发送失败: %s", e)
            save_debug(page, "error")
            return False
        finally:
            browser.close()


if __name__ == "__main__":
    ok = send_message()
    raise SystemExit(0 if ok else 1)
