# 🤖 AI 芯片新闻日报系统

一个自动化的 AI 芯片新闻收集系统，使用 NewsAPI 每天自动收集 20 条最新新闻，并发送到您的邮箱。

## ✨ 功能特性

- 📰 **每天自动收集** 20 条 AI 芯片相关新闻
- 📧 **邮件推送** 漂亮的 HTML 格式新闻摘要
- 📊 **本地存储** JSON 格式的完整新闻数据
- 🌍 **多语言支持** 英文新闻收集
- ⚙️ **完全自动化** 使用 GitHub Actions 定时运行
- 🔍 **智能搜索** 多个关键词组合确保全面覆盖

## 🚀 快速开始

### 1️⃣ 获取 NewsAPI 密钥

1. 访问 [https://newsapi.org](https://newsapi.org)
2. 点击 "Get API Key" 注册账户
3. 获取免费的 API 密钥（免费版本每月 100 个请求，足够日常使用）

### 2️⃣ 配置邮件服务

#### 使用 Gmail

1. 启用 [Google Two-Step Verification](https://myaccount.google.com/security)
2. 生成 [App Password](https://myaccount.google.com/apppasswords)
3. 使用生成的密码而不是原始密码

#### 使用 QQ 邮箱

1. 进入 [QQ 邮箱设置](https://mail.qq.com)
2. 账户 → 生成授权码
3. 使用生成的授权码作为密码

#### 使用 Outlook

1. 启用 [Two-Step Verification](https://account.microsoft.com/security)
2. 生成应用密码
3. 使用生成的密码

### 3️⃣ 配置 GitHub Secrets

在仓库中设置以下 Secrets（Repository → Settings → Secrets and variables → Actions）：

```
NEWSAPI_KEY              = 你的 NewsAPI 密钥
SMTP_SERVER              = smtp.gmail.com (Gmail) / smtp.qq.com (QQ) / smtp-mail.outlook.com (Outlook)
SMTP_PORT                = 587
SENDER_EMAIL             = 你的邮箱地址
SENDER_PASSWORD          = 应用专用密码 或 授权码
RECIPIENT_EMAIL          = 接收邮件的地址
```

**设置步骤：**
1. 打开仓库设置：`https://github.com/Kevin9167/news/settings/secrets/actions`
2. 点击 "New repository secret"
3. 输入上面列出的每个密钥和值
4. 保存

### 4️⃣ 运行工作流

- **自动运行**：每天早上 8 点 UTC（北京时间下午 4 点）自动运行
- **手动运行**：
  1. 打开 Actions 标签
  2. 选择 "📰 Fetch AI Chip News Daily"
  3. 点击 "Run workflow"

## 📁 文件结构

```
.
├── .github/
│   └── workflows/
│       └── fetch_ai_chip_news.yml    # GitHub Actions 工作流
├── fetch_news.py                     # 主要爬虫脚本
├── requirements.txt                  # Python 依赖
├── .env.example                      # 环境变量示例
├── NEWS_LATEST.md                    # 最新新闻摘要（自动生成）
├── news/                             # 存储 JSON 格式新闻（自动生成）
│   ├── ai_chip_news_20240101.json
│   ├── ai_chip_news_20240102.json
│   └── ...
└── README.md                         # 本文件
```

## 🔍 搜索关键词

系统搜索以下关键词组合：

- AI chip / AI芯片
- semiconductor AI / 半导体 AI
- GPU chip / GPU芯片
- neural processor / 神经处理器

## 📧 邮件格式

收到的邮件包含：

- 📊 新闻统计（总共 X 条）
- 📅 当前日期和时间
- 各新闻项目：
  - 标题
  - 来源
  - 发布时间
  - 摘要
  - 原文链接
  - 配图（如有）

## 🛠️ 本地运行

如果想在本地测试：

```bash
# 1. 克隆仓库
git clone https://github.com/Kevin9167/news.git
cd news

# 2. 创建 Python 虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate      # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 创建 .env 文件
cp .env.example .env
# 编辑 .env 文件，填入你的配置

# 5. 运行脚本
python fetch_news.py
```

## 📊 NewsAPI 免费版本限制

| 限制项 | 免费版 |
|-------|-------|
| 每月请求数 | 100 |
| 每请求结果数 | 100 |
| 新闻年限 | 30 天 |
| 更新频率 | 实时 |

每日运行一次，月费用为：30（天）= 30 个请求，远低于 100 限制。

## 🔧 故障排除

### 邮件发送失败

**问题**：`SMTPAuthenticationError`

**解决**：
- 检查 `SENDER_EMAIL` 和 `SENDER_PASSWORD` 是否正确
- 对于 Gmail，确保使用应用专用密码，不是普通密码
- 对于 QQ，使用生成的授权码
- 检查 SMTP 服务器和端口是否匹配

### 没有获取到新闻

**问题**：`articles: []`

**解决**：
- 确保 `NEWSAPI_KEY` 有效
- 检查 API 是否达到月度限制
- 验证网络连接
- 查看工作流运行日志

### GitHub Actions 运行失败

**查看日志**：
1. 打开仓库的 Actions 标签
2. 点击失败的工作流
3. 查看 "Fetch AI chip news" 步骤的日志

## 📝 自定义

### 修改运行时间

编辑 `.github/workflows/fetch_ai_chip_news.yml`：

```yaml
schedule:
  - cron: '0 8 * * *'  # 改为你需要的时间
```

Cron 格式：`分钟 小时 日期 月份 星期`

示例：
- `0 8 * * *` - 每天 8 点
- `0 0 * * 0` - 每周日 0 点
- `0 9 * * 1-5` - 周一到周五 9 点

### 修改新闻数量

编辑 `fetch_news.py`：

```python
articles = self.fetch_news(page_size=50)  # 改为 50 条
```

### 修改搜索关键词

编辑 `fetch_news.py` 中的 `fetch_news()` 方法：

```python
queries = [
    "你的搜索词1",
    "你的搜索词2",
    # ...
]
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 支持

有问题或建议？请提交 GitHub Issue。

---

**祝您阅读愉快！** 🎉
