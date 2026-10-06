# REVISION AUDIT — adversarial-editor pass

**Scope.** Audit of `paper/main.md` (traceable record) and `paper/main_clean.md`
(authoritative publication copy), against `data/`, `pilot/`, `experiments/`, `docs/`,
`prompts/`, and the frozen artifacts. Written 2026-10-06 at commit `769b7d9`.

**Status vocabulary** (per the task's rule 4):
- **VERIFIED** — confirmed against a frozen artifact in this workspace.
- **STATED-NOT-CHECKED** — the paper asserts it; I did not independently re-derive it here.
- **MISSING** — no artifact in this workspace supports it.
- **NEEDS-HUMAN** — requires new annotation, a PI decision, or an authorized experiment.

**Canonical source and build.** Canonical publication source is `paper/main_clean.md`
(declared authoritative at `c981c9a`); `paper/main.md` is the traceable record.
The reviewer PDF is built by `paper/preview/build_preview.py` → pandoc → Chromium.
Exact commands in §"Reproduction commands" below.

---

## A. Findings that survived checking

### RA-01 — HIGH — Truncation bucket asserts a re-review outcome the artifact marks *pending*
- **Section / quote** — §6.4 flagged-non-TP taxonomy, `paper/main_clean.md:444`:
  `| Truncation artifact (trigger withdrew on full text) | 3 | rows 58, 70, 72 — flagged on the truncated 300-char view; full-text re-review confirmed benign |`
- **Still applies?** **YES.** Three separate problems in one row.
- **Supporting artifact** — `data/validation_report.md`, §"Truncation-validity check":
  > `analyze.py` writes the CSV `description` column truncated to 300 chars (`CSV_DESC_LIMIT`) while the detector scanned the **full** text from `github_tools.jsonl`. The initial labeling pass therefore showed the human a 300-char excerpt …
  1. **"flagged on the truncated 300-char view" is false.** The detector scanned full text; only the
     *human* saw the 300-char excerpt. The flag cannot have arisen on the excerpt.
  2. **"trigger withdrew on full text" is unsupported.** The recorded rationale for each of the three
     rows is excerpt-based, not full-text-based — `data/labels.jsonl`:
     row 58 `… truncated — visible portion supports these judgments.`,
     row 70 `… truncated — visible triggers benign.`,
     row 72 `… truncated — visible triggers sufficient; channel-open.`
  3. **"full-text re-review confirmed benign" contradicts the artifact.** The same report's
     re-extraction table lists rows 58, 70, 72 with re-extraction `no` and disposition
     **`pending PI pass`**. The 7 labels that did flip after full-text re-review are enumerated in
     that report as rows 3, 6, 9, 11, 16, 94, 95 — these three are not among them.
- **Proposed change** — either (a) narrow the label and cell to
  `Truncation artifact (adjudicated from the 300-char excerpt; full-text pass pending)` — count stays 3,
  no number moves; or (b) have the PI complete the full-text pass for these 3 rows and only then
  restore confirmed wording. Do **not** ship "full-text re-review confirmed benign" as is.
- **Author action** — **YES / NEEDS-HUMAN** (complete the 3-row pass, or approve the narrowed wording).

### RA-02 — HIGH — `1,484` conflated: distinct duplicated **names** vs duplicate **rows**
- **Section / quote** — §5 censuses, `paper/main_clean.md:290`:
  `**1,484/16,763** duplicate server/tool name pairs (collection report, §A.4; …)`
  versus §5 GitHub enrichment, `paper/main_clean.md:224`:
  `1,484 tool names appear in multiple rows (6,740 rows share one of these names …)`
- **Still applies?** **YES** — the two sentences define `1,484` differently.
- **Supporting artifact** — `data/collection_report.md` §5.10: `**(a)** 1,484 distinct full names`
  and `**(d)** descriptions **differ** across rows for 1,327 of the 1,484 duplicated names (89.3%)`.
  `1,484` is a count of **names**; `16,763` is a count of **rows**. Pairing them as a ratio is a
  category error, and "server/tool name pairs" is a third, unsupported reading.
- **Proposed change** — `**1,484 of the 16,763 rows carry a tool name shared with at least one other row** (6,740 rows share one of these 1,484 names; …)`.
- **Author action** — no (mechanical wording fix).

### RA-03 — HIGH — Unicode null result ships without its extraction caveat
- **Section / quote** — §5, `paper/main_clean.md:291`:
  `**0 control/format Unicode codepoints** corpus (negative; NFKC+Cc/Cf byte-diff, §A.5)`
- **Still applies?** **PARTIALLY** — the count is right; the scope caveat exists only in the artifact.
- **Supporting artifact** — `data/collection_report.md` §5.12:
  > the extractor already collapses newlines (0 of 16,763 stored descriptions contain `\n`), so the one
  > trivially-expected `Cc` class is absent **by extraction, not by absence upstream**; the finding is that
  > *nothing beyond that* … hides in the stored text.
  Without this clause the paper reads as "no hidden Unicode exists", which is stronger than the scan supports.
- **Proposed change** — append: `— a narrow null: the extractor already collapses newlines, so the one trivially-expected Cc class is absent by extraction, not by absence upstream (§A.5)`.
- **Author action** — no.

### RA-04 — MEDIUM — Taxonomy bucket name collides with the "all 100 rows carry a poison flag" claim
- **Section / quote** — `paper/main_clean.md:445` `| Capability only (no model-addressed instruction) | 3 |`
  versus `:346` `(all 100 of those rows carry at least one poison-family flag)`.
- **Still applies?** **YES as a terminology conflict; NO as a numeric conflict.**
- **Supporting artifact** — `data/labels.jsonl`: 173 rows carry ≥1 `POI:` flag, and **0 rows carry a
  `CAP:` flag without a `POI:` flag**. So `Capability only` cannot mean "no poison flag fired"; it
  describes *why the fired flags were unsupported*. The §6.4 buckets explain unsupportedness, not presence.
- **Proposed change** — rename the bucket `Capability-only reading (poison flags fired but unsupported)`
  and add one gloss above the table: *buckets describe why the detector's flags were unsupported; they are
  not claims about which classes fired.*
- **Author action** — no.

### RA-05 — MEDIUM — `15/268` described as the top-score stratum rate, but 268 contains 5 control instances
- **Section / quote** — §6.1, `paper/main_clean.md:341`:
  `the text-support rate within that purposive top-score review is what the 15/268 ratio measures`
  versus §5 `:298`: `5 of the 268 sampled flag instances (5 of the 42 channel-family instances), all unsupported`.
- **Still applies?** **PARTIALLY** — §5 discloses the 5 control instances; the §6.1 sentence over-attributes them.
- **Supporting artifact** — §5 statement above plus `data/validation_family_split.csv`
  (`channel,2,4,38,42,0.0952` → 42 channel instances, 4 supported; `ALL,…,253,268,0.0560`).
- **Supporting artifact (stratum counts now VERIFIED)** — `data/analysis_toollevel.csv` is the
  frozen 150-row sample (columns include `suspicion_score`, `rules_version`, `n_capability_flags`,
  `n_poison_flags`, `n_addressing_flags`). Measured from it: 50 rows with zero capability **and** zero
  poison flags; 100 rows with ≥1 poison flag; **5** channel flags distributed over **5** control rows,
  each exactly one **and** all `model_addressed`; **268** flag instances in the sample. Every published
  stratum name reproduces exactly.
- **Verified sub-count** — flagged-stratum denominator = 268 − 5 = **263** (channel family 42 − 5 =
  **37**, supported unchanged at 4 → `4/37`). Stratum-specific all-family rate = **15/263 = 5.70%**.
- **Proposed change** — add: `the 268-instance denominator includes the 5 channel-family instances that
  fire on the zero-flag controls (all unsupported); the flagged-stratum denominator is 263 (15/263 =
  5.70%), and the channel family is 4/37 in that stratum`.
- **Author action** — no (sub-count verified above; wording change only).

### RA-06 — LOW — "latest" is `isLatest` at crawl time, inside the crawled prefix
- **Section / quote** — `paper/main_clean.md:205`: `each server was deduplicated to its latest published version`.
- **Still applies?** **PARTIALLY** — the prefix limitation *is* disclosed two sentences later (`:208`: `a **prefix of the registry in cursor order**, not a census`).
- **Proposed change** — `deduplicated to the version the registry flags isLatest at crawl time, within the crawled cursor prefix`.
- **Author action** — no.

### RA-14 — MEDIUM — `data/labels.jsonl` is not the frozen 150-row sample; stratum math from it is unsafe
- **Section / quote** — §5 `paper/main_clean.md:296`: `150/150 rows carry a rationale note`;
  and every stratum count in §5/§6 (`5 TP / 95 flagged non-TP / 50 controls`).
- **Still applies?** **YES** as a reproducibility hazard — but the hazard is now **located**, not open.
- **Supporting artifact** — `data/labels.jsonl` contains **244** records (measured: 173 with ≥1 `POI:`
  flag, 71 with neither `CAP:` nor `POI:`), so it cannot be the 150-row sample behind the published
  strata. Deriving any stratum count from it gives a wrong answer: my own first pass produced 6 control
  channel flags over 71 "control-like" rows, versus the paper's 5 over 50.
- **Resolution (VERIFIED)** — the frozen sample is **`data/analysis_toollevel.csv`**, exactly 150 data
  rows, and the published strata reproduce from it exactly: 50 zero-capability/zero-poison rows (the
  controls), 100 rows with ≥1 poison flag, 5 control channel flags each on a distinct control row, and
  268 total flag instances. It carries no `label` column, which is why labels must be joined from
  `data/labels.jsonl` — that join is the step that must be constrained.
- **Proposed change** — state in §5 (and the manifest) that **`data/analysis_toollevel.csv` is the frozen
  150-row sample** and that `data/labels.jsonl` also carries labels for rows outside it; add an assert
  pinning the 150 row ids and recomputing the strata (50/100/5/268) before any stratum count is emitted.
- **Author action** — no.

### RA-07 — LOW — server → repository → row unit transition is implicit
- **Section / quote** — `paper/main_clean.md:222`: `yielding **16,763 tool-description rows from 4,725 repositories**`.
- **Still applies?** **PARTIALLY.** 11,288 GitHub-linked *servers* → 4,725 *repositories* → 16,763 *rows*
  are three different units; the paper never says repositories ≠ servers.
- **Proposed change** — state the mapping in one clause; **the many-to-many claim must be derived from
  `data/github_tools.jsonl` first** (servers per repository) rather than asserted.
- **Author action** — no, but needs a verified mapping statement.

---

## B. Reviewer concerns already addressed in the current copy

| Concern | Status | Evidence in the current text |
|---|---|---|
| AI-assisted labeling disclosure | **Already addressed** | `:279–281` — "Candidate rationale drafts and per-row checklists were proposed by an unversioned AI assistant … 7 verdicts revised on re-review — rows 3, 6, 9, 11, 16, 94, 95" |
| Registry-link denominators in the funnel | **Already addressed** | `:206–216` — 60,000 → 17,167 → 11,370 (66.2%) → 11,288 (65.8%) |
| Headline Wilson intervals | **Already addressed** | §6.1 intervals for 15/268, 6/124, 5/100, 5/150; assert-guarded in `pilot/derive_r4_numbers.py` |
| Why the two κ variants coincide | **Already addressed** | `:538–541` — "the second rater never returned `unclear`, so the 3-class and 2-class rows coincide" |
| κ SE / CI formula | **Already addressed** | `pilot/derive_r4_numbers.py:252–282` implements a genuine influence-function delta method (SE 0.162), not a simplified approximation; untruncated upper bound 1.08 is disclosed |
| κ recomputation | **VERIFIED here** | Independent recomputation from the packet 2×2 `[[4,1],[1,24]]`: po = 0.9333, pe = 0.7222, **κ = +0.760**; n=21 subset po = 0.9048 — both match the paper exactly |
| "covert" prose | **Already addressed** | long form "without final-answer disclosure" used; banned-phrase grep for "steered covertly" returns 0 |
| `15/268` called "precision" | **Already addressed** | `:330` — "labelled as such, not as \"precision\"" |

---

## C. Concerns that are real but blocked on a decision or new evidence

| ID | Concern | Why blocked |
|---|---|---|
| RA-08 | Reviewer asks to revise "human validated" in the **title/abstract** | The title is **locked** by `paper/CONVENTIONS.md` rule 8 (PI choice B, 2026-09-28) and `AGENTS.md`. Retitling is a PI decision; `AUTHOR_ACTION_REQUIRED.md` records it. |
| RA-09 | A second **human** annotation of a 40-row subset is required to claim human-human reliability | No second human rater exists. The pack, protocol, and scorer are built (`pilot/second_rater_pack.csv`, `docs/SECOND_RATER_PROTOCOL.md`, `docs/SECOND_RATER_SCORER.py`) but **not run**. The paper already states it "remains future work". NEEDS-HUMAN. |
| RA-10 | Matched description-ablation runs to license causal language | No ablation exists; §9 already says "no description-neutral ablation was run". `FUTURE_WORK.md` item; needs authorized live runs. NEEDS-HUMAN. |
| RA-11 | Rows 58/70/72 full-text pass (RA-01) | NEEDS-HUMAN (PI). |
| RA-12 | Independent verification of the 12 related-work entries | Metadata is recorded as verified in `docs/RELATED_WORK_MAP.md` (rev 1 PI-verified 2026-09-28; four 2026 works agent-verified 2026-09-29). I did **not** re-fetch anything — the task forbids network use. STATED-NOT-CHECKED here. |
| RA-13 | Public release location / Zenodo DOI | `paper/main_clean.md` prints `<repo-url placeholder>` and `DOI placeholder`. No release location is documented in this workspace. MISSING — must not be claimed until it exists. |

---

## D. NOT YET AUDITED (explicitly unresolved)

These reviewer concerns were **not** reached in this pass and must not be treated as cleared:

- **Phase 3.8** — whether Wilson intervals are presented with their binomial model assumption stated, and
  whether "compatibility interval" is doing work it cannot do.
- **Phase 3.9–3.12** — i.i.d. trial-independence assumptions, pooled-arm interchangeability,
  multiplicity framing, top-score selection bias direction.
- **Phase 4** — full labeling-chronology reconstruction; what the assistant saw and proposed where documented;
  whether the labeling assistant and the κ probe were related; whether the 40-row subset can contain positives.
- **Phase 5** — the FL scoring rule vs quotation/adoption; the 6 fixture rows vs 4 mechanisms;
  timeout exclusions by arm/model; the two hand-selected live control fixtures.
- **Phase 6** — OWASP identifier qualification, client/runtime authority separation wording,
  disclosure status.
- **Phase 7** — duplicate figure numbering, obsolete §5.10 cross-references, stale version banners.

---

## E. Deliverable status

| # | Deliverable | Status |
|---|---|---|
| 1 | Revised paper source + built PDF | PDF rebuilt this session: `paper/preview/paper-reviewer-copy.pdf`, 23 pages A4, 1,003,760 B. **Content revision NOT applied** — findings RA-01…RA-07 and RA-14 are specified but unapplied. |
| 2 | Number-derivation script + regression tests | **Exists**: `pilot/derive_r4_numbers.py` (assert-guarded, exit 0) + `experiments/trial_accounting.py --check` (exit 0). |
| 3 | Machine-readable claim ledger | **MISSING** — not yet built. Proposed: `data/claim_ledger.csv` with numerators/denominators already asserted in `derive_r4_numbers.py`. |
| 4 | Reviewer-response matrix | **This document**, §A–§D. |
| 5 | Reproducibility manifest | **MISSING** — proposed `REPRODUCIBILITY_MANIFEST.md`. |
| 6 | `AUTHOR_ACTION_REQUIRED.md` | **Written this session.** |
| 7 | Change summary + reproduction commands | §"Reproduction commands" below. |

---

## Reproduction commands

```bash
# deterministic gates (exit code is the assertion)
python3 pilot/derive_r4_numbers.py
python3 experiments/trial_accounting.py --check

# figures (fails loud on any value mismatch with frozen artifacts)
python3 paper/preview/make_figures.py

# reviewer package: HTML, then PDF
python3 paper/preview/build_preview.py
python3 -m http.server 8231 --bind 127.0.0.1          # from paper/preview/
chromium --headless --no-sandbox --disable-gpu --virtual-time-budget=20000 \
  --print-to-pdf="$PWD/paper/preview/paper-reviewer-copy.pdf" \
  "http://127.0.0.1:8231/paper.html"
```

---

## F. REVISION APPLIED — 2026-10-06 (baseline `769b7d9`)

Original audit above is preserved as written. This section records what was actually
implemented, with the verification that establishes it. `python3 scripts/verify_claims.py`
is the single entry point (exit 0).

| ID | Severity | Disposition | Revised location | Verification |
|---|---|---|---|---|
| RA-01 | HIGH | **FIXED** — bucket renamed `Truncation artifact (adjudicated from the 300-char excerpt)`; cell no longer claims a completed full-text review and marks rows 58/70/72 unresolved | §6.4, both files | `verify_claims.py` C9; `derive_r4_numbers.py` bucket still 3, sum 95 |
| RA-01b | HIGH | **FIXED** — keyword `withdrew` removed from the bucket rule (it encoded the unsupported causal claim); membership proven unchanged | `pilot/derive_r4_numbers.py` | `derive_r4_numbers.py` exit 0, sum 95 PASS |
| RA-02 | HIGH | **FIXED** — units and grouping key corrected to `1,484 of the 16,763 rows carry a name shared with at least one other row` | §5, both files | C9 required-string check |
| RA-03 | HIGH | **FIXED** — Unicode null re-scoped to stored text + extraction caveat | §5, both files | C9 |
| RA-04 | MEDIUM | **FIXED** — bucket renamed to `Capability-only reading (poison flags fired but unsupported)`; measurement backing: 0 rows carry CAP without POI | §6.4 both files + script | `verify_claims.py` C4 |
| RA-05 | MEDIUM | **FIXED** — stratum figures `15/263 = 5.70%` and channel `4/37` added | §6.1, both files | C5, C6 |
| RA-06 | LOW | **FIXED** — "latest published version" pinned to the registry `isLatest` field at crawl time within the prefix | §5, both files | C9 |
| RA-07 | LOW | **PARTIALLY ADDRESSED** — controls now attributed to the single-PI read; the server→repository mapping statement still needs a verified sub-count | §5, both files | C4 |
| RA-14 | MEDIUM | **RESOLVED** — frame identified as `data/analysis_toollevel.csv` (`ae1aff9f…8f77`) with the join key pinned; stratum math no longer derivable from `labels.jsonl` | audit + manifest | C1, C2, C3 |
| RA-19 | HIGH (new) | **FIXED** — κ `n = 25` row was labelled `Flagged non-TP subset` while containing 9 zero-flag control rows; relabelled as packet composition with a `fp`→non-positive mapping note | §7, both files | C10 (C-019 `CORRECTED`), C5 |
| RA-08 | HIGH | **BLOCKED** — title lock; approval needed before any retitle | — | `AUTHOR_ACTION_REQUIRED.md` A2 |
| RA-09 | HIGH | **BLOCKED** — no second human rater; pack/protocol/scorer exist and are unrun | — | A3 |
| RA-10 | HIGH | **BLOCKED** — matched description-ablation not performed; causal wording already declined by the manuscript | — | A4 |
| RA-11 | HIGH | **BLOCKED** — rows 58/70/72 full-text pass pending PI | — | A1 |
| RA-12 | MEDIUM | **STATED_NOT_CHECKED** — offline pass; related-work metadata not re-fetched | — | A7 |
| RA-13 | HIGH | **BLOCKED** — release location and DOI remain placeholders | — | A5 |

Removed by measurement rather than by edit: RA-01's causal claim, RA-02's unit error,
RA-04's literal reading, and the "structurally uninformative about recall" phrasing.
The bucket `withdrew` keyword turned out to be dead code — removing it changed no
membership, which is itself evidence it never described the data.

### RA-20 — HIGH (found this pass) — the manuscript claimed an adjudication granularity the code does not implement
- **Section / quote** — §5 *Human labeling protocol*, both files (pre-revision):
  `and (b) **per-flag-instance adjudication** — every fired (row, class) instance is separately
  judged against its class definition, which is what the per-class table in §6.2 reports.`
- **Still applies?** **YES, and it was false.** Provenance is now established end to end:
  `data/labels.jsonl` → `pilot/label_sample.py --report` → `data/validation_report.md` per-class
  table → `pilot/derive_family_split.py` → `data/validation_family_split.csv` → manuscript.
- **Evidence** — `pilot/label_sample.py` `report()` implements:
  `if lab == 'tp': for _, c in flags: tp[c] += 1` / `elif lab == 'fp': for _, c in flags: fp[c] += 1`.
  The per-class counts are therefore **apportioned from the ROW verdict**: every flag on a positive
  row counts as supported, every flag on a non-positive row as unsupported, `unclear` contributes
  nothing. No instance is ever judged on its own. Re-derived under exactly this rule, the published
  table is reproduced with **zero mismatches** (13 classes, sums 15 supported / 268 instances).
- **A false lead, recorded** — an earlier hypothesis in this pass was that the per-class rationales
  contradict the counts (16 rationales mention `secret_env_access TP-by-text` against a published 3).
  That hypothesis is **wrong**: the report never reads the rationale text, so the note language is not
  the source of the counts. Reporting it as an inconsistency would have been an error, which is why
  the producer was read before the claim was made.
- **Disposition** — **FIXED (wording made true, not the numbers).** Both files now say *per-class
  apportionment*, state the rule explicitly, and disclose the limitation: an instance is never
  separately judged once its row is decided, so a class's supported count on a positive row is
  inherited from the row verdict, and class-level support recorded in a rationale for a non-positive
  row is not counted. **No number changed.** A genuine per-instance adjudication is new human work.
- **Verification** — `scripts/verify_claims.py` C11 reproduces the published table from the row
  verdict; C9 asserts the old phrasing is absent and the new phrasing present.
- **Author action** — **YES** — `AUTHOR_ACTION_REQUIRED.md` A8.
