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
> **Provenance — R2 pass (2026-09-29, external reviewer feedback):** four 2026 works were
> added and **verified by the agent against public pages** (not by PI summary): the three
> arXiv IDs `2607.11086`, `2605.24069`, `2603.23802` by fetching each `arxiv.org/abs/` page
> (HTTP 200; title, cs class, submission date and abstract read off the page), and the IEEE
> TSE DOI `10.1109/TSE.2026.3694876` through the public **Crossref** and **Semantic Scholar**
> APIs (the IEEE Xplore landing page is JS-gated, so no direct fetch was possible). MCPZoo's
> headline numbers were re-derived a third time from the **paper's own full text**
> (`arxiv.org/html/2607.11086v1`, §5.1–§5.3 + Table 7): 64,611 unique servers (113,927
> total), 37,288 interactable, 96.89% flagged risky by ≥1 of 8 scanners, **overall average
> precision 45.53%** (per-scanner 10.40%–96.88%; recall on their CVE ground truth 24.17%;
> their reviewer agreement Cohen's κ = 0.87, disagreements resolved by a third reviewer) —
> so those cells are *full-text verified*, not PI-supplied. Their **multi-market** population
> (MCP Store, MCP World, MCP Market, AIBase, Pulse MCP, MCP.so, Smithery, NPM, PyPI) is also
> read from the full text. The TSE row's design cells come from the Crossref/Semantic
> Scholar record plus the abstract of its arXiv preprint (`2506.02040`).
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
| **MCPTox** (arXiv 2508.14925, cs.CR, 2025-08; PI-verified) | synthetic benchmark over real servers | tool (description) | 45 servers / 353 tools / 1,348 cases (v2) (as reported by authors) | Yes (poisoned tool descriptions) | No | No | No (benchmark construction) |
| **MSB** (arXiv 2510.15994, cs.CR, 2025-10; ICLR 2026; PI-verified) | synthetic benchmark | tool (attack case) | 405 tools / 2,000 attack instances (as reported by authors) | Yes (attack cases incl. description channel) | No | No | No (benchmark construction) |
| **Breaking the Protocol** (arXiv 2601.17549, cs.CR, 2026-01; PI-verified) | protocol specification | spec mechanism | spec analysis | No (design/spec level) | No | No | No |
| **Hou et al. — MCP Landscape** (arXiv 2503.23278, cs.CR, 2025-03; PI-verified) | MCP ecosystem (survey/landscape) | ecosystem survey | taxonomy / landscape survey (as reported by authors) | No (survey level) | No | No | No (survey) |
| **MCP Safety Audit** — Radosevich & Halloran (arXiv 2504.03767, 2025-04; PI-verified) | individually audited servers | server (audit) | single audits (as reported by authors) | Partial (audit reports cover descriptions among surfaces) | Yes (manual audits, n ≈ single digits) | No | No |
| **Errico — Securing MCP** (arXiv 2511.20920, cs.CR, 2025-11; PI-verified) | MCP security architecture (per PI summary) | design/protocol analysis | design analysis (no corpus) | No (design level) | No | No | No |
| **MCPZoo — Rethinking MCP Security** (arXiv 2607.11086, cs.CR, 2026-07-13; verified 2026-09-29, full text) | runtime-deployed MCP servers crawled from **multiple MCP markets** (MCP Store, MCP World, MCP Market, AIBase, Pulse MCP, MCP.so, Smithery, NPM, PyPI) | **server** (runtime) + scanner alert | 64,611 unique servers (113,927 total); 37,288 interactable/dynamic (as reported by authors; full-text verified) | Partial (scanners span static/dynamic/hybrid; some are metadata scanners reading tool descriptions, but the reliability unit is the server-level alert) | **Yes** (manual validation of sampled scanner reports; reviewer κ = 0.87 + third reviewer; **45.53% overall average precision** across 8 scanners, 10.40%–96.88%) | **Yes** (scanner-reliability measurement: cross-scanner Jaccard 15.66%, CVE-ground-truth recall 24.17%) | No (multi-market repos, not the official registry) |
| **MCP-TDP — When the Manual Lies** (arXiv 2605.24069, cs.CR; cs.AI, 2026-05-22; verified 2026-09-29) | synthetic sandbox benchmark over MCP tool descriptions | tool (attack case) | 32 realistic test cases / 6 risk categories / 8 LLMs (as reported by authors) | Yes (TDP injects malicious instructions into descriptive metadata — the "manual", not the code) | No (attack-success evaluation, no detector-precision validation) | No | No (benchmark construction) |
| **Stein — How are AI agents used?** (arXiv 2603.23802, cs.CY, 2026-03-25; verified 2026-09-29) | public MCP server repositories monitored over time | tool | 177,436 agent tools, 11/2024–02/2026 (as reported by authors) | Partial (tool text/metadata categorized by impact class + O\*NET task domain; not a poisoning detector) | No | No | Partial (monitors public MCP server repositories, not the official registry) |
| **Song et al. — Beyond the Protocol** (IEEE TSE 52(8):2410–2426, 2026-08; DOI 10.1109/TSE.2026.3694876; verified 2026-09-29 via Crossref + Semantic Scholar; preprint arXiv 2506.02040) | MCP ecosystem attack vectors (malicious-server attacks on aggregator platforms) | attack vector / server | 4 attack classes (tool poisoning, puppet, rug pull, malicious external resources); malicious servers uploaded to 3 aggregator platforms; user study n = 20 (as reported by authors) | Yes (tool poisoning is the description channel) | Partial (20-participant user study + interviews; no detector-precision validation) | No | No (aggregator platforms, not the official registry) |
| **Ours** (this study) | **official MCP Registry** (`registry.modelcontextprotocol.io`, 17,167 servers after `isLatest` dedupe) + GitHub tool-registration source | **tool description** | **16,763 tool-description rows / 4,725 repos** | **Yes** (the entire detector surface is description text) | **Yes** (150/150 rows human-labeled; 5 TP / 145 FP; flag-instance precision **5.6%**) | **Yes** (rubric-application consistency check, n=30, **κ = +0.760** — second rater an *unversioned consumer LLM*, a methodological limitation, paper §7; `data/kappa_report.md`) | **Yes** (official registry crawl, raw snapshots committed) |

**Ours is the only row with YES on the last three columns** (human validation, reliability
artifact, registry-grounded).

## 2. Cite-as lines

> **R4 update (2026-09-29):** the MCPTox case count was corrected from 1,312 to **1,348**
> against the current arXiv abstract (v2, last revised 2026-09-29), which states
> "45 live, real-world MCP servers and 353 authentic tools … a comprehensive suite of
> 1348 malicious test cases". Propagated to `paper/main.md` §4. Same v1->v2 note applies
> to the *as reported* qualifier: the number tracks the latest published version. (PI-verified 2026-09-28; four 2026 works added + agent-verified 2026-09-29, R2)

- **2506.13538** — Hasan et al., *MCP at First Glance* — cs.SE, 2025-06 (v5 2026-04) — <https://arxiv.org/abs/2506.13538>
- **2508.14925** — *MCPTox* — cs.CR, 2025-08 — <https://arxiv.org/abs/2508.14925>
- **2510.15994** — *MSB* — cs.CR, 2025-10; ICLR 2026 — <https://arxiv.org/abs/2510.15994>
- **2601.17549** — *Breaking the Protocol* — cs.CR, 2026-01 — <https://arxiv.org/abs/2601.17549>
- **2503.23278** — Hou et al., *MCP Landscape* — cs.CR, 2025-03 — <https://arxiv.org/abs/2503.23278>
- **2504.03767** — Radosevich & Halloran, *MCP Safety Audit* — 2025-04 (cs class not stated at verification) — <https://arxiv.org/abs/2504.03767>
- **2511.20920** — Errico, *Securing MCP* — cs.CR, 2025-11 — <https://arxiv.org/abs/2511.20920>

**Added at R2 (2026-09-29; all four verified by the agent against public pages):**

- **2607.11086** — Chen et al., *Rethinking MCP Security: A Large-Scale Study of Runtime MCP Servers and Security Scanner Reliability* (MCPZoo) — cs.CR, submitted 2026-07-13 — <https://arxiv.org/abs/2607.11086> (abstract fetched HTTP 200; headline numbers re-derived from the full text `https://arxiv.org/html/2607.11086v1`; extends the 3-page dataset note arXiv:2512.15144)
- **2605.24069** — Liu et al., *When the Manual Lies: A Realistic Benchmark to Evaluate MCP Poisoning Attacks for LLM Agents* (MCP-TDP benchmark) — cs.CR; cs.AI, submitted 2026-05-22 — <https://arxiv.org/abs/2605.24069> (abstract fetched HTTP 200)
- **2603.23802** — Stein, *How are AI agents used? Evidence from 177,000 MCP tools* — cs.CY, submitted 2026-03-25 — <https://arxiv.org/abs/2603.23802> (abstract fetched HTTP 200; 177,436 tools in the abstract)
- **10.1109/TSE.2026.3694876** — Song et al., *Beyond the Protocol: Unveiling Attack Vectors in the Model Context Protocol (MCP) Ecosystem* — IEEE Trans. Softw. Eng. **52(8):2410–2426**, 2026-08 — <https://doi.org/10.1109/TSE.2026.3694876> (metadata + abstract verified via Crossref and Semantic Scholar APIs, 2026-09-29; the IEEE landing page is JS-gated; open preprint arXiv:2506.02040)

(Verification method: PI confirmation of ID ↔ title/author/venue mapping, 2026-09-28 for the
seven pre-existing lines; **R2 pass 2026-09-29** for the four lines above — direct fetch of
the three arXiv abstract pages, Crossref + Semantic Scholar records for the TSE DOI, and a
full-text read of MCPZoo for its quantitative cells. No number in this map is carried
forward unverified.)

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
precision of 5.6% (15/268)** and a **rubric-application consistency check of κ = +0.760**
(second rater an *unversioned consumer LLM* — a methodological limitation, not a human-
annotation gold standard; paper §7). Where
AgentsID-style censuses report unvalidated counts — numbers that would, on our evidence,
carry ~94% false positives at this population's base rate — every rate we publish is
calibrated. The two results are **complementary, not competing**: their (vendor, non-peer-
reviewed) census provides breadth and the Type I–V taxonomy; ours provides the registry-
grounded, human-validated calibration that turns such counts into measurable prevalence.
Even the apparent disagreements are population facts, not replication conflicts: AgentsID
reports 145 hidden-character findings in its npm/PyPI corpus, while our registry-grounded
corpus contains **zero** hidden characters in 16,763 stored descriptions (§5.12, same
byte-diff method) — different populations, honestly scanned on both sides.

**Scanner-reliability cluster (paper-facing, added at R2 2026-09-29): convergent evidence
at two units, not a rivalry.** Independent work measuring a *different* instrument reports
the same calibration gap we measure. **MCPZoo** (Chen et al., arXiv 2607.11086, cs.CR,
2026-07) evaluates eight static/dynamic/hybrid security scanners on a **multi-market,
runtime-deployed population** of servers (64,611 unique; 37,288 interactable) and finds the
raw signal inflated: **96.89% of interactable servers are flagged risky by at least one
scanner, while manually validated overall average precision is 45.53%** (per-scanner
10.40%–96.88%) — a *server-level* alert-reliability measurement, validated by human
reviewers. **We** measure a different instrument at a different unit: the **tool-description
poisoning-pattern detector**, at the **description** level, on the official-registry +
GitHub population, under a **stricter, text-bound rubric** (a row counts as a true positive
only when the stored text adds a behavioral instruction to the model), and find **5.6%
flag-instance precision, reported per class**. Framed as what it is — **convergent
evidence**: *independent work at a different unit reports the same calibration gap, and
ours shows the gap is even wider for poisoning-pattern detection*. The two studies differ
in unit (server-level alert vs. description row), population (multi-market repos vs.
official registry + GitHub), and ontology (runtime vulnerability alerts vs. instruction-
shaped steering text), and agree on the operative conclusion: unvalidated scanner or regex
output must not be read as prevalence.

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
