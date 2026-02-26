# AI 日报 · 全球人工智能动态

**🌐 在线访问：[https://ericarnold6.github.io/newspaper-about-ai/](https://ericarnold6.github.io/newspaper-about-ai/)**

每日北京时间 09:00 自动更新，追踪全球 AI 行业产品发布与技术突破。支持手机端访问，支持查阅历史每日报告。

---

## 功能

- 📰 **每日自动更新**：每天凌晨 1:00 UTC（北京时间 09:00）自动抓取前一天的全球 AI 资讯，通过 GPT-4o 整理成中文日报
- 🗂️ **三大版块**：产品更新 / 技术突破 / 趣闻速递，每条新闻标注重要程度
- 📅 **历史回顾**：点击日期按钮或选择日历，可查阅任意历史一天的日报
- 📱 **响应式设计**：手机、平板、电脑均可正常访问

## 快速部署（Fork 后自行使用）

1. **Fork 本仓库**
2. **添加 Repository Secrets**（Settings → Secrets and variables → Actions → New repository secret）：
   - `NEWS_API_KEY` — 在 [newsapi.org](https://newsapi.org/) 免费注册获取
   - `OPENAI_API_KEY` — 在 [platform.openai.com](https://platform.openai.com/) 获取
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
