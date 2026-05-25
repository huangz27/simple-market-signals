"""Claude-powered analysis of Reddit posts + F&G context into market signals."""
from __future__ import annotations

import json
import os
from typing import Literal

import anthropic
from pydantic import BaseModel, Field

from fng import FearGreed
from reddit import Post

MODEL = "claude-opus-4-7"

SYSTEM_PROMPT = """You are a market sentiment analyst. You receive:
  1. The current CNN Fear & Greed Index score (0-100) and historical context.
  2. A batch of recent posts from retail-investor subreddits (titles, body text, scores, comment counts).

Your job is to extract actionable market signals — not generic summaries.

Focus on:
  - Specific tickers and assets being discussed unusually heavily
  - Concrete bullish or bearish theses being argued (not just "to the moon" noise)
  - Contrarian opportunities: when retail sentiment diverges from professional indicators
  - Emerging themes (sector rotations, macro fears, specific catalysts like earnings/Fed)
  - Risk signals: euphoria, panic selling, leverage talk, "this time is different" thinking

Be skeptical. Retail forums are noisy and often wrong. When the F&G index shows extreme
greed and Reddit echoes it, that is a contrarian warning sign — note it explicitly. When
the index shows fear but specific posts argue thoughtful bull cases, surface those too.

Cite the URLs of specific posts that support each signal. Do not invent tickers or themes
not actually present in the input."""


class TickerMention(BaseModel):
    ticker: str = Field(description="Ticker symbol, e.g. TSLA, SPY, BTC")
    mention_count: int = Field(description="How many posts referenced this ticker")
    sentiment: Literal["bullish", "bearish", "mixed", "neutral"]
    context: str = Field(description="One or two sentences on what people are saying")


class Signal(BaseModel):
    kind: Literal["bullish", "bearish", "contrarian", "risk"]
    title: str = Field(description="Short headline for this signal")
    rationale: str = Field(description="Why this matters; what the crowd is saying or missing")
    confidence: Literal["low", "medium", "high"]
    supporting_post_urls: list[str] = Field(description="URLs of posts supporting this signal")


class Analysis(BaseModel):
    sentiment_label: Literal[
        "extreme_fear", "fear", "neutral", "greed", "extreme_greed"
    ] = Field(description="Aggregate retail sentiment from the posts, not the F&G score")
    sentiment_vs_fng: str = Field(
        description="One sentence comparing retail sentiment to the F&G index reading"
    )
    summary: str = Field(description="2-4 sentence executive summary of the current market mood")
    top_tickers: list[TickerMention] = Field(description="Most-discussed tickers, max 10")
    signals: list[Signal] = Field(description="Actionable signals, ranked by importance, max 8")
    notable_themes: list[str] = Field(description="Recurring themes (e.g. 'AI bubble talk', 'rate-cut speculation'), max 6")
    contrarian_take: str = Field(
        description="One paragraph: what is the crowd likely wrong about right now?"
    )


def _compact_post(p: Post) -> dict:
    return {
        "sub": p.subreddit,
        "title": p.title,
        "body": p.selftext[:800] if p.selftext else "",
        "score": p.score,
        "comments": p.num_comments,
        "ratio": round(p.upvote_ratio, 2),
        "flair": p.flair,
        "url": p.url,
    }


def analyze(fng: FearGreed, posts: list[Post]) -> Analysis:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    fng_context = (
        f"CNN Fear & Greed Index: {fng.score:.1f} ({fng.rating})\n"
        f"  Previous close: {fng.previous_close:.1f}\n"
        f"  1 week ago:     {fng.one_week_ago:.1f}\n"
        f"  1 month ago:    {fng.one_month_ago:.1f}\n"
        f"  1 year ago:     {fng.one_year_ago:.1f}\n"
    )

    posts_json = json.dumps([_compact_post(p) for p in posts], ensure_ascii=False)

    user_message = (
        f"{fng_context}\n"
        f"Recent posts ({len(posts)} total, JSON):\n"
        f"{posts_json}\n\n"
        "Produce the structured analysis."
    )

    response = client.messages.parse(
        model=MODEL,
        max_tokens=8000,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
        output_format=Analysis,
    )

    if response.parsed_output is None:
        raise RuntimeError(
            f"Model did not return parseable output. stop_reason={response.stop_reason}"
        )
    return response.parsed_output


if __name__ == "__main__":
    from dotenv import load_dotenv

    import fng as fng_mod
    import reddit as reddit_mod

    load_dotenv()
    print("Fetching F&G...")
    fng_data = fng_mod.fetch()
    print("Fetching Reddit...")
    posts = reddit_mod.fetch_all()
    print(f"Analyzing {len(posts)} posts with {MODEL}...")
    result = analyze(fng_data, posts)
    print(json.dumps(result.model_dump(), indent=2))
