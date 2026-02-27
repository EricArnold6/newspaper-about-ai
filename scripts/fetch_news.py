#!/usr/bin/env python3
"""
Fetch AI news from configurable RSS/Atom feeds and save as structured JSON.

By default, generates today's edition (CST/UTC+8) using yesterday's articles (CST).
Use --date YYYY-MM-DD to generate data for a specific date.

No API keys required. Feed sources are defined in sources.yml at the repository root.
"""

import argparse
import html
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

import feedparser
import yaml

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(REPO_ROOT, "data")
MANIFEST_FILE = os.path.join(DATA_DIR, "manifest.json")
SOURCES_FILE = os.path.join(REPO_ROOT, "sources.yml")

# Maximum articles kept per section
MAX_PER_SECTION = 10


def load_sources() -> dict:
    """Load feed sources and section definitions from sources.yml."""
    with open(SOURCES_FILE, encoding="utf-8") as f:
        return yaml.safe_load(f)


def strip_html(text: str) -> str:
    """Remove HTML tags and decode HTML entities from a string."""
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def entry_date(entry) -> datetime | None:
    """Return a timezone-aware datetime for a feedparser entry, or None."""
    for field in ("published_parsed", "updated_parsed"):
        t = getattr(entry, field, None)
        if t:
            return datetime(*t[:6], tzinfo=timezone.utc)
    return None


def fetch_feed(source: dict, target_date: str) -> list[dict]:
    """Fetch a single RSS/Atom feed and return articles published on target_date."""
    articles = []
    try:
        feed = feedparser.parse(source["url"])
        if feed.bozo and not feed.entries:
            print(f"  [WARN] {source['name']}: feed parse error – {feed.bozo_exception}")
            return articles

        for entry in feed.entries:
            pub = entry_date(entry)
            # Accept articles published on target_date (UTC) or with no date info
            if pub and pub.strftime("%Y-%m-%d") != target_date:
                continue

            title = strip_html(getattr(entry, "title", "") or "")
            if not title:
                continue

            # Prefer summary; fall back to content
            content = ""
            if hasattr(entry, "summary"):
                content = strip_html(entry.summary)
            elif hasattr(entry, "content"):
                content = strip_html(entry.content[0].get("value", ""))
            # Truncate to 300 chars for readability
            if len(content) > 300:
                content = content[:297] + "…"

            url = getattr(entry, "link", "") or ""

            articles.append(
                {
                    "title": title,
                    "content": content,
                    "source": source["name"],
                    "url": url,
                    "published": pub.isoformat() if pub else "",
                }
            )
    except Exception as exc:
        print(f"  [WARN] {source['name']}: {exc}", file=sys.stderr)

    return articles


def load_manifest() -> dict:
    if os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"dates": []}


def save_manifest(manifest: dict) -> None:
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch AI news and save as JSON.")
    parser.add_argument(
        "--date",
        metavar="YYYY-MM-DD",
        help="Edition date to generate (YYYY-MM-DD). "
             "If omitted, generates today's edition in CST (UTC+8) "
             "using yesterday's articles (CST).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.date:
        # Manual override: generate data for the specified date, fetching articles from that same date
        date_str = args.date
        target_date = args.date
    else:
        # Default: today's edition in CST, articles from yesterday (CST).
        # Using CST-yesterday (not UTC-yesterday) ensures the same edition date
        # always fetches from the same calendar day, regardless of run time.
        cst_now = datetime.now(timezone.utc) + timedelta(hours=8)
        date_str = cst_now.strftime("%Y-%m-%d")
        target_date = (cst_now - timedelta(days=1)).strftime("%Y-%m-%d")

    # Skip if data for this date already exists
    manifest = load_manifest()
    output_file = os.path.join(DATA_DIR, f"{date_str}.json")
    if date_str in manifest.get("dates", []) and os.path.exists(output_file):
        print(f"Data for {date_str} already exists. Skipping.")
        sys.exit(0)

    config = load_sources()
    sections_cfg: dict = config.get("sections", {})
    sources: list[dict] = config.get("sources", [])

    # Initialise section buckets
    sections: dict[str, list[dict]] = {key: [] for key in sections_cfg}

    print(f"Fetching AI news for {date_str} (articles from {target_date} CST) from {len(sources)} configured feed(s) …")
    total = 0
    for source in sources:
        section_key = source.get("section", "")
        if section_key not in sections:
            print(f"  [SKIP] {source['name']}: unknown section '{section_key}'")
            continue
        print(f"  Fetching {source['name']} …")
        articles = fetch_feed(source, target_date)
        # Keep at most MAX_PER_SECTION newest items per section
        bucket = sections[section_key]
        bucket.extend(articles)
        bucket.sort(key=lambda a: a.get("published") or "", reverse=True)
        sections[section_key] = bucket[:MAX_PER_SECTION]
        total += len(articles)
        print(f"    → {len(articles)} article(s) found")

    if total == 0:
        print(f"No articles found for {target_date} (edition {date_str}). Skipping.", file=sys.stderr)
        sys.exit(0)

    article_count = sum(len(v) for v in sections.values())

    os.makedirs(DATA_DIR, exist_ok=True)
    output: dict = {
        "date": date_str,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "article_count": article_count,
        "sections": sections,
        "sections_meta": {
            key: {"label": cfg.get("label", key), "icon": cfg.get("icon", "📌")}
            for key, cfg in sections_cfg.items()
        },
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Saved {article_count} article(s) to {output_file}")

    if date_str not in manifest["dates"]:
        manifest["dates"].append(date_str)
        manifest["dates"].sort(reverse=True)
    manifest["last_updated"] = datetime.now(timezone.utc).isoformat()
    save_manifest(manifest)
    print("Updated manifest.json")


if __name__ == "__main__":
    main()
