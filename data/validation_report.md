# Brief 03 — Validation Report

> Generated 2026-09-26T11:17:19.588413+00:00 from `/home/sajjad/Paper/mcp-security-research/mcp-security-research/data/labels.jsonl` over `/home/sajjad/Paper/mcp-security-research/mcp-security-research/data/analysis_toollevel.csv`.

## Summary

| Metric | Value |
|---|---|
| Total rows in sample | 150 |
| Labeled rows | 20 |
| Unlabeled rows | 130 |
| Skip | 0 |
| TP rows | 1 |
| FP rows | 19 |
| Unclear rows | 0 |
| False-negative (zero-flag) rows | 0 |
| Flag instances on TP rows | 2 |
| Flag instances on FP rows | 56 |

*Rows count rows. Flag instances count (row, class) pairs across those rows: one row can carry several classes, so flag instances on FP rows exceed FP rows. Precision below uses the per-class instance counts.*


## Per-class precision (TP / (TP+FP), unclear excluded)

| Class | TP | FP | Precision |
|---|---|---|---|
| `cross_tool_shadowing` | 1 | 1 | 0.50 |
| `exfiltration_language` | 0 | 12 | 0.00 |
| `imperative_to_model` | 1 | 19 | 0.05 |
| `model_addressed` | 0 | 3 | 0.00 |
| `network_egress` | 0 | 2 | 0.00 |
| `second_person_imperative` | 0 | 6 | 0.00 |
| `secret_env_access` | 0 | 4 | 0.00 |
| `shell_execution` | 0 | 2 | 0.00 |
| `stealth_concealment` | 0 | 7 | 0.00 |

## Unclear rate

Unclear / all labeled: 0/20 = 0.00%

## False-negative rate (zero-flag rows only)

FN / zero-flag rows: 0/50 = 0.00%

## Truncation-validity check (added 2026-09-26)

`analyze.py` writes the CSV `description` column truncated to 300 chars (`CSV_DESC_LIMIT`; lines 176 and 212), while the detector scanned the **full** text from `github_tools.jsonl`. The initial labeling pass therefore showed the human a 300-char excerpt, so labels on capped rows rest on less evidence than the detector saw — 43/150 sample rows sit exactly on the cap.

* Cap-affected labeled rows: **12 of 20** labeled (60%).
* Of these, 0 carry a `u` label and are covered by `--review-unclear`: none.
* The remaining **12** are the `--review-truncated` queue: 0, 1, 2, 3, 4, 5, 6, 9, 10, 12, 16, 18.
* Re-review is done on full text in `github_tools.jsonl`; every replacement is archived to `labels.jsonl.superseded` and logged to `labels.audit.jsonl`.
* **Labels flipped after full-text re-review: 5** — 12 of 12 queued rows re-reviewed so far; 5 row(s) were decided through `--verdict` (written-up answers to `--review-unclear`, which the queue cannot carry because it excludes `u` rows).

* Flips: row 3 `u` → `fp`, row 6 `u` → `fp`, row 9 `u` → `fp`, row 11 `u` → `fp`, row 16 `u` → `fp`.


| row_id | label now | excerpt | full | hidden | source_file | re-reviewed | outcome |
|---|---|---|---|---|---|---|---|
| 0 | `fp` | 300 | 858 | +558 | `src/mcp.ts` | yes | confirmed fp |
| 1 | `fp` | 300 | 478 | +178 | `integrations/open-webui/cernion-process-intake-tool-server.js` | yes | confirmed fp |
| 2 | `fp` | 300 | 328 | +28 | `src/server.ts` | yes | confirmed fp |
| 3 | `fp` | 300 | 431 | +131 | `mcp/package.json` | yes | FLIPPED u -> fp |
| 4 | `fp` | 300 | 529 | +229 | `lhm.plugin.json` | yes | confirmed fp |
| 5 | `fp` | 300 | 522 | +222 | `src/server.ts` | yes | confirmed fp |
| 6 | `fp` | 300 | 470 | +170 | `src/tools.js` | yes | FLIPPED u -> fp |
| 9 | `fp` | 300 | 508 | +208 | `src/tools/createTaskLink.ts` | yes | FLIPPED u -> fp |
| 10 | `fp` | 300 | 611 | +311 | `src/tools/schedule_post.ts` | yes | confirmed fp |
| 12 | `tp` | 300 | 316 | +16 | `src/tools/rules.ts` | yes | confirmed tp |
| 16 | `fp` | 300 | 1079 | +779 | `src/tools/script.ts` | yes | FLIPPED u -> fp |
| 18 | `fp` | 300 | 995 | +695 | `server.js` | yes | confirmed fp |


## FP-reason taxonomy

One entry per FP ROW; the first matching bucket wins (marketing/product language → benign legitimate use → bare URL/link → no note given → first 60 chars of the note).

| Reason | Count |
|---|---|
| benign legitimate use | 4 |
| marketing/product language | 3 |
| fp under strict rule: covert-channel CAPABILITY is real by d | 1 |
| fp confirmed on full text; all triggers negated ('never exec | 1 |
| fp; imperative REAL but DEFENSIVE (anti-injection guard: 'do | 1 |
| fp confirmed on full text; exfil=sending is function via use | 1 |
| bare URL/link | 1 |
| fp; both regex noise: 'never' = Chrome limitation statement  | 1 |
| fp after full-text; exfil neutralized ('pure formatter, no n | 1 |
| fp; 'never overwritten silently' = transparency GUARANTEE (a | 1 |
| fp; same template-boilerplate as crop_image ('never overwrit | 1 |
| no note given | 1 |
| fp after full-text; dry_run/approval-prompt/mutation-log are | 1 |
| fp; shadowing FP: 'Start here, then use the other tools for  | 1 |

## TP examples by class

### `cross_tool_shadowing` (1 examples)

- `com.webflow/mcp::generic:unnamed` — note: first genuine TP; cross_tool_shadowing pattern fully present from OFFICIAL vendor ('ALWAYS CALL THIS TOOL FIRST BEFORE CALLING ANY OTHER TOOLS', all-caps + repeated, universal ANY-OTHER-TOOLS claim = priority capture); benign intent (guidelines-first) but structurally identical to the attack pattern; intent: benign-vendor; hero candidate for Discussion
### `imperative_to_model` (1 examples)

- `com.webflow/mcp::generic:unnamed` — note: first genuine TP; cross_tool_shadowing pattern fully present from OFFICIAL vendor ('ALWAYS CALL THIS TOOL FIRST BEFORE CALLING ANY OTHER TOOLS', all-caps + repeated, universal ANY-OTHER-TOOLS claim = priority capture); benign intent (guidelines-first) but structurally identical to the attack pattern; intent: benign-vendor; hero candidate for Discussion

## Detector status

Detector rules (v2) are **frozen**. Any regex fix proposals derived from
these FP patterns must be filed as a **separate proposal diff** —
never auto-applied to `pilot/analyze.py`.
