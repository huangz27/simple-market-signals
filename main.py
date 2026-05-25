"""Entry point: fetch F&G + Reddit posts, analyze with Claude, write markdown report."""
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

import analyze
import fng
import reddit
import report


def main() -> int:
    load_dotenv()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set. Copy .env.example to .env and fill it in.")
        return 1

    print("[1/4] Fetching CNN Fear & Greed Index...")
    fng_data = fng.fetch()
    print(f"      -> {fng_data.score:.0f} ({fng_data.rating})")

    print("[2/4] Fetching Reddit hot posts...")
    posts = reddit.fetch_all()
    print(f"      -> {len(posts)} posts across {len(set(p.subreddit for p in posts))} subs")

    print(f"[3/4] Analyzing with {analyze.MODEL} (this may take a minute)...")
    result = analyze.analyze(fng_data, posts)
    print(f"      -> {len(result.signals)} signals, {len(result.top_tickers)} tickers")

    print("[4/4] Writing report...")
    markdown = report.render(fng_data, result, len(posts))

    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    filename = f"report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    out_path = reports_dir / filename
    out_path.write_text(markdown, encoding="utf-8")

    print(f"\nDone. Report written to: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
