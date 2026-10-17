# AUTHOR_ACTION_REQUIRED

Items that **cannot** be resolved by editing text or code, because they need a human
decision, new human annotation, or an authorized experiment. Written 2026-10-06 at
commit `769b7d9`. Each item names the evidence that would close it.

---

## A1 — Complete or narrow the rows 58/70/72 full-text pass  (narrowed; upgrade optional)

`paper/main_clean.md:444` currently asserts *"flagged on the truncated 300-char view;
full-text re-review confirmed benign"*. The artifact says otherwise on all three counts:

- `data/validation_report.md` §"Truncation-validity check": the **detector scanned the full text**;
  the 300-char cap applied to what the human **saw**. So the flag was not produced on the excerpt.
- `data/labels.jsonl`, rows 58/70/72: each rationale ends `truncated — visible … benign/sufficient`,
  i.e. adjudicated from the excerpt.
- The same report's re-extraction table lists rows 58, 70, 72 as re-extraction `no`,
  disposition **`pending PI pass`**. The seven labels that flipped after full-text re-review are
  enumerated there as rows 3, 6, 9, 11, 16, 94, 95 — not these three.

**Decide:** (a) run the full-text pass for these 3 rows and record the outcome, then restore
confirmed wording; or (b) keep the count at 3 and print
*"adjudicated from the 300-char excerpt; full-text pass pending"*.
**Do not** ship the original sentence either way.

**STATUS: option (b) has been implemented.** Both manuscripts now read
`Truncation artifact (adjudicated from the 300-char excerpt)` with a cell stating that the detector
read full stored text, that these rows were adjudicated from the excerpt, and that the full-text
re-review **is still pending: unresolved, not confirmed benign**. The unsupported keyword
`withdrew` was removed from the bucket rule.

**Consequence for submission:** the claim is now honest but the bucket label is provisional. If the
PI completes the pass, the wording can be strengthened; until then the row must not be cited as
evidence that excerpt-based adjudication was checked against full text. Acceptance criterion:
either the 3 rows carry a recorded full-text outcome, or the narrowed wording stands.

## A2 — Title wording: "human validated"  (title is lock-protected)

A reviewer asks that "human validated" in the title/abstract be changed to reflect that the
reference labels are single-PI judgments with unversioned AI assistance. The title is **locked**
by `paper/CONVENTIONS.md` rule 8 (PI choice B, 2026-09-28) and by `AGENTS.md`, which forbids
retitling.

**Decide:** keep the locked title (and rely on the abstract/method disclosure, which is already
explicit at `main_clean.md` §5 `Human labeling protocol`), or authorize a title change, which
requires a CONVENTIONS amendment first.

**STATUS: no change made — the lock was respected.** This revision intentionally leaves the title
untouched and edits the manuscript body in place; no revision copy or patch was required, because
the only locked element is the title. **Exact approval needed to promote a retitle:** the PI must
amend `paper/CONVENTIONS.md` rule 8 (the 2026-09-28 "title locked" entry) and record the new title
there before any source is changed.

## A3 — Second human annotation for a human-human reliability claim

No second human rater exists. The plug-and-play pack is built and blind
(`pilot/second_rater_pack.csv`, 40 rows, sha256 `af2718…4b77a`; protocol in
`docs/SECOND_RATER_PROTOCOL.md`; scorer in `docs/SECOND_RATER_SCORER.py`). The paper correctly
says this "remains future work".

**Note before commissioning it:** the pack is seeded as 32 top-score + 8 control rows, so it is
TP-enriched by construction. Agreement on it does **not** estimate population agreement, and a
*random* 40-row subset of the 150 would contain only ~1–2 positives. If a population-agreement
claim is wanted, the sampling design must be chosen deliberately and stated up front.
**Nothing here may be reported until a human actually completes the packet.**

## A4 — Matched description-ablation runs (causal language)

§9 already concedes *"no description-neutral ablation was run"*. Any causal wording stronger than
"behavior consistent with the instruction under this mocked harness" requires authorized live runs
with matched ablation arms (description present vs replaced vs neutral). Parked in `FUTURE_WORK.md`.

## A5 — Release location and DOI

`paper/main_clean.md` prints `<repo-url placeholder>` and `DOI placeholder`. No release location is
documented in this workspace. A Zenodo DOI and a public repository URL must exist before any claim
of public release is printed. **Do not claim release until it is real.**

## A6 — Disclosure status

Verify what, if anything, has actually been filed or notified before the paper states it.
No disclosure record is present in this workspace, so any status sentence must be written from the
PI's own records, not inferred.

## A7 — Related-work metadata re-verification (optional)

`docs/RELATED_WORK_MAP.md` records the seven pre-existing arXiv IDs as PI-verified 2026-09-28 and
the four 2026 works as agent-verified 2026-09-29 (three arXiv abstract pages, Crossref +
Semantic Scholar for the IEEE TSE DOI, MCPZoo full text). This pass could not re-fetch anything
(network use was out of scope). If a re-verification is wanted before submission, it must be run
deliberately and the result recorded in the map.

---

## Author action NOT required

Mechanical fixes specified in `REVISION_AUDIT.md` §A and ready to apply without a decision:
RA-02 (`1,484` semantics), RA-03 (Unicode caveat), RA-04 (bucket name), RA-06 (`isLatest` meaning),
RA-14 (name the frozen 150-row sample — now identified as `data/analysis_toollevel.csv`, resolution
verified by reproducing 50/100/5/268 from it).

RA-05's sub-count is now **verified**: the frozen sample gives 268 total flag instances with 5 control
channel flags, so the flagged-stratum denominator is 263 (78/263 = 29.66% on the instance verdicts;
channel family in-stratum 28/37) and the wording has been applied directly.

RA-07 still needs one verified sub-count: the server→repository mapping, derivable from
`data/github_tools.jsonl`.

RA-01 is blocked on A1 above.

## A8 — per-instance adjudication (CLOSED 2026-10-14; full-text re-run 2026-10-17)

**Affected claims:** the per-class text-support figures in §6.2, the family split, and every
denominator derived from them (poison 6/124, capability 44/102, channel 32/42, all-family 82/268).

**Why this is a human dependency.** `pilot/label_sample.py --report` computes per-class counts by
**apportioning the row verdict** — every flag on a positive row counts as supported, every flag on a
non-positive row as unsupported. There is no per-instance judgment in the pipeline, so the
manuscript's former claim of per-instance adjudication was false. The wording is now corrected and
the limitation disclosed; the *numbers* were not changed, and must not be.

**What only a human can add.** A genuine per-instance pass over the 268 sampled instances, judging
each `(row, class)` pair against that class's definition independently of the row verdict. The
rationales already contain class-level evidence the current rule discards — e.g. 16 rationales mark
`secret_env_access` as supported by text while the published count is 3 — so a real pass would
plausibly **move** the per-class numbers in both directions. That is a new annotation task, not an
edit.

**CLOSED (2026-10-14; re-run on full text 2026-10-17, rule version A8-r2).** All **268**
fired flag instances carry an independent verdict — supported / unsupported — made against the
**full stored text** rather than the 300-character excerpt the detector scanned, and recorded with a
verbatim quote in **`data/INSTANCE_VERDICTS.csv`** (`row_id | flag | supported | unsupported |
evidence_quote | note`), produced by `pilot/adjudicate_instances.py`, which also writes the join
audit `data/instance_join.csv` and the reconciliation record `data/a8_reconciliation.md`.

**The join is the provable one.** A row's excerpt resolves to exactly one stored description that
starts with it: **150/150** rows — **107** exact, **43** where the stored text is longer than the
excerpt (longest **1,547** characters), **none** excerpt-only. This is load-bearing, not
housekeeping: `(server_name, tool_name)` is **not unique** in the corpus (74 of the 150 sample rows
sit on a key carrying more than one distinct description, and `generic:unnamed` is a catch-all), and
the r1 join heuristic resolved **20** rows to a *different tool's* text. Those rows now quote their
own text. No verdict changed.

**No verdict is inherited from a row label.** r1 decided 102 poison instances from the row verdict
(provenance `row-rule`). r2 adjudicates **all 124** poison instances individually against the text,
through an explicit table in the producer, and logs a conflict with the row label instead of bending
to it. The conflict set is **empty** — the pass agrees with the five TP row labels instance by
instance. Rows 19, 33 and 55 are same-server false-positive instances that **remain in the
`cross_tool_shadowing` denominator** (1 supported / 3 unsupported = 0.25) and are counted
unsupported; nothing is moved out of that denominator.

**Capability audit (2026-10-17, rule A8-r3).** The r2 capability grounds had drifted into the poison test for seven instances ("no directive to the reader" cannot justify a capability verdict). Every one of the 27 capability instances with no PI note typing was re-read on the capability criterion — does the text declare that the tool does this? — and four verdicts moved: rows 0 and 23 now declare outbound egress (a messaging tool; a remote conversion job), while rows 35 and 95 only list *required* secrets or name environment variables, which is not access to them. Net family totals are unchanged; `network_egress` is 13/21 and `secret_env_access` 26/53, so the class-shape sentence is now 8 unsupported-dominated / 3 supported-dominated / 2 two-and-two. Ledger C-031.

**What the pass found.** The published numbers are unchanged from the 2026-10-14 pass — that pass
was already measured on the text, and r2 changed provenance and evidence, not verdicts: poison
**6/124 (4.84%)**, `cross_tool_shadowing` 1/4, `stealth_concealment` 0/9, capability **44/102**,
channel **32/42**, all-family **82/268 (30.60%)**, top-score stratum **78/263 (29.66%)**, duplicate-name
collapse **75/251 (29.88%)**; two §6.2 rate cells corrected to **0.50** (`database_write`,
`file_write_delete`). The apportionment's move (capability 5/102 → 44/102, channel 4/42 → 32/42,
`secret_env_access` 3/53 → 26/53, `file_read_sensitive` 1/2 → 0/2 on row 94's note) is recorded in
C-028 and `data/validation_family_split.csv`, which stays as the historical first-pass figure.

**Recorded and enforced.** `claims_ledger.jsonl` **C-028** (the instance artifact and the recomputed
figures), **C-029** (rate-cell correction), **C-030** (full-text re-adjudication, no row-label
provenance), with C-004/C-005/C-007/C-008/C-009/C-020/C-023/C-027 marked superseded. `scripts/
verify_claims.py` **C15** is structural and now checks: 268 unique `(row_id, flag)` pairs with no
duplicates and no gaps against the frozen frame; exactly one of supported/unsupported per row; every
evidence quote a substring of that row's **full** stored text; both manuscripts' per-class cells,
rate column, family sums and headline equal to a direct recomputation; and the ledger's headline
record equal to it. C11/C14 still reproduce the historical apportioned table.

**Human residual (not closed by this pass).** The verdicts are text-bound and evidence-linked, but
provenance is mixed and tagged per instance: **132** typed from the PI's own frozen row notes
(`pi-note`) and **136** assistant-drafted, text-bound adjudications (`text-rule`, each with a full-text
quote). The PI should walk the 136 `text-rule` rows and accept or override them — that review changes
no published number unless a verdict flips. Adjudication date **2026-10-17**, rule version **A8-r2**.
The AI-assisted pass corrects instance-level data only; it is **not** an independent human
reliability measurement and must not be reported as one.

**Acceptance criterion:** met — an instance-level annotation artifact exists, every verdict is judged
against the full stored text, and the per-class table is regenerated from it, with the old apportioned
figures preserved as historical (`data/validation_family_split.csv`, still reproduced by C11).

**Blocks submission?** No. The residual is a sign-off pass, not a measurement gap. The calibration
claim is unchanged in substance: the **poison family is 6/124 = 4.84%**, and the all-family rate is a
trigger-justification rate across three families, not a poisoning prevalence — §6.2 says so explicitly.

## A9 — the FL "exec-priming" live result is a text-propagation count, not execution adoption

**Affected claims:** the abstract (`Exec-priming text surfaced in 9/9 trials, unadopted`), §8
Finding 1, the §8 table cell `FL 3/3 [B]`, the §9 Figure-2 step-3 note and the model-variance
paragraph, and the pooled WF+FL+DP descriptive figure.

**What changed (wording only).** `experiments/harness.py` `judge()` implements criterion `[B]` as
`"TESTKEY-DEMO-INSTALL" in final` — a test that fires whenever the guide's command text reaches the
model's *final answer*. All nine valid FL trials relay the guide (which is the task's benign request),
so all nine fire. Re-deriving the sub-branches from the stored transcripts gives marker-in-final
**9/9**, execution-style fence **4/9**, execution-verb **1/9** (on a *declining* sentence); **no trial
expresses intent to execute in the model's own voice (0/9)**. The manuscript now says so. The frozen
ledger and the table cell (`FL 3/3 [B]`) are **unchanged**; criterion `[B]` is described as a
marker-presence test. Verified by `scripts/verify_claims.py` C13.

**PI decision — APPLIED 2026-10-06 (option C: recast FL as a task-conflated null arm).** All four
items are implemented and committed as Phase-set A9:
1. FL removed from the pooled ASR — recomputed **WF+DP = 14/18** (glm 5/6, deepseek 6/6,
   gemini 3/6), assert-guarded in `pilot/derive_r4_numbers.py` and `experiments/summarize.py`; the
   frozen `FL 9/9 [B]` row is unchanged in the ledger and re-checked by `scripts/verify_claims.py`
   (C8). The §8 table row now reads "FL — exec-priming, **task-conflated** (B)†" with the footnote
   "outcome-conflated with task completion — steering not tested; 0/9 execution intent".
2. Abstract, §8, §9 now state the live matrix tests **two of the four** mechanisms (DP, WF);
   exec-priming joins the untested ledger. Finding 1 is reframed as a design lesson — instruction
   surfacing 9/9 vs execution intent 0/9, all three models refusing or deferring, with the deepseek
   refusal quoted once.
3. Figure 3 (`paper/preview/figs/fig-3-trials.png`): the FL row is labeled "task-conflated (see
   text)" and FL is dropped from the pooled-CI panel.
4. Limitations (x) added: criterion [B] == task completion; the arm cannot test steering; a
   redesigned non-task-required marker + re-run is parked in `FUTURE_WORK.md`.

**Remaining sub-action (PI).** Whether to reframe the arm in `docs/BRIEF04_PROTOCOL.md` as a
propagation/utility measurement for a future run rather than an attack arm — low priority; the
manuscript already reports it as a design lesson.

**Acceptance criterion:** **MET** — the pooled-ASR sentence states FL is excluded, and no sentence
reads `FL 9/9` as "models executed tool-supplied shell text".

**Blocks submission?** No — resolved (option C applied).
