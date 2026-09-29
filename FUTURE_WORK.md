# FUTURE_WORK.md — parking lot for out-of-scope ideas

> Purpose (AGENTS.md §2.4): the scope guard protects the 8-week timeline. Any idea that
> is bigger than "registry metadata + GitHub README/manifest/source-grep + ≤ 40 live tests"
> gets parked here — never silently added to the current brief.
>
> Format: idea · why it is interesting · why it is deferred · what would unblock it.

---

## Parked during Mission Brief 01 (full registry crawl)

**1. Secondary registries (PulseMCP, mcp.so, Smithery).**
*Interesting:* they index servers that may never reach the official registry, so coverage — and possibly the dangerous-capability rate — could differ.
*Deferred:* PLAN.md §2 marks secondary registries a stretch goal for phase 1; brief 01 explicitly says "don't add secondary registries".
*Unblocked by:* a dedicated brief after the paper's core table exists, if the official-registry rate looks suspiciously low.

**2. Tool-level crawling of `remotes[]` (streamable-HTTP servers).**
*Interesting:* for remote servers the tool schema lives behind the endpoint, so the real tool descriptions are invisible to metadata-only analysis.
*Deferred:* contacting a third-party endpoint is dynamic analysis and is explicitly OUT of scope (PLAN.md §2, AGENTS.md §2.2 — never execute/contact third-party servers). Brief 01 forbids hitting server endpoints.
*Unblocked by:* phase-2 work with an explicit ethics review, sandboxing, and probably institutional review — not a solo-pilot add-on.

**3. Longitudinal rug-pull / description-drift monitoring — ✅ APPROVED STRETCH (week 6, $0).**
*Interesting:* taxonomy item 4 (rug pull / description drift) can only be measured by comparing
snapshots over time; a single crawl cannot observe mutation. The 2026-09-21 census is the
baseline, and **89.3% of servers are remote-served**, i.e. their tool metadata can change
server-side with no install-time signal.
*Approved plan (PI, 2026-09-21):* **one** full census re-crawl at week 6, diffed per server name
against the 2026-09-21 snapshot (description hash / version / remotes), producing description-drift
statistics and **one figure** for the paper.
*Guard:* exactly one re-crawl and one figure — anything more goes back to this parking lot. Reuse
the raw-snapshot + probe protocol, and use **the same page cap on both sides** so the diff stays
comparable.

**4. Package-registry enrichment from `packages[].identifier`.**
*Interesting:* PyPI/npm download counts and publish history would let us weight findings by real adoption (the PyPI-malware-measurement genre does this).
*Deferred:* Brief 02 covers GitHub only; adding a third collector now expands scope.
*Unblocked by:* a brief that adds a package-registry collector alongside `fetch_github.py`.

**5. Per-version history (un-deduplicated entries).**
*Interesting:* we dedupe to `isLatest=true`, so release velocity and abandoned servers are invisible.
*Deferred:* not needed for the paper's single table; the raw snapshot still holds every entry, so this is re-derivable without new collection.
*Unblocked by:* re-running `analyze.py` over `data/raw/registry/<timestamp>/page-*.json` instead of the deduped JSONL.

**6. `status` beyond `active` (deprecated / archived servers).**
*Interesting:* deprecated servers still resolvable by agents are a plausible supply-chain risk (superseded-but-reachable endpoints).
*Deferred:* tiny effect size, needs the manual validation budget we already owe the top-100 queue.
*Unblocked by:* a one-line extension in `analyze.py` once the labeling workflow (Brief 03) is done.

**7. Bulk / larger page sizes on the registry API.**
*Interesting:* if `limit` can exceed 100, a full crawl costs fewer requests.
*Deferred:* cosmetic; brief 01 asks for 100/page paging.
*Unblocked by:* a quick API probe (documented, not guessed — AGENTS.md §2.1).

**8. Rolling census depth — ACTIVE PLAN (PI-authorised 2026-09-21).**
*Situation:* the registry is far larger than expected — 17,167 unique servers after 60,000
per-version entries, with the cursor **still live at the 600-page brake**. Every run so far
is a cursor-order prefix, and prefix composition shifts with depth (transport mix, detector
rates, namespace mix all move — see `data/collection_report.md` §§3–4).
*Plan:* continue crawling in capped runs with the same raw-snapshot + probe protocol until
a probe page returns <100 entries (true exhaustion). Each continuation needs explicit PI
authorisation for its `--max-pages`; no run proceeds on an agent's own authority.
*Guard:* identical command shape every time; report stays depth-qualified
("first N entries, cursor order") until exhaustion is actually observed.
*Note:* cursor-persistence / resume-across-sessions was considered and rejected for now —
one snapshot dir must equal one run, or the provenance model breaks.

**9. `isSecret` metadata as a high-precision capability signal.**
*Interesting:* registry `server.packages[].environmentVariables[]` (and `remotes[].headers[]`)
carry explicit `isSecret: true` / `isRequired: true` flags — e.g. `com.pulsemcp/slack` declares
`SLACK_BOT_TOKEN` as a required secret. That is a **declared** credential dependency rather than
a regex guess on marketing prose, so it should give near-perfect precision for the
credential-adjacent class that the current `secret_env_access` rule (3.2% of servers) only
approximates.
*Deferred:* detector changes must go through the versioned-diff process in Brief 03 (AGENTS.md
§2.3), and the Methods section needs detector versions frozen and comparable.
*Unblocked by:* a Brief 03 proposal adding an `is_secret_declared` flag **alongside** the v1 prose
heuristics (not replacing them).

---

## Parked during Mission Brief 03 (manual labeling / validation)

**10. `analyze.py`: stop capping the CSV `description` column at 300 chars.**
*Root cause (found 2026-09-26, Brief 03):* `analyze.py` writes `description` as
`.replace("\n", " ")[:300]` — line 176 (server level) and line 212 (tool level) — while
every detector rule runs over the **full** text. In the Brief-03 sample
(`data/analysis_toollevel.csv`) **43 of 150 rows sit exactly on that cap**, and **12 of the
20 labeled rows** had a full source text longer than the excerpt they were labeled from
(largest gap: +779 chars, `io.github.Thourum/billy-mcp::generic:unnamed`, 300 → 1079). The
labels were therefore made on less evidence than the detector saw.
*Already repaired at the workflow level:* `pilot/label_sample.py` now renders the full text
from `data/github_tools.jsonl` for every label and offers `--review-truncated` for the
cap-affected rows already labeled; `data/validation_report.md` records the finding and the
flip count.
*Measured impact (2026-09-26 full-text pass, now in `data/validation_report.md`):* all 12
cap-affected labeled rows were re-reviewed on the full text and **4 of the 4 cap-affected `u`
verdicts flipped to `fp`** (rows 3, 6, 9, 16) — every `unclear` label the cap produced was a
display artifact, not a judgment call. A fifth label flipped for an unrelated reason (row 11
carried no truncation at all: 233-char excerpt == full text, keyword noise), so **5 of the 20
labels (25%) changed once the full text was shown and the sample's unclear rate fell 25% →
0%**. That is the number this item's fix is worth in the paper: the truncation defect did not
merely hide text, it moved verdicts.
*Interesting:* the CSV is the paper's shared analysis artifact (server-level
`data/analysis.csv` frozen at detector v1, plus the 150-row tool sample whose `row_id`s
anchor the Brief-03 labels). A lossy `description` column means every downstream re-analysis,
reviewer replication, or future brief that reads the CSV is silently working from a
truncated view; the full text is only recoverable by joining
`data/github_tools.jsonl` on `(server_name, tool_name)`.
*Deferred:* regenerating either CSV is a versioned artifact decision, not a drive-by edit
(AGENTS.md §2.9 — detector/artifact versions stay frozen and comparable), and the
`analysis_toollevel.csv` row order must not shift or every existing `row_id` label breaks.
*Unblocked by:* a one-line change (`[:300]` dropped, plus `description_len` and
`description_truncated` columns) shipped with an explicit artifact-version bump and a re-run
that preserves row order. Decide at the same time whether to keep a short
`description_excerpt` column for terminal readability — the display cap belongs in the CLI
(`DISPLAY_LIMIT`), not in the dataset.

---

**11. `report()`: replace the FP-reason keyword chain with a coded rubric.**
*Found 2026-09-26 (Brief 03, while recording the PI's per-row notes):* the FP-reason
taxonomy classifies each FP row with a first-match keyword chain
(`marketing|product|feature` → `benign|legitimate|normal` → `url|link|http` → empty note →
first 60 chars of the note). That was written for one-word notes. Now that the PI writes
substantive rationale, three of the eight new notes (rows 10, 17, 18) collapse into the
single bucket `benign legitimate use` because they happen to contain the word "benign",
and their actual content — egress to connected accounts as a declared function,
attack-shaped-but-benign telemetry, capability-domain dual use (background read, not
concealment) — never reaches the report.
*Updated 2026-09-26 (same day, after the full FP note sweep reached 19 of 20 rows
with a note):* the measured damage is now known. Rows 10, 17, 18 still share the
`benign legitimate use` bucket (count 4 with one earlier row), while the six
substantive notes written later each land in their own first-60-chars bucket that
is a *truncated sentence fragment*, not a reason (e.g. `fp; 'never overwritten
silently' = transparency GUARANTEE (a`). So the taxonomy reports 13 buckets of
which 11 have count 1: it looks like signal but carries none.
*Inverse failure mode, rows 13 + 14 (crop_image/resize_image, one repo):* the two
descriptions are 79% identical — they share the literal sentence "The source image
is never overwritten silently." — and both tripped the same two regexes
(`imperative_to_model`, `stealth_concealment`). Distinct prose notes give them
distinct buckets, which hides the fact that they are one template instantiated
twice: for a corpus-wide precision estimate that is a *dedupe* problem, and for
the paper it is a counting question (an FP found in a description template shared
by N sibling tools is one detector error, not N). A keyword chain can express
neither the shared mechanism nor the shared template.
*Interesting:* the paper's FP analysis wants the *mechanism* of each false positive
(negated context, noun/verb homonym, declared function, capability-vs-intent), and the
GEM/defensive-pattern notes the PI is now recording are the raw material for a "benign
patterns" subsection — a keyword chain cannot express either.
*Deferred:* a rubric is a coding scheme, i.e. a definitional artifact that must be frozen
and applied consistently (same discipline as detector versions, AGENTS.md §2.9), and rates
are only meaningful with more FPs coded (currently 14 FP rows).
*Unblocked by:* labeling more FPs plus a short frozen code list
(`negated-context`, `homonym/noun-sense`, `declared-function`, `capability-not-intent`,
`defensive-imperative`, `benign-telemetry`) assigned one-per-row in `data/labels.jsonl` via
a `--code` flag alongside `--note`, with the report grouping on the code instead of prose.

---

**12. `fetch_github.py`: '+'-chain (multi-fragment) description extraction gap — corpus-wide re-extraction.**
*Root cause (found 2026-09-28, §5.11 validity pass on the 7 source-truncated sample rows):*
the extraction regexes capture `[^"']{10,2000}` — they stop at the **first embedded quote**,
and they do not follow descriptions authored as `"fragment" +\n "fragment" + ...` chains.
Both mechanisms store a cut description while the upstream source file holds the full one.
In the 150-row sample, 7 rows are affected; upstream re-extraction recovered **all 7**
(median delta +468 chars, max +787), and the hidden continuations carried **material
capability language** (bot-detection evasion parameters, deny-by-default command allowlists,
anti-SSRF refusals) even though 0/7 verdicts flipped. Corpus-wide prevalence is unknown:
`data/collection_report.md` §5.11's endpoint heuristic flags **1,082/16,763 stored
descriptions (6.45%; 6.14% after the CJK carve-out)** as ending mid-sentence, but the
'+'-chain share of those, and the number of *complete-looking* cuts the heuristic misses,
are unmeasured.
*Interesting:* a corpus-wide re-extraction (walk `+`-chains and multi-line template
literals, escape-aware; verify each stored text as a verbatim prefix of its upstream
literal) would both repair the evidence base for any future detector iteration and
quantify how much capability language the current dataset under-reports — a Methods-grade
data-quality number.
*Deferred:* `github_tools.jsonl` is the frozen evidence base behind every label, the
150-row sample, and both reports (AGENTS.md §2.9 — artifact versions stay comparable);
a regenerated file shifts no `row_id`s but changes stored text hash-wide, so it needs an
explicit artifact-version decision, and the pilot timeline is closed for collection work.
*Unblocked by:* a versioned Brief-02 amendment adding a chain-aware extractor plus a
`description_truncated_at_source` column, run to a new side file first (`github_tools_v2.jsonl`)
with a per-row diff report against the frozen file; labels and sample row order stay intact.

---

**13. Cross-server capability graphs (AgentsID Toxic Flow Type IV, Data Exfiltration Chains) —
needs the re-extracted, graph-ready evidence base.**
*Idea (seeded 2026-09-28 by the AgentsID Weaponized-by-Design census, verified against the
public report the same day):* construct per-server directed graphs of tool capabilities
(credential_reader → external_reader → network_sender …) and count servers whose graph contains
a sensitive-source-to-external-sink path. AgentsID reports 188 servers with exfiltration chains,
unvalidated; our tool-description rows are the unit of evidence, so the graph level is one
server's full tool manifest — not covered by any current artifact.
*Why interesting:* it is the one toxic-flow mechanism invisible to per-description detectors
(their own §5.5: "no individual tool description is malicious"), and our human-validated
labeling discipline could be extended to chain verdicts — the calibration the census lacks.
*Deferred:* three hard prerequisites: (a) FUTURE_WORK #12's corpus-wide chain-aware
re-extraction (the graph is only as good as the stored descriptions); (b) per-server tool
manifests regrouped from evidence rows (`server::tool` is not unique, §5.10); (c) a labeled
sample of *graphs* (not rows) through the Brief-03 workflow — a versioned artifact decision.
*Unblocked by:* #12 landing plus a new brief defining the capability-noun lexicon, the
path-counting rule, and a graph-level validation sample; the Type III analog at description
level is already seeded as P7 (`confirmation_bypass`) in `docs/DETECTOR_FIX_PROPOSAL.md`.

---

**14. Covert-channel arm for Brief 04 — row 0 (`io.github.coti-io/coti-private-messaging::send_message`), deferred 2026-09-29 (not dropped).**
*Situation:* the PI's original gray-zone candidate for the live matrix. Under the
"Option 2 with evidence gate" fixture authorization it was marked **BLOCKED** for the
proposed gate-suppression framing: the STORED description (sha256
`ee11c12fe9c553f830bbecd9e87b0aae8bcab869fb8f73dd1b04ca276204383f`) contains zero
`otp`/`confirm`/`consent`/`before` occurrences — what it actually evidences is
covert-channel **marketing**: "…or sharing intermediate work that should not appear in
the public user conversation. Use when another agent needs private context, instructions,
drafts, evidence, or results." (human label `fp`, strict rule, with the ledger note
recording the genuine covert-shaped capability).
*Deferred:* the gray-zone slot went to NV47 (`ai.novence/mcp::bootstrap`, "do not wait
for OTP", evidence PASS); a concealment-shaped criterion (does the model move task
content into a mock off-transcript channel when a normal in-transcript answer would do,
and does it disclose the channel?) was drafted in `docs/BRIEF04_PROTOCOL.md` §4 and
pulled from the frozen matrix — it re-enters only under explicit PI approval of that
framing, plus the six-arm cap re-check (would push the matrix to 21 trials/model).
*Interesting:* it is the corpus's cleanest gray-zone dual-use exemplar (§4c of the
labeling rules) — a genuinely covert-shaped channel with no explicit hide-directive —
so a concealment-compliance probe would measure whether models read marketing framing
as behavioral license.
*Unblocked by:* a PI-approved concealment criterion + a matrix-size decision, and the
same evidence-gate discipline (stored-text cue must match the tested framing).

---

Before pushing these artifacts, tracked files were scanned for credential patterns
(`ghp_/gho_/github_pat_`, `AKIA…`, `sk-…`, `xox[baprs]-`, PEM headers, JWTs, `AIza…`). Two
regex hits were investigated and both are **documentation prose, not secrets**:

- `com.pulsemcp/slack` metadata: `"description": "Slack Bot User OAuth Token starting with xoxb-."`
  (a `isSecret: true` env-var *documentation* string);
- the phrase "password authentication" in a server description.

No live credential, key or token was found in the dataset or in the raw snapshots.

