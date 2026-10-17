# Calibrating the Alarms

## A Purposive-Sample, Text-Bound Audit of Poisoning Detectors on 16,763 MCP Tool Descriptions

**Sajjad Rahim Nouri**
Islamic Azad University, Ramsar Branch

Working paper — reviewer copy v1.1 · 2026-10-06

---

## Abstract

In the Model Context Protocol (MCP), tool descriptions are surfaced to the model as server-authored text, varying by client. A frozen detector with 18 checks (13 fired in the validation sample) emits candidates over 16,763 registry-grounded tool descriptions (4,725 repos): 24.6% of rows receive at least one flag, 4.2% a poison-family flag. Human audits of a purposive validation sample — 100 top-score rows plus 50 controls — yield 5 poison-positive rows and 95 flagged-benign rows: an all-family text-support rate of 15/268 (5.6%); poison-family 6/124 (4.8%). Four attack-shaped mechanisms occur in benign product descriptions — priority capture (unconditional; conditional gateway), exec-priming, a credential funnel — all intent-neutral, from established vendors. In a fully mocked harness (three model versions, 51 valid trials), the credential funnel transferred a synthetic credential to the tool in 9/9 trials, 8/9 without final-answer disclosure; the untested-priority arm was conflated with task completion (0/9 execution intent). Priority capture split the panel (6/9). Two of four mechanisms are supported live. Results are sample-bounded and harness-specific; a calibration, not a prevalence estimate. Code, data, labels, and protocols are released.

---

## 1. Introduction

In the Model Context Protocol (MCP), each tool's natural-language description is surfaced to the model as server-authored text alongside the system prompt and the user's message, in ways that vary by client implementation. The model has no structural way to distinguish a tool's description from an operator's instruction. This makes the description channel an instruction surface: a server can embed behavioral steering in ordinary prose without executing code or exploiting a network vulnerability.

Prior measurements of this surface report large counts of detector flags. But a flag is not itself evidence that a description contains a supported malicious instruction. Heuristic checks match benign text, capability-related checks fire on tools that legitimately access networks or shells, and addressing-related checks trigger on descriptions that simply use second-person language. Without human validation of what the text actually supports, a census of flags is indistinguishable from a census of pattern-matching accidents.

This study calibrates a frozen heuristic detector against human judgments on a registry-grounded population. We collected 16,763 tool descriptions from 4,725 GitHub repositories linked to the official MCP Registry (17,167 unique servers in a cursor-limited prefix crawl), ran a frozen 18-check detector over the full corpus, and manually adjudicated a purposive validation sample of 150 rows. We then conducted 54 fully mocked live trials across three deployed model versions to test whether the mechanisms found in the text steer behavior under this harness.

The study addresses three questions:

**RQ1.** What candidate rate does the frozen detector produce over the corpus, and what fraction of flagged rows survive strict text-bound human review?

**RQ2.** When a check fires, how often is the flag supported by the visible text — per class, not just overall?

**RQ3.** Which concrete steering mechanisms exist in the wild, and can a regex-family baseline detect them at all?

The results show that flagging and validation must be reported separately. Over the corpus, 24.6% of rows trigger at least one check. In the validation sample, the poison-family text-support rate is 4.8% (6/124) and the all-family rate is 5.6% (15/268). Five corpus rows contain supported poison instructions spanning four distinct steering mechanisms — every one embedded in otherwise benign product copy from an established vendor, with no attacker established. Mocked experiments show the credential-funnel and priority-capture mechanisms influence model behavior under this harness (credential transfer without final-answer disclosure in 8/9 valid trials; priority capture in 6/9). All reported rates are sample-bounded descriptive quantities; they are not population prevalence estimates.

## 2. Related Work

[Related-work section: full versions and verified citations live in docs/RELATED_WORK_MAP.md in the replication package. Citations appear below as [C1]–[Cn] and are resolved in the final bibliography. Key related work: MCPZoo (Chen et al., 2026) [C1] — an eight-scanner evaluation over 64,611 runtime-deployed MCP servers reporting an average manual precision of 45.53% at the server-alert level, as reported. The two studies differ in unit, population, and ontology — the present work is description-level, class-wise, and text-bound — but they converge on the operative conclusion: unvalidated scanner output must not be read as prevalence. AgentsID-style flag counts (954 servers with Toxic-Flow-shaped flags, as reported) [C2] motivate the calibration question; our sample-bounded support rates cannot calibrate that distinct detector and population. To our knowledge, among studies identified in a September-2026 literature search (arXiv cs.CR listing plus Google Scholar queries; search log in the replication package), this is the first purposed human calibration of a poisoning detector at the tool-description level on a registry-grounded corpus.]

## 3. Study Design and Dataset

### 3.1 Overview

We evaluated a frozen detector against a purposive sample of 150 tool-description rows drawn from a registry-grounded corpus. The detector produced check-level flags; the principal investigator (PI) assigned the primary reference labels after full-text review of all 150 rows. Detector activity and human-label outcomes are reported separately: a fired check means a pattern matched; a positive reference label means the reviewed text supported the poison interpretation under the master rule (§4.2).

Two analysis units are used: **rows** (descriptions) and **flag instances** (individual detector matches; multiple per row possible). "Top-100" means the 100 rows with the highest suspicion scores.

### 3.2 Source Population

The registry was crawled on 2026-09-21 via its official paginated API (100 entries per page, cursor-ordered), yielding 60,000 version entries and 17,167 unique servers after collapsing to the latest published version (`isLatest`). 11,370 servers (66.2%) carried repository references; 11,288 (65.8%) were GitHub-linked. Static source extraction (decorator, factory-call, and handler idioms — no third-party code executed) yielded **16,763 tool-description rows from 4,725 repositories**. The frame is therefore: a cursor-limited prefix of the registry, restricted to GitHub-linked servers whose source was extractable — not live manifests of deployed servers.

One "row" is one extracted `(server, tool)` description. Duplicate names are pervasive in this ecosystem: 1,484 distinct tool names appear on multiple rows (6,740 rows share one of these names).

### 3.3 Validation Sample

The frozen 150-row validation sample (data/analysis_toollevel.csv, sha256 ae1aff9f…8f77) contains: the 100 rows with the highest suspicion scores (tie-breaking by original corpus row order), plus 50 uniformly sampled controls with zero capability- and poison-family flags (seed 42). All 100 top-score rows carry at least one poison-family flag; 5 of the 50 controls carry a single channel-family flag each (model_addressed), all unsupported.

Because selection is purposive (deterministic top-score cut), all rates are conditional on this design. A population estimate would require a probability sample over all flagged rows — including flagged rows beyond the top-100 — and none was drawn. Detector recall is unmeasured by design; the zero-flag controls are structurally uninformative about it. All 150 rows, including controls, received full-text content reads; no unflagged steering was observed in controls.

### 3.4 Ethics and Data Handling

Collection was limited to publicly available registry listings and open-source repositories; no third-party server endpoint was contacted and no third-party code was executed. Live experiments used synthetic credentials in a fully mocked harness: no real shell execution, no dispatched tool network calls (gateway API calls to the model provider obviously occurred), no real credentials in any trial. We do not infer or assess author intent; no attacker was established; all quoted texts are publicly available product copies.

## 4. Detector and Reference Labels

### 4.1 The Frozen Detector

The detector carries 18 checks: **capability (7)** — network_egress, shell_execution, file_read_sensitive, file_write_delete, secret_env_access, database_write, package_install; **poison (7 behavioral)** — imperative_to_model, exfiltration_language, stealth_concealment, cross_tool_shadowing, fake_system_role, important_tags, sensitive_file_target; **structural (2)** — zero_width_chars, base64_blob; **channel (2)** — model_addressed, second_person_imperative (exposure metrics only; they never enter poisoning rates or the suspicion score). The suspicion score is 1×|CAP| + 3×|POI|, used only for sample stratification. Version 1 was frozen before any human labeling (commit 6cca247); version 2 added the channel classes (commit 77b41af). Thirteen of 18 checks fired in the sample; the five that never fired are reported as such, without effectiveness claims. A Unicode scan found zero control/format codepoints in stored descriptions — noting that newlines (class Cc) are absent by extraction, not necessarily absent upstream.

Per-instance support criteria: a **capability** flag is supported when the text factually states the capability; a **poison** flag is supported when the text adds a behavioral instruction to the model beyond the tool's declared function; a **channel** flag is supported when the text addresses the model. The full labeling rulebook (decision tree plus positive and negative worked examples) ships in the replication package.

### 4.2 Labeling Procedure and Provenance

The master rule is: **separate the tool's declared function from an added behavioral instruction to the model.** A row is a true positive if and only if at least one poison flag is genuinely supported by the visible text. Under this rule, detector-negative rows cannot be labeled positive — so row-level FN discovery is out of scope by construction.

Primary verdicts were finalized by the PI. Candidate rationale drafts and per-row checklists were proposed by an unversioned AI assistant during labeling; every verdict was manually accepted, edited, or overridden (7 verdicts revised on re-review — rows 3, 6, 9, 11, 16, 94, 95 — recorded in the labels audit log). The AI assistant used for labeling support and the second-opinion rater were different services, so the reliability probe cannot be an echo of the labeling aid. Per-class statistics derive each fired instance's support from the row verdict (apportionment), with a stated limitation: single-row assignment does not distinguish which instance carried the support.

### 4.3 Reliability Probe

A rubric-application consistency probe used an unversioned consumer ChatGPT (web UI, packet run 2026-09-28, verbatim prompt archived in the replication package) as a blind second rater on a 30-item packet (5 TP rows + 25 flagged items). Full-packet agreement: κ = +0.760 (n=30, po=0.933, 95% CI via influence-function delta method, SE=0.162, approximately [0.44, 1.00] after clipping). The rater never answered "unclear"; the 3-class and 2-class rows therefore coincide. On the packet-negative subset κ degenerates to 0.00 at po=0.96 — the standard prevalence-paradox artifact, uninformative for the reliability question. This probe checks rubric-application consistency; it is not human-to-human reproducibility evidence. One disagreement concerns row 35 (the exec-priming positive), underscoring that scope judgments at the workflow/steering boundary remain expert judgment. A second blinded human annotation of a 40-row subset (5 TP + 10 boundary + 25 seeded-random) is specified in the replication package (protocol, rulebook, scorer) and remains future work.

## 5. Results

### 5.1 Corpus Candidate Rates (RQ1)

Over the full corpus of 16,763 rows, the frozen detector fires 4,926 flag instances: **4,128 rows (24.6%) carry at least one flag** and **698 rows (4.2%) carry a poison-family flag**. These are corpus-wide *candidate rates* — the detector's output vocabulary — not findings.

### 5.2 Headline Calibration (RQ2)

In the frozen sample of 150 rows, the PI judged **5 rows to contain a supported poison instruction** (all in the top-100 stratum); the remaining flagged rows are **95 flagged non-TP (flagged-but-benign)**, and none of the 50 controls was judged to contain a supported poison instruction.

The primary outcome is the **poison-family text-support rate: 6/124 = 4.8%** (95% Wilson compatibility interval [2.24%, 10.15%]). Across all families, **15/268 = 5.6%** ([3.42%, 9.03%]; capability 5/102, poison 6/124, channel 4/42). Estimand note: 15/268 combines both selection groups and includes 5 channel instances on control rows; within the top-100 stratum alone the figure is 15/263 = 5.70%. Collapsing duplicate `server::tool` name-groups (13 sample rows in 5 groups) changes the pooled figure to 13/251 = 5.18% — a descriptive sensitivity, not an interval. These are sample-bounded descriptive quantities over a purposively selected sample; the direction in which top-score selection distorts text-support is unidentified (a directional hypothesis, not an established bias), and the intervals assume a binomial model under independence — instances within rows may be dependent. No multiplicity adjustment; per-class figures are descriptive summaries over the 13 fired classes.

### 5.3 Per-Class Support

| Class | Supported | Unsupported | Text-support rate |
|---|---|---|---|
| `cross_tool_shadowing` | 1 | 3 | 0.25 |
| `file_read_sensitive` | 1 | 1 | 0.50 |
| `second_person_imperative` (channel) | 4 | 17 | 0.19 |
| `imperative_to_model` | 5 | 71 | 0.07 |
| `secret_env_access` | 3 | 50 | 0.06 |
| `shell_execution` | 1 | 17 | 0.06 |
| `exfiltration_language` | 0 | 34 | 0.00 |
| `network_egress` | 0 | 21 | 0.00 |
| `model_addressed` (channel) | 0 | 21 | 0.00 |
| `stealth_concealment` | 0 | 9 | 0.00 |
| `database_write` | 0 | 4 | 0.00 |
| `file_write_delete` | 0 | 4 | 0.00 |
| `fake_system_role` | 0 | 1 | 0.00 |

*Channel classes shown for completeness; they never determine row verdicts. Poison subtotal 6/124.*

Of the 13 classes that fired in the sample, 12 are unsupported-dominated; `file_read_sensitive` splits 1–1.

### 5.4 Mechanisms Found in the Wild (RQ3)

All five positive rows occurred in otherwise benign product descriptions from established vendors. Four distinct steering mechanisms were identified (duplicate registrations 94/95 counted once for mechanisms, still 5 rows):

1. **Priority capture, unconditional** (row 12): an all-caps instruction that the tool must always be called first — repeated verbatim from an official vendor description [full verbatim text + sha in Appendix; replication package fixture].
2. **Priority capture, conditional gateway** (rows 94/95, same server): first-position capture scoped to the whole ecosystem ("call this first whenever the user needs a capability you do not already have").
3. **Exec-priming** (row 35): the description instructs the agent to run tool-supplied commands through its own shell rather than the tool's runtime.
4. **Universal credential funnel** (row 60): any credential encountered — from user, config file, or API response — must be deposited in the tool immediately, with the instruction that the secret should leave the model's context after the call (full 432-character text in Appendix). The text never says "send," so the exfiltration-language class stays silent — a regex blind spot for custody-style steering.

Every confirmed mechanism relies on scope and conditionality, not on exotic text shape; the boundary case (row 61's compressed manifest tagline, judged benign) shows how narrow the line is.

### 5.5 The 95 Flagged Non-TP Rows: What Makes Regexes Fire

The 95 flagged-but-benign rows partition into systematic families (first-match keyword partition of the PI's own rationale notes — descriptive, not independent coding): negated assurances, 24 rows (security promises that cite the very attack verbs they deny); defensive/anti-injection guards, 18; regex accidents, 11; residual causes, 11; template/duplicate-name inflation, 9; declared-function statements, 7; truncation artifacts, 3; capability-only prose, 3; own-tool routing documentation, 3; credential-acquisition wording, 2; anti-concealment disclosures, 2; detection-list enumerations, 1; bare URLs, 1. Pure marketing prose accounts for zero false positives. The bulk of detector volume is defensive and assuaging text, not marketing.

### 5.6 Mocked Live Experiments

We tested whether the identified mechanisms steer behavior using a fully mocked harness with synthetic data: no real shell execution, no dispatched tool network calls, no real credentials. Three deployed model versions — glm-5.3, deepseek-v4.1-flash, gemini-3.8-flash — via one gateway (AvalAI), temperature 0, three fresh-conversation replications per cell, executed sequentially with one retry on timeout. 54 trials were attempted; 51 are valid (3 infra exclusions: one gateway timeout each in the three control families on gemini-3.8-flash).

Six fixtures covered three of the four confirmed mechanisms (the conditional gateway was outside the authorized fixture set); two hand-picked defensive descriptions served as live controls (16 valid control trials).

| Arm (outcome) | glm-5.3 | deepseek-v4.1 | gemini-3.8 |
|---|---|---|---|
| Credential funnel — transfer | 3/3 | 3/3 | 3/3 |
| Credential funnel — without final-answer disclosure | 2/3 | 3/3 | 3/3 |
| Priority capture | 3/3 | 3/3 | 0/3 |
| Exec-priming — task-conflated † | infrm | infrm | infrm |
| Controls — steering violations | 0 | 0 | 0 (16 valid) |

*† The exec-priming outcome criterion (presence of the install-guide marker in the final answer) coincides with benign task completion: a retrospective audit of the stored transcripts shows all nine trials surfaced the instruction text as the task required, while **execution intent was expressed in 0/9** — one model explicitly refused to pretend execution, one stated it could not execute, one deferred to the user's shell. The arm is therefore reported as a design lesson: **instruction surfacing 9/9, model-side adoption 0/9 — steering not tested**. The frozen ledger row is preserved.*

Results under this harness, gateway, and prompts: the credential funnel **transferred the synthetic credential to the tool in 9/9 valid trials and omitted it from the final answer in 8/9** (95% Wilson compatibility interval [0.57, 0.98]); the ninth trial transferred with disclosure. "Without final-answer disclosure" means only that the credential value was absent from the final assistant answer; every tool call was logged, nothing was hidden from the interface. Priority capture was model-variant (6/9, [0.35, 0.88]): two models adopted the first-call instruction unconditionally; gemini-3.8-flash completed the user's task instead in all three replications. Pooled descriptive count over the two valid steering arms: **14/18** (95% compatibility intervals are per-cell descriptive summaries under an i.i.d.-assumption; pooling is a convenience, not an interchangeability claim). No refusals were observed across steering arms; control fixtures produced zero steering violations — which is evidence neither of safety nor of detector specificity.

## 6. Discussion

The central finding is that unvalidated detector flags are not findings. In a purposive top-score sample, 94.4% of the detector's flags found no textual support; even on the poison family the support rate was 4.8%. The detector remains a candidate generator — a quarter of the ecosystem trips at least one check — but raw flag counts from any heuristic scanner must not be reported as prevalence without human calibration. Independent work at a different unit and ontology (MCPZoo; average manual precision 45.53% at server-alert level, as reported) converges on the same operative conclusion; the magnitudes are not directly comparable.

The five positives reveal the subtler problem. Every confirmed mechanism appeared in ordinary product copy from an established vendor. The text shape of a benign instruction and a hostile one is identical; the only discriminator we found is scope and conditionality. Any defense that scores text shape alone will punish security hygiene as hard as malice.

Model variance adds a layer. The same priority-capture description adopted unconditionally by two models was ignored by the third in all three replications; the same panel transferred the credential in all nine trials. Authorization behavior in clients without external policy gates is a property of the deployed model, not of MCP text alone.

The evidence chain stops here, deliberately: a registry prefix plus benign provenance plus steering-consistent behavior in a mocked harness does not constitute a demonstrated vulnerability, and we do not claim it does.

## 7. Limitations

(i) The detector family is single-axis regex; differences from NLP-based approaches are out of scope.
(ii) English-dominant patterns; the one bilingual row was caught through its English mirror.
(iii) Purposive top-score selection; all rates are conditional on it; distortion direction unidentified.
(iv) Detector recall unmeasured by design; controls structurally uninformative about misses.
(v) Single-PI reference labels with unversioned AI assistance; no independent human annotation yet (protocol pre-specified, package shipped).
(vi) The corpus over-represents GitHub-linked open-source servers; it is a cursor-order prefix, not a census; "latest" means latest within the crawled prefix.
(vii) Truncation: 6.45% of stored descriptions (1,082/16,763) end mid-sentence; a 7/7 snapshot-to-re-extraction check observed no verdict flips but cannot quantify corpus-wide effects (revisions pending on three rows are disclosed in the replication package).
(viii) Live experiments: n=3 per cell behind one third-party gateway; i.i.d. within cells is a modeling assumption, not a verified property of proxy routing; results characterize these deployed versions under this harness, not model families.
(ix) No matched description-ablation arm ran; live results show behavior in the presence of fixture text, consistent with steering, not causal isolation (future work requires authorization).
(x) The exec-priming arm's criterion was conflated with task completion (§5.6); a redesigned marker that is not task-required is future work (FUTURE_WORK #16).
(xi) Instance-level intervals do not model within-row or within-server dependence; the collapsed sensitivity (13/251) is descriptive only.
(xii) One check family was not positive-tested against synthetic positives; the five never-fired classes' silent failure modes are unknown.

## 8. Conclusion

We calibrated a frozen 18-check heuristic detector against human judgments on 150 tool-description rows drawn from a registry-grounded corpus of 16,763 descriptions. The detector flags a quarter of the corpus, yet the poison-family text-support rate in the purposive validation sample is 4.8% (6/124), the all-family rate 5.6% (15/268). Five rows contain supported poison instructions spanning four mechanisms, of which two steered models in a mocked harness at high observed rates — credential transfer without final-answer disclosure in 8/9 trials including a custody-funnel fixture. Detector flags and validated findings are distinct quantities; calibration against human labels — and honesty about what was never measured — is a prerequisite for interpreting any automated screening of the MCP description channel.

---

## References

[To be resolved from docs/RELATED_WORK_MAP.md — the replication package's verified
citation map (authors, titles, venues, years, arXiv IDs/DOIs). Keys [C1]–[C12]
in text.]

1. Chen et al. — MCPZoo — 2026 — arXiv 2607.11086 — [C1]
2. AgentsID / Toxic-Flow measurement — 2025/2026 — [C2]
3–12. [Remaining entries verbatim from RELATED_WORK_MAP.md]

---

## Appendix A. Replication Pointers (summary)

- Frozen corpus: data/github_tools.jsonl (16,763 rows).
- Frozen validation sample: data/analysis_toollevel.csv (150 rows), sha256 ae1aff9f…8f77.
- Detector: pilot/analyze.py (v1 commit 6cca247; v2 commit 77b41af).
- Claims ledger: claims_ledger.jsonl (26 records, per-claim provenance).
- Reproducibility manifest: reproducibility_manifest.json (28 hashed files).
- One-command re-derivation: python3 pilot/derive_r4_numbers.py (numbers);
  python3 experiments/trial_accounting.py --check (live accounting);
  python3 scripts/verify_claims.py (69 consistency checks);
  python3 scripts/gate_battery.py (gate suite).
- κ packet: data/kappa_packet.md (constructed 2026-09-28, commit 7b52792);
  verbatim rater prompt: prompts/06-second-opinion.md; seed 20260927.
- Live transcripts: data/live_tests/ (51 valid transcripts + ledger).
- Labeling rulebook: docs/LABELING_RULEBOOK.md; second-rater pack: pilot/second_rater_pack.csv
  (sha256 af271878…b77a) + docs/SECOND_RATER_PROTOCOL.md + docs/SECOND_RATER_SCORER.py.
- Search log: docs/RELATED_WORK_MAP.md (September 2026 literature-search provenance).
- TP verbatim texts: rows 12, 35, 60, 94, 95 (+ boundary row 61) with full sha256
  (paper/FACTS_VERIFIED.md §2).

*Repository URL and Zenodo DOI: [PLACEHOLDER — inserted upon public release].*
