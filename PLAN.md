# Research Plan — Security Posture of Public MCP Servers
## A measurement study · 8 weeks · part-time (~7 h/week)

---

## 1. At a glance

| | |
|---|---|
| **Working title** | Security Posture of Public MCP Servers: A Measurement Study of Dangerous Capabilities and Tool-Description Poisoning Surface |
| **Single RQ** | Among public MCP servers, what fraction expose dangerous capabilities, and what fraction ship tool descriptions exploitable for tool poisoning? |
| **OWASP mapping** | ASI04 (Agentic Supply Chain) + ASI02 (Tool Misuse) |
| **Outputs** | 1) arXiv preprint · 2) dataset + code (Zenodo DOI) · 3) 1–3 CVEs if confirmed |
| **Budget** | ~$300 total (API), pilot ≤ $50 |
| **Timeline** | 8 weeks × ~7 h/week |
| **Agent context** | Everything an AI agent needs is in `AGENTS.md`; task briefs in `prompts/` |

---

## 2. Scope boundaries (the reason this stays fast)

**IN scope**
- Crawl official MCP Registry metadata + GitHub READMEs/manifests/source-grep
- Static heuristic analysis of server/tool descriptions
- Limited live experiments (20–40 tests, 2–3 models, MCPTox-style)
- Coordinated disclosure of confirmed findings

**OUT of scope (do not add):**
- ❌ A new comprehensive benchmark (MCPTox/MSB own that space; we measure the ecosystem)
- ❌ A new defense framework (that's paper #2)
- ❌ Dynamic analysis / executing third-party servers (phase 2)
- ❌ Secondary registries (PulseMCP, mcp.so) in phase 1 — stretch goal only
- ❌ Any interaction with live third-party servers beyond reading public metadata

---

## 3. The pilot (weeks 1–2) ⭐ — STATUS: PASSED on first smoke test

> Smallest end-to-end pipeline. It already ran on the first 108 registry servers:
> **18.5%** had ≥1 dangerous-capability flag, **1.9%** poisoning-pattern candidates, **46%** GitHub-linked.
> ⚠️ **Pilot-only figures, deliberately superseded** — the same v1 detectors give 7.1% / 4.2% / 51.1% at
> 1,967 servers, 6.2% / 2.6% / 47.0% at 7,766, and 8.8% / 1.8% / 65.8% at 17,167 servers.
> Crawl-depth series: `data/collection_report.md` §4.

**Remaining pilot work:**
- [x] Full crawl — **DONE 2026-09-21, three runs**: 60 pages → **1,967 unique servers**; pre-authorised continuation to the **200-page brake** → 20,000 entries → **7,766**; PI-authorised continuation to the **600-page brake** → 60,000 per-version entries → **17,167 unique servers** (28.6% kept by `isLatest` dedupe), $0.00 all runs. Snapshots: `data/raw/registry/20260921T111217Z/` (60 pages, 6.2 MB), `.../20260921T111907Z/` (200 pages, 19.0 MB), `.../20260921T115232Z/` (600 pages, 64 MB); write-up in `data/collection_report.md`. ⚠️ the cursor was still live at page 600 → the dataset is a *prefix* of the registry (**>60,000 entries**), not a census; `FUTURE_WORK.md` item 8 is the standing plan.
- [ ] Manual labeling of top-100 candidates → detector precision
  **Brief 03 hypothesis (PI, 2026-09-21): precision ≈ 0–15% at server level** — the null-result
  framing for registry-level heuristics is accepted. Brief 03 proceeds on the 150-sample exactly
  as designed, and the false-positive analysis (substring overreach: bare URLs, `never`, `.env`,
  `assistant:`) goes into `data/validation_report.md` **verbatim**.
  *Structural explanation now on record:* the registry schema caps `server.description` at
  **100 chars** — observed max exactly 100 across all 20,000 entries (median 91) — so a
  server-level description is roughly one sentence of marketing copy. Sentence-level poisoning
  heuristics at this level are therefore near-blind by construction, which is why the tool-level
  surface (Brief 02) carries the real signal.
- [ ] 5 real suspicious descriptions → 20 templated cases → ASR on 2 models

**Pilot success criteria (met/pending):**
- ~~≥15% servers with dangerous capabilities → the story exists~~ **RETIRED 2026-09-21 (PI decision) — replaced by per-class composition at scale.** Reasons: (a) registry **server-level descriptions are short marketing text**, so a headline % measures prose rather than capability — the real poisoning surface is **tool descriptions** (Brief 02); (b) the pilot was a **non-random head-of-cursor slice** and the rate drifts with crawl depth (18.5% @ 108 → 7.1% @ 1,967 → 6.2% @ 7,766), which is itself a **Methods-section finding about sampling bias**; (c) **no ASI03 pivot**. Contribution = composition + validated detector precision (Brief 03) + tool-level surface (Brief 02). See `data/collection_report.md` §4.
- [ ] ≥1 manually-confirmed poisoning case → the hero example
- [ ] ASR > 0 on ≥1 model → the impact section

*If all failed → pivot to the ASI03 privilege/scope angle on the same dataset.* (Exit criterion left on the books for the record; **the PI explicitly declined this pivot on 2026-09-21**.)

---

## 4. Eight-week timeline

| Week | Work | Deliverable |
|---|---|---|
| 1 | Read the 6 key papers (AGENTS.md §5) · run pilot pipeline · **start arXiv endorser search** | servers.jsonl (pilot) |
| 2 | Finish pilot · draft methods section rough | pilot table |
| 3–4 | Full crawl ✅ (done 2026-09-21: 7,766 servers) · GitHub enrichment · label 100-sample for precision/recall | final dataset + validated detectors |
| 5 | Full live experiments (40 tests, 3 models) · begin responsible disclosure | ASR results + disclosure tickets |
| 6 | Full draft (8–10 pp, ACM/USENIX style) · **approved stretch: re-crawl the census and diff it against the 2026-09-21 snapshot → description-drift statistics over the ~89% mutable-remote surface (one figure, $0)** | draft v1 + drift figure |
| 7 | Polish · public repo · Zenodo DOI · 1–2 external reviews (OWASP community) | draft v2 + artifact |
| 8 | **Submit to arXiv** · update résumé/LinkedIn | ✅ arXiv ID |

---

## 5. Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| No arXiv endorser (cs.CR requires one for first-time submitters) | High | Start week 1; academic co-author as fallback; worst case SSRN/TechRxiv |
| Registry API changes | Medium | Defensive code; raw JSON snapshots saved in `data/raw/` |
| High false-positive rate in detectors | High | Manual 100-sample validation; report precision — it's a methodological contribution |
| Legal/ethics exposure | Low | Public metadata only; no executing third-party code; 90-day disclosure; Ethics section |
| Scope creep | High | This file's §2; every new idea → `FUTURE_WORK.md` |
| **Pilot rate did not survive scaling** (≥1 dangerous-capability flag: 18.5% @ n=108 → 7.1% @ n=1,967 → **6.2% @ n=7,766**) | **Realised** | Criterion retired, no ASI03 pivot (PI, 2026-09-21); contribution re-framed as per-class composition + validated detector precision; the drift itself is written up as a sampling-bias finding (`data/collection_report.md` §4) |
| **Registry is larger than any run's page cap** (cursor still live at page 200; 7,766 unique and rising) | **Realised** | All claims phrased as "first 20,000 registry entries (cursor order)"; another `--max-pages` run is a $0 one-flag change pending authorisation |
| ~~No git repository → git-status stamp impossible~~ **RESOLVED 2026-09-21** | Closed | Repo initialised at the project root; pre-crawl checkpoint `0429072`; raw API snapshots committed (rule §2.6 satisfied) |
| **Detector precision likely very low** (informal triage: the 15 highest-scoring rows are all benign substring matches — URLs, "never", "assistant:", ".env" — and the max `suspicion_score` over 7,766 rows is 4) | High | Brief 03 owns the validation protocol: label the top-100 + 50 random negatives, report precision per class, propose regex fixes as a versioned diff; never build a case study straight from `analysis.csv` |

---

## 6. Paper skeleton (fill continuously, don't write at the end)

```
1 Intro        — ecosystem explosion + 3 motivating real-world examples
2 Background   — MCP in half a page + server-side supply-chain threat model
3 Methodology  — collection, detectors, validation protocol, ethics
4 Findings     — the one table + 3–4 figures + case studies
5 Live tests   — do real poisoned descriptions fool frontier models?
6 Discussion   — implications for registries/clients + disclosure
7 Related      — MCPTox/MSB/MCP-TDP/MCPSecBench; our delta: first ecosystem-wide view
```

---

## 7. Delegation workflow

Work is delegated to AI agents via the briefs in `prompts/` (numbered in execution order). Each brief is self-contained: goal, inputs, outputs, acceptance criteria, and don'ts. Give an agent `AGENTS.md` + exactly one brief per run. Rule: a brief is merged only when its acceptance criteria are met and `PLAN.md` is updated.
