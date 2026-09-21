# Pilot — MCP Ecosystem Security Measurement

Smallest end-to-end version of the study (PLAN.md §3). If the pilot works, we only scale; we don't redesign.

## Setup

```bash
cd pilot
python3 -m venv .venv && source .venv/bin/activate
pip install requests
```

## Run

```bash
# 1) crawl registry metadata (deduped to latest version per server).
#    Every raw page is saved VERBATIM to ../data/raw/registry/<UTC stamp>/ first, alongside
#    crawl_meta.json (timestamp, git stamp, counts, sha256) — AGENTS.md §2.6.
python3 crawl_registry.py --max-pages 5 --out ../data/servers.jsonl     # smoke test: ~500 entries
python3 crawl_registry.py --max-pages 60 --probe-pages 1 \
        --out ../data/servers.jsonl --raw-dir ../data/raw/registry      # full run (~2 min, $0.00)
# --probe-pages 1 fetches one page past the cap WITHOUT normalizing it, purely to record
# whether the registry cursor was exhausted (census) or still live (prefix).

# 2) static heuristic analysis -> CSV + printed summary stats
python3 analyze.py
# stderr carries a [repro] line (input/output sha256 + git stamp); the CSV itself stays
# byte-stable so repeated runs can be compared exactly.
```

> Note: the old dead `--raw-out` flag was replaced by `--raw-dir` (the raw dump is now the
> default behaviour: `../data/raw/registry/<UTC stamp>/page-NNN.json`).

## Status

- **Brief 01 (full crawl) done 2026-09-21, two runs:** 60 pages → 6,000 entries →
  **1,967 unique servers**; then the pre-authorised continuation to the 200-page brake →
  20,000 entries → **7,766 unique servers**. **$0.00** both runs; raw snapshots + provenance in
  `data/raw/registry/`. Write-up, limitations, crawl-depth series: `../data/collection_report.md`.
- ⚠️ The cursor was **still live at page 200**, so the dataset is a **prefix** of the registry,
  not a census. Detector rates drift with crawl depth — 18.5% dangerous-capability @ 108 servers,
  7.1% @ 1,967, 6.2% @ 7,766 — so never quote a single headline percentage (report §4).
- Out-of-scope ideas surfaced while crawling are parked in `../FUTURE_WORK.md`.

The summary printout **is** the pilot's "one table" draft:
`% dangerous capabilities · % poisoning-pattern candidates · top triage queue`.

## Pilots' success criteria

- ~~≥15% of servers flag ≥1 dangerous capability~~ **RETIRED 2026-09-21 (PI decision)** —
  replaced by **per-class composition at scale**. Registry server-level descriptions are short
  marketing text (low signal) and the pilot was a non-random head-of-cursor slice whose rate
  drifts with depth (18.5% @ 108 → 7.1% @ 1,967 → 6.2% @ 7,766); the real poisoning surface is
  tool descriptions, which Brief 02 extracts. See `../PLAN.md` §3 and report §4.
- ≥1 manually-confirmed poisoning-pattern case → the paper has its hero example
- (optional) one model fooled by one real-world-derived test case → section 5 exists

If none hold → pivot to the ASI03 (privilege/scope) angle on the same dataset. See PLAN.md.

## Ethics & legal guardrails

- We analyze **public metadata and public source only**. We never execute third-party server code.
- Detectors yield **candidates**; every case-study candidate must be manually verified.
- **90-day coordinated disclosure** to the registry maintainers and server authors before public detail.
- Publish methods + aggregate stats; don't ship weaponizable payloads for unpatched live servers.

## Roadmap inside this folder (after pilot)

- `fetch_github.py` — pull README + package manifest + grep tool-registration blocks (`@mcp.tool`, `server.tool(`, `ListToolsResult`) from linked repos
- `label_sample.py` — interactive helper to label top-100 candidates (computes precision/recall)
- `experiments/` — MCPTox-style live tests: take 5 real suspicious descriptions → 20 templated cases → run on one frontier API model + one open model → log ASR/RR. **Keep budget ≤ $50 for the pilot.**
