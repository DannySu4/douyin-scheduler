import os
import json

class Config:
    def __init__(self):
        self.cookie_raw = os.getenv("DOUYIN_COOKIE") or ""
        self.target_user = os.getenv("TARGET_USER")
        self.message_text = os.getenv("MESSAGE_TEXT")

    def validate(self):
        missing = []
        if not self.cookie_raw:
            missing.append("DOUYIN_COOKIE")
        if not self.target_user:
            missing.append("TARGET_USER")
        if not self.message_text:
            missing.append("MESSAGE_TEXT")
        if missing:
            raise RuntimeError(f"缺少必需的环境变量: {', '.join(missing)}")
        return True

    @property
    def masked_cookie(self) -> str:
        raw = self.cookie_raw.strip()
        if len(raw) <= 18:
            return "****"
        return raw[:8] + "..." + raw[-6:]

    def get_cookies_list(self) -> list[dict]:
        """
        返回适合 Playwright add_cookies 的 cookie 列表。
        自动识别 JSON 数组格式（Cookie-Editor 导出）或字符串格式。
        """
        raw = self.cookie_raw.strip()
        if raw.startswith("["):
            # JSON 数组格式
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    # 确保每个 cookie 包含必要字段
                    for c in parsed:
                        c.setdefault("domain", ".douyin.com")
                        c.setdefault("path", "/")
                        c.setdefault("secure", True)
                        c.setdefault("httpOnly", False)
                    return parsed
            except json.JSONDecodeError:
                pass

        # 字符串格式："key1=val1; key2=val2"
        cookies = []
        for item in raw.split(";"):
            item = item.strip()
            if not item or "=" not in item:
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
        return cookies
