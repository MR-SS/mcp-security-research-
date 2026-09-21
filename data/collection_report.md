# Collection Report — Official MCP Registry Crawl (Mission Brief 01)

> Produced by `pilot/crawl_registry.py`. Every number below is computed from the frozen
> snapshots named in §1 — nothing is estimated or recalled (AGENTS.md §2.1). Detector outputs
> are **candidates, not verdicts** (AGENTS.md §2.3). This snapshot is a **prefix** of the
> registry, not a census: the 600-page brake was reached with the cursor still live (§5.1).
> Earlier reports (60-page run, 1,967 servers; 200-page run, 7,766 servers) are preserved
> in git history (`0429072`, `beceb9d`, `6cca247`) and summarised in the depth series in §4.

## 1. Provenance

| | |
|---|---|
| Current dataset run started (UTC) | `2026-09-21T11:52:32.875924+00:00` |
| Current dataset run finished (UTC) | `2026-09-21T12:09:53.660976+00:00` (wall clock 17 min 21 s) |
| Command | `python3 pilot/crawl_registry.py --max-pages 600 --probe-pages 1 --out data/servers.jsonl --raw-dir data/raw/registry` |
| Endpoint | `GET https://registry.modelcontextprotocol.io/v0/servers` — params `limit=100`, `cursor` from `metadata.nextCursor` |
| Raw snapshot (current) | `data/raw/registry/20260921T115232Z/` — 600 × `page-NNN.json` + 1 × `probe-001.json` + `crawl_meta.json` (64 MB) |
| Raw snapshot (earlier runs, kept for drift comparison) | `data/raw/registry/20260921T111217Z/` — 60 pages + probe + meta (6.2 MB); `data/raw/registry/20260921T111907Z/` — 200 pages + probe + meta (19.0 MB) |
| `data/servers.jsonl` | 8,196,508 bytes · sha256 `be197ec0c56445796fd1f2024de739726a2537dfb32775b29957b1d000ed993c` |
| `data/analysis.csv` | sha256 `2d0a58c17549bb50858eadfd98e43c10f8f152dea08957f392abee228023b76a` · rules v2 (`model_addressed` added; v1 frozen at `6cca247`) |
| Python / deps | CPython 3.11.11 · `requests` 2.34.2 (stdlib + `requests` only, AGENTS.md §2.7) |
| Git stamp at capture | `77b41af-dirty` |
| **External spend** | **$0.00** — public unauthenticated GETs, no API key, no credential, no third-party server endpoint contacted |

Raw-page fidelity was verified byte-for-byte **for both snapshots**: each `page-001.json`
(sha256 `69f471324a5fb032b4e09a249350094cbd40efd8b0b023b60681816a6a21ca80`, identical across
runs) equals a fresh live `GET ?limit=100` of the same page. The registry head was therefore
stable across the whole session, which is why the two snapshots are drift-comparable.

## 2. Collection scale

| Metric | Value |
|---|---|
| Pages fetched | **600** (100 entries/page) — the pre-authorised hard brake |
| Entries seen (per-version, pre-dedupe) | **60,000** |
| **Unique servers after `isLatest` dedupe** | **17,167** |
| Kept by dedupe | **28.6%** of entries |
| Entries that replaced an earlier same-name record | 36,636 |
| Entries dropped as older non-latest versions | 6,197 |
| Structural anomalies | **0** — every entry carried `server.name`; no retries, no malformed page |
| Exhaustion probe (page 601) | 100 entries returned → **cursor still live** |

Reconciliation: 17,167 + 36,636 + 6,197 = **60,000** entries ✓

**Why 60,000 entries become 17,167 servers.** The registry paginates **per version**
(`metadata.nextCursor` is a `<name>:<version>` key), so the stream interleaves releases of the
same server — a **3.49× inflation factor** for anyone counting entries instead of deduping
(2.58× at the 200-page checkpoint: version duplication grows with depth). The Methods section
must state the dedupe rule explicitly, because "number of MCP servers" is otherwise off by
more than 3×.

> Dedupe-rule check: all 17,167 retained rows are `is_latest=true` — the
> non-`isLatest` fallback did not fire once in this run (it had fired once at the 200-page
> checkpoint, `dev.eusend/eusend`, which has since gained a latest-flagged entry or been
> displaced). The dataset is therefore purely `isLatest`-filtered this time.

## 3. Composition of the 17,167 unique servers (ecosystem-composition figure inputs)

| Property | Servers | Share |
|---|---|---|
| `repository.url` present | 11,370 | **66.2%** |
| … of those, `github.com` | 11,288 | **65.8%** |
| Package-based (`packages[]` non-empty) | 7,170 | 41.8% |
| Remote-based (`remotes[]` non-empty) | 10,837 | **63.1%** |
| Both package and remote | 1,046 | 6.1% |
| Neither (metadata-only listing) | 206 | 1.2% |

Remote transport types (a server may expose several remotes): `streamable-http` **10,343
(60.2%)**, `sse` **809 (4.7%)**. Remote URL schemes: `https` 11,152 (65.0% of servers).
`status` among retained servers: `active` 16,919 (98.6%), `deprecated` 248. Across all
60,000 raw entries: `active` 59,152, `deprecated` 848.

Name namespaces (first segment of the reverse-DNS name), top 12 of **11,976** distinct:
`io.github.Evozim` 375 (2.2%) · `io.github.CSOAI-ORG` 354 (2.1%) · `ai.smithery` 213
(1.2%) · `io.github.cyanheads` 129 (0.8%) · `io.github.codespar` 127 (0.7%) ·
`app.wishpool` 125 (0.7%) · `io.github.Wxt-ai` 122 (0.7%) · `eu.ansvar` 106 (0.6%) ·
`com.a2awire` 102 (0.6%) · `io.github.Br0ski777` 101 (0.6%) · `ai.getvda` 94 (0.5%) ·
`io.github.WYRE-AI` 79 (0.5%).

Description lengths (chars): min 5 · p25 81 · **median 90** · p75 95 · max 100 · mean 85.1;
empty descriptions 0. **The schema caps descriptions at 100 chars** (max exactly 100 over
all 60,000 entries) — the structural reason Brief 03's hypothesis expects 0–15% server-level
precision.

⚠️ **Transport mix shifts with depth** (figure-relevant): any-remote 89.7% → **63.1%**,
any-package 15.7% → **41.8%**, GitHub-linked 47.0% → **65.8%** from the 200-page to the
600-page checkpoint. Pages 201–600 are package/GitHub-heavy (`io.github.*` namespaces
dominate the new top-12). Any transport-share claim must therefore be depth-qualified,
exactly like the detector rates in §4.

## 4. Detector rates across crawl depths — and the framing decision

| Metric | Pilot (2 pages, n=108) | 60-page run (n=1,967) | 200-page run (n=7,766) | Current (600 pages, n=17,167) |
|---|---|---|---|---|
| ≥1 dangerous-capability pattern | 18.5% | 7.1% | 6.2% | **8.8%** |
| ≥1 poisoning-pattern candidate | 1.9% | 4.2% | 2.6% | **1.8%** |
| GitHub-linked | 46.3% | 51.1% | 47.0% | **65.8%** |

**Decision taken (PI, 2026-09-21).** The pilot success criterion "≥15% of servers with
dangerous capabilities" is **retired**, and there will be **no pivot to the ASI03
privilege/scope angle**. Rationale recorded at decision time:

1. Registry **server-level descriptions are short marketing text** — a few dozen words written
   to sell the server (median 90 chars, hard-capped at 100 by the schema, §3).
   Sentence-level regexes have almost nothing to bite on, so the headline
   percentage measures prose style more than capability. The real poisoning surface is **tool
   descriptions**, which Brief 02 (`fetch_github.py`) extracts from source.
2. The pilot figure was **not a sample** — it was the head of the cursor order, and it is
   biased. The capability rate drifts 18.5% → 7.1% → 6.2% → **8.8%** as the crawl deepens
   (the uptick at 600 pages tracks the package/GitHub-heavy tail, §3), and the poisoning
   rate is non-monotonic (1.9% → 4.2% → 2.6% → **1.8%**). A number that keeps moving with
   crawl depth is not a finding about the ecosystem; it is a finding about sampling.
3. Therefore the contribution is stated as **per-class composition at scale** (below) plus
   **validated detector precision** (Brief 03) and the tool-level surface (Brief 02) — not as
   a single headline percentage.

**This delta is itself a Methods-section contribution:** registry cursor order is not random,
so head-of-cursor slices of MCP registries are biased, and any prior or future work that
crawls "the first N pages" will over- or under-estimate prevalence depending on where it
stops. Quantified here as: 18.5% (first 2 pages) vs 6.2% (first 200 pages) vs 8.8%
(first 600 pages) on identical v1 detectors -- and the *transport mix itself* shifts with
depth (89.7% to 63.1% remote, section 3), so even the denominator's character changes.

**Detector output at 17,167 servers** (`data/analysis.csv`, rules v2, all still candidates):

*Dangerous-capability classes (v1 rules)* -- `secret_env_access` 685 (4.0%) ·
`network_egress` 380 (2.2%) · `shell_execution` 358 (2.1%) · `database_write` 84 (0.5%) ·
`file_read_sensitive` 38 (0.2%) · `file_write_delete` 13 (0.1%) · `package_install` 7
(0.0%). Total with >=1 flag: **1,511 (8.8%)**. Note the composition change vs the 200-page
checkpoint: `shell_execution` rose 24 to 358 (0.3% to 2.1%), tracking the package-heavy tail
-- local-execution servers describe shells; remote-HTTP servers describe APIs.

*Poisoning-pattern candidates (v1 rules)* -- `imperative_to_model` 191 (1.1%) ·
`exfiltration_language` 60 (0.3%) · `fake_system_role` 27 (0.2%) ·
`stealth_concealment` 19 (0.1%) · `sensitive_file_target` 4 (0.0%) ·
`cross_tool_shadowing` 1 (0.0%). Total with >=1 flag: **302 (1.8%)**.

*Instruction-channel measurement (v2 `model_addressed`, reported separately -- NOT malice)* --
3,390 servers (19.7%) describe themselves as addressed to an agent/model:
`model_addressed` 3,371 (19.6%) · `second_person_imperative` 24 (0.1%).
This measures whether the instruction channel is *in use*, independently of intent: about
one server in five speaks to the model as its audience, while only ~2% trip any
poisoning-pattern candidate. The gap between "channel open" (19.7%) and "pattern flagged"
(1.8%) is itself a finding -- most agent-addressed prose is benign marketing.

**Brief 03 hypothesis on record (PI, 2026-09-21): precision approx 0-15% at server level.**
The verbatim false-positive analysis that Brief 03 must carry into `data/validation_report.md`:
substring overreach -- bare marketing URLs tripping `exfiltration_language`
(`https?://\\S+`), "never a safety score" / "Never spends" tripping `imperative_to_model`
(`\\bnever\\b`), "for your assistant:" tripping `fake_system_role` (`\\bassistant[,:]`),
"check a document for hidden text" tripping `stealth_concealment` (`\\bhidden\\b`), and a
*security-auditing* server (`com.opzyai/mcp`, "secrets, .env exposure, git-history leaks,
CVEs") tripping `sensitive_file_target`. Re-confirmed at 17,167: the top
`suspicion_score` rows are again all benign matches of the same kinds (including a new
score-5 top row, `io.github.78degrees/ghosthunt` -- "Find every leaked secret on your
machine", a credential-scanner flagged for describing credentials), and the queue's max
score is still only **5**. **No case study may be built from `analysis.csv` without manual
validation** (AGENTS.md section 2.3).

## 5. Limitations and anomalies

**5.1 Still a prefix, not a census.** The 600-page brake was reached with the cursor live
(probe page 601 returned 100 entries), so the registry holds **more than 60,000 per-version
entries** and 17,167 is a **lower bound** on unique servers. The page cap was pre-authorised at
600 (PI decision, 2026-09-21); the cursor is still live, so any continuation needs a new
authorisation. Every claim must read "the first 60,000 registry entries (cursor order)".
The honest conclusion is that **the ecosystem is bigger than any previous estimate in this
repo**: 108 → 1,967 → 7,766 → 17,167 unique servers, each checkpoint still short of exhaustion.
`FUTURE_WORK.md` item 8 (rolling census depth) records the standing plan for getting to exhaustion.

**5.2 No secondary registries, by design.** PulseMCP / mcp.so / Smithery were not touched
(brief `Don'ts`; PLAN.md §2). Coverage is official-registry-only, so servers published only
elsewhere are invisible. Parked in `FUTURE_WORK.md`.

**5.3 Registry API only.** No `remotes[]` endpoint was contacted and no server code was
executed (AGENTS.md §2.2). This dataset therefore contains **no tool descriptions** — only
server-level metadata. The tool-level poisoning surface is Brief 02's job.

**5.4 Detectors are heuristics.** Every percentage in §4 says "patterns consistent with", not
"these servers are malicious". The `analysis.csv` top rows are dominated by substring false
positives (§4), so expect low precision until Brief 03 reports it. Do not quote §4 rates
without the precision numbers.

**5.5 Single logical snapshot per run, over a mutating registry.** Each run takes minutes
(17 min 21 s for 600 pages) against a live, concurrently-updated collection. Keyset pagination
during inserts can in principle skip or duplicate entries; the crawl makes no attempt to
correct for that, and all snapshots are therefore "as observed", not point-in-time. The three
snapshots on disk (60-, 200- and 600-page) permit a first drift check: the registry head was
byte-stable across the session (§1), but no per-server drift analysis has been done
(`FUTURE_WORK.md` item 3).

**5.6 Git stamp — resolved.** The working tree is now a git repository (initialised
2026-09-21 at the project root where `AGENTS.md` lives), so the AGENTS.md §2.6 git-status
stamp is satisfied: this crawl recorded `77b41af-dirty`. Raw API snapshots **are** version-controlled
(64 MB + 19.0 MB + 6.2 MB),
so the dataset — not just the code — is reproducible from the repo.

**5.7 Dedupe rule.** For each name we keep `isLatest=true`; if no entry is flagged latest we
fall back to the lexicographically newest `version` string. That fallback fired **zero times**
in 17,167 servers (§2), so the rule is documented but not load-bearing.

**5.8 Version strings are not semver-compared,** which only matters for the fallback in §5.7.

**5.9 Rate/latency variance.** The registry intermittently slowed from ~1.5 s/page to ~11 s/page
with no HTTP errors and no retries, then recovered. Timing is therefore not a stable
reproducibility property; content is (see §6). If a future run appears stalled, check the log
before assuming a hang.

## 6. Reproducing these numbers

```bash
# from the repository root
sha256sum data/servers.jsonl     # expect be197ec0…993c
python3 /tmp/collection_stats.py                 # composition table in §3
python3 pilot/analyze.py --inp data/servers.jsonl --out data/analysis.csv   # §4 detector numbers
python3 pilot/crawl_registry.py --max-pages 2 --probe-pages 1 \
        --out /tmp/replay.jsonl --raw-dir /tmp/replay   # live re-crawl check
```

Determinism evidence: `pilot/analyze.py` was run twice over the frozen snapshot and both runs
produced byte-identical output (`2d0a58c17549bb50858eadfd98e43c10f8f152dea08957f392abee228023b76a`, rules v2).
Re-running the *crawl* is not expected to be byte-identical — the registry is live. Determinism
is therefore claimed **over the frozen snapshot**, which is exactly why `data/raw/` exists and
is committed.

## 7. Acceptance criteria — Brief 01

| Criterion | Status | Evidence |
|---|---|---|
| `data/servers.jsonl` ≥1,500 unique servers, or documents why fewer | ✅ **PASS** | **17,167** unique servers (§2), sha256 `be197ec0…993c` |
| Raw snapshot on disk | ✅ **PASS** | `data/raw/registry/20260921T115232Z/` — 600 pages + probe + `crawl_meta.json` (§1); earlier 60-/200-page snapshots retained |
| Re-running analysis reproduces identical counts | ✅ **PASS** | two `analyze.py` runs → identical sha256 (§6); caveat: the crawl itself is not re-runnable against a live registry (§5.5) |
| Collection report committed | ✅ **PASS** | this file is under version control (repo initialised 2026-09-21, §5.6) |
| Don't add secondary registries | ✅ honored | official registry only (§5.2) |
| Don't hit any server endpoint — registry API only | ✅ honored | no `remotes[]` contacted; registry GETs only (§5.3) |

**Spend:** $0.00 against the $50 pilot cap (all crawls, probes and re-checks this session).
**Standing items:** the 600-page brake still stopped short of exhaustion (§5.1) — `FUTURE_WORK.md` item 8 (rolling census depth) is the authorised path forward; week-6 re-crawl diff (item 3) reuses the same protocol.

## Appendix A — the §3 statistics snippet (verbatim)

```python
import json, collections

servers = [json.loads(l) for l in open('data/servers.jsonl', encoding='utf-8') if l.strip()]
n = len(servers)
repo = sum(1 for s in servers if s.get('repository_url'))
gh   = sum(1 for s in servers if 'github.com' in (s.get('repository_url') or ''))
pkg  = sum(1 for s in servers if s.get('packages'))
rem  = sum(1 for s in servers if s.get('remotes'))
bot  = sum(1 for s in servers if s.get('packages') and s.get('remotes'))
nei  = sum(1 for s in servers if not s.get('packages') and not s.get('remotes'))
tt   = collections.Counter(t for s in servers for t in (s.get('transport_types') or []))

print('unique servers           :', n)
print('with repository.url      : %d (%.1f%%)' % (repo, 100 * repo / n))
print('  of which github.com    : %d (%.1f%%)' % (gh, 100 * gh / n))
print('with packages[]          : %d (%.1f%%)' % (pkg, 100 * pkg / n))
print('with remotes[]           : %d (%.1f%%)' % (rem, 100 * rem / n))
print('with BOTH pkg+remote     : %d (%.1f%%)' % (bot, 100 * bot / n))
print('with NEITHER             : %d (%.1f%%)' % (nei, 100 * nei / n))
print('remote transport types   :', dict(tt))
print('statuses                 :', dict(collections.Counter(s.get('status') for s in servers)))
print('is_latest true           :', sum(1 for s in servers if s.get('is_latest')))
```

The `/tmp` helper scripts used this session (`collection_stats.py`, `census_checks.py`,
`top15.py`, `acceptance_check.py`) are throwaway analysis aids; the only maintained code is
`pilot/`. Reproduce §3 from the snippet above and §4 from `pilot/analyze.py`.



