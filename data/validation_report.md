# Brief 03 — Validation Report

> Generated 2026-09-27T11:49:06.843809+00:00 from `/home/sajjad/Paper/mcp-security-research/data/labels.jsonl` over `/home/sajjad/Paper/mcp-security-research/data/analysis_toollevel.csv`.

## Summary

| Metric | Value |
|---|---|
| Total rows in sample | 150 |
| Labeled rows | 50 |
| Unlabeled rows | 100 |
| Skip | 0 |
| TP rows | 2 |
| FP rows | 48 |
| Unclear rows | 0 |
| False-negative (zero-flag) rows | 0 |
| Flag instances on TP rows | 6 |
| Flag instances on FP rows | 137 |

*Rows count rows. Flag instances count (row, class) pairs across those rows: one row can carry several classes, so flag instances on FP rows exceed FP rows. Precision below uses the per-class instance counts.*


## Per-class precision (TP / (TP+FP), unclear excluded)

| Class | TP | FP | Precision |
|---|---|---|---|
| `cross_tool_shadowing` | 1 | 2 | 0.33 |
| `database_write` | 0 | 4 | 0.00 |
| `exfiltration_language` | 0 | 24 | 0.00 |
| `fake_system_role` | 0 | 1 | 0.00 |
| `file_write_delete` | 0 | 2 | 0.00 |
| `imperative_to_model` | 2 | 35 | 0.05 |
| `model_addressed` | 0 | 6 | 0.00 |
| `network_egress` | 0 | 11 | 0.00 |
| `second_person_imperative` | 1 | 10 | 0.09 |
| `secret_env_access` | 1 | 20 | 0.05 |
| `shell_execution` | 1 | 13 | 0.07 |
| `stealth_concealment` | 0 | 9 | 0.00 |

## Unclear rate

Unclear / all labeled: 0/50 = 0.00%

## False-negative rate (zero-flag rows only)

FN / zero-flag rows: 0/50 = 0.00%

## Truncation-validity check (added 2026-09-26)

`analyze.py` writes the CSV `description` column truncated to 300 chars (`CSV_DESC_LIMIT`; lines 176 and 212), while the detector scanned the **full** text from `github_tools.jsonl`. The initial labeling pass therefore showed the human a 300-char excerpt, so labels on capped rows rest on less evidence than the detector saw — 43/150 sample rows sit exactly on the cap.

* Cap-affected labeled rows: **24 of 50** labeled (48%).
* Of these, 0 carry a `u` label and are covered by `--review-unclear`: none.
* The remaining **24** are the `--review-truncated` queue: 0, 1, 2, 3, 4, 5, 6, 9, 10, 12, 16, 18, 20, 22, 23, 26, 27, 28, 29, 30, 32, 33, 35, 38.
* Re-review is done on full text in `github_tools.jsonl`; every replacement is archived to `labels.jsonl.superseded` and logged to `labels.audit.jsonl`.
* **Labels flipped after full-text re-review: 5** — 12 of 24 queued rows re-reviewed so far; 5 row(s) were decided through `--verdict` (written-up answers to `--review-unclear`, which the queue cannot carry because it excludes `u` rows).

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
| 20 | `fp` | 300 | 325 | +25 | `apps/web/agent/tools/index.ts` | no | pending PI pass |
| 22 | `fp` | 300 | 459 | +159 | `src/server.ts` | no | pending PI pass |
| 23 | `fp` | 300 | 635 | +335 | `packages/mcp/src/server.mjs` | no | pending PI pass |
| 26 | `fp` | 300 | 495 | +195 | `src/coordination-workspace-agent-tools.ts` | no | pending PI pass |
| 27 | `fp` | 300 | 452 | +152 | `src/app/api/mcp/route.ts` | no | pending PI pass |
| 28 | `fp` | 300 | 1270 | +970 | `packages/mcp/src/tools.ts` | no | pending PI pass |
| 29 | `fp` | 300 | 710 | +410 | `src/mcp/discovery-tools.ts` | no | pending PI pass |
| 30 | `fp` | 300 | 1396 | +1096 | `src/index.js` | no | pending PI pass |
| 32 | `fp` | 300 | 321 | +21 | `packages/mcp/src/index.ts` | no | pending PI pass |
| 33 | `fp` | 300 | 501 | +201 | `src/mcp/server.ts` | no | pending PI pass |
| 35 | `tp` | 300 | 1325 | +1025 | `integrations/mcp/froglet/lib/tools.js` | no | pending PI pass |
| 38 | `fp` | 300 | 1156 | +856 | `src/index.ts` | no | pending PI pass |


## FP-reason taxonomy

One entry per FP ROW; the first matching bucket wins (marketing/product language → benign legitimate use → bare URL/link → no note given → first 60 chars of the note).

| Reason | Count |
|---|---|
| no note given | 14 |
| marketing/product language | 7 |
| benign legitimate use | 4 |
| bare URL/link | 3 |
| fp under strict rule: covert-channel CAPABILITY is real by d | 1 |
| fp confirmed on full text; all triggers negated ('never exec | 1 |
| fp; imperative REAL but DEFENSIVE (anti-injection guard: 'do | 1 |
| fp confirmed on full text; exfil=sending is function via use | 1 |
| fp; both regex noise: 'never' = Chrome limitation statement  | 1 |
| fp after full-text; exfil neutralized ('pure formatter, no n | 1 |
| fp; 'never overwritten silently' = transparency GUARANTEE (a | 1 |
| fp; same template-boilerplate as crop_image ('never overwrit | 1 |
| fp after full-text; dry_run/approval-prompt/mutation-log are | 1 |
| fp; shadowing FP: 'Start here, then use the other tools for  | 1 |
| fp; shadowing FP: 'the token the other tools take' + 'then c | 1 |
| fp; imperative REAL but defensive anti-IPI guard stated BILI | 1 |
| database_write/file_write_delete contradicted by read-only/n | 1 |
| exfiltration_language unsupported; network_egress unsupporte | 1 |
| no network and shell execution | 1 |
| secret_env_access unsupported; exfiltration_language is decl | 1 |
| fp — secret_env_access is authentication wording, not explic | 1 |
| secret_env_access is authentication wording, not explicit cr | 1 |
| shell_execution unsupported; exfiltration_language is declar | 1 |
| exfiltration_language is declared proxy function, not added/ | 1 |

## TP examples by class

### `cross_tool_shadowing` (1 examples)

- `com.webflow/mcp::generic:unnamed` — note: first genuine TP; cross_tool_shadowing pattern fully present from OFFICIAL vendor ('ALWAYS CALL THIS TOOL FIRST BEFORE CALLING ANY OTHER TOOLS', all-caps + repeated, universal ANY-OTHER-TOOLS claim = priority capture); benign intent (guidelines-first) but structurally identical to the attack pattern; intent: benign-vendor; hero candidate for Discussion
### `imperative_to_model` (2 examples)

- `com.webflow/mcp::generic:unnamed` — note: first genuine TP; cross_tool_shadowing pattern fully present from OFFICIAL vendor ('ALWAYS CALL THIS TOOL FIRST BEFORE CALLING ANY OTHER TOOLS', all-caps + repeated, universal ANY-OTHER-TOOLS claim = priority capture); benign intent (guidelines-first) but structurally identical to the attack pattern; intent: benign-vendor; hero candidate for Discussion
- `io.github.armanas/froglet::generic:unnamed` — note: tp (2nd genuine); imperative REAL: instructs agent to EXECUTE tool-supplied shell commands in its own shell ('get_install_guide returns canonical shell commands — execute those through your own shell, not the Froglet runtime') = ASI05-shaped exec-priming; benign intent but verbatim what a hostile server would plant; intent: benign-vendor. Also anti-hallucination rule 'Do not invent actions'. CAP shell_execution FP (tool returns commands, no own exec) — detector missed exec-priming; FUTURE_WORK: new class exec_priming; ADR TP ('your own shell'). HERO #2 + Brief-04 live test
### `second_person_imperative` (1 examples)

- `io.github.armanas/froglet::generic:unnamed` — note: tp (2nd genuine); imperative REAL: instructs agent to EXECUTE tool-supplied shell commands in its own shell ('get_install_guide returns canonical shell commands — execute those through your own shell, not the Froglet runtime') = ASI05-shaped exec-priming; benign intent but verbatim what a hostile server would plant; intent: benign-vendor. Also anti-hallucination rule 'Do not invent actions'. CAP shell_execution FP (tool returns commands, no own exec) — detector missed exec-priming; FUTURE_WORK: new class exec_priming; ADR TP ('your own shell'). HERO #2 + Brief-04 live test
### `secret_env_access` (1 examples)

- `io.github.armanas/froglet::generic:unnamed` — note: tp (2nd genuine); imperative REAL: instructs agent to EXECUTE tool-supplied shell commands in its own shell ('get_install_guide returns canonical shell commands — execute those through your own shell, not the Froglet runtime') = ASI05-shaped exec-priming; benign intent but verbatim what a hostile server would plant; intent: benign-vendor. Also anti-hallucination rule 'Do not invent actions'. CAP shell_execution FP (tool returns commands, no own exec) — detector missed exec-priming; FUTURE_WORK: new class exec_priming; ADR TP ('your own shell'). HERO #2 + Brief-04 live test
### `shell_execution` (1 examples)

- `io.github.armanas/froglet::generic:unnamed` — note: tp (2nd genuine); imperative REAL: instructs agent to EXECUTE tool-supplied shell commands in its own shell ('get_install_guide returns canonical shell commands — execute those through your own shell, not the Froglet runtime') = ASI05-shaped exec-priming; benign intent but verbatim what a hostile server would plant; intent: benign-vendor. Also anti-hallucination rule 'Do not invent actions'. CAP shell_execution FP (tool returns commands, no own exec) — detector missed exec-priming; FUTURE_WORK: new class exec_priming; ADR TP ('your own shell'). HERO #2 + Brief-04 live test

## Detector status

Detector rules (v2) are **frozen**. Any regex fix proposals derived from
these FP patterns must be filed as a **separate proposal diff** —
never auto-applied to `pilot/analyze.py`.
