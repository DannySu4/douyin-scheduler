"""
将 GitHub Secrets 中的 Cookie 字符串转换为 Playwright 的 storage_state 状态文件
"""
import json
import os
import asyncio

def parse_cookie_to_state(cookie_str: str) -> dict:
    cookies_list = []
    for part in cookie_str.split(";"):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            cookies_list.append({
                "name": k.strip(),
                "value": v.strip(),
                "domain": ".douyin.com",
                "path": "/",
                "sameSite": "Lax"  # 统一设置为合法值
            })
    return {"cookies": cookies_list, "origins": []}

async def main():
    cookie_str = os.getenv("DOUYIN_COOKIE", "").strip()
    if not cookie_str:
        print("❌ 错误：未检测到 DOUYIN_COOKIE 环境变量！")
        return

    state = parse_cookie_to_state(cookie_str)
    with open("auth_state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False)
    print("✅ Cookie 已成功转换为 storage_state 并保存为 auth_state.json")

if __name__ == "__main__":
    asyncio.run(main())
