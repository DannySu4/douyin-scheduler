import os
import sys

class Config:
    def __init__(self):
        self.cookie_str = os.getenv("DOUYIN_COOKIE")
        self.target_user = os.getenv("TARGET_USER")
        self.message_text = os.getenv("MESSAGE_TEXT")

    def validate(self):
        missing = []
        if not self.cookie_str:
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
        """脱敏显示 Cookie 前8后6"""
        if len(self.cookie_str) <= 14:
            return "****"
        return self.cookie_str[:8] + "..." + self.cookie_str[-6:]
