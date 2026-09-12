"""
将 GitHub Secrets 中的 Cookie 字符串转换为 Playwright 需要的 storage_state 格式
"""
import json
import os
import sys

def normalize_cookie(cookie_str: str) -> dict:
    """规范化单个 Cookie 字段，补全 Playwright 必须的字段"""
    parts = [p.strip() for p in cookie_str.split(";") if p.strip()]
    cookie_dict = {}
    for part in parts:
        if "=" in part:
            key, value = part.split("=", 1)
            cookie_dict[key.strip()] = value.strip()
        else:
            # 处理类似 HttpOnly, Secure 的标志位
            cookie_dict[part.strip()] = True

    # Playwright 强制要求的字段校验与补全
    name = cookie_dict.pop("name", None) or list(cookie_dict.keys())[0]
    value = cookie_dict.pop("value", None) or cookie_dict.pop(name, "")
    
    return {
        "name": name,
        "value": str(value),
        "domain": cookie_dict.get("domain", ".douyin.com"),
        "path": cookie_dict.get("path", "/"),
        "expires": -1,
        "httpOnly": bool(cookie_dict.get("HttpOnly", False)),
        "secure": bool(cookie_dict.get("Secure", False)),
        "sameSite": cookie_dict.get("SameSite", "Lax").capitalize() # 必须首字母大写
    }

def main():
    raw_cookie = os.getenv("DOUYIN_COOKIE", "").strip()
    if not raw_cookie:
        print("❌ 错误：未检测到 DOUYIN_COOKIE 环境变量！")
        sys.exit(1)

    # 解析 Cookie 字符串
    cookies = []
    for part in raw_cookie.split(";"):
        part = part.strip()
        if "=" in part:
            cookies.append(normalize_cookie(part))

    # 构造 Playwright storage_state 标准结构
    state = {
        "cookies": cookies,
        "origins": [
            {
                "origin": "https://www.douyin.com",
                "localStorage": []
            }
        ]
    }

    with open("auth_state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        
    print(f"✅ 成功生成 auth_state.json，包含 {len(cookies)} 条 Cookie")

if __name__ == "__main__":
    main()
