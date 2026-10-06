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
channel flags, so the flagged-stratum denominator is 263 (15/263 = 5.70%; channel family 4/37) and the
wording can be applied directly.

RA-07 still needs one verified sub-count: the server→repository mapping, derivable from
`data/github_tools.jsonl`.

RA-01 is blocked on A1 above.

## A8 — A true per-instance adjudication does not exist

**Affected claims:** the per-class text-support figures in §6.2, the family split, and every
denominator derived from them (poison 6/124, capability 5/102, channel 4/42, all-family 15/268).

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

**Acceptance criterion:** either an instance-level annotation artifact exists and the per-class table
is regenerated from it (with the old figures preserved as historical), or the manuscript continues to
describe the row-verdict apportionment and carries the disclosed limitation.

**Blocks submission?** Not by itself — the corrected wording is defensible and the headline 15/268 is
unaffected. It does block any claim of per-class instance-level precision, and it should be resolved
before a reviewer with the code in hand finds it.
