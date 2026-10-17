# Security Posture of Public MCP Servers

A measurement study of the public **Model Context Protocol (MCP)** ecosystem: what fraction of public servers expose dangerous capabilities, and what fraction ship metadata with patterns that are exploitable for **tool poisoning**?

**Research questions**

1. What dangerous capabilities and tool-poisoning patterns are present in public MCP server metadata?
2. How precise are heuristic detectors when evaluated against human-validated labels?
3. How do detector precision and attack/refusal outcomes vary across capability and poisoning categories?

**Threat model.** The study analyzes public registry metadata and public source-code/repository information. It does not execute third-party server code or contact server endpoints. A hypothetical adversary may control tool descriptions, server metadata, or public repository content; the defender is an MCP client or registry operator attempting to identify risky tools before deployment.

> **Status: measurement in progress (Brief 01 complete).** No results here are final, and none of the detector outputs are verdicts — see *Ethics* below.

## Artifact and citation

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23435929.svg)](https://doi.org/10.5281/zenodo.23435929)
[![Concept DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23435928.svg)](https://doi.org/10.5281/zenodo.23435928)

This repository is the research artifact for the pre-paper snapshot **v1.0.0**.

If you use the code, dataset, prompts, or results, please cite:

```bibtex
@software{nouri_2026_mcp_security,
  author       = {Nouri, Sajjad Rahim},
  title        = {Calibrating the Alarms: A Registry-Grounded, Human-Validated Measurement of Poisoning Detectors on 16,763 MCP Tool Descriptions},
  year         = {2026},
  version      = {v1.0.0},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.23435929},
  url          = {https://doi.org/10.5281/zenodo.23435929}
}
```

- **Version DOI:** [10.5281/zenodo.23435929](https://doi.org/10.5281/zenodo.23435929)
- **Concept DOI:** [10.5281/zenodo.23435928](https://doi.org/10.5281/zenodo.23435928)
- **License:** MIT
- **Citation metadata:** [`CITATION.cff`](CITATION.cff)

## Dataset snapshot (2026-09-21)

| | |
|---|---|
| Source | Official MCP Registry — `GET https://registry.modelcontextprotocol.io/v0/servers` (public metadata only) |
| Crawl | 200 pages × 100 entries = **20,000 per-version entries** → **7,766 unique servers** after `isLatest` dedupe |
| Tool descriptions analyzed | **16,763** |
| Raw snapshot | `data/raw/registry/20260921T111907Z/` (200 verbatim pages + exhaustion probe + `crawl_meta.json`, 19 MB); earlier 60-page run in `.../20260921T111217Z/` |
| Dataset | `data/servers.jsonl` (sha256 `65022f3e…7b92d8`) · triage queue `data/analysis.csv` |
| Report | [`data/collection_report.md`](data/collection_report.md) — provenance, composition, limitations, acceptance criteria |
| API spend | **$0.00** (unauthenticated public GETs only) |

Headline composition: 89.3% remote-served (`streamable-http`/`sse`), 15.7% package-based, 47.0% linked to a GitHub repo. Detector triage (heuristic, **unvalidated**): 6.2% of servers match ≥1 dangerous-capability pattern, 2.6% match ≥1 tool-poisoning-pattern candidate.

⚠️ **Rates drift with crawl depth** — 18.5% ≥1 dangerous-capability flag at n=108, 7.1% at n=1,967, 6.2% at n=7,766 — so head-of-cursor subsamples are biased and **no single headline percentage should be quoted**. The registry cursor was still live at our page cap; this is a prefix of the registry, not a census.

## Repository map

```text
AGENTS.md         Operating context, hard rules, threat taxonomy, metrics vocabulary
PLAN.md           Eight-week plan, scope boundaries, risks, paper skeleton
EXPERIMENTS.md    Research questions, threat model, metrics, validation and reporting protocol
prompts/          Mission briefs (01 crawl → 05 paper draft)
pilot/            crawl_registry.py, analyze.py, README.md (stdlib + requests only)
data/             servers.jsonl, analysis.csv, collection_report.md, raw/ (verbatim API snapshots)
FUTURE_WORK.md    Parked out-of-scope ideas (scope guard)
```

## Reproduce

```bash
cd pilot
python3 -m venv .venv
source .venv/bin/activate
pip install requests

python3 crawl_registry.py --max-pages 200 --probe-pages 1 \
  --out ../data/servers.jsonl --raw-dir ../data/raw/registry

python3 analyze.py
# -> ../data/analysis.csv + summary on stdout
```

Analysis is deterministic over a frozen snapshot; the crawl is not, because the registry is live. For exact reproduction of published numbers, use the frozen snapshot associated with Zenodo release **v1.0.0**.

## Metrics vocabulary

- **Candidate flag:** a heuristic pattern match; not evidence of malicious intent.
- **Validated positive:** a candidate confirmed by the predefined human-adjudication protocol.
- **Precision:** validated positives divided by sampled candidates, reported with the sample scope.
- **Attack success rate (ASR):** proportion of live experiments meeting the predefined success criterion.
- **Refusal rate:** proportion of live experiments in which the model declines or safely abstains.
- **False-positive rate:** proportion of benign samples incorrectly flagged by a detector.

## Ethics and disclosure

- **Public metadata and public source only.** We never execute third-party server code and never contact a server's own endpoint — registry API and public repositories only.
- **Detectors produce candidates, never verdicts.** Every pattern-based claim is phrased as “patterns consistent with X” until it passes the manual-validation protocol (`pilot/label_sample.py`, Brief 03). False positives are expected and will be reported as precision figures.
- **90-day coordinated disclosure** to maintainers/registry before any public case study, and no weaponizable payloads for unpatched live servers.
- **Responsible use.** Do not use this code to attack systems you do not own or do not have explicit permission to test.
- Aggregate statistics and methodology are published; per-server findings are anonymised until disclosure completes.

## Limitations

- The registry crawl is a prefix of a live registry, not a complete census.
- Heuristic detectors can produce false positives and false negatives; their outputs require human validation.
- Public metadata may be incomplete, stale, or inconsistent with deployed server behavior.
- Live experiment results are model-, prompt-, and configuration-dependent.

## License

MIT. See [`CITATION.cff`](CITATION.cff) for citation metadata.
