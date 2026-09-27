# Mission Brief 01 — Full Registry Crawl

**Context:** Read `AGENTS.md` first. Pilot crawl of 108 servers already works (`pilot/crawl_registry.py`).

**Goal:** Complete snapshot of the official MCP registry, deduped to latest versions, with raw responses preserved.

**Tasks**
1. Run `pilot/crawl_registry.py --max-pages 60 --out data/servers.jsonl`.
2. Save every raw API page to `data/raw/registry/<timestamp>/page-NNN.json` for reproducibility (modify the script to dump pages before normalization).
3. Produce `data/collection_report.md`: timestamp, pages fetched, entries seen, unique servers, % with `repository.url`, % with remote (`streamable-http`) transport vs package-based, % `isLatest` dedupe kept, any API anomalies.

**Acceptance criteria**
- [ ] `data/servers.jsonl` has ≥1500 unique servers or documents why fewer
- [ ] Raw snapshot on disk; re-running analysis reproduces identical counts
- [ ] Collection report committed

**Don'ts**
- Don't add secondary registries (stretch goal, not this brief)
- Don't hit any server endpoint itself — registry API only
