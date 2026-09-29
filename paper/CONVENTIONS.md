# Paper Conventions — paper/main.md

> Binding for every future edit of `paper/main.md`. Purpose: every number in the paper must
> trace to a committed repo artifact, and the paper must never claim a novelty superlative.

## 1. Number provenance (all counts derive from these artifacts)

| Paper number | Where it comes from | Regeneration |
|---|---|---|
| Registry population (17,167 servers post-dedupe; prefix-of-cursor caveat) | `data/collection_report.md` §2–§4; raw snapshots `data/raw/registry/20260921T115232Z/` | `python3 pilot/crawl_registry.py` runs (PI-authorised page caps only) |
| 16,763 tool descriptions / 4,725 repos | `data/github_tools.jsonl` (`wc -l`); `data/collection_report.md` §8 | `python3 pilot/fetch_github.py` (Brief 02 protocol) |
| 150-row sample construction (top-100 by score + 50 zero-flag, seed 42) | `data/analysis_toollevel.csv` (sha256 `ae1aff9f…8f77`) | Brief 03 sampling, frozen — do not regenerate |
| Per-class precision (5.6% = 15/268; 5 TP / 145 FP) | `data/validation_report.md` Summary + per-class table | `python3 pilot/label_sample.py --report` (⚠ regenerates the file wholesale; re-append the Reliability section after any label mutation) |
| Labels & verbatim quotes | `data/labels.jsonl` (last-wins; supersessions in `labels.jsonl.superseded`, audit in `labels.audit.jsonl`) | human-owned; never agent-written |
| κ = +0.760 (po 0.9333, pe 0.7222, n=30); POI-only +0.738; strata; 2 disagreements | `data/kappa_report.md`; packet `data/kappa_packet.md` @ `7b52792`; rater verdicts `data/labels_llm.jsonl` | `python3 pilot/kappa_report.py` |
| 7 CSV-cap flips / 43 cap-affected; 0/7 source-level flips | `data/validation_report.md` truncation-validity section; `data/collection_report.md` §5.11 | same as validation report |
| §5.10 duplicate-name census (1,484) / §5.11 source-cuts (1,082 = 6.45%) / §5.12 Unicode scan (0 Cc/Cf) / §5.13 P7 surface (2 rows) | `data/collection_report.md` §5.10–§5.13 + `data/unicode_scan.csv` + `data/p7_bypass_scan.csv` | producing commands embedded in each §5.x subsection |
| FP taxonomy buckets | `data/validation_report.md` FP-reason table (semantic grouping in `docs/FINDINGS_DISCUSSION.md` §c) | same as validation report |
| Related-work rows & cite-as lines | `docs/RELATED_WORK_MAP.md` (AgentsID row verified against the public report 2026-09-28; arXiv IDs PI-verified 2026-09-28) | edit only with provenance note updated |

## 2. Style rules for future edits

1. **No superlative novelty claims.** FORBIDDEN as claims: "first", "largest",
   "census-scale", "ecosystem-wide", "novel" applied to the study itself. The headline is:
   *a registry-grounded, human-validated calibration of tool-description poisoning
   detectors on the official MCP Registry.* Describe the contribution as a measurement of
   the detectors within a defined population, never as a first-of-its-kind survey.
2. **Detectors emit candidates, never verdicts** (AGENTS.md §2.3): every detector output in
   prose is a "flag", "candidate", or "pattern consistent with" — a label becomes TP/FP
   only through the human protocol.
3. **Capability ≠ poison**: capability classes (CAP) describe what a tool can do; poison
   classes (POI) describe instruction-shaped steering text. Never merge the two in one
   rate; channel classes (ADR) are reported separately by v2 design.
4. **Every number carries its artifact citation** — `[labels.jsonl]`, `[validation_report.md]`,
   `[collection_report.md §5.x]`, `[kappa_report.md]`, `[FINDINGS_DISCUSSION.md]`,
   `[RELATED_WORK_MAP.md]` — or a paper-facing footnote at LaTeX conversion time.
5. **Unverifiable or future items are marked**, never implied: `(PENDING — Brief 04)` for
   live experiments; `(as reported by authors)` for numbers taken from related work;
   explicit caveats for the prefix-of-cursor population and the stored-cut evidence base
   (§5.11).
6. **Quotes are verbatim** from `data/github_tools.jsonl` full texts via the row notes in
   `data/labels.jsonl` — no paraphrase inside quotation marks; "count-once" pairs
   (12-style same-server siblings: rows 24/25, 36/37, 60/61, 94/95) are never double-counted.
7. **Markdown now, LaTeX later**: keep structure in `##` sections with the numbering used
   in `main.md`; figures/tables stay simple pipes so conversion is mechanical.
8. **Title locked 2026-09-28 (PI choice B)**: *Calibrating the Alarms: A Registry-Grounded,
   Human-Validated Measurement of Poisoning Detectors on 16,763 MCP Tool Descriptions* —
   do not retitle; the working title "Security Posture of Public MCP Servers…" is retired.
