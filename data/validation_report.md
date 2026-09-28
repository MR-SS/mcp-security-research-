# Brief 03 — Validation Report

> Generated 2026-09-28T07:32:27.582959+00:00 from `/home/sajjad/Paper/mcp-security-research/data/labels.jsonl` over `/home/sajjad/Paper/mcp-security-research/data/analysis_toollevel.csv`.

## Summary

| Metric | Value |
|---|---|
| Total rows in sample | 150 |
| Labeled rows | 150 |
| Unlabeled rows | 0 |
| Skip | 0 |
| TP rows | 5 |
| FP rows | 145 |
| Unclear rows | 0 |
| False-negative (zero-flag) rows | 0 |
| Flag instances on TP rows | 15 |
| Flag instances on FP rows | 253 |

*Rows count rows. Flag instances count (row, class) pairs across those rows: one row can carry several classes, so flag instances on FP rows exceed FP rows. Precision below uses the per-class instance counts.*


## Per-class precision (TP / (TP+FP), unclear excluded)

| Class | TP | FP | Precision |
|---|---|---|---|
| `cross_tool_shadowing` | 1 | 3 | 0.25 |
| `database_write` | 0 | 4 | 0.00 |
| `exfiltration_language` | 0 | 34 | 0.00 |
| `fake_system_role` | 0 | 1 | 0.00 |
| `file_read_sensitive` | 1 | 1 | 0.50 |
| `file_write_delete` | 0 | 4 | 0.00 |
| `imperative_to_model` | 5 | 71 | 0.07 |
| `model_addressed` | 0 | 21 | 0.00 |
| `network_egress` | 0 | 21 | 0.00 |
| `second_person_imperative` | 4 | 17 | 0.19 |
| `secret_env_access` | 3 | 50 | 0.06 |
| `shell_execution` | 1 | 17 | 0.06 |
| `stealth_concealment` | 0 | 9 | 0.00 |

## Unclear rate

Unclear / all labeled: 0/150 = 0.00%

## False-negative rate (zero-flag rows only)

FN / zero-flag rows: 0/50 = 0.00%

## Truncation-validity check (added 2026-09-26)

`analyze.py` writes the CSV `description` column truncated to 300 chars (`CSV_DESC_LIMIT`; lines 176 and 212), while the detector scanned the **full** text from `github_tools.jsonl`. The initial labeling pass therefore showed the human a 300-char excerpt, so labels on capped rows rest on less evidence than the detector saw — 43/150 sample rows sit exactly on the cap.

* Cap-affected labeled rows: **43 of 150** labeled (29%).
* Of these, 0 carry a `u` label and are covered by `--review-unclear`: none.
* The remaining **43** are the `--review-truncated` queue: 0, 1, 2, 3, 4, 5, 6, 9, 10, 12, 16, 18, 20, 22, 23, 26, 27, 28, 29, 30, 32, 33, 35, 38, 52, 58, 60, 70, 71, 72, 78, 79, 80, 81, 82, 83, 84, 85, 95, 96, 97, 98, 99.
* Re-review is done on full text in `github_tools.jsonl`; every replacement is archived to `labels.jsonl.superseded` and logged to `labels.audit.jsonl`.
* **Labels flipped after full-text re-review: 7** — 13 of 43 queued rows re-reviewed so far; 7 row(s) were decided through `--verdict` (written-up answers to `--review-unclear`, which the queue cannot carry because it excludes `u` rows).

* Flips: row 3 `u` → `fp`, row 6 `u` → `fp`, row 9 `u` → `fp`, row 11 `u` → `fp`, row 16 `u` → `fp`, row 94 `fp` → `tp`, row 95 `fp` → `tp`.


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
| 52 | `fp` | 300 | 1187 | +887 | `workers/fantasy-mcp/src/mcp/tools.ts` | no | pending PI pass |
| 58 | `fp` | 300 | 676 | +376 | `packages/commerce-mcp/src/Tools.ts` | no | pending PI pass |
| 60 | `tp` | 300 | 432 | +132 | `mcp-server.js` | no | pending PI pass |
| 70 | `fp` | 300 | 518 | +218 | `src/tools/mod.rs` | no | pending PI pass |
| 71 | `fp` | 300 | 381 | +81 | `server.mjs` | no | pending PI pass |
| 72 | `fp` | 300 | 1263 | +963 | `src/index.ts` | no | pending PI pass |
| 78 | `fp` | 300 | 796 | +496 | `src/tools/composite.ts` | no | pending PI pass |
| 79 | `fp` | 300 | 661 | +361 | `src/tools/indicatorsTools.ts` | no | pending PI pass |
| 80 | `fp` | 300 | 662 | +362 | `src/tools/indicatorsTools.ts` | no | pending PI pass |
| 81 | `fp` | 300 | 1120 | +820 | `src/tools/selectionsTools.ts` | no | pending PI pass |
| 82 | `fp` | 300 | 1183 | +883 | `src/tools/marketContextTools.ts` | no | pending PI pass |
| 83 | `fp` | 300 | 1547 | +1247 | `src/tools/marketContextTools.ts` | no | pending PI pass |
| 84 | `fp` | 300 | 394 | +94 | `src/tools.ts` | no | pending PI pass |
| 85 | `fp` | 300 | 674 | +374 | `src/core/tools.ts` | no | pending PI pass |
| 95 | `tp` | 300 | 353 | +53 | `packages/mcp-server/src/index.ts` | yes | FLIPPED fp -> tp |
| 96 | `fp` | 300 | 402 | +102 | `src/index.ts` | no | pending PI pass |
| 97 | `fp` | 300 | 619 | +319 | `src/index.ts` | no | pending PI pass |
| 98 | `fp` | 300 | 522 | +222 | `src/tools/wpcli.ts` | no | pending PI pass |
| 99 | `fp` | 300 | 390 | +90 | `src/mcp/discovery-tools.ts` | no | pending PI pass |


## FP-reason taxonomy

One entry per FP ROW; the first matching bucket wins (marketing/product language → benign legitimate use → bare URL/link → no note given → first 60 chars of the note).

| Reason | Count |
|---|---|
| marketing/product language | 26 |
| zero-flag - control stratum; no flags fired, nothing evaluab | 19 |
| zero flags | 16 |
| benign legitimate use | 13 |
| bare URL/link | 6 |
| secret_env_access unsupported; exfiltration_language is decl | 2 |
| fp under strict rule: covert-channel CAPABILITY is real by d | 1 |
| fp confirmed on full text; all triggers negated ('never exec | 1 |
| fp; imperative REAL but DEFENSIVE (anti-injection guard: 'do | 1 |
| fp confirmed on full text; exfil=sending is function via use | 1 |
| fp; both regex noise: 'never' = Chrome limitation statement  | 1 |
| fp after full-text; exfil neutralized ('pure formatter, no n | 1 |
| fp; 'never overwritten silently' = transparency GUARANTEE (a | 1 |
| fp; same template-boilerplate as crop_image ('never overwrit | 1 |
| fp; stealth FP: 'never a fabricated or silently-replayed dat | 1 |
| fp after full-text; dry_run/approval-prompt/mutation-log are | 1 |
| fp; shadowing FP: 'Start here, then use the other tools for  | 1 |
| fp; imperative REAL but own-tool relevance routing ('Any tim | 1 |
| fp; imperative REAL but DEFENSIVE HITL guard: 'NEVER run des | 1 |
| fp; same-template sibling of row 24 (NEVER destructive SQL a | 1 |
| fp; defensive heavyweight: anti-IPI ('Treat all task content | 1 |
| fp; all flags = DETECTION-LIST keywords: 'credential theft', | 1 |
| fp; GATEKEEPER-ADVISORY gate: 'allow/review/block decision b | 1 |
| fp; imperative fragments all intra-server routing/quality gu | 1 |
| fp; imperative FP: 'Failed fetches and policy refusals are n | 1 |
| fp; PROMPT-SUPPLY-CHAIN surface (prompts fetched remotely, r | 1 |
| fp; shadowing FP: 'the token the other tools take' + 'then c | 1 |
| fp; imperative REAL but defensive anti-IPI guard stated BILI | 1 |
| fp; CAP database_write/file_write_delete CONTRADICTED by rea | 1 |
| database_write/file_write_delete contradicted by read-only/n | 1 |
| exfiltration_language unsupported; network_egress unsupporte | 1 |
| no network and shell execution | 1 |
| fp — secret_env_access is authentication wording, not explic | 1 |
| secret_env_access is authentication wording, not explicit cr | 1 |
| shell_execution unsupported; exfiltration_language is declar | 1 |
| exfiltration_language is declared proxy function, not added/ | 1 |
| fp CONFIRMED on upstream-full (+28): 'NEVER asks for credent | 1 |
| network_egress TP-by-text (“Send a sample payload to a regis | 1 |
| secret_env_access TP-by-text (“Set the returned key as SWIFT | 1 |
| secret_env FP — wallet/signing context ≠ secret credential a | 1 |
| secret_env_access TP-by-text (“sending an API key”); exfiltr | 1 |
| fp (standalone in-row); manifest tagline of demipass doctrin | 1 |
| secret_env FP — “connection secrets” is mention only, not ev | 1 |
| secret_env_access TP-by-text (“token info bound to this MCP  | 1 |
| network_egress TP-by-text (“Fetch ranked Lunoo results”); im | 1 |
| secret_env_access TP-by-text (“Supply your keys in providerK | 1 |
| network_egress TP-by-text (“optional media upload”); exfiltr | 1 |
| shell_execution FP — no shell/command execution stated; impe | 1 |
| secret_env_access FP — secret-pattern detection ≠ secret acc | 1 |
| secret_env_access FP — “tokens” = billing/usage units, not c | 1 |
| network_egress TP-by-text (“Send an Instagram DM”); exfiltra | 1 |
| network_egress TP-by-text (“publish, schedule, ... social me | 1 |
| secret_env_access FP — “Never store secrets” is a prohibitio | 1 |
| secret_env_access TP-by-text ('your API token'); imperative  | 1 |
| secret_env_access TP-by-text (“Kamy API key” + Authorization | 1 |
| fp CONFIRMED on upstream-full (+668); self-service onboardin | 1 |
| file_write_delete TP-by-text (“written to output_path”); imp | 1 |
| secret_env_access FP — “secrets” appears in a prohibition, n | 1 |
| zero-flag — ordinary Watchgoose check listing/health-check w | 1 |
| zero-flag — simple stock-name/code input description; no poi | 1 |
| zero-flag — ordinary food-name resolution capability; no mod | 1 |
| zero-flag — ordinary time-tracking query/use guidance; “Use  | 1 |
| zero-flag — ordinary AI fashion-design functionality descrip | 1 |
| zero-flag — ordinary expense-data access description; no mod | 1 |
| model_addressed TP-by-text (“AI agents”); channel-only, no m | 1 |
| model_addressed TP-by-text (“the model”); defensive security | 1 |
| fp CONFIRMED on upstream-full (+468, was zero-flag control r | 1 |
| model_addressed TP-by-text (“Built for AI agents”); channel- | 1 |
| model_addressed only; channel measurement (channel-open), no | 1 |

## TP examples by class

### `cross_tool_shadowing` (1 examples)

- `com.webflow/mcp::generic:unnamed` — note: first genuine TP; cross_tool_shadowing pattern fully present from OFFICIAL vendor ('ALWAYS CALL THIS TOOL FIRST BEFORE CALLING ANY OTHER TOOLS', all-caps + repeated, universal ANY-OTHER-TOOLS claim = priority capture); benign intent (guidelines-first) but structurally identical to the attack pattern; intent: benign-vendor; hero candidate for Discussion
### `file_read_sensitive` (1 examples)

- `dev.mcpfinder/server::generic:unnamed` — note: tp (4th genuine); CONDITIONAL priority capture: 'Call this first whenever you do not already have a trustworthy tool' = webflow mechanism in conditional form (FIRST + whenever, scope = whole ecosystem); attack anatomy: becomes the ecosystem gateway, funnels agents to attacker-recommended servers (supply-chain vector); benign-vendor intent but attack-shaped; same-server pair w/ row 95, count mechanism once; cross_tool_shadowing regex did NOT fire on 'first/whenever' phrasing (recall gap); row previously self-noted 'imperative_to_model TP' (divergence fixed); Brief-04 candidate
### `imperative_to_model` (3 examples)

- `com.webflow/mcp::generic:unnamed` — note: first genuine TP; cross_tool_shadowing pattern fully present from OFFICIAL vendor ('ALWAYS CALL THIS TOOL FIRST BEFORE CALLING ANY OTHER TOOLS', all-caps + repeated, universal ANY-OTHER-TOOLS claim = priority capture); benign intent (guidelines-first) but structurally identical to the attack pattern; intent: benign-vendor; hero candidate for Discussion
- `io.github.armanas/froglet::generic:unnamed` — note: tp (2nd genuine); imperative REAL: instructs agent to EXECUTE tool-supplied shell commands in its own shell ('get_install_guide returns canonical shell commands — execute those through your own shell, not the Froglet runtime') = ASI05-shaped exec-priming; benign intent but verbatim what a hostile server would plant; intent: benign-vendor. Also anti-hallucination rule 'Do not invent actions'. CAP shell_execution FP (tool returns commands, no own exec) — detector missed exec-priming; FUTURE_WORK: new class exec_priming; ADR TP ('your own shell'). HERO #2 + Brief-04 live test
- `com.dustforge/demipass::demipass_store` — note: secret_env TP-by-text ('credential (API key, password, token, SSH key)' enumerated); imperative TP ('deposit it here immediately' = universal credential funnel to this service — predatory-hygiene siphon, betrayal-of-purpose exfil semantics); second_person TP (you + imperative); family echo = row 61, count once; DETECTOR RECALL GAP: POI exfiltration_language silent because text says deposit/store not send/leak (paraphrase hole, cf. rows 94/95) — Methods: regex classes miss paraphrases; Brief-04 candidate; truncated — visible triggers sufficient.
### `second_person_imperative` (3 examples)

- `io.github.armanas/froglet::generic:unnamed` — note: tp (2nd genuine); imperative REAL: instructs agent to EXECUTE tool-supplied shell commands in its own shell ('get_install_guide returns canonical shell commands — execute those through your own shell, not the Froglet runtime') = ASI05-shaped exec-priming; benign intent but verbatim what a hostile server would plant; intent: benign-vendor. Also anti-hallucination rule 'Do not invent actions'. CAP shell_execution FP (tool returns commands, no own exec) — detector missed exec-priming; FUTURE_WORK: new class exec_priming; ADR TP ('your own shell'). HERO #2 + Brief-04 live test
- `com.dustforge/demipass::demipass_store` — note: secret_env TP-by-text ('credential (API key, password, token, SSH key)' enumerated); imperative TP ('deposit it here immediately' = universal credential funnel to this service — predatory-hygiene siphon, betrayal-of-purpose exfil semantics); second_person TP (you + imperative); family echo = row 61, count once; DETECTOR RECALL GAP: POI exfiltration_language silent because text says deposit/store not send/leak (paraphrase hole, cf. rows 94/95) — Methods: regex classes miss paraphrases; Brief-04 candidate; truncated — visible triggers sufficient.
- `dev.mcpfinder/server::generic:unnamed` — note: tp (4th genuine); CONDITIONAL priority capture: 'Call this first whenever you do not already have a trustworthy tool' = webflow mechanism in conditional form (FIRST + whenever, scope = whole ecosystem); attack anatomy: becomes the ecosystem gateway, funnels agents to attacker-recommended servers (supply-chain vector); benign-vendor intent but attack-shaped; same-server pair w/ row 95, count mechanism once; cross_tool_shadowing regex did NOT fire on 'first/whenever' phrasing (recall gap); row previously self-noted 'imperative_to_model TP' (divergence fixed); Brief-04 candidate
### `secret_env_access` (3 examples)

- `io.github.armanas/froglet::generic:unnamed` — note: tp (2nd genuine); imperative REAL: instructs agent to EXECUTE tool-supplied shell commands in its own shell ('get_install_guide returns canonical shell commands — execute those through your own shell, not the Froglet runtime') = ASI05-shaped exec-priming; benign intent but verbatim what a hostile server would plant; intent: benign-vendor. Also anti-hallucination rule 'Do not invent actions'. CAP shell_execution FP (tool returns commands, no own exec) — detector missed exec-priming; FUTURE_WORK: new class exec_priming; ADR TP ('your own shell'). HERO #2 + Brief-04 live test
- `com.dustforge/demipass::demipass_store` — note: secret_env TP-by-text ('credential (API key, password, token, SSH key)' enumerated); imperative TP ('deposit it here immediately' = universal credential funnel to this service — predatory-hygiene siphon, betrayal-of-purpose exfil semantics); second_person TP (you + imperative); family echo = row 61, count once; DETECTOR RECALL GAP: POI exfiltration_language silent because text says deposit/store not send/leak (paraphrase hole, cf. rows 94/95) — Methods: regex classes miss paraphrases; Brief-04 candidate; truncated — visible triggers sufficient.
- `dev.mcpfinder/server::generic:unnamed` — note: tp (same gateway-capture mechanism as row 94): 'Always call this before...' imposes FIRST-call priority whenever a capability is missing; detector recall gap: flagged only as imperative_to_model; same-server pair, count once; truncated 53 chars, trigger visible; benign-vendor intent, attack-shaped
### `shell_execution` (1 examples)

- `io.github.armanas/froglet::generic:unnamed` — note: tp (2nd genuine); imperative REAL: instructs agent to EXECUTE tool-supplied shell commands in its own shell ('get_install_guide returns canonical shell commands — execute those through your own shell, not the Froglet runtime') = ASI05-shaped exec-priming; benign intent but verbatim what a hostile server would plant; intent: benign-vendor. Also anti-hallucination rule 'Do not invent actions'. CAP shell_execution FP (tool returns commands, no own exec) — detector missed exec-priming; FUTURE_WORK: new class exec_priming; ADR TP ('your own shell'). HERO #2 + Brief-04 live test

## Detector status

Detector rules (v2) are **frozen**. Any regex fix proposals derived from
these FP patterns must be filed as a **separate proposal diff** —
never auto-applied to `pilot/analyze.py`.

## Reliability (Mode B inter-rater)

*Added 2026-09-28. NOTE: `label_sample.py --report` regenerates this file wholesale;
re-run `python3 pilot/kappa_report.py` and re-append if that ever happens after a
label mutation. The full machine-readable report lives in `data/kappa_report.md`.*

Per `prompts/06-second-opinion.md` Mode B, a second rater relabeled the 30-item blind
packet (`data/kappa_packet.md`, commit `7b52792`: all 5 tp rows + 25 fp rows,
`random.seed(20260927)`, seed-shuffled, texts served FULL) **with no access to the human
labels, the sample map, or any prior note**. **Rater provenance:** ChatGPT web UI (OpenAI,
default consumer model, not version-pinned), accessed 2026-09-28, blind rating of full-text
items; verdicts stored verbatim in `data/labels_llm.jsonl` (provenance sidecar
`data/labels_llm.provenance.txt`). Agreement is computed by `pilot/kappa_report.py`
(stdlib only) against the human labels; per the Mode B hard rule the rater's opinions
**never modify** `data/labels.jsonl`.

**Result (n = 30):** observed agreement po = **0.9333** (28/30); expected chance agreement
pe = **0.7222**; **Cohen's kappa = +0.760** (Landis & Koch: *substantial*, 0.61–0.80 band).
The 2-class (tp / not-tp) variant is numerically identical here (po 0.9333, pe 0.7222,
kappa +0.760) because the two disagreements are one tp→fp miss and one fp→tp miss, leaving
the marginals unchanged. **POI-flag-carrying items only (n = 21 of 30;** the 9 items with
zero poison flags excluded**):** po = 0.9048, pe = 0.6372, kappa = **+0.738**.

Contingency matrix (3-class; human rows × LLM-rater columns):

| human \ llm | tp | fp | unclear | total |
|---|---|---|---|---|
| **tp** | 4 | 1 | 0 | 5 |
| **fp** | 1 | 24 | 0 | 25 |
| **unclear** | 0 | 0 | 0 | 0 |
| **total** | 5 | 25 | 0 | 30 |

Per-stratum agreement: tp stratum **4/5 (80.0%)** · fp stratum **24/25 (96.0%)**.

**Disagreements (2), resolved to sample row_ids via `data/kappa_sample_map.json`:**

| item | row_id | human | llm rater | reading |
|---|---|---|---|---|
| Q05 | 35 | tp | fp | froglet exec-priming: the rater read "execute those through your own shell" as intra-toolkit workflow constraint; the human verdict treats the same sentence as an added behavioral rule (ASI05-shaped exec-priming) — the hardest item in the packet, and the one whose tp rests on the §4d gray-zone logic |
| Q26 | 20 | fp | tp | flaim relevance routing: the rater counted "Any time the user references another post, you should use this" as a model-directed behavioral rule; the human verdict scopes it to the server's own forum posts (no cross-tool effect) — the §3 imperative rule's scope question, which the packet's rules leave to judgment |

Both disagreements are rule-interpretation calls on §3's "behavioral rule" boundary, not
perception errors — which is the useful finding for Methods: the reliability of the labeling
category is substantial, and the residual disagreement concentrates exactly where the rubric
leaves scope judgment open (the same items flagged as gray-zone in the TP/FP analyses above).
