"""CNN Fear & Greed Index fetcher."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import httpx

CNN_URL = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://www.cnn.com",
    "Referer": "https://www.cnn.com/",
}


@dataclass
class FearGreed:
    score: float
    rating: str
    timestamp: datetime
    previous_close: float
    one_week_ago: float
    one_month_ago: float
    one_year_ago: float


def fetch() -> FearGreed:
    with httpx.Client(timeout=20.0, headers=HEADERS) as client:
        resp = client.get(CNN_URL)
        resp.raise_for_status()
        data = resp.json()

    fg = data["fear_and_greed"]
    return FearGreed(
        score=float(fg["score"]),
        rating=str(fg["rating"]),
        timestamp=datetime.fromisoformat(fg["timestamp"].replace("Z", "+00:00")),
        previous_close=float(fg["previous_close"]),
        one_week_ago=float(fg["previous_1_week"]),
        one_month_ago=float(fg["previous_1_month"]),
        one_year_ago=float(fg["previous_1_year"]),
    )


if __name__ == "__main__":
    result = fetch()
    print(f"Fear & Greed: {result.score:.1f} ({result.rating})")
    print(f"  Previous close: {result.previous_close:.1f}")
    print(f"  1 week ago:     {result.one_week_ago:.1f}")
    print(f"  1 month ago:    {result.one_month_ago:.1f}")
    print(f"  1 year ago:     {result.one_year_ago:.1f}")
