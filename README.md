# AI 日报 · 全球人工智能动态

**🌐 在线访问：[https://ericarnold6.github.io/newspaper-about-ai/](https://ericarnold6.github.io/newspaper-about-ai/)**

每日北京时间 09:00 自动更新，追踪全球 AI 行业产品发布与技术突破。支持手机端访问，支持查阅历史每日报告。

---

## 功能

- 📰 **每日自动更新**：每天凌晨 1:00 UTC（北京时间 09:00）自动抓取前一天的全球 AI 资讯，通过 GPT-4o 整理成中文日报
- 🗂️ **三大版块**：产品更新 / 技术突破 / 趣闻速递，每条新闻标注重要程度
- 📅 **历史回顾**：点击日期按钮或选择日历，可查阅任意历史一天的日报
- 📱 **响应式设计**：手机、平板、电脑均可正常访问

## 如何获取 API 密钥

### NEWS_API_KEY（免费）

1. 打开 [https://newsapi.org/register](https://newsapi.org/register)
2. 填写姓名、邮箱、密码，点击 **Submit** 完成注册（无需信用卡）
3. 注册成功后页面会直接显示你的 API Key，同时也会发送到注册邮箱
4. 免费计划限制：每天最多 100 次请求，仅能查询最近 1 个月的新闻——对本项目每日一次的调用完全够用

### OPENAI_API_KEY（按量付费，用量极少）

1. 打开 [https://platform.openai.com/signup](https://platform.openai.com/signup)，用邮箱或 Google/Microsoft 账号注册
2. 登录后进入 [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
3. 点击 **Create new secret key**，复制生成的密钥（只显示一次，请立即保存）
4. 新账号通常会赠送免费额度可直接使用（具体以注册时页面提示为准）；若额度用尽，进入 [https://platform.openai.com/settings/billing](https://platform.openai.com/settings/billing) 充值
5. 本项目每次运行约消耗 2000–5000 个 Token（输入新闻摘要 + 输出结构化 JSON），实际费用请参考 [OpenAI 官方定价页面](https://openai.com/api/pricing/)，每月用量极少

> **安全提示：** API 密钥属于私密凭证，请勿提交到代码仓库或泄露给他人。本项目通过 GitHub Secrets 安全传递密钥，代码中不会出现明文密钥。

---

## 快速部署（Fork 后自行使用）

1. **Fork 本仓库**（点击右上角 Fork 按钮）
2. **添加 Repository Secrets**（仓库页面 → Settings → Secrets and variables → Actions → New repository secret）：
   - 名称 `NEWS_API_KEY`，值填入上面获取的 NewsAPI 密钥
   - 名称 `OPENAI_API_KEY`，值填入上面获取的 OpenAI 密钥
3. **开启 GitHub Pages**（Settings → Pages → Source → **GitHub Actions**）
4. 点击 Actions → **Deploy to GitHub Pages** → **Run workflow** 完成首次部署
5. 访问 `https://<你的用户名>.github.io/newspaper-about-ai/`

## 架构

```
每日 cron (01:00 UTC)
  └─ Daily AI News Update workflow
       ├─ NewsAPI 获取昨日 AI 新闻 (最多 50 篇)
       ├─ GPT-4o 生成结构化中文摘要
       ├─ 保存 data/YYYY-MM-DD.json
       ├─ 更新 data/manifest.json
       └─ git push → 触发 Deploy workflow

push to main / workflow_dispatch
  └─ Deploy to GitHub Pages workflow
       └─ 将 index.html + data/ 发布到 GitHub Pages
```

## 技术栈

- **前端**：纯 HTML/CSS/JS，无构建步骤，无依赖
- **数据获取**：Python 3 + [NewsAPI](https://newsapi.org/) + [OpenAI API](https://platform.openai.com/)
- **部署**：GitHub Actions + GitHub Pages（免费静态托管）
