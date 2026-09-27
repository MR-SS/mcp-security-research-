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
- [x] GitHub enrichment (Brief 02) — **DONE 2026-09-22**: `pilot/fetch_github.py` → `data/github_tools.jsonl` (**16,763** tool-description rows from **4,725** repos; median 2 tools/repo; yield **74.6%** of 6,330 reached repos; $0.00, final-run 8,458 API calls, 4 h 55 m). Detector v2 with `level` column: tool-level any-poison **4.2%**, any-capability **11.3%**, `model_addressed` **13.1%** vs server **19.7%** (**−6.7 pp** delta). Why-not arm (404 / no-extractable / ProxyError) + checklist: `data/collection_report.md` §8. **Brief 03 sample ready:** `data/analysis_toollevel.csv` (top-100 + 50 random zero-flag, seed 42, sha256 `ae1aff9f…8f77`); frozen server `data/analysis.csv` untouched.
- [ ] **Manual labeling of top-100 candidates → detector precision — Brief 03 is now UNBLOCKED (human task)**: label `data/analysis_toollevel.csv` (150 rows) via `pilot/label_sample.py` (to be written); write `data/validation_report.md`.
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
| 3–4 | Full crawl ✅ (done 2026-09-21: 7,766 → 17,167 servers) · GitHub enrichment ✅ (done 2026-09-22: Brief 02 + §8 tool-level delta) · label 100-sample for precision/recall (**Brief 03 unblocked**, sample in `data/analysis_toollevel.csv`) | final dataset + validated detectors |
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
| **Evidence truncation — labels made on 300-char excerpts** (`analyze.py` caps the CSV `description` column at 300 chars while the detectors scan the full text; 43/150 sample rows sit exactly on the cap and 12/20 labels were affected, max +779 hidden chars) | **Realised** | `label_sample.py` now renders the FULL text from `data/github_tools.jsonl` for every label with explicit `[FULL TEXT]` / `[TRUNCATED-AT-SOURCE]` / `[TRUNCATED-AT-DISPLAY]` markers; `--review-truncated` re-reviews the cap-affected labeled rows and `data/validation_report.md` records the flip count. **Measured outcome of the full-text pass (2026-09-26): 12 of the 12 cap-affected labeled rows were re-reviewed, 5 of 20 labels (25%) changed, and the sample's unclear rate fell 25% → 0%** — for 4 of them (`u` → `fp`, rows 3/6/9/16) truncation was the direct cause. The artifact-level fix (stop capping the CSV) is parked as `FUTURE_WORK.md` #10 |
| **Verdict/note divergence — a rationale can contradict the label it annotates** (the earlier row-12 note repair and these five `u` rows each needed a *label change* alongside the PI's rationale; `--note` refuses non-`fp` rows, and `--set-note` would have stored "fp after full-text review…" on a row still counted as `unclear`. Caught 2026-09-26 before any write: the requested `--note` commands were refused rather than silently misfiled) | **Realised** | Fixed 2026-09-26: new `--verdict ROW_ID LABEL NOTE` writes label + rationale atomically through the same `supersede`/audit path (empty note refused, so no label can move without a stated reason; the script still never picks a verdict itself). The report now counts full-text re-reviews from **both** actions, so the flips truncation caused can no longer be invisible in the flip count |
| **Evidence note silently truncated by the terminal** (a pasted multi-line note stored only its first line — row 12's note became a 90-char mid-sentence fragment at 09:06Z; the surplus lines leaked into later prompts) | **Realised** | Fixed 2026-09-26 (`7b05ba7`): note entry now reads the tty byte-by-byte and drains the rest of the paste, a substituted `input()` always wins, and EOF quits cleanly; regression-tested in a real pty (paste stored whole, nothing leaked, no deadlock). No corrupted note survives — the fragment is archived in `labels.jsonl.superseded` and every mutation is in `labels.audit.jsonl` |
| **Unit confusion in the validation report** (FP reasons were counted once per flag class rather than once per row — one row's reason shown as 5; the Summary's `FP 41` is flag instances and sat next to `Labeled rows 20`) | **Realised** | Fixed 2026-09-26 (`7b05ba7`): one taxonomy reason per FP row (sums to the FP row count), rows vs flag instances labelled explicitly in the table and on stdout; verified no labeled row carries a duplicated flag class, so the per-class precision denominators were never affected. The coarse keyword buckets themselves are parked as `FUTURE_WORK.md` #11 |
| **Detector precision likely very low** (informal triage: the 15 highest-scoring rows are all benign substring matches — URLs, "never", "assistant:", ".env" — and the max `suspicion_score` over 7,766 rows is 4) | High | Brief 03 owns the validation protocol: label the top-100 + 50 random negatives, report precision per class, propose regex fixes as a versioned diff; never build a case study straight from `analysis.csv` |
| **One detector error can be counted as several** — descriptions are duplicated at two levels: (a) *template reuse* — rows 13 + 14 (`crop_image`/`resize_image`, repo `Stianlars1/tinify-mcp`) are 79% identical and share the literal sentence "The source image is never overwritten silently.", so one regex false positive appears as 2 of the 19 FP rows; (b) *registration duplication* — the same repo registers each tool name twice with different text (`src/tools/crop.ts` 187 chars vs `src/tools/remote.ts` 259; `resize.ts` 247 vs `remote.ts` 325), so `server::tool` is not a unique key | **Realised** (2 of 19 FPs; checked 2026-09-26 — each of the 20 labeled rows resolves to exactly one exact evidence match, and the `remote.ts` variants do not contain the trigger phrase, so no verdict depends on the duplicate) | Both facts are recorded verbatim in the affected notes (`template-boilerplate shared with resize_image`, `dedupe relevance`); denominators stay per-row until a dedupe pass (identical `tool_description`, or ≥N-char shared runs within one repo) lands with the coded FP rubric in `FUTURE_WORK.md` #11, and Methods must state the counting unit explicitly either way |

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
