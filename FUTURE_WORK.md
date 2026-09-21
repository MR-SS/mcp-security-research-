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

**8. Resumable crawling (cursor persistence).**
*Interesting:* the registry is far larger than expected — 7,766 unique servers after 20,000
per-version entries, with the cursor **still live at the 200-page brake**. A true census within
one process would take a long single run (and any interruption loses everything); persisting
`metadata.nextCursor` after each page would let a census be assembled across sessions and make
the raw snapshots appendable.
*Deferred:* adding a resume mode changes the provenance model (one snapshot dir would then span
several runs), which is a design decision for the PI, not a silent crawler change.
*Unblocked by:* a brief that specifies the snapshot layout for multi-run crawls + the authorisation
to raise `--max-pages` beyond 200.

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

## Security-scan note (2026-09-21, pre-publication)

Before pushing these artifacts, tracked files were scanned for credential patterns
(`ghp_/gho_/github_pat_`, `AKIA…`, `sk-…`, `xox[baprs]-`, PEM headers, JWTs, `AIza…`). Two
regex hits were investigated and both are **documentation prose, not secrets**:

- `com.pulsemcp/slack` metadata: `"description": "Slack Bot User OAuth Token starting with xoxb-."`
  (a `isSecret: true` env-var *documentation* string);
- the phrase "password authentication" in a server description.

No live credential, key or token was found in the dataset or in the raw snapshots.

