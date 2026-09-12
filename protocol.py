"""
抖音发私信 —— 纯 HTTP 协议模拟（备用方案，无需浏览器）

⚠️ 重要前提：
抖音发私信接口带有动态签名（X-Bogus / a_bogus 等）和反爬校验，
直接 requests 重放**大概率 403**。此模块仅在你已经通过抓包拿到：
  1) 发消息接口的完整 URL + 请求体结构
  2) 签名参数的生成方式（或本次会话的有效签名）
的前提下才有用。

如果跑不通，请退回 douyin_web.py（无头浏览器方案），更稳定。

使用方式：
  先在本机浏览器抓包一次发消息请求，把字段填到下面的 _build_payload，
  再调用 send_via_http()。
"""
import time
import requests

from config import config
from utils import get_logger, mask_cookie

log = get_logger()

SEND_API = "https://www.douyin.com/aweme/v1/im/direct_message/send/"  # 示例，以实际抓包为准


def _build_headers() -> dict:
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Cookie": config.COOKIE,
        "Referer": "https://www.douyin.com/im/",
        "Content-Type": "application/json; charset=utf-8",
        # ⚠️ 以下签名参数必须从抓包请求里原样复制，缺一不可
        # "X-Bogus": "...",
        # "a_bogus": "...",
        # "msToken": "...",
    }


def _build_payload(text: str) -> dict:
    """按抓包到的请求体结构构造。字段名以你抓到的为准。"""
    return {
        "content": text,
        "conversation_id": "",   # ⚠️ 填目标会话 ID
        "message_type": 1,        # 1 = 文本
        "client_message_id": str(int(time.time() * 1000)),
    }


def send_via_http(text: str = None) -> bool:
    """
    用纯 HTTP 请求发送私信，无需浏览器。
    返回是否成功（按业务字段判断，不止看 200）。
    """
    message = text or config.MESSAGE_TEXT
    log.info("HTTP 发送（备用方案），Cookie=%s", mask_cookie(config.COOKIE))

    try:
        resp = requests.post(
            SEND_API,
            headers=_build_headers(),
            json=_build_payload(message),
            timeout=15,
        )
        log.info("HTTP %s, body=%s", resp.status_code, resp.text[:500])

        # 抖音成功响应通常 code == 0
        if resp.status_code == 200 and "code" in resp.text:
            data = resp.json()
            if data.get("code") == 0:
                log.info("发送成功")
                return True
        log.error("发送未成功，请检查签名/Cookie/接口地址")
        return False
    except Exception as e:
        log.exception("HTTP 请求异常: %s", e)
        return False


if __name__ == "__main__":
    ok = send_via_http()
    raise SystemExit(0 if ok else 1)
