import os
from pathlib import Path

# ---------- 路径与配置 ----------
BASE_DIR = Path(__file__).resolve().parent
LOGIN_URL = "https://www.douyin.com"
MESSAGE_URL_TEMPLATE = "https://www.douyin.com/messages/{user}"
DEBUG_DIR = Path("debug-logs")

# ---------- 选择器（抖音网页版可能变化，需自行调整）----------
SELECTORS = {
    "chat_item": ".chat-list-item",
    "message_input": ".public-DraftEditor-content",
    "send_button": "button[class*='send']",
}


class Config:
    def __init__(self):
        self.mode = os.getenv("MODE", "cookie")
        self.target_user = os.getenv("TARGET_USER", "")
        self.message_text = os.getenv("MESSAGE_TEXT", "")
        
        # 读取 Cookie（支持字符串和 Cookie-Editor 导出的 JSON）
        self.cookie_raw = os.getenv("DOUYIN_COOKIE", "")
        self.masked_cookie = "***" if self.cookie_raw else "(空)"

    def get_cookies_list(self):
        """自动识别 Cookie 格式并转换为 Playwright 需要的列表"""
        import json
        cookie_str = self.cookie_raw.strip()
        if not cookie_str:
            raise RuntimeError("DOUYIN_COOKIE 环境变量为空，请检查 GitHub Secrets 设置")
            
        if cookie_str.startswith("["):
            try:
                return json.loads(cookie_str)
            except json.JSONDecodeError:
                raise RuntimeError("Cookie JSON 格式解析失败，请检查复制是否完整")
        else:
            # 兼容传统 name=value; 格式
            cookies = []
            for part in cookie_str.split(";"):
                if "=" in part:
                    name, value = part.strip().split("=", 1)
                    cookies.append({
                        "name": name,
                        "value": value,
                        "domain": ".douyin.com",
                        "path": "/"
                    })
            return cookies

    def validate(self):
        missing = []
        if not self.target_user:
            missing.append("TARGET_USER")
        if not self.message_text:
            missing.append("MESSAGE_TEXT")
        if not self.cookie_raw:
            missing.append("DOUYIN_COOKIE (如果是手动触发，请确认勾选了 Run workflow with secrets)")
            
        if missing:
            raise RuntimeError(f"缺少必需的环境变量: {', '.join(missing)}")
