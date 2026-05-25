"""Fetch CNN Fear & Greed Index + Reddit hot posts and dump them to data.json.

Two modes:
  - Default (no API key needed): writes data/snapshot-<timestamp>.json. Then ask
    Claude Code (or any LLM) to read the file and produce the signals report per
    the rubric in ANALYSIS_PROMPT.md.
  - --use-api: also runs analyze.py + report.py to call Anthropic's API directly.
    Requires ANTHROPIC_API_KEY in env or .env.
"""
from __future__ import annotations

import dataclasses
import json
import sys
from datetime import datetime
from pathlib import Path

import fng
import reddit


def _serialize(obj):
    if dataclasses.is_dataclass(obj):
        d = dataclasses.asdict(obj)
        for k, v in d.items():
            if isinstance(v, datetime):
                d[k] = v.isoformat()
        return d
    raise TypeError(f"Cannot serialize {type(obj)}")


def main() -> int:
    use_api = "--use-api" in sys.argv

    print("[1/2] Fetching CNN Fear & Greed Index...")
    fng_data = fng.fetch()
    print(f"      -> {fng_data.score:.0f} ({fng_data.rating})")

    print("[2/2] Fetching Reddit hot posts...")
    posts = reddit.fetch_all()
    subs = sorted(set(p.subreddit for p in posts))
    print(f"      -> {len(posts)} posts across {len(subs)} subs: {', '.join(subs)}")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    snapshot = {
        "collected_at": datetime.now().isoformat(),
        "fear_and_greed": _serialize(fng_data),
        "posts": [_serialize(p) for p in posts],
    }
    snapshot_path = data_dir / f"snapshot-{timestamp}.json"
    snapshot_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    print(f"\nSnapshot written: {snapshot_path}")

    if use_api:
        import os

        from dotenv import load_dotenv

        load_dotenv()
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("ERROR: --use-api requires ANTHROPIC_API_KEY in env or .env")
            return 1

        import analyze
        import report

        print(f"\nAnalyzing with {analyze.MODEL} via Anthropic API...")
        result = analyze.analyze(fng_data, posts)
        markdown = report.render(fng_data, result, len(posts))

        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        report_path = reports_dir / f"report-{timestamp}.md"
        report_path.write_text(markdown, encoding="utf-8")
        print(f"Report written: {report_path}")
    else:
        print(
            "\nNext: ask Claude Code to read the snapshot and produce a report.\n"
            f'  Example: "read {snapshot_path} and produce a market signals report"\n'
            "\nClaude Code follows the rubric in ANALYSIS_PROMPT.md and writes to reports/."
            "\n(Or re-run with --use-api to call the Anthropic API directly.)"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
