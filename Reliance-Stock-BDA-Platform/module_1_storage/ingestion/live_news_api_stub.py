"""
live_news_api_stub.py — Extensible Live News Scraper & API Hook for Reliance
=============================================================================
Fetches live market news feeds via Moneycontrol, Economic Times, and LiveMint RSS.
Filters articles matching Reliance keywords ('Reliance', 'RIL', 'Mukesh Ambani', 'Jio').
Provides an extensible scaffold for integrating real Moneycontrol or NewsAPI keys.

Usage:
    python module_1_storage/ingestion/live_news_api_stub.py [--max-items 20]
"""

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import re
import html
import argparse
import datetime
import pandas as pd

RELIANCE_KEYWORDS = ["reliance", "ril", "mukesh ambani", "jio", "jamnagar", "retail", "telecom"]

LIVE_RSS_FEEDS = {
    "moneycontrol": [
        "https://www.moneycontrol.com/rss/latestnews.xml",
        "https://www.moneycontrol.com/rss/stocksnews.xml"
    ],
    "economic_times": [
        "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms"
    ],
    "livemint": [
        "https://www.livemint.com/rss/markets"
    ]
}

DEFAULT_OUTPUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "news", "reliance_live_news.csv"))


def strip_html(raw_html: str) -> str:
    """Removes HTML tags and entities."""
    clean = re.sub(r"<[^>]+>", "", str(raw_html))
    return html.unescape(clean).strip()


def matches_reliance(text: str) -> bool:
    """Checks if article text mentions Reliance Industries."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in RELIANCE_KEYWORDS)


def fetch_live_news_rss(max_items: int = 20) -> pd.DataFrame:
    """Scrapes RSS feeds and extracts matching articles."""
    try:
        import feedparser
    except ImportError:
        print("  [WARN] feedparser library not found. Install feedparser to enable live RSS feeds.")
        return pd.DataFrame()

    articles = []
    print("  [NET] Connecting to financial news RSS endpoints...")

    for source_name, urls in LIVE_RSS_FEEDS.items():
        for url in urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    title = strip_html(entry.get("title", ""))
                    summary = strip_html(entry.get("summary", ""))
                    published = entry.get("published", datetime.date.today().isoformat())
                    link = entry.get("link", "")

                    if matches_reliance(f"{title} {summary}"):
                        articles.append({
                            "trade_date": published[:10] if len(published) >= 10 else datetime.date.today().isoformat(),
                            "source": source_name,
                            "title": title,
                            "summary": summary,
                            "link": link,
                            "ticker": "RELIANCE",
                            "fetched_at": datetime.datetime.now().isoformat()
                        })
                        if len(articles) >= max_items:
                            break
            except Exception as e:
                print(f"  [WARN] Error parsing feed {url}: {e}")

    df = pd.DataFrame(articles)
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Live Financial News Scraper for Reliance")
    parser.add_argument("--max-items", type=int, default=20, help="Maximum articles to collect")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output CSV path")
    args = parser.parse_args()

    print(f"[{datetime.datetime.now()}] Ingestion: Starting Live News Fetch...")
    df_live = fetch_live_news_rss(args.max_items)
    if not df_live.empty:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        df_live.to_csv(args.output, index=False)
        print(f"  [OK] Saved {len(df_live)} live articles matching Reliance to: {args.output}")
    else:
        print("  [INFO] Live RSS feed run completed (0 new articles found or feedparser inactive).")
