# Mode B inter-rater reliability — Cohen's kappa (phase 2)

> Generated 2026-09-28T08:48:49Z by `pilot/kappa_report.py` (stdlib only). Mode B hard rule: the blind rater never modifies `data/labels.jsonl`.
> Inputs: `kappa_sample_map.json` (sha256 41fa24a5bd99d4af…), `labels.jsonl` (sha256 be587210928db242…), `labels_llm.jsonl` (sha256 891103e4b27992a5…), seed 20260927 · base_commit 183334e.

## All 30 items — 3-class (tp / fp / unclear)

- observed agreement (po): **0.9333** (93.3%)
- expected agreement by chance (pe): **0.7222** (72.2%)
- Cohen's kappa: **+0.760**

| human \ llm | tp | fp | unclear | total |
|---|---|---|---|---|
| **tp** | 4 | 1 | 0 | 5 |
| **fp** | 1 | 24 | 0 | 25 |
| **unclear** | 0 | 0 | 0 | 0 |
| **total** | 5 | 25 | 0 | 30 |

## All 30 items — 2-class (tp / not-tp)

- observed agreement: **0.9333** (93.3%) · expected: **0.7222** · kappa: **+0.760**

| human \ llm | tp | not-tp | total |
|---|---|---|---|
| **tp** | 4 | 1 | 5 |
| **not-tp** | 1 | 24 | 25 |

## POI-flag-carrying items only (n = 21 of 30)

- 3-class: po **0.9048** · pe **0.6372** · kappa **+0.738**
- 2-class (tp / not-tp): po **0.9048** · pe **0.6372** · kappa **+0.738**
- excluded: 9 item(s) with zero poison flags (capability/addressing-only or zero-flag controls)

## Per-stratum agreement

| stratum | n | agree | agreement |
|---|---|---|---|
| tp stratum (all 5) | 5 | 4 | 80.0% |
| fp stratum (25) | 25 | 24 | 96.0% |

## Disagreements (2)

| item | row_id | human | llm rater |
|---|---|---|---|
| Q05 | 35 | tp | fp |
| Q26 | 20 | fp | tp |

*Interpretation convention (Landis & Koch): <0 poor · 0.01–0.20 slight · 0.21–0.40 fair · 0.41–0.60 moderate · 0.61–0.80 substantial · 0.81–1.00 almost perfect. The blind rater's opinions never modify `data/labels.jsonl` (Mode B hard rule).*

*Errata 2026-09-28: the Q26/row 20 disagreement row is `io.github.basehub-ai/forums::generic:unnamed` (basehub forums); earlier draft text called it 'flaim' — app.flaim/mcp is sample row 52, which is not in the packet.*

