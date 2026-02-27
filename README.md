# AI 日报 · 全球人工智能动态

**🌐 在线访问：[https://ericarnold6.github.io/newspaper-about-ai/](https://ericarnold6.github.io/newspaper-about-ai/)**

每日北京时间 09:00 自动更新，追踪全球 AI 行业产品发布与技术突破。支持手机端访问，支持查阅历史每日报告。

---

## 功能

- 📰 **每日自动更新**：每天凌晨 1:00 UTC（北京时间 09:00）自动从配置的 RSS/Atom 订阅源抓取前一天的全球 AI 资讯
- 🗂️ **三大版块**：产品更新 / 技术突破 / 趣闻速递，版块和来源均可在 `sources.yml` 中自由配置
- 📅 **历史回顾**：点击日期按钮或选择日历，可查阅任意历史一天的日报
- 📱 **响应式设计**：手机、平板、电脑均可正常访问
- 🔑 **无需 API 密钥**：仅依赖公开 RSS/Atom 订阅源，无需注册任何第三方服务

## 配置新闻源

编辑仓库根目录下的 **`sources.yml`** 文件即可添加、修改或删除订阅源：

```yaml
sections:
  product_updates:
    label: "产品更新"
    icon: "🚀"
  technical_breakthroughs:
    label: "技术突破"
    icon: "🔬"
  interesting_news:
    label: "趣闻速递"
    icon: "✨"

sources:
  - name: "TechCrunch AI"
    url: "https://techcrunch.com/category/artificial-intelligence/feed/"
    section: "product_updates"

  - name: "MIT Technology Review"
    url: "https://www.technologyreview.com/feed/"
    section: "technical_breakthroughs"
  # 在此处添加更多订阅源 …
```

- `sections`：定义版块的显示名称和图标，可自定义
- `sources`：每个订阅源需提供 `name`（显示名称）、`url`（RSS/Atom 地址）、`section`（所属版块 key）

---

## 快速部署（Fork 后自行使用）

1. **Fork 本仓库**（点击右上角 Fork 按钮）
2. **开启 GitHub Pages**（Settings → Pages → Source → **GitHub Actions**）
3. 点击 Actions → **Deploy to GitHub Pages** → **Run workflow** 完成首次部署
4. 访问 `https://<你的用户名>.github.io/newspaper-about-ai/`

> **无需配置任何 Secret**：本项目完全通过公开 RSS 订阅源获取数据，不调用任何付费 API。

## 本地运行

```bash
pip install -r requirements.txt
python scripts/fetch_news.py
```

## 架构

```
每日 cron (01:00 UTC)
  └─ Daily AI News Update workflow
       ├─ 读取 sources.yml 中配置的 RSS/Atom 订阅源
       ├─ 抓取昨日各订阅源文章
       ├─ 保存 data/YYYY-MM-DD.json
       ├─ 更新 data/manifest.json
       └─ git push → 触发 Deploy workflow

push to main / workflow_dispatch
  └─ Deploy to GitHub Pages workflow
       └─ 将 index.html + data/ 发布到 GitHub Pages
```

## 技术栈

- **前端**：纯 HTML/CSS/JS，无构建步骤，无依赖
- **数据获取**：Python 3 + [feedparser](https://feedparser.readthedocs.io/)（RSS/Atom 解析）+ [PyYAML](https://pyyaml.org/)（配置读取）
- **部署**：GitHub Actions + GitHub Pages（免费静态托管）
