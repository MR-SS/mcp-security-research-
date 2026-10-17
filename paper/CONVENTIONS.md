# Paper Conventions — paper/main.md

> Binding for every future edit of `paper/main.md`. Purpose: every number in the paper must
> trace to a committed repo artifact, and the paper must never claim a novelty superlative.

## 1. Number provenance (all counts derive from these artifacts)

| Paper number | Where it comes from | Regeneration |
|---|---|---|
| Registry population (17,167 servers post-dedupe; prefix-of-cursor caveat) | `data/collection_report.md` §2–§4; raw snapshots `data/raw/registry/20260921T115232Z/` | `python3 pilot/crawl_registry.py` runs (PI-authorised page caps only) |
| 16,763 tool descriptions / 4,725 repos | `data/github_tools.jsonl` (`wc -l`); `data/collection_report.md` §8 | `python3 pilot/fetch_github.py` (Brief 02 protocol) |
| 150-row sample construction (top-100 by score + 50 zero-flag, seed 42) | `data/analysis_toollevel.csv` (sha256 `ae1aff9f…8f77`) | Brief 03 sampling, frozen — do not regenerate |
| Published per-class + family text-support, instance level (poison 6/124 = 4.84%; capability 44/102 = 43.14%; channel 32/42 = 76.19%; all-family 82/268 = 30.60%; stratum 78/263 = 29.66%; collapse 75/251 = 29.88%) | `data/INSTANCE_VERDICTS.csv` (268 verdicts, each with an evidence quote) → `data/instance_summary.csv` (Wilson intervals) | `python3 pilot/adjudicate_instances.py`, `python3 pilot/derive_r4_numbers.py`, `python3 scripts/verify_claims.py` (C15) |
| Historical first-pass apportionment — retained as the earlier figure, not the published table (15/268 = 5.6%; 5 TP / 145 FP rows) | `data/validation_family_split.csv`; `data/validation_report.md` Summary + per-class table | `python3 pilot/label_sample.py --report` (⚠ regenerates the file wholesale; re-append the Reliability section after any label mutation) + `python3 pilot/derive_family_split.py` |
| Labels & verbatim quotes | `data/labels.jsonl` (last-wins; supersessions in `labels.jsonl.superseded`, audit in `labels.audit.jsonl`) | human-owned; never agent-written |
| κ = +0.760 (po 0.9333, pe 0.7222, n=30); POI-only +0.738; strata; 2 disagreements | `data/kappa_report.md`; packet `data/kappa_packet.md` @ `7b52792`; rater verdicts `data/labels_llm.jsonl` | `python3 pilot/kappa_report.py` |
| 7 CSV-cap flips / 43 cap-affected; 0/7 source-level flips | `data/validation_report.md` truncation-validity section; `data/collection_report.md` §5.11 | same as validation report |
| §5.10 duplicate-name census (1,484) / §5.11 source-cuts (1,082 = 6.45%) / §5.12 Unicode scan (0 Cc/Cf) / §5.13 P7 surface (2 rows) | `data/collection_report.md` §5.10–§5.13 + `data/unicode_scan.csv` + `data/p7_bypass_scan.csv` | producing commands embedded in each §5.x subsection |
| FP taxonomy buckets | `data/validation_report.md` FP-reason table (semantic grouping in `docs/FINDINGS_DISCUSSION.md` §c) | same as validation report |
| Related-work rows & cite-as lines | `docs/RELATED_WORK_MAP.md` (AgentsID row verified against the public report 2026-09-28; arXiv IDs PI-verified 2026-09-28; **four 2026 works agent-verified 2026-09-29 at R2** — three arXiv abstract fetches, the TSE DOI via Crossref + Semantic Scholar, MCPZoo's numbers re-derived from its full text) | edit only with provenance note updated |
| Headline Wilson intervals (82/268, 6/124, 44/102, 32/42, 5/100, 5/150) + cluster sensitivity 75/251 + κ delta-method CI (n = 30) | `pilot/derive_r4_numbers.py` (assert-guarded; STRUCTURE-LOCK block) | `python3 pilot/derive_r4_numbers.py` (must exit 0) |
| Labeling rulebook + second-rater pack (40 rows, seed 2026, sha256 `af2718…4b77a`) | `docs/LABELING_RULEBOOK.md`, `pilot/second_rater_pack.csv`, `docs/SECOND_RATER_PROTOCOL.md`, `docs/SECOND_RATER_SCORER.py` | pack generation recipe recorded in the protocol; scorer sha-verifies the pack |

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
    Figure 2).
12. **Every support rate is scoped to its unit, its family and the validation sample.**
    The published per-class and family counts come from the instance-level adjudication
    (`data/INSTANCE_VERDICTS.csv` — one verdict per fired flag; A8 closed 2026-10-14); the
    earlier row-verdict apportionment (`data/validation_family_split.csv`, 15/268) is
    retained only as the **first-pass default** and as the replication package's earlier
    figure. Wherever a rate appears (abstract, §2, §4, §6.1–§6.2, §9, tables) it must name
    both its unit and its family: *"instance-level text-support 82/268 (30.60%)"* is a
    **flag-justification** rate across three families, *"poison-family text-support 6/124
    (4.84%)"* is the calibration number — and both must be written as **in the purposive
    top-score validation sample** (the abstract's shorter form is *"in a top-score
    validation sample"*) —
    never as a bare or unweighted population claim. The sample is the top 100 rows by
    `suspicion_score` (capability flags + 3 × poison flags, stable descending sort, ties
    by corpus row order) plus 50 zero-flag controls — a **purposive top-score review**,
    renamed from "stratified sample" at STRUCTURE-LOCK because the design is purposive,
    not probability-based — so it over-represents the detector's highest-scoring output;
    a population estimate would require a probability sample over ALL flagged rows, which
    was not drawn (§6.1). (Binding from the R3 review, 2026-09-29; wording updated at
    STRUCTURE-LOCK, 2026-10-05; re-based on the instance-level table 2026-10-14.)
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
- **2026-10-03 R5 review integrated** — 14-point external audit, PI-approved; two phases.
  **Phase 1 (new computed numbers, reproducible):** `pilot/derive_family_split.py` →
  `data/validation_family_split.csv` regroups the frozen 13 classes into poison (5),
  capability (6), channel (2) — **primary metric: poison-family text-support 6/124 = 4.8%**
  (capability 5/102 = 4.9%, channel 4/42 = 9.5%, all-family 15/268 = 5.6%; script asserts
  268 instances / 15 supported); `pilot/derive_candidate_rate.py` →
  `data/candidate_rate_scan.csv` full-corpus RQ1 scan — **4,128/16,763 rows any-flag
  (24.6%), 698 rows poison-flag (4.2%), 1,892 capability / 2,183 channel rows, 4,926 flag
  instances**; both persisted with producing commands in `data/collection_report.md` §5.14.
  **Phase 2 (wording/scope, no new data):** abstract rewritten to **179/180** words carrying
  the family split, sample-bounded phrasing, mocked-trial scope (54 trials across three model
  versions; no real shell execution or network calls), row-level 5/150, κ, and the
  control-trial accounting (2/18 infra-excluded); §2/§5 RQ1 stated as a corpus **candidate
  rate** with the row↔server distinction (one row = one `(server, tool-name)` registration
  entry; 16,763 rows ≠ 17,167 servers); §6.1 primary metric re-anchored to the poison family
  and labelled a **sample-bounded descriptive quantity** (bias direction unknown, no
  lower-bound claim anywhere — sweep verified); §5 zero-flag control stratum (seed 42,
  addressing-only rows allowed) + single-rater / keyword-rulebook labeling disclosures
  (FIX 9/10); §8 explicit no-real-shell scope statement and intent-neutral "models expressed
  intent" phrasing; §4/§9 MCPZoo 45.53% phrased "average over scanners, as reported";
  intro novelty hedged ("to our knowledge, based on a literature search conducted 2026-09");
  **OWASP ASI titles unverifiable from the official page → "OWASP-adjacent mapping (see
  note)"** downgrade with a dated retrieval note (genai.owasp.org, fetched 2026-02-17
  capture); 94.4%/95.2% reframed as unsupported-flag rates ("statement about the
  instrument"); our-metric "precision" → "text-support rate" in §4/§6/§8, §9 Q1, and
  `docs/RELATED_WORK_MAP.md` (incl. removing "even wider" from the positioning paragraph);
  "Detector precision (§6.2)" → "Per-class text-support (§6.2)". Footer word-count comment
  re-verified: whole paper **8,030** words (comments stripped). Builder gates: BOTH
  `pilot/make_publication.py --check` and `pilot/make_clean_copy.py --check` pass — stage1's
  `numbers()` gained a `derive_r\d+` normalization (the citation rewrite removes the
  `derive_r4_numbers.py` filename, and the embedded id was counted as data; the drift
  pre-existed R4 and is now closed). New rules: none; the existing binding rules govern the
  new phrasing (§2.10 κ wording, §2.11 calibration-only, §2.12–§2.15 from R3 incl.
  sample-bounded). Open at R5: `paper/latex/main.tex`
  mirror NOT yet re-synced (format-only; flagged as a risk in `PLAN.md` §5).
- **2026-10-04: clean-copy builders retired post-R7; main_clean.md authoritative;
  number-parity must henceforth be checked manually per CONVENTIONS rule 4.**
  `pilot/make_publication.py` and `pilot/make_clean_copy.py` moved to `pilot/legacy/`
  (kept for history; both had been red since R6 — stale `REPLACEMENTS`/`PROSE_REWRITES`
  tables could no longer rebuild `main_clean.md`, which has been hand-maintained and
  authoritative since). No code imports them; the historical log entries above (R5 gate
  record) stay as written.
- **2026-10-05: STRUCTURE-LOCK (batches A + A-ext + limitation commitments) applied to
  both papers.** Canonical mechanism count = **four** (priority capture carries an
  unconditional and a conditional-gateway variant); **funnel figure = Figure 1** (denominator
  funnel: 60,000 → 17,167 (28.6%) → 11,370 repo-ref (66.2%) / 11,288 GitHub (65.8%) →
  16,763 rows / 4,725 repos — the task's "8,767 (51.0%)" does not appear in any committed
  artifact and was replaced with the verified report figures), **evidence chain = Figure 2**
  (the legacy `FIGURE_*_RE` strippers in `pilot/legacy/make_publication.py` accept both the
  old and new captions so the 5-op number-parity baseline stays computable at HEAD);
  completed-vs-valid wording (54 completed with transcripts / 51 valid / 3 excluded);
  Wilson CIs + cluster sensitivity (13/251) + κ delta-method CI assert-guarded in
  `pilot/derive_r4_numbers.py`; "stratified" → "purposive top-score review" (rule 12
  updated); honest-aid and second-rater-future-work sentences in §5/§7; κ-packet POI=21
  defined (5 TP + 16 flagged non-TP; 9 zero-flag controls excluded); Appendix provenance
  chronology table; second-rater pack specified as future work (no in-progress claim).
  Gates at this commit: abstract **179/180**, number parity **5 ops == HEAD baseline**,
  `derive_r4_numbers.py` exit 0, `trial_accounting --check` exit 0, banned-phrase grep 0,
  secret scan clean.
- **2026-10-06: Phase-sets A9 + C applied to both papers.** A9 (PI option C) recast the FL
  exec-priming arm as a **task-conflated null arm**: its criterion `[B]` is satisfied by
  relaying the install guide (the benign task), so it tests no steering and is excluded from
  the pooled attack ASR — now **WF+DP = 14/18** — and from the live-mechanism count (**two of
  four** mechanisms live-tested). The frozen `FL 9/9 [B]` row is unchanged; Finding 1 is a
  design lesson (instruction surfacing 9/9 vs execution intent 0/9). Phase-set C (consistency):
  **figure numbering disambiguated** — numbered paper figures are **Figure 1** (denominator
  funnel) and **Figure 2** (evidence chain); the two reviewer-package plots are labeled
  **supplemental figure S1/S2** (renamed from R1/R2, which collided with the "R2" review-round
  label and the legacy "Figure R2-1" caption). Rule: never label a supplemental plot "R<n>".
  **Dangling `§5.1x` cross-references qualified** — the paper's §5 has no numbered subsections,
  so bare `§5.10–§5.13` (collection-report sections) now read `` `data/collection_report.md` §5.10 ``
  etc. in `main.md`, and the Appendix-A mapping `§A.3`–`§A.6` in `main_clean.md`. **Version
  banners refreshed** (both papers dated `2026-09-29; revised 2026-10-06`; the stale "Skeleton"
  banner removed). Gates: abstract **178/178**, parity **5**, derive exit 0, accounting exit 0.
- **2026-10-06: Phase-set D (statistical caveats + taxonomy wording).** §6.1 now states the
  Wilson intervals' binomial assumption and the `server::tool` clustering, ties "no multiplicity
  adjustment" to the 13 fired classes, and explains the top-score selection-bias direction as
  non-identifiable from this sample (a directional hypothesis, not a bound). §8 frames i.i.d. as
  a modeling assumption and states the pooled-AASR interchangeability it cannot assume. §2 scopes
  the  authority-separation claim to the evaluated models ("we found no standard mechanism"); §10
  time-stamps the disclosure status. Gates: abstract **178/178**, parity **5**, derive/accounting exit 0.
- **2026-10-14: `cross_tool_shadowing` per-instance reclassification (targeted fix, both papers).**
  The one per-class cell whose instances the frozen row notes adjudicate individually now derives from
  those notes rather than from the row verdict: `cross_tool_shadowing` = **1 supported** (row 12, a
  priority-capture transfer — the universal all-caps "call this first before any other tools"
  instruction) / **3 unsupported** (rows 19 and 33: same-server toolkit/workflow guidance; row 55:
  dependency/setup guidance) = **0.25**, carried by a **†** mark on the class name plus a §6.2 footnote,
  and announced by an exception clause in §5's per-class-apportionment paragraph. `stealth_concealment`
  was checked the same way, in the negative direction (9 instances, each with an instance-level
  false-positive note; **0/9** unchanged). Counts are **deliberately unchanged** — all-family 15/268,
  poison 6/124, capability 5/102, channel 4/42 and every derived figure stay as published (A8: "the
  numbers were not changed, and must not be"), because the four instances are already typed in the
  notes and their verdicts match the apportioned cell. The other 11 classes stay row-verdict
  apportioned; the one disagreement running the other way (`file_read_sensitive`, apportioned 1/2 while
  row 94's note records a false positive on a positive row) is disclosed in the same footnote and left
  as published. Enforced by `scripts/verify_claims.py` **C14** (cell == note-derived counts; Σ supported
  == 15) and recorded in `claims_ledger.jsonl` **C-027**; `docs/REVIEWER_QA.md` D3 and
  `AUTHOR_ACTION_REQUIRED.md` A8 carry the partial status. Gates at this commit: abstract **178/178**,
  parity **5**, `derive_r4_numbers.py` exit 0, `trial_accounting --check` exit 0.
- **2026-10-14: A8 closed — full instance-level adjudication of all 268 fired flags (both papers).**
  Every fired flag in the 150-row sample now carries an independent verdict against its stored text,
  recorded with a verbatim evidence quote in **`data/INSTANCE_VERDICTS.csv`** (`row_id | flag |
  instance_verdict | evidence_quote | note`; provenance tags `pi-note` / `row-rule` / `text-rule`) and
  summarized with Wilson intervals in `data/instance_summary.csv`; the producer is
  `pilot/adjudicate_instances.py` and the row rule is still enforced (a poison instance is supported
  iff its row is `tp`). **Numbers move, because the truth moved, not the rule:** poison family
  **6/124** and the four note-adjudicated cells are unchanged, while capability goes 5/102 → **44/102**,
  channel 4/42 → **32/42**, and the all-family headline 15/268 → **82/268 (30.60%)** — the apportionment
  had inherited a class's support from its *row*, so it read 0.00 on four classes whose triggers are
  simply true (`database_write`, `file_write_delete` 0/4 → 2/4; `model_addressed` 0/21 → 19/21;
  `second_person_imperative` 4/21 → 13/21) and 3/53 → 28/53 on `secret_env_access`. The stratum figure
  becomes **78/263 (29.66%)** (the 5 control channel instances are 4 supported + 1 over-trigger, not 5
  unsupported), the cluster collapse **75/251 (29.88%)**, and two §6.2 rate cells that had been carried
  over as **1.00** are now **0.50** (`database_write`, `file_write_delete`; C-029). §5 now calls the
  apportionment a **first-pass default** with the full instance data available; §6.1 states the class
  shape (7 unsupported-dominated / 4 supported-dominated / 2 two-and-two) and the family rates; §6.2's
  reading note states that capability and channel support measure *trigger justification*, not malice.
  The **poison family remains the calibration claim** (single-digit); the all-family 30.6% is not a
  poisoning rate. Enforced by `scripts/verify_claims.py` **C15** (artifact ↔ both manuscripts, cell by
  cell, rate column included; family sums; 268 coverage) with C11/C14 retained for the historical table;
  `claims_ledger.jsonl` **C-028** (new) plus C-004/C-005/C-007/C-008/C-009/C-020/C-023/C-027 marked
  superseded and **C-029** (rate-cell correction). Provenance is tagged per instance and stated in the
  paper (**131** from the PI's own row notes, **102** poison instances decided by the PI's own row
  verdict, **35** assistant-drafted text-bound judgments pending PI sign-off — asserted in C15). Gates
  at this commit: abstract **179/179**, parity **5**, `derive_r4_numbers.py` exit 0,
  `trial_accounting --check` exit 0, `verify_claims.py` ALL CHECKS PASSED (117 checks).

- **2026-10-17: A8-r2 — full-text re-adjudication, no row-label provenance (both papers).**
  The r1 artifact was rebuilt on a provable join. The frame's `description` is a 300-character
  **excerpt** of the text the detector scanned, and `(server_name, tool_name)` is not unique in
  `data/github_tools.jsonl` (74 of the 150 sample rows sit on a key with more than one distinct
  description; `generic:unnamed` is a catch-all), so r1's "candidate that reproduces the flag set"
  heuristic resolved **20 rows to a different tool's text**. A row now joins iff exactly one stored
  text under its key starts with its excerpt: **150/150** resolved (**107** exact, **43** where the
  stored text is longer — longest **1,547** characters), **0** excerpt-only, audited row by row in
  `data/instance_join.csv`. Artifact schema is now `row_id | flag | supported | unsupported |
  evidence_quote | note`; every quote is asserted to be a substring of the row's **full** stored
  text. The 102 poison instances that r1 decided from the row verdict (`row-rule`) are adjudicated
  individually in an explicit 124-entry table in `pilot/adjudicate_instances.py`, and a poison
  verdict that conflicts with its row label is written to `data/a8_reconciliation.md` instead of
  being absorbed — the conflict set is **empty**, so the five TP row labels stand untouched.
  **Framing correction:** `cross_tool_shadowing` rows 19/33/55 are same-server false positives that
  **remain in the denominator** (1/4) and are counted unsupported; the earlier "reclassification"
  wording never meant moving instances out, and the §5/§6.2 text now says so. **No published number
  moved** (r1 == r2 verdict-for-verdict: poison **6/124**, capability **44/102**, channel **32/42**,
  all-family **82/268**, stratum **78/263**, collapse **75/251**); 15 evidence quotes changed to the
  rows' own text. Provenance is now two tags only — **132** `pi-note`, **136** `text-rule` — with the
  adjudication date (**2026-10-17**), rule version (**A8-r2**) and the AI-assistance role stated in §5;
  the paper claims no independent human reliability. `verify_claims.py` **C15** was rewritten as a
  structural check (unique pairs / no gaps, exactly one verdict per row, quotes ⊆ full text, tables
  and ledger == recomputation); `claims_ledger.jsonl` **C-030** added and **C-028** re-scoped. Gates:
  abstract **179/179**, parity **5**, `derive_r4_numbers.py` exit 0, `trial_accounting --check` exit 0.
