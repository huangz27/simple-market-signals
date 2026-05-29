"""Reddit hot-posts fetcher via public JSON endpoint (no auth required)."""
from __future__ import annotations

import time
from dataclasses import dataclass

import httpx

DEFAULT_SUBREDDITS = ("wallstreetbets", "stocks", "investing", "StockMarket")

HEADERS = {
    # Browser-like UA — Reddit aggressively 403s generic and obvious-bot UAs.
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
}


@dataclass
class Post:
    subreddit: str
    title: str
    selftext: str
    score: int
    num_comments: int
    upvote_ratio: float
    url: str
    flair: str | None


def fetch_subreddit(name: str, limit: int = 25) -> list[Post]:
    # old.reddit.com tends to be more lenient with unauthenticated JSON requests
    # than www.reddit.com.
    url = f"https://old.reddit.com/r/{name}/hot.json?limit={limit}"
    with httpx.Client(timeout=20.0, headers=HEADERS, follow_redirects=True) as client:
        resp = client.get(url)
        resp.raise_for_status()
        data = resp.json()

    posts: list[Post] = []
    for child in data.get("data", {}).get("children", []):
        p = child.get("data", {})
        # Skip stickied moderator posts — usually rules / daily threads.
        if p.get("stickied"):
            continue
        posts.append(
            Post(
                subreddit=name,
                title=p.get("title", ""),
                selftext=(p.get("selftext") or "")[:2000],
                score=int(p.get("score", 0)),
                num_comments=int(p.get("num_comments", 0)),
                upvote_ratio=float(p.get("upvote_ratio", 0.0)),
                url=f"https://reddit.com{p.get('permalink', '')}",
                flair=p.get("link_flair_text"),
            )
        )
    return posts


def fetch_all(
    subreddits: tuple[str, ...] = DEFAULT_SUBREDDITS,
    limit_per_sub: int = 20,
) -> list[Post]:
    all_posts: list[Post] = []
    for sub in subreddits:
        try:
            all_posts.extend(fetch_subreddit(sub, limit=limit_per_sub))
        except Exception as e:
            # Reddit occasionally 403s individual subreddits — keep going so the
            # rest of the scan (F&G + news + other subs) still completes.
            print(f"  warning: failed to fetch r/{sub}: {e}")
        time.sleep(2.0)  # be polite — Reddit rate limits unauthenticated calls
    return all_posts


if __name__ == "__main__":
    posts = fetch_all()
    print(f"Fetched {len(posts)} posts")
    for p in posts[:5]:
        print(f"  [{p.subreddit}] ({p.score}↑ {p.num_comments}💬) {p.title[:80]}")
