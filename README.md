# 抖音定时发私信 (GitHub Actions)

> ⚠️ **合规声明**：本工具仅供**本人账号、低频、合规**场景使用（如每日给自己/熟人发送提醒）。
> 请勿用于陌生用户批量群发、营销导流、绕过验证码等，此类行为违反抖音用户协议，可能导致封号。

每天定时自动发送抖音私信，运行在 GitHub Actions 上，**无需自备服务器**。

## 两种方案

| 方案 | 模式 | 稳定性 | 速度 | 适用 |
|------|------|--------|------|------|
| 无头浏览器 | `MODE=web`（默认） | ⭐⭐⭐ 高 | 较慢（~30s） | **推荐**，绕过签名校验 |
| 纯 HTTP 协议 | `MODE=http` | ⭐ 易失效 | 快（~1s） | 抓包拿到签名后的极客玩法 |

## 部署步骤

### 1. Fork / 克隆本项目到你的 GitHub

### 2. 配置 Secrets（Settings → Secrets and variables → Actions）

| Secret 名 | 内容 |
|------------|------|
| `DOUYIN_COOKIE` | 抖音网页版完整 Cookie（见下方获取方式） |
| `TARGET_USER` | 私信会话 URL（含 `conversation_id`）或对方主页 URL |
| `MESSAGE_TEXT` | 要发送的文本 |

### 3. 设置定时时间

编辑 `.github/workflows/daily-send.yml` 里的 `cron`：

```yaml
schedule:
  - cron: "0 1 * * *"   # = 北京时间 09:00（UTC+8）
```

Cron 为 **UTC 时间**，换算：`北京时间 = UTC + 8`。
[在线工具](https://crontab.guru/)可帮你生成表达式。

### 4. 手动触发试跑

在 GitHub → Actions → 选 workflow → "Run workflow"，验证能否成功。

## 如何获取 Cookie

1. 桌面 Chrome 登录 [抖音网页版](https://www.douyin.com)
2. F12 → Application → Storage → Cookies → `https://www.douyin.com`
3. 推荐复制这几条拼接：`sessionid`、`passport_csrf_token`、`ttwid`、`msToken`
   格式：`sessionid=xxx; ttwid=yyy; msToken=zzz`
4. 整段粘进 `DOUYIN_COOKIE` Secret

> 💡 更简单：DevTools → Network → 任意请求 → Copy as cURL，从里面提取 `Cookie:` 后全部内容。

## 获取 TARGET_USER（会话 URL）

- **方式 A（推荐）**：网页版先手动给对方发一条消息 → 复制浏览器地址栏 `https://www.douyin.com/im/?conversation_id=xxx`
- **方式 B**：填对方主页 URL（`https://www.douyin.com/user/xxx`），脚本会自动点"发私信"

## 本地调试

```bash
cp .env.example .env       # 填入真实值
pip install -r requirements.txt
playwright install chromium
pytest tests/              # 先跑离线单测
python main.py             # 实际发一条
```

## 常见问题排查

失败时 GitHub Actions 会上传 `debug-logs` 压缩包（含截图 `*.png` 和页面 HTML），
下载后对照排查：

| 现象 | 原因 / 解决 |
|------|------------|
| 截图显示登录页 | Cookie 失效，重新获取 |
| `not_logged_in` | Cookie 缺关键字段（sessionid/ttwid），补全 |
| 找不到输入框/发私信按钮 | 抖音改了 DOM，**按截图手动更新 `douyin_web.py` 里的选择器** |
| HTTP 方案 403 | 签名过不了，改回 `MODE=web` |
| 整点被识别 | 设置 `RANDOM_DELAY_MAX` 加随机延时 |

## 项目结构

```
douyin-scheduler/
├── .github/workflows/daily-send.yml   # 定时任务配置
├── config.py                          # 配置（读环境变量）
├── utils.py                           # 日志 / 延时 / Cookie 工具
├── douyin_web.py                      # 方案A：Playwright 无头浏览器（默认）
├── protocol.py                        # 方案B：纯 HTTP 协议模拟（备用）
├── main.py                            # 入口，按 MODE 分发
├── tests/test_utils.py                # 离线单测
├── requirements.txt
└── .env.example
```
