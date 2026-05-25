# simple-market-signals

Fetches the CNN Fear & Greed Index and scans hot posts from retail-investor subreddits
(r/wallstreetbets, r/stocks, r/investing, r/StockMarket), then extracts structured market
signals into a markdown report.

Sample report: [reports/report-20260525-230145.md](reports/report-20260525-230145.md).

## Two modes

| Mode | How you run it | Cost | When to use |
|---|---|---|---|
| **Claude Code** (default) | `python main.py` then ask Claude Code to analyze | $0 (uses your Claude subscription) | You're already using Claude Code daily |
| **API** | `python main.py --use-api` | ~$0.20-0.40/run on Opus 4.7 | Fully standalone; for scheduled/headless runs |

## Setup

```powershell
git clone https://github.com/huangz27/simple-market-signals
cd simple-market-signals
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

API mode only:

```powershell
copy .env.example .env
# edit .env with your key from https://console.anthropic.com/settings/keys
```

## Usage — with Claude Code (no API cost)

If you have [Claude Code](https://claude.com/claude-code) installed, just open the project
and run the slash command:

```
/scan
```

This runs `python main.py` to fetch fresh data, then Claude Code analyzes the snapshot
using the rubric in `ANALYSIS_PROMPT.md` and writes a report to `reports/`.

Or do it in two steps manually:

```powershell
python main.py
```

then in Claude Code:

> analyze the latest snapshot

The `CLAUDE.md` at repo root tells Claude Code how to find and process the snapshot, so any
phrasing works (`/scan`, "analyze it", "produce a report" — all do the same thing).

## Usage — API mode (fully standalone)

```powershell
python main.py --use-api
```

Does everything in one shot: fetch + Claude Opus 4.7 analysis + report write.

## File layout

```
main.py              # entry point (default = collect only; --use-api = collect + analyze)
fng.py               # CNN Fear & Greed fetcher
reddit.py            # Reddit hot-posts fetcher
analyze.py           # API-mode analyzer (Anthropic SDK + Pydantic)
report.py            # API-mode markdown renderer
ANALYSIS_PROMPT.md   # rubric Claude Code follows in default mode
CLAUDE.md            # auto-loaded project context for Claude Code
.claude/commands/    # slash commands (/scan)
data/                # raw JSON snapshots (gitignored)
reports/             # generated markdown reports (committed)
```

## Scheduling daily runs (optional)

On Windows, use Task Scheduler to run `python main.py` daily — the snapshot will be ready
each morning. Then `/scan` (or just open Claude Code and ask) to get the report.

For fully unattended daily reports, schedule `python main.py --use-api` instead — costs
API credits but produces the report without any human in the loop.

## Not investment advice

Retail forums are noisy and often wrong. Treat outputs as starting points for research,
not trade ideas.
