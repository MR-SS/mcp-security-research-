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
> — the NO-human-validation cell is its own stated limitation. The **five arXiv items remain
> PI-supplied and are not yet independently re-verified here**; each cell must be checked
> against the actual papers before submission.
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
| **Hasan et al.** (arXiv 2506.13538) | MCP servers (1,899) | server | 1,899 servers | No (code-health / quality metrics) | No | No | Partial (unverified here) |
| **MCPTox** (arXiv 2508.14925) | synthetic benchmark over real servers | tool (description) | 45 servers / 353 tools | Yes (poisoned tool descriptions) | No | No | No (benchmark construction) |
| **MSB** (arXiv 2510.15994, ICLR 2026) | synthetic benchmark | tool (attack case) | 405-tool benchmark | Yes (attack cases incl. description channel) | No | No | No (benchmark construction) |
| **Breaking the Protocol** (arXiv 2601.17549) | protocol specification | spec mechanism | spec analysis | No (design/spec level) | No | No | No |
| **MCP Safety Audit** (arXiv 2504.03767) | individually audited servers | server (audit) | single audits | Partial (audit reports cover descriptions among surfaces) | Yes (manual audits, n ≈ single digits) | No | No |
| **Ours** (this study) | **official MCP Registry** (`registry.modelcontextprotocol.io`, 17,167 servers after `isLatest` dedupe) + GitHub tool-registration source | **tool description** | **16,763 tool-description rows / 4,725 repos** | **Yes** (the entire detector surface is description text) | **Yes** (150/150 rows human-labeled; 5 TP / 145 FP; flag-instance precision **5.6%**) | **Yes** (blind Mode B inter-rater, n=30, **Cohen's κ = +0.760**, `data/kappa_report.md`) | **Yes** (official registry crawl, raw snapshots committed) |

**Ours is the only row with YES on the last three columns** (human validation, reliability
artifact, registry-grounded).

AgentsID headline counts, for the contrast: **954 servers exhibiting Toxic Flow behavior
across five types** (incl. 145 hidden-character findings), unvalidated; on our evidence an
unvalidated count at this population's base rate carries ~94% false positives.

## 2. Positioning paragraph (paper-facing)

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

## 3. Concrete borrowings already made (traceability)

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
