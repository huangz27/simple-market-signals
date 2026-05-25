---
description: Fetch fresh F&G + Reddit data and produce a market signals report
allowed-tools: Bash, Read, Write, Glob
---

Run a fresh market signals scan end-to-end. The user may be on a fresh clone — handle setup gracefully.

## Steps

### 1. Bootstrap if needed (first run only)

Try `python main.py` via Bash. If it fails with `ModuleNotFoundError` (missing `httpx`, `pydantic`, or `dotenv`), install the dependencies first:

```
pip install -q -r requirements.txt
```

Then retry `python main.py`. On subsequent runs, dependencies are already installed and the first attempt will succeed.

If `python` itself isn't found, stop and tell the user they need Python 3.10+ installed (https://www.python.org/downloads/). Don't try to install Python yourself.

### 2. Capture the snapshot path

`main.py` prints the snapshot path on the last line, e.g. `Snapshot written: data/snapshot-20260525-230145.json`. Capture it. If you can't parse it from output, use `Glob` to find the newest file matching `data/snapshot-*.json`.

### 3. Read the snapshot

Read the full file. Snapshots are large (~30K tokens for ~70 posts) — if a single Read call truncates, paginate with `offset`/`limit` until you have everything. Don't summarize prematurely.

### 4. Produce the report

Follow the rubric in `ANALYSIS_PROMPT.md` exactly:
- Same section structure: F&G table, Summary, Signals, Top Tickers, Themes, Contrarian Take
- Signal kinds: `[BULL]`, `[BEAR]`, `[CONTRA]`, `[RISK]`
- Cite specific post URLs for every signal
- Do not invent tickers or themes not present in the snapshot

### 5. Write the report

Write to `reports/report-<timestamp>.md` using the same timestamp suffix as the snapshot.

### 6. Tell the user

Print the report path and give a 3-5 bullet TL;DR of the top signals. Do not commit the report — leave that for the user to decide.
