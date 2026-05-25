---
description: Fetch fresh F&G + Reddit data and produce a market signals report
allowed-tools: Bash, Read, Write, Glob
---

Run a fresh market signals scan end-to-end.

Steps:

1. Run `python main.py` via the Bash tool. This fetches the CNN Fear & Greed Index and Reddit hot posts, then writes a snapshot JSON file under `data/snapshot-<timestamp>.json`.

2. Capture the snapshot filename from the script's output (it prints the path).

3. Read the snapshot file in full. It's likely large (~30K tokens for ~70 posts) — paginate with `offset`/`limit` if needed until you have all of it. Don't truncate or summarize prematurely.

4. Produce a market signals report following the rubric in `ANALYSIS_PROMPT.md` exactly:
   - Same section structure (F&G table, Summary, Signals, Top Tickers, Themes, Contrarian Take)
   - Same signal kinds: `[BULL]`, `[BEAR]`, `[CONTRA]`, `[RISK]`
   - Cite specific post URLs for every signal
   - Do not invent tickers or themes not in the snapshot

5. Write the report to `reports/report-<same-timestamp>.md` using the same timestamp suffix as the snapshot.

6. Tell the user the path to the new report and give them a 3-5 bullet TL;DR of the key signals.

Do not commit the report — leave that for the user to decide.
