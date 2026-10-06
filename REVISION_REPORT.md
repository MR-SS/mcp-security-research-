# REVISION_REPORT

Revision executed 2026-10-06 on branch `pilot`, from baseline commit `769b7d9`.
Deliverable paths and a resolution table follow; every claim below names the check
that establishes it.

---

## 1. What was verified before editing (Phase 1)

**Manuscript generation chain.** `paper/main.md` (traceable record) → `paper/main_clean.md`
(authoritative publication copy, hand-maintained since `c981c9a`) → `paper/preview/paper.html`
via `paper/preview/build_preview.py` (pandoc, one pass) → `paper/preview/paper-reviewer-copy.pdf`
via headless Chromium. The two Markdown files are edited independently; there is no longer an
automated clean-copy builder (retired at `c981c9a`, documented in `paper/CONVENTIONS.md`).

**Sample identity — resolved and cryptographically pinned.** The frozen 150-row frame is
`data/analysis_toollevel.csv`, sha256
`ae1aff9fdccda9c88d77fbc605eb99d5327326e3e7931040ca1ade5b20e18f77` — i.e. the `ae1aff9f…8f77`
checksum the manuscript already cites. `data/labels.jsonl` is **not** the frame: it holds 244
records over the same 150 row ids, as an append-only trail (74 ids carry more than one record;
the last record per id is the current label).

**Join key established, and the unsafe key shown to be unsafe.** `labels.jsonl.row_id` is the
positional index into the frame: **244/244** records satisfy
`analysis_toollevel.csv[row_id].name == labels.name`. Joining on `name` is provably unsafe — the
frame has 150 rows but only **142 distinct names**.

**Strata reproduced from the correct join.** 100 top-score rows (≥1 poison-family flag) and 50
zero-capability/zero-poison controls; top-score labels 95 non-positive + 5 positive; combined
**268** flag instances, top-score stratum **263**; **5** control channel-family instances, each on
a distinct control row; **0** rows carry a capability flag without a poison flag.

**Frozen-input hashes recorded** before any edit and re-checked after (unchanged) — see
`reproducibility_manifest.json`.

---

## 2. Corrections applied to the manuscript (Phase 2)

Both `paper/main.md` and `paper/main_clean.md` were revised, each in its own voice (the record
keeps repo paths; the publication copy does not). No frozen label, count, detector version, or
sample membership was altered.

| ID | Correction | Where |
|---|---|---|
| RA-01 | Truncation-artifact bucket **renamed and de-claimed**: was `Truncation artifact (trigger withdrew on full text) … flagged on the truncated 300-char view; full-text re-review confirmed benign`. Now `Truncation artifact (adjudicated from the 300-char excerpt)` with cell text stating the detector read full stored text, that these rows were adjudicated from the excerpt, and that their full-text re-review is **still pending: unresolved, not confirmed benign**. | §6.4 (both files) |
| RA-01b | The bucket's keyword rule dropped the token `withdrew`, which encoded the unsupported causal claim. Membership is unchanged (still 3) — proven by the bucket-sum assert still reading 95. | `pilot/derive_r4_numbers.py` |
| RA-02 | `**1,484/16,763** duplicate server/tool name pairs` → `**1,484 of the 16,763 rows carry a server::tool name shared with at least one other row**` (6,740 rows share one of these 1,484 names). Grouping key and unit now explicit. | §5 (both files) |
| RA-03 | Unicode null re-scoped: `0 control/format Unicode codepoints corpus` → **in the stored text**, plus `— a scanner- and representation-scoped null: the extractor already collapses newlines, so the one trivially-expected Cc class is absent by extraction, not by absence upstream`. | §5 (both files) |
| RA-04 | Bucket `Capability only (no model-addressed instruction)` → `Capability-only reading (poison flags fired but unsupported)`. Confirmed by measurement: **0** rows carry a capability flag without a poison flag, so the old name could not be literal. Renamed in the script too. | §6.4 (both files) + script |
| RA-05 | Added the **verified** stratum figure: `263 of those 268 instances fall in the top-score stratum, the other 5 being channel-family instances that fire on the zero-flag controls (all unsupported), so the stratum-specific rate is 15/263 = 5.70%`. | §6.1 (both files) |
| RA-19 | κ table row `Flagged non-TP subset (25)` → `Packet non-positive subset (9 of 25 are zero-flag controls)`, with a footnote stating it is a packet-composition statistic rather than a flagged-stratum rate, and that the legacy code `fp` means "not a positive" and is applied to controls too. | §7 (both files) |
| RA-06 | Recall sentence replaced. Was `Detector recall is unmeasured by design; the zero-flag controls are structurally uninformative about it.` Now states what the design did and did not assess: controls are detector-negative **by construction**, no content standard beyond the PI's read was applied, and detector-negative rows outside the sample were never examined — so no false-negative rate and no recall estimate are reported. Applied at both occurrences, including §7. | §5 and §7 (both files) |
| RA-07 | Control rows described as `the detector's negative calls` **attributed to the same single-PI read**, rather than bare `true negatives`. | §5 (both files) |

---

## 3. Deliverables created (Phase 3)

| Path | What it is |
|---|---|
| `claims_ledger.jsonl` | 22 records, one per quantitative or consequential claim: id, location, exact claim, unit, numerator/denominator, scope/sampling frame, source paths, locator, derivation command, result, status, limitation. Statuses: VERIFIED 15, CORRECTED 3, QUALIFIED 4. |
| `reproducibility_manifest.json` | 11 hashed frozen inputs with roles, 12 derived artifacts, sample identity and join key, seeds, software versions, commands, and **7 explicit unknowns**. Does not hash itself. |
| `scripts/verify_claims.py` | Offline verification entry point: C1 frozen hashes, C2 sample identity, C3 join integrity, C4 strata, C5 instance counts, C6 family splits, C7 κ recomputation, C8 trial accounting, C9 manuscript wording, C10 ledger shape. |
| `REVISION_AUDIT.md` | Extended with a §F applied-revision record (original audit preserved). |
| `AUTHOR_ACTION_REQUIRED.md` | Updated: A1 narrowed, title-lock approval recorded. |
| `REVISION_REPORT.md` | This file. |

No revision copy was needed: only the **title** is locked (CONVENTIONS rule 8), and the title was
not touched. Content edits were made in place in both canonical sources.

---

## 4. Verification (Phase 4)

| Command | Exit |
|---|---|
| `python3 pilot/derive_r4_numbers.py` | **0** |
| `python3 experiments/trial_accounting.py --check` | **0** |
| `python3 scripts/verify_claims.py` | **0** (all 10 check groups pass) |
| `python3 paper/preview/build_preview.py` | **0** — 802,955 B, 3 figures, 12 references |
| `chromium --headless … --print-to-pdf` | **0** — 23 pages, A4 |

**Frozen inputs unchanged** — the pinned hashes in `verify_claims.py` (C1) re-verify, including
`data/analysis_toollevel.csv` and `data/validation_family_split.csv`.

**Build inspection.** Page count 23, page size A4 (594.96 × 841.92 pt), file size 1,006,050 B.
Extracted text is searchable (10,521 words) and contains every corrected string; the withdrawn
claim `full-text re-review confirmed benign` appears **0** times. Zero soft-hyphenation line breaks
were detected, so the CSS `hyphens: auto` setting is not corrupting searchability.

**Visual inspection is partial and is not claimed as complete.** Page geometry, page count, and
searchability were checked programmatically; the funnel figure was visually reviewed at the prior
revision. The revised text blocks and table breaks were **not** re-screenshotted in this pass.

**"assert-verified" labels audited.** The three figure captions carry `(assert-verified)`. Each is
backed by value asserts that actually run in `paper/preview/make_figures.py` against
`data/collection_report.md`/`candidate_rate_scan.csv`/`validation_family_split.csv` (figure 1),
`data/validation_report.md` (figure R1), and `data/live_tests/trials_ledger.jsonl` (figure R2).
No false `assert-verified` label was found.

---

## 5. Recomputed headline numbers and changes in interpretation

| Quantity | Before | After | Basis |
|---|---|---|---|
| All-family text-support, combined | 15/268 = 5.60% | unchanged | family split |
| **All-family text-support, top-score stratum** | not reported | **15/263 = 5.70%** | 268 − 5 control channel instances |
| Channel family, top-score stratum | not reported | **4/37** | 42 − 5 |
| Duplicate-name quantity | `1,484/16,763` pairs | **1,484 names spanning 6,740 rows** | collection report §5.10 |
| Unicode null | corpus-wide | **stored-text-scoped**, extraction-caveated | §5.12 |
| Truncation bucket (rows 58/70/72) | "confirmed benign" | **unresolved; full-text pass pending** | validation report + labels |
| κ n=25 variant | "Flagged non-TP subset" | **packet non-positive subset, 9 of 25 are controls** | packet map vs frame |
| Recall | "unmeasured by design" | **not assessed by this design; no FN rate reported** | design review |

**Interpretation changes that matter.** (i) The truncation bucket was the only place where the
manuscript asserted a completed human review the artifacts do not support; it no longer does, and
that dependency is now visible where the result is interpreted. (ii) The κ n=25 row was presented
as a flagged-stratum statistic while containing 9 control rows; it is now labelled as packet
composition. (iii) The stratum-specific rate `15/263` is now reported alongside `15/268`, so the
headline is no longer a combined-sample number wearing a top-score label.

---

## 6. What remains blocked (Phase 5)

`AUTHOR_ACTION_REQUIRED.md` holds the human dependencies. Submission remains **partially blocked**:
A1 (rows 58/70/72 full-text pass) and A3 (human-human reliability, if claimed) require a human;
A5 (release location / DOI placeholders) and A6 (disclosure status) are unverified from records in
this workspace. The paper is **not** described as submission-ready: scripts passing is not evidence
of scientific completeness, and the manuscript still prints placeholder URLs and a placeholder DOI.

## 7. Reproduction

```bash
python3 pilot/derive_r4_numbers.py                                    # exit 0
python3 experiments/trial_accounting.py --check                        # exit 0
python3 scripts/verify_claims.py                                      # exit 0
python3 paper/preview/make_figures.py                                 # exit 0
python3 paper/preview/build_preview.py                                # exit 0
(cd paper/preview && python3 -m http.server 8231 --bind 127.0.0.1 &)
chromium --headless --no-sandbox --disable-gpu --virtual-time-budget=25000 \
  --print-to-pdf="$PWD/paper/preview/paper-reviewer-copy.pdf" \
  "http://127.0.0.1:8231/paper.html"
```
