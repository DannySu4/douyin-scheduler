"""
配置层：所有敏感信息从环境变量读取（GitHub Secrets 注入），
禁止把 Cookie / 账号写死在代码或日志里。
"""
import os
from dotenv import load_dotenv

load_dotenv()  # 本地调试时读取 .env


def _required(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if not val:
        raise RuntimeError(f"缺少必需的环境变量: {name}")
    return val


class Config:
    """
    配置对象：属性在访问时才校验，避免「仅导入模块」就报错，
    方便测试环境 / 无 Secret 场景正常收集用例。
    """

    @property
    def COOKIE(self) -> str:
        return _required("DOUYIN_COOKIE")

    @property
    def TARGET_USER(self) -> str:
        return _required("TARGET_USER")

    @property
    def MESSAGE_TEXT(self) -> str:
        return _required("MESSAGE_TEXT")

    @property
    def NAV_TIMEOUT_MS(self) -> int:
        return int(os.environ.get("NAV_TIMEOUT_MS", "30000"))

    @property
    def HEADLESS(self) -> bool:
        return os.environ.get("HEADLESS", "true").lower() == "true"

    @property
    def RANDOM_DELAY_MAX(self) -> int:
        return int(os.environ.get("RANDOM_DELAY_MAX", "0"))

    def validate(self) -> None:
        """主动校验所有必需项，触发 _required 报错（供启动入口调用）。"""
        _ = self.COOKIE
        _ = self.TARGET_USER
        _ = self.MESSAGE_TEXT


# 全局单例（懒校验，导入时不报错）
config = Config()

if __name__ == "__main__":
    config.validate()
    print("配置校验通过")
