"""Financial news headlines via RSS (no auth required, stdlib XML parsing)."""
from __future__ import annotations

import re
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET

import httpx

# (display_name, rss_url)
DEFAULT_FEEDS: tuple[tuple[str, str], ...] = (
    ("MarketWatch", "https://feeds.marketwatch.com/marketwatch/topstories/"),
    (
        "CNBC",
        "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114",
    ),
    ("Seeking Alpha", "https://seekingalpha.com/market_currents.xml"),
)

HEADERS = {
    "User-Agent": "simple-market-signals/0.1 (personal market sentiment scanner)",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

_TAG_RE = re.compile(r"<[^>]+>")


@dataclass
class Headline:
    source: str
    title: str
    summary: str
    url: str
    published: datetime | None


def _parse_date(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        dt = parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        return None
    if dt and dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _strip_html(text: str) -> str:
    return _TAG_RE.sub("", text).strip()


def fetch_feed(source: str, url: str) -> list[Headline]:
    with httpx.Client(timeout=15.0, headers=HEADERS, follow_redirects=True) as client:
        resp = client.get(url)
        resp.raise_for_status()
        root = ET.fromstring(resp.text)

    headlines: list[Headline] = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        if not title:
            continue
        desc = _strip_html(item.findtext("description") or "")[:500]
        link = (item.findtext("link") or "").strip()
        published = _parse_date(item.findtext("pubDate"))
        headlines.append(
            Headline(source=source, title=title, summary=desc, url=link, published=published)
        )
    return headlines


def fetch_all(
    feeds: tuple[tuple[str, str], ...] = DEFAULT_FEEDS,
    hours_back: int = 24,
) -> list[Headline]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    all_headlines: list[Headline] = []
    for source, url in feeds:
        try:
            items = fetch_feed(source, url)
        except Exception as e:
            print(f"  warning: failed to fetch {source}: {e}")
            continue
        # Keep entries with unknown publish time too — better noise than missing context.
        recent = [h for h in items if h.published is None or h.published >= cutoff]
        all_headlines.extend(recent)
        time.sleep(0.5)
    all_headlines.sort(
        key=lambda h: h.published or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    return all_headlines


if __name__ == "__main__":
    items = fetch_all()
    print(f"Fetched {len(items)} headlines (last 24h)")
    for h in items[:15]:
        when = h.published.strftime("%Y-%m-%d %H:%M") if h.published else "unknown"
        print(f"  [{h.source}] {when} — {h.title[:90]}")
