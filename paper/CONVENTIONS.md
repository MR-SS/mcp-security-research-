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
| Related-work rows & cite-as lines | `docs/RELATED_WORK_MAP.md` (AgentsID row verified against the public report 2026-09-28; arXiv IDs PI-verified 2026-09-28; **four 2026 works agent-verified 2026-09-29 at R2** — three arXiv abstract fetches, the TSE DOI via Crossref + Semantic Scholar, MCPZoo's numbers re-derived from its full text) | edit only with provenance note updated |

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
9. **Stage-gated live experiments (Brief 04)**: live model runs happen only on explicit PI
   "go"; $0 spend via the company proxy; real keys live in env vars only and are never
   written to the repo, logs, transcripts, or chat. Protocol: `docs/BRIEF04_PROTOCOL.md`.
10. **κ = +0.760 is worded as a rubric-application consistency check** — "second rater: an
    unversioned consumer LLM — a methodological limitation (see §7)" — in *every* location
    where the number appears (abstract, intro, tables, §5, §7, §10). It is never called or
    implied to be a human-annotation gold standard; the gold reference is always the
    150/150 human labels. (Binding from the R2 review, 2026-09-29.)
11. **Calibration claims only.** Abstract, Introduction and Discussion must never assert
    that "the ecosystem is dangerous" / "is compromised" / "is at risk" as a study result —
    every claim is about *detector calibration*, *candidate prevalence under a stated
    rubric*, or *controlled steering in a mocked harness*. Attack-shaped text from a
    benign vendor is reported as a mechanism, never as a vulnerability (paper §9,
    Figure R2-1).
12. **5.6% is always scoped to the validation sample.** Wherever flag-instance precision
    appears (abstract, §2, §4, §6.1–§6.2, §9, tables) it must be written as
    *"flag-instance precision 5.6% (15/268) **in the stratified validation sample**"* —
    never as a bare or unweighted population claim. The sample is the top 100 rows by
    `suspicion_score` plus 50 zero-flag controls, so it over-represents the detector's
    highest-scoring output; a population estimate would require score-weighted
    re-weighting, which was not performed (§6.1). (Binding from the R3 review,
    2026-09-29.)
13. **No author-intent claims.** The five TP rows are described as occurring in *otherwise
    benign product descriptions*; the paper never asserts that their authors were
    "benign-intent" or "in good faith", and never contrasts the rows with a hypothetical
    "planting attack" on intent grounds. The classification axis is textual: does the
    stored text add a behavioral instruction to the model? (Binding from the R3 review,
    2026-09-29.)
14. **No absolute novelty phrasing.** "nobody has measured" / "no prior work" are
    replaced by bounded search statements ("we found no prior study that calibrates … on
    this registry-grounded population"), and mechanism claims in §2 are hedged to what the
    model can perceive from text alone. (Binding from the R3 review, 2026-09-29.)
15. **Trial denominators are asserted, not hand-copied.** The §8 counts (54 scheduled /
    54 completed / 51 valid / 3 infra-excluded) and the Appendix A per-arm table are
    regenerated by `experiments/trial_accounting.py` from
    `data/live_tests/trials_ledger.jsonl`; `--check` must pass before any commit that
    touches the ledger or the §8/Appendix A numbers. (Binding from the R3 review,
    2026-09-29.)

## 3. Edit log (append-only)

- **2026-09-29 R2 review integrated** — external reviewer feedback, PI-approved: four 2026
  works verified and cited (`docs/RELATED_WORK_MAP.md` + `paper/main.md` §4: MCPZoo
  arXiv 2607.11086, MCP-TDP arXiv 2605.24069, Stein arXiv 2603.23802, *Beyond the Protocol*
  DOI 10.1109/TSE.2026.3694876); new §4 **scanner-reliability cluster** paragraph
  (server-level 45.53% vs description-level 5.6%, framed as convergent evidence); §9
  anticipated reviewer Q1–Q3 + **Figure R2-1** evidence chain; κ wording pass per new rule
  §2.10; calibration-only framing per new rule §2.11; abstract re-verified at **179/180**
  words, whole paper **5,960** words (comments stripped).
- **2026-09-29 R3 review integrated** — external reviewer feedback, PI-approved; wording-level
  only, **no new data collected**: (1) **sample-bounded precision** — every appearance of 5.6%
  (abstract, §2, §4 table + cluster paragraph, §6.1, §9 Q1) now reads "flag-instance precision
  5.6% (15/268) in the stratified validation sample", with a new §6.1 paragraph stating the
  sample is top-100-by-`suspicion_score` + 50 zero-flag controls, that 5.6% is therefore
  **sample-bounded, not a population estimate**, and that a population figure would need
  score-weighted re-weighting (left to future work); (2) **RQ1 rewritten** to the reviewer's
  clean option — "What candidate rate does the frozen detector produce across the
  registry-grounded population, and what fraction of those candidates survive strict
  text-bound human review?" — with the intro stating that prevalence-of-pattern is measured
  as a *candidate rate* and true prevalence is **not claimed**, only bounded by the sample TP
  rate; (3) **intent-neutrality** — §6.3 now says the five rows "occurred in otherwise benign
  product descriptions; we do not infer or assess author intent", with the textual
  classification axis stated, and the same wording propagated to §9 Q3, the
  "Benign authoring…" paragraph, and Figure R2-1 step 1; (4) **intro de-absolutized** —
  "nobody has measured" → "we found no prior study that calibrates poisoning-pattern detector
  outputs against human labels on this registry-grounded population", plus hedges on the
  system-prompt/authority sentences and "the ecosystem **appears to be** adapting"; (5) new
  **Appendix A trial-accounting table** (per-arm scheduled | completed | valid |
  infra-excluded; totals 54 | 54 | 51 | 3), regenerated and asserted by the new
  `experiments/trial_accounting.py` from `data/live_tests/trials_ledger.jsonl`. New binding
  rules §2.12–§2.15. Abstract **180/180** words (R3 qualifications offset by four
  compressions), whole paper **6,360** words. LaTeX mirror `paper/latex/main.tex` re-synced
  and recompiles clean (10 pages, 0 undefined references, 6 minor overfull boxes).
