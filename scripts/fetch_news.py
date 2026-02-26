#!/usr/bin/env python3
"""
Fetch yesterday's global AI industry news and generate a Chinese-language daily summary.

Required environment variables:
  NEWS_API_KEY   - API key from https://newsapi.org/
  OPENAI_API_KEY - API key from https://platform.openai.com/
               OR
  GITHUB_TOKEN   - GitHub personal access token or Actions token (uses GitHub Models/Copilot)
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone

import requests
from openai import OpenAI

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MANIFEST_FILE = os.path.join(DATA_DIR, "manifest.json")
DEFAULT_MODEL = "gpt-4o"


def fetch_ai_news(date_str: str, api_key: str) -> list[dict]:
    """Return up to 50 AI-related articles published on *date_str* via NewsAPI."""
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": (
            "(artificial intelligence OR machine learning OR LLM OR GPT OR Claude"
            " OR Gemini OR Sora OR diffusion model) AND"
            " (product launch OR release OR breakthrough OR research OR model OR agent)"
        ),
        "from": f"{date_str}T00:00:00",
        "to": f"{date_str}T23:59:59",
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": 50,
        "apiKey": api_key,
    }
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    articles = data.get("articles", [])
    # Filter out removed/blocked articles
    return [a for a in articles if a.get("title") and a["title"] != "[Removed]"]


def summarize_with_llm(articles: list[dict], date_str: str, client: OpenAI, model: str = "gpt-4o") -> dict:
    """Use an LLM to curate and summarise the articles into structured Chinese JSON."""
    articles_text = "\n\n".join(
        f"Title: {a['title']}\n"
        f"Source: {a['source']['name']}\n"
        f"Description: {a.get('description') or 'N/A'}\n"
        f"URL: {a['url']}"
        for a in articles[:40]
    )

    prompt = f"""你是全球AI行业资深分析师，请基于以下 {date_str} 的英文新闻，为中文读者撰写一份专业日报。

新闻列表：
{articles_text}

请严格按照以下 JSON 格式返回（必须是合法 JSON，不要添加注释）：
{{
  "headline": "一句话概括当日最重要的AI动态",
  "summary": "整体概述，2-3段，用中文",
  "sections": {{
    "product_updates": [
      {{
        "title": "新闻标题（中文）",
        "content": "详细介绍，包含你的分析（中文，2-4句）",
        "source": "来源媒体名",
        "url": "原文链接",
        "importance": "high 或 medium 或 low"
      }}
    ],
    "technical_breakthroughs": [
      {{
        "title": "新闻标题（中文）",
        "content": "详细介绍（中文，2-4句）",
        "source": "来源媒体名",
        "url": "原文链接",
        "importance": "high 或 medium 或 low"
      }}
    ],
    "interesting_news": [
      {{
        "title": "新闻标题（中文）",
        "content": "详细介绍（中文，2-4句）",
        "source": "来源媒体名",
        "url": "原文链接",
        "importance": "high 或 medium 或 low"
      }}
    ]
  }}
}}

要求：
1. 每个分类选取 3-5 条最值得关注的内容
2. 如某分类无相关新闻则返回空数组
3. 重点关注 OpenAI、Google、Anthropic、Meta、百度、阿里等主流 AI 公司动态，以及重要学术突破
4. importance 字段反映新闻对行业影响力
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是专业AI行业分析师，专门为中文读者整理全球AI行业动态。"
                    "输出必须是合法的 JSON 对象，不要包含任何 Markdown 代码块标记。"
                ),
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.5,
    )
    return json.loads(response.choices[0].message.content)


def load_manifest() -> dict:
    if os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"dates": []}


def save_manifest(manifest: dict) -> None:
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def main() -> None:
    news_api_key = os.environ.get("NEWS_API_KEY")
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    github_token = os.environ.get("GITHUB_TOKEN")

    if not news_api_key:
        print("ERROR: NEWS_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    if not openai_api_key and not github_token:
        print(
            "ERROR: Neither OPENAI_API_KEY nor GITHUB_TOKEN environment variable is set.",
            file=sys.stderr,
        )
        sys.exit(1)

    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")

    # Skip if data for this date already exists
    manifest = load_manifest()
    output_file = os.path.join(DATA_DIR, f"{date_str}.json")
    if date_str in manifest.get("dates", []) and os.path.exists(output_file):
        print(f"Data for {date_str} already exists. Skipping.")
        sys.exit(0)

    print(f"Fetching AI news for {date_str} …")
    articles = fetch_ai_news(date_str, news_api_key)

    if not articles:
        print(f"No articles found for {date_str}. Skipping.", file=sys.stderr)
        sys.exit(0)

    print(f"Found {len(articles)} articles. Generating summary …")
    if openai_api_key:
        client = OpenAI(api_key=openai_api_key)
        model = DEFAULT_MODEL
        print("Using OpenAI API.")
    else:
        client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=github_token,
        )
        model = DEFAULT_MODEL
        print("Using GitHub Models (Copilot) API.")
    summary = summarize_with_llm(articles, date_str, client, model)

    os.makedirs(DATA_DIR, exist_ok=True)
    output: dict = {
        "date": date_str,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "article_count": len(articles),
        **summary,
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Saved summary to {output_file}")

    if date_str not in manifest["dates"]:
        manifest["dates"].append(date_str)
        manifest["dates"].sort(reverse=True)
    manifest["last_updated"] = datetime.now(timezone.utc).isoformat()
    save_manifest(manifest)
    print("Updated manifest.json")


if __name__ == "__main__":
    main()
