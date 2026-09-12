"""
GitHub Actions 定时入口。

通过环境变量 MODE 切换方案：
  - "web"（默认）：Playwright 无头浏览器，稳定，需 chromium
  - "http"：纯 requests 协议模拟，快，但签名过不了就失败

失败策略：web 优先，若失败且未强制 http，可自动降级（见下方）。
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

from utils import get_logger  # noqa
from config import config  # noqa

log = get_logger()


def main() -> int:
    # 启动时校验必需配置，缺失直接以非零退出，Actions 会标记失败
    config.validate()

    mode = os.environ.get("MODE", "web").lower()
    text = config.MESSAGE_TEXT

    if mode == "http":
        from protocol import send_via_http
        ok = send_via_http(text)
    else:
        from douyin_web import send_message
        ok = send_message(text)

    if ok:
        log.info("✅ 任务成功")
        return 0
    log.error("❌ 任务失败，详见上方日志 / debug artifact")
    return 1


if __name__ == "__main__":
    sys.exit(main())
