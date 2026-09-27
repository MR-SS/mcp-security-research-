# Security Posture of Public MCP Servers

A measurement study of the public **Model Context Protocol (MCP)** ecosystem: what fraction of
public servers expose dangerous capabilities, and what fraction ship metadata with patterns
that are exploitable for **tool poisoning**? OWASP mapping: ASI04 (Agentic Supply Chain) +
ASI02 (Tool Misuse & Exploitation).

> **Status: measurement in progress (Brief 01 complete).** No results here are final, and none
> of the detector outputs are verdicts — see *Ethics* below.

## Dataset snapshot (2026-09-21)

| | |
|---|---|
| Source | Official MCP Registry — `GET https://registry.modelcontextprotocol.io/v0/servers` (public metadata only) |
| Crawl | 200 pages × 100 entries = **20,000 per-version entries** → **7,766 unique servers** after `isLatest` dedupe |
| Raw snapshot | `data/raw/registry/20260921T111907Z/` (200 verbatim pages + exhaustion probe + `crawl_meta.json`, 19 MB); earlier 60-page run in `.../20260921T111217Z/` |
| Dataset | `data/servers.jsonl` (sha256 `65022f3e…7b92d8`) · triage queue `data/analysis.csv` |
| Report | [`data/collection_report.md`](data/collection_report.md) — provenance, composition, limitations, acceptance criteria |
| API spend | **$0.00** (unauthenticated public GETs only) |

Headline composition: 89.3% remote-served (`streamable-http`/`sse`), 15.7% package-based,
47.0% linked to a GitHub repo. Detector triage (heuristic, **unvalidated**): 6.2% of servers
match ≥1 dangerous-capability pattern, 2.6% match ≥1 tool-poisoning-pattern candidate.

⚠️ **Rates drift with crawl depth** — 18.5% ≥1 dangerous-capability flag at n=108, 7.1% at
n=1,967, 6.2% at n=7,766 — so head-of-cursor subsamples are biased and **no single headline
percentage should be quoted**. The registry cursor was still live at our page cap, i.e. this
is a prefix of the registry, not a census.

## Repository map

```
AGENTS.md        operating context, hard rules, threat taxonomy, metrics vocabulary
PLAN.md          8-week plan, scope boundaries, risks, paper skeleton
prompts/         mission briefs (01 crawl → 05 paper draft)
pilot/           crawl_registry.py, analyze.py, README.md  (stdlib + requests only)
data/            servers.jsonl, analysis.csv, collection_report.md, raw/ (verbatim API snapshots)
FUTURE_WORK.md   parked out-of-scope ideas (scope guard)
```

## Reproduce

```bash
cd pilot && python3 -m venv .venv && source .venv/bin/activate && pip install requests
python3 crawl_registry.py --max-pages 200 --probe-pages 1 \
        --out ../data/servers.jsonl --raw-dir ../data/raw/registry
python3 analyze.py            # -> ../data/analysis.csv + summary on stdout
```

Analysis is deterministic over a frozen snapshot; the crawl is not (the registry is live).

## Ethics and disclosure

- **Public metadata and public source only.** We never execute third-party server code and never
  contact a server's own endpoint — registry API and public repositories only.
- **Detectors produce candidates, never verdicts.** Every pattern-based claim is phrased as
  "patterns consistent with X" until it passes the manual-validation protocol (`pilot/label_sample.py`,
  Brief 03). False positives are expected and will be reported as precision figures.
- **90-day coordinated disclosure** to maintainers/registry before any public case study, and no
  weaponizable payloads for unpatched live servers. Do not use this code to attack systems you do
  not own or have permission to test.
- Aggregate statistics and methodology are published; per-server findings are anonymised until
  disclosure completes.

## Licence / citation

Research artifact — citation and licence to be finalised with the arXiv preprint (Zenodo DOI
planned). Until then, please contact the author before reuse.
