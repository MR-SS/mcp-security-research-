# Related-Work Map — how this study is positioned

> **Purpose:** one table placing this study against the closest prior work, plus the
> positioning paragraph the paper's Related Work / Intro builds on. Created 2026-09-28.
>
> **Provenance (AGENTS.md §2.1):** the **AgentsID** row was verified 2026-09-28 against the
> public report itself (`raw.githubusercontent.com/AgentsID-dev/agentsid-scanner`,
> `master:docs/census-2026/weaponized-by-design.md`, fetched HTTP 200): vendor research
> ("AgentsID Security Research — April 2026", published on agentsid.dev/research + repo docs;
> **no peer-review venue** — cite as industry census) and its own §3.3 concedes
> "some findings may be false positives where our linguistic patterns match benign content"
> — the NO-human-validation cell is its own stated limitation. **All seven arXiv IDs in this
> map are PI-verified 2026-09-28** (format confirmed; cite-as lines in §2). Quantitative
> cells carry "as reported by authors" markers wherever we have not re-derived the number
> from the paper itself; scope cells for the two rows added at verification (Hou et al.,
> Errico) come from the PI's one-line summaries.
>
> **Numbering note:** AgentsID's verified Toxic Flow types are I Concealment · II Behavioral
> Mandates · III Confirmation Bypass · IV Data Exfiltration Chains (capability graphs) ·
> V Hidden Unicode Characters. Earlier task notes saying "Type V multilingual" and "Type III
> capability graphs" were slips against this numbering; the entries below use the verified
> numbers.

## 1. Comparison table

| Work | Population | Unit | Scale | Description-level? | Human validation? | Reliability artifact? | Registry-grounded? |
|---|---|---|---|---|---|---|---|
| **AgentsID — Weaponized-by-Design** (Apr 2026, vendor; verified) | npm/PyPI MCP packages | tool manifest / server | 15,982 packages (6,526 npm + 9,456 PyPI) · 40,081 tools · 3,789 tool-bearing servers | Yes (Toxic Flow types I–V live in tool descriptions) | **No** (static analysis only; own §3.3 concedes possible FPs) | **No** | No (package registries, not the MCP registry) |
| **Hasan et al.** (arXiv 2506.13538, cs.SE, 2025-06, v5 2026-04; PI-verified) | MCP servers (1,899) | server | 1,899 servers (as reported by authors) | No (code-health / quality metrics) | No | No | Partial (per PI summary; extent not re-verified here) |
| **MCPTox** (arXiv 2508.14925, cs.CR, 2025-08; PI-verified) | synthetic benchmark over real servers | tool (description) | 45 servers / 353 tools / 1,312 cases (v1) (as reported by authors) | Yes (poisoned tool descriptions) | No | No | No (benchmark construction) |
| **MSB** (arXiv 2510.15994, cs.CR, 2025-10; ICLR 2026; PI-verified) | synthetic benchmark | tool (attack case) | 405 tools / 2,000 attack instances (as reported by authors) | Yes (attack cases incl. description channel) | No | No | No (benchmark construction) |
| **Breaking the Protocol** (arXiv 2601.17549, cs.CR, 2026-01; PI-verified) | protocol specification | spec mechanism | spec analysis | No (design/spec level) | No | No | No |
| **Hou et al. — MCP Landscape** (arXiv 2503.23278, cs.CR, 2025-03; PI-verified) | MCP ecosystem (survey/landscape) | ecosystem survey | taxonomy / landscape survey (as reported by authors) | No (survey level) | No | No | No (survey) |
| **MCP Safety Audit** — Radosevich & Halloran (arXiv 2504.03767, 2025-04; PI-verified) | individually audited servers | server (audit) | single audits (as reported by authors) | Partial (audit reports cover descriptions among surfaces) | Yes (manual audits, n ≈ single digits) | No | No |
| **Errico — Securing MCP** (arXiv 2511.20920, cs.CR, 2025-11; PI-verified) | MCP security architecture (per PI summary) | design/protocol analysis | design analysis (no corpus) | No (design level) | No | No | No |
| **Ours** (this study) | **official MCP Registry** (`registry.modelcontextprotocol.io`, 17,167 servers after `isLatest` dedupe) + GitHub tool-registration source | **tool description** | **16,763 tool-description rows / 4,725 repos** | **Yes** (the entire detector surface is description text) | **Yes** (150/150 rows human-labeled; 5 TP / 145 FP; flag-instance precision **5.6%**) | **Yes** (blind Mode B inter-rater, n=30, **Cohen's κ = +0.760**, `data/kappa_report.md`) | **Yes** (official registry crawl, raw snapshots committed) |

**Ours is the only row with YES on the last three columns** (human validation, reliability
artifact, registry-grounded).

## 2. Cite-as lines (arXiv, PI-verified 2026-09-28)

- **2506.13538** — Hasan et al., *MCP at First Glance* — cs.SE, 2025-06 (v5 2026-04) — <https://arxiv.org/abs/2506.13538>
- **2508.14925** — *MCPTox* — cs.CR, 2025-08 — <https://arxiv.org/abs/2508.14925>
- **2510.15994** — *MSB* — cs.CR, 2025-10; ICLR 2026 — <https://arxiv.org/abs/2510.15994>
- **2601.17549** — *Breaking the Protocol* — cs.CR, 2026-01 — <https://arxiv.org/abs/2601.17549>
- **2503.23278** — Hou et al., *MCP Landscape* — cs.CR, 2025-03 — <https://arxiv.org/abs/2503.23278>
- **2504.03767** — Radosevich & Halloran, *MCP Safety Audit* — 2025-04 (cs class not stated at verification) — <https://arxiv.org/abs/2504.03767>
- **2511.20920** — Errico, *Securing MCP* — cs.CR, 2025-11 — <https://arxiv.org/abs/2511.20920>

(Verification method: PI confirmation of ID ↔ title/author/venue mapping, 2026-09-28; no
independent fetch of the arXiv abstracts was made or needed for this pass.)

AgentsID headline counts, for the contrast: **954 servers exhibiting Toxic Flow behavior
across five types** (incl. 145 hidden-character findings), unvalidated; on our evidence an
unvalidated count at this population's base rate carries ~94% false positives.

## 3. Positioning paragraph (paper-facing)

Prior work measured ecosystems **raw**: AgentsID's census reports 954 servers with Toxic Flow
behavior over npm/PyPI without human validation, the benchmarks (MCPTox, MSB) construct synthetic
attack sets whose rates answer "how bad can an attack be," not "how often is it there," and
the code-health and audit studies sample servers without a description-level detector
protocol. **We calibrated detection WITHIN the official registry population**: the same
pattern classes others report as raw counts are here measured against the full registry
crawl, human-labeled row by row (150/150), with the detector's **measured flag-instance
precision of 5.6% (15/268)** and a blind inter-rater reliability of **κ = +0.760**. Where
AgentsID-style censuses report unvalidated counts — numbers that would, on our evidence,
carry ~94% false positives at this population's base rate — every rate we publish is
calibrated. The two results are **complementary, not competing**: their (vendor, non-peer-
reviewed) census provides breadth and the Type I–V taxonomy; ours provides the registry-
grounded, human-validated calibration that turns such counts into measurable prevalence.
Even the apparent disagreements are population facts, not replication conflicts: AgentsID
reports 145 hidden-character findings in its npm/PyPI corpus, while our registry-grounded
corpus contains **zero** hidden characters in 16,763 stored descriptions (§5.12, same
byte-diff method) — different populations, honestly scanned on both sides.

## 4. Concrete borrowings already made (traceability)

- **Type V (hidden characters) mirror:** the §5.12 Unicode scan (`data/unicode_scan.csv`,
  `data/collection_report.md`) runs the AgentsID Type V hidden-character check on our
  corpus — result: **0 Cc/Cf codepoints in 16,763 stored descriptions** (negative result,
  scanner-blind classes stated in §5.12).
- **Type III (Confirmation Bypass) seed:** proposed as the `confirmation_bypass`
  v3 candidate class (P7 in `docs/DETECTOR_FIX_PROPOSAL.md`), anchored on our row 47
  watch-item; **non-scoring until v3 validation** per the proposal's protocol. The trigger
  family matches the verified §5.4 detection pattern ("avoid redundant approvals", "skip
  verification", "not needed before", "proceed without").
- **Type IV (capability graphs) follow-on:** cross-tool toxic-chain analysis is parked in
  `FUTURE_WORK.md` — it needs whole-server tool graphs, which the tool-description-row
  evidence base does not yet support.
- **Multilingual blind spot** (row 34, the sample's only non-English text) remains P6
  (multilingual review flag) in the same proposal — our finding; AgentsID's verified
  taxonomy has no multilingual type (I–V as listed above).
