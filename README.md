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

## Quick start (Claude Code, no API cost)

Prerequisite: Python 3.10+ and [Claude Code](https://claude.com/claude-code).

```powershell
git clone https://github.com/huangz27/simple-market-signals
cd simple-market-signals
claude   # open Claude Code in this directory
```

Then in Claude Code:

```
/scan
```

That's it. `/scan` installs dependencies on first run, fetches the F&G index and Reddit
posts, then writes a report to `reports/`. Subsequent runs skip the install step.

You can also just say "analyze the latest snapshot" or "produce a report" — `CLAUDE.md`
tells Claude Code what to do regardless of phrasing.

## Setup for API mode

Only needed if you want fully unattended runs that don't depend on Claude Code being open:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# edit .env with your key from https://console.anthropic.com/settings/keys
```

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
