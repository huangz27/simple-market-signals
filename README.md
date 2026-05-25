# simple-market-signals

Fetches the CNN Fear & Greed Index and scans hot posts from retail-investor subreddits,
then uses Claude Opus 4.7 to extract structured market signals into a markdown report.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# edit .env and paste your Anthropic API key
```

Get an API key at https://console.anthropic.com/.

## Usage

```powershell
python main.py
```

Writes a timestamped markdown file to `reports/`.

## What it does

1. `fng.py` — pulls the current CNN Fear & Greed score (and 1w / 1m / 1y history)
2. `reddit.py` — fetches ~20 hot posts each from r/wallstreetbets, r/stocks, r/investing, r/StockMarket
3. `analyze.py` — sends both to Claude Opus 4.7 with a structured-output schema, asking for:
   - Aggregate retail sentiment vs. the F&G reading
   - Most-discussed tickers and the dominant take on each
   - Ranked signals (bullish / bearish / contrarian / risk) with supporting post URLs
   - Notable themes and a contrarian take
4. `report.py` + `main.py` — assembles the result into a markdown report

## Cost

One run analyzes ~80 posts (~30-50K input tokens) with Opus 4.7. Expect roughly $0.20-$0.40 per run.
Drop the model in `analyze.py` to `claude-sonnet-4-6` or `claude-haiku-4-5` to cut cost by 2-5x.

## Not investment advice

Retail forums are noisy and often wrong. Treat outputs as starting points for research,
not trade ideas.
