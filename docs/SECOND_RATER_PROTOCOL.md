# Second-rater protocol — blinded 40-row re-annotation (future work)

> Status: **specified and frozen; not yet run.** A second blinded human annotation of a
> random 40-row subset is specified here (protocol, rulebook, and scoring script
> included) and remains future work — this document makes no claim about when it will run.
> Cited by `paper/main.md` / `paper/main_clean.md` §5 and Appendix A.

## 1. What is being annotated

| Item | Value |
|---|---|
| Pack file | `pilot/second_rater_pack.csv` |
| Rows | 40 (`blind_id` R01–R40, fixed presentation order) |
| Columns | `blind_id`, `stored_text`, `classes_fired` |
| sha256 | `af27187869f749f69e95080b806ae4e5bd43ec771ca4226caece9b1d4124b77a` |
| Composition | 32 rows drawn from the 100 top-score rows + 8 rows drawn from the 50 zero-flag controls |
| Sampling recipe | Python `random.Random(2026)`; each pool is sorted by `row_id` first (`row_id` is the tie-break), `rng.sample(top, 32)` then `rng.sample(controls, 8)`, then one `rng.shuffle` of the combined 40 to fix the blind order |
| `stored_text` | the **full** stored description from `data/github_tools.jsonl` (not the 300-char CSV excerpt) |
| `classes_fired` | the frozen v2 detector's fired classes for that row (`CAP:` / `POI:` / `ADR:` groups; `none` = zero-flag control). Provided as context only — see §3 |
| Hidden from the rater | every PI verdict, rationale note, `row_id`, stratum membership, and the blind→row map |

`row_id` is the 0-based ordinal of `data/analysis_toollevel.csv` (row order = descending
`suspicion_score`, controls last). The blind→`row_id` map is not shipped with the pack;
`docs/SECOND_RATER_SCORER.py` re-derives it from the recipe above and verifies the pack
sha256 before scoring.

## 2. Instructions for the rater

1. **Blind labeling.** Work from `pilot/second_rater_pack.csv` alone. Do not open
   `data/labels.jsonl`, the row notes, the validation report, the κ packet, or any other
   study artifact. If you are an LLM assistant, do not use the study's own prompt files.
2. **Fixed row order.** Label R01 → R40 in the order given. Do not reorder, skip, or
   re-sample rows. (If you split the work across sessions, resume at the next `blind_id`.)
3. **Allowed labels.** Exactly one of `tp`, `fp`, `unclear` per row:
   - `tp` — at least one poison-family (`POI:`) flag is genuinely supported by the text;
   - `fp` — every `POI:` flag is unsupported (benign or within-purpose text);
   - `unclear` — structurally impossible to judge from the stored text (write both
     readings in the rationale). Zero-flag rows with no `POI:` flags to judge are `fp`.
4. **Free-text rationale is mandatory** for every row: one or two sentences naming the
   sentence(s) you relied on and why they are (not) an added behavioral instruction.
5. **Master rule.** Separate the tool's *declared function* from an *added behavioral
   instruction to the model*. Within-purpose constraints, negated assurances and
   defensive guards are benign; universal ordering, execution relocation, hide-from-user
   directives and off-purpose custody funnels are `tp`. Full decision tree and worked
   exemplars: `docs/LABELING_RULEBOOK.md`.
6. **Time budget.** Plan for **~60 minutes** for 40 rows (about 90 seconds per row).
   There is no benefit in racing; if you run over, stop at a row boundary and record where
   you stopped rather than rushing the remaining rows.
7. **Output format.** Return one CSV (or TSV) with the header
   `blind_id,label,rationale`, one row per `blind_id`, e.g.
   `R01,fp,"product URL, no added instruction"`. Do not add columns.

## 3. Reading `classes_fired`

The column is the detector's own output, shown so the annotation can be read against the
candidates it is meant to judge. It is **not** evidence: the study's standing rule is that
heuristics produce candidates, never verdicts. Judge the text first; use the flag list only
to know which classes you must adjudicate. A row with `classes_fired = none` carries no
capability, poison, or channel flags (control stratum).

## 4. Confidentiality note

The pack is **pre-publication research data** under CC BY 4.0 at release, but is
unpublished until the paper is out. Keep the file and your answers private: do not
redistribute the pack, do not paste it into public services beyond what is needed to
perform the annotation, and do not attempt to look up the source repositories (the
annotation is text-bound by design). Return answers to the PI only.

## 5. Scoring

`docs/SECOND_RATER_SCORER.py` (stdlib only) joins the answers to the PI's frozen verdicts
and prints human–human Cohen's κ with a delta-method 95% interval, the observed agreement,
and the full disagreement set with `row_id`s:

```bash
python3 docs/SECOND_RATER_SCORER.py second_rater_answers.csv
```

Note the scorer reports one dependence caveat on its face: duplicate-name rows (the same
`server::tool` registered more than once — e.g. rows 94/95 in the full sample, and rows
79/82 inside this pack) are not independent items, so κ is a descriptive consistency
figure for this pack, not an independent-trials estimate.
