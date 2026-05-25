# simple-market-signals — context for Claude Code

This repo collects retail-investor sentiment data and turns it into a structured market signals report.

## Layout

- `main.py` — entry point. Default mode: fetches data and writes `data/snapshot-<timestamp>.json`. With `--use-api`: also calls the Anthropic API (Opus 4.7) to produce a report directly.
- `fng.py` — CNN Fear & Greed Index fetcher (no auth needed)
- `reddit.py` — Reddit hot-posts fetcher across r/wallstreetbets, r/stocks, r/investing, r/StockMarket (public JSON, no auth)
- `analyze.py` — API-mode analyzer using the Anthropic SDK with a Pydantic schema
- `report.py` — markdown renderer for API mode
- `ANALYSIS_PROMPT.md` — the rubric you (Claude Code) follow when analyzing a snapshot in default mode
- `data/` — raw JSON snapshots (gitignored)
- `reports/` — generated markdown reports (committed)

## What to do when the user asks you to analyze a snapshot

If the user says anything like "analyze the latest snapshot", "produce a report", "run a scan", or invokes `/scan`:

1. Find the most recent file matching `data/snapshot-*.json` (or use the file the user names).
2. Read it. Snapshots can be large (~30K tokens for ~70 posts) — read the whole thing, don't truncate. If it doesn't fit in one Read call, paginate with `offset`/`limit` until you have all of it.
3. Apply the rubric in `ANALYSIS_PROMPT.md` exactly — same section structure, same signal kinds, same ticker table format.
4. Write the report to `reports/report-<same-timestamp>.md` using the same timestamp suffix as the snapshot file.
5. Cite specific post URLs for every signal. Do not invent tickers or themes that aren't actually in the snapshot.

## What this project is for

The user wants to spot contrarian opportunities and risk signals by combining the F&G index (institutional sentiment proxy) with retail-forum chatter. Be skeptical — retail forums are noisy and often wrong. When F&G and retail both show extreme greed, that's a contrarian warning sign; when they diverge, surface the divergence.

## Two modes — don't confuse them

- **Claude Code mode (default)** — `python main.py` collects data only. You (Claude Code) do the analysis on demand using your subscription. No API key needed.
- **API mode** — `python main.py --use-api` runs `analyze.py` + `report.py` to call the Anthropic API directly. Requires `ANTHROPIC_API_KEY`. Costs ~$0.20-0.40 per run on Opus 4.7.

If the user mentions API costs or wants automation, point them to API mode. If they want zero cost, Claude Code mode is the default.

## Things NOT to do

- Don't run `python main.py --use-api` without confirming the user wants to spend on the API call.
- Don't change the analysis rubric in `ANALYSIS_PROMPT.md` without asking — consistency across reports is the point.
- Don't commit anything in `data/` (it's gitignored on purpose; snapshots are raw and bulky).
- Don't give specific trade recommendations. The output is research material, not advice.
