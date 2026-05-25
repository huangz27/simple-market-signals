# simple-market-signals

Fetches the CNN Fear & Greed Index and scans hot posts from retail-investor subreddits,
then extracts structured market signals into a markdown report.

Two modes:
- **Claude Code mode (default, no API cost)** — `main.py` just collects data into a JSON
  snapshot; you ask Claude Code to read it and produce the report. Uses your Claude Max
  subscription, no API key needed.
- **API mode** — `main.py --use-api` calls Anthropic's API directly (Opus 4.7). Standalone
  but pay-per-token (~$0.20-0.40 per run).

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

API mode only:
```powershell
copy .env.example .env
# edit .env and paste your Anthropic API key from https://console.anthropic.com/settings/keys
```

## Usage — Claude Code mode

```powershell
python main.py
```

Writes `data/snapshot-<timestamp>.json`. Then in Claude Code:

> read `data/snapshot-<timestamp>.json` and produce a market signals report

Claude Code will read the snapshot, apply the rubric in `ANALYSIS_PROMPT.md`, and write
`reports/report-<timestamp>.md`.

## Usage — API mode

```powershell
python main.py --use-api
```

Does everything in one shot — fetch, analyze via Opus 4.7, write report.

## What it does

1. `fng.py` — pulls the current CNN Fear & Greed score (and 1w / 1m / 1y history)
2. `reddit.py` — fetches ~20 hot posts each from r/wallstreetbets, r/stocks, r/investing, r/StockMarket
3. **Analysis** (either Claude Code reading the snapshot, or `analyze.py` calling the API):
   - Aggregate retail sentiment vs. the F&G reading
   - Most-discussed tickers and the dominant take on each
   - Ranked signals (bullish / bearish / contrarian / risk) with supporting post URLs
   - Notable themes and a contrarian take
4. Report written to `reports/`

## Files

- `main.py` — orchestrator
- `fng.py`, `reddit.py` — data fetchers
- `analyze.py`, `report.py` — API-mode analyzer + renderer
- `ANALYSIS_PROMPT.md` — rubric Claude Code follows in default mode

## Not investment advice

Retail forums are noisy and often wrong. Treat outputs as starting points for research,
not trade ideas.
