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
> **18.5%** had ≥1 dangerous-capability flag (criterion was ≥15% ✅), **1.9%** poisoning-pattern candidates, **46%** GitHub-linked.

**Remaining pilot work:**
- [x] Full crawl (`--max-pages 60`) — **DONE 2026-09-21**: 60 pages → 6,000 per-version entries → **1,967 unique servers**, $0.00, raw snapshot + `crawl_meta.json` provenance in `data/raw/registry/20260921T111217Z/`; full write-up in `data/collection_report.md`. ⚠️ the cursor was still live at page 60 → this is a *prefix* of the registry, not a census.
- [ ] Manual labeling of top-100 candidates → detector precision
- [ ] 5 real suspicious descriptions → 20 templated cases → ASR on 2 models

**Pilot success criteria (met/pending):**
- [x] ≥15% servers with dangerous capabilities → the story exists — ⚠️ **REVISED by the full crawl: 7.1% (n=1,967) vs 18.5% (n=108 pilot head-of-cursor)**. The ≥15% bar is NOT met at scale; the framing has to be re-argued (prevalence + capability-class concentration, or the ASI03 pivot) — human decision, see `data/collection_report.md` §4.
- [ ] ≥1 manually-confirmed poisoning case → the hero example
- [ ] ASR > 0 on ≥1 model → the impact section

*If all failed → pivot to the ASI03 privilege/scope angle on the same dataset.*

---

## 4. Eight-week timeline

| Week | Work | Deliverable |
|---|---|---|
| 1 | Read the 6 key papers (AGENTS.md §5) · run pilot pipeline · **start arXiv endorser search** | servers.jsonl (pilot) |
| 2 | Finish pilot · draft methods section rough | pilot table |
| 3–4 | Full crawl ✅ (done 2026-09-21: 1,967 servers) · GitHub enrichment · label 100-sample for precision/recall | final dataset + validated detectors |
| 5 | Full live experiments (40 tests, 3 models) · begin responsible disclosure | ASR results + disclosure tickets |
| 6 | Full draft (8–10 pp, ACM/USENIX style) | draft v1 |
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
| **Pilot rate did not survive scaling** (dangerous-capability share 18.5% @ n=108 → **7.1% @ n=1,967**) | **Realised** | Report both numbers honestly; state that the pilot was a non-random head-of-cursor sample; re-frame the contribution around capability-class composition + validated detector precision rather than a headline %; ASI03 pivot stays available |
| **Snapshot is a registry prefix** (cursor still live after 60 pages → ≥100 further entries) | **Realised** (2026-09-21) | Phrase every claim as "first 6,000 registry entries (cursor order)"; `--max-pages N` gives a true census for $0 (~1.4 s/page) — human decision, deliberately not taken unilaterally |
| **No git repository in the working tree** → AGENTS.md §2.6 git-status stamp cannot be satisfied | **Realised** | Artifacts are stamped `git: unavailable (not a repository)` plus timestamps and input/output sha256; human decision: `git init` + initial commit, or amend the rule |

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
