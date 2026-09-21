# Collection Report — Official MCP Registry Crawl (Mission Brief 01)

> Produced by `pilot/crawl_registry.py`. Every number below is computed from the frozen
> snapshots named in §1 — nothing is estimated or recalled (AGENTS.md §2.1). Detector outputs
> are **candidates, not verdicts** (AGENTS.md §2.3). This snapshot is a **prefix** of the
> registry, not a census: the 200-page brake was reached with the cursor still live (§5.1).
> v1 of this report (60-page run, 1,967 servers) is preserved in git commit `0429072`.

## 1. Provenance

| | |
|---|---|
| Current dataset run started (UTC) | `2026-09-21T11:19:07.746726+00:00` |
| Current dataset run finished (UTC) | `2026-09-21T11:24:33.737273+00:00` (wall clock 5 min 26 s) |
| Command | `python3 pilot/crawl_registry.py --max-pages 200 --probe-pages 1 --out data/servers.jsonl --raw-dir data/raw/registry` |
| Endpoint | `GET https://registry.modelcontextprotocol.io/v0/servers` — params `limit=100`, `cursor` from `metadata.nextCursor` |
| Raw snapshot (current) | `data/raw/registry/20260921T111907Z/` — 200 × `page-NNN.json` + 1 × `probe-001.json` + `crawl_meta.json` (19.0 MB) |
| Raw snapshot (earlier 60-page run, kept for drift comparison) | `data/raw/registry/20260921T111217Z/` — 60 pages + probe + meta (6.2 MB) |
| `data/servers.jsonl` | 3,685,409 bytes · sha256 `65022f3e2c6ba4e7785543e17c2867d254e2513b66576722621c4b9fcc7b92d8` |
| `data/analysis.csv` | sha256 `7091455e2cec4f13068441c17dbf530c774514ab48ed47dc685545446450648f` |
| Python / deps | CPython 3.11.11 · `requests` 2.34.2 (stdlib + `requests` only, AGENTS.md §2.7) |
| Git stamp at capture | `0429072-dirty` — repo initialised 2026-09-21; checkpoint commit `0429072` precedes this crawl |
| **External spend** | **$0.00** — public unauthenticated GETs, no API key, no credential, no third-party server endpoint contacted |

Raw-page fidelity was verified byte-for-byte **for both snapshots**: each `page-001.json`
(sha256 `69f471324a5fb032b4e09a249350094cbd40efd8b0b023b60681816a6a21ca80`, identical across
runs) equals a fresh live `GET ?limit=100` of the same page. The registry head was therefore
stable across the whole session, which is why the two snapshots are drift-comparable.

## 2. Collection scale

| Metric | Value |
|---|---|
| Pages fetched | **200** (100 entries/page) — the pre-authorised hard brake |
| Entries seen (per-version, pre-dedupe) | **20,000** |
| **Unique servers after `isLatest` dedupe** | **7,766** |
| Kept by dedupe | **38.8%** of entries |
| Entries that replaced an earlier same-name record | 10,451 |
| Entries dropped as older non-latest versions | 1,783 |
| Structural anomalies | **0** — every entry carried `server.name`; no retries, no malformed page |
| Exhaustion probe (page 201) | 100 entries returned → **cursor still live** |

Reconciliation: 7,766 + 10,451 + 1,783 = **20,000** entries ✓

**Why 20,000 entries become 7,766 servers.** The registry paginates **per version**
(`metadata.nextCursor` is a `<name>:<version>` key), so the stream interleaves releases of the
same server — a **2.58× inflation factor** for anyone counting entries instead of deduping.
The effect is uneven: pages 5–12 added no new name at all, while pages 33–41 added 474
(886 → 1,360) and pages 130–140 added ~1,600. The Methods section must state the dedupe rule
explicitly, because "number of MCP servers" is otherwise off by more than 2×.

**One retained server is `is_latest=false`:** `dev.eusend/eusend` v0.5.0 — none of its
registry entries is flagged latest, so the fallback rule (§5.7) selected it. This is the only
row in 7,766 where the fallback decided the outcome, and it is harmless at this rate, but it
means the dataset is not *purely* `isLatest`-filtered.

## 3. Composition of the 7,766 unique servers

| Property | Servers | Share |
|---|---|---|
| `repository.url` present | 3,677 | **47.3%** |
| … of those, `github.com` | 3,652 | **47.0%** |
| Package-based (`packages[]` non-empty) | 1,216 | 15.7% |
| Remote-based (`remotes[]` non-empty) | 6,936 | **89.3%** |
| Both package and remote | 418 | 5.4% |
| Neither (metadata-only listing) | 32 | 0.4% |

Remote transport types (a server may expose several remotes): `streamable-http` **6,968**,
`sse` **191**. The ecosystem is overwhelmingly **remote/HTTP** rather than package-install,
which matters for the threat model: a remote server's tool descriptions can change at any
time with no install-time signal (rug-pull / description-drift exposure), and the
`repository.url` we rely on for GitHub enrichment covers only 47% of it.

`status` among retained servers: `active` 7,718 (99.4%), `deprecated` 48.
Across all 20,000 raw entries: `active` 19,702, `deprecated` 298.

Namespace labels (first segment of the reverse-DNS name): `com` 5,010 (64.5%) · `ai` 1,495
(19.3%) · `app` 532 (6.9%) · `co` 162 · `dev` 136. The namespace mix changed substantially
with depth (the 60-page prefix was 76% `ai.*`), which is a concrete reason why
head-of-cursor subsampling is not representative — see §4.

## 4. Detector rates across crawl depths — and the framing decision

| Metric | Pilot (2 pages, n=108) | 60-page run (n=1,967) | Current (200 pages, n=7,766) |
|---|---|---|---|
| ≥1 dangerous-capability pattern | 18.5% | 7.1% | **6.2%** |
| ≥1 poisoning-pattern candidate | 1.9% | 4.2% | **2.6%** |
| GitHub-linked | 46.3% | 51.1% | **47.0%** |

**Decision taken (PI, 2026-09-21).** The pilot success criterion "≥15% of servers with
dangerous capabilities" is **retired**, and there will be **no pivot to the ASI03
privilege/scope angle**. Rationale recorded at decision time:

1. Registry **server-level descriptions are short marketing text** — a few dozen words written
   to sell the server. Sentence-level regexes have almost nothing to bite on, so the headline
   percentage measures prose style more than capability. The real poisoning surface is **tool
   descriptions**, which Brief 02 (`fetch_github.py`) extracts from source.
2. The pilot figure was **not a sample** — it was the head of the cursor order, and it is
   biased. The rate drifts 18.5% → 7.1% → 6.2% as the crawl deepens, and the poisoning rate is
   non-monotonic (1.9% → 4.2% → 2.6%). A number that keeps moving with crawl depth is not a
   finding about the ecosystem; it is a finding about sampling.
3. Therefore the contribution is stated as **per-class composition at scale** (below) plus
   **validated detector precision** (Brief 03) and the tool-level surface (Brief 02) — not as
   a single headline percentage.

**This delta is itself a Methods-section contribution:** registry cursor order is not random,
so head-of-cursor slices of MCP registries are biased, and any prior or future work that
crawls "the first N pages" will over-estimate dangerous-capability prevalence. Quantified here
as: 18.5% (first 2 pages) vs 6.2% (first 200 pages) on identical detectors.

**Detector output at 7,766 servers** (`data/analysis.csv`, all still candidates):

*Dangerous-capability classes* — `secret_env_access` 251 (3.2%) · `network_egress` 182 (2.3%) ·
`shell_execution` 24 (0.3%) · `database_write` 23 (0.3%) · `file_read_sensitive` 12 (0.2%) ·
`file_write_delete` 4 (0.1%) · `package_install` 2 (0.0%). Total ≥1 flag: **480 (6.2%)**,
i.e. the surface is dominated by *credential-adjacent* and *network* access rather than
shell/file destruction — a composition statement, which is what the decision above asks for.

*Poisoning-pattern candidates* — `imperative_to_model` 128 (1.6%) · `exfiltration_language`
38 (0.5%) · `fake_system_role` 21 (0.3%) · `stealth_concealment` 10 (0.1%) ·
`sensitive_file_target` 1 (0.0%) · `cross_tool_shadowing` 1 (0.0%). Total ≥1 flag: **199 (2.6%)**.

**A caution that Brief 03 must settle.** The 15 highest-`suspicion_score` rows were inspected
by hand for the first time during this brief. Every one of them is a **plausible false
positive**: a marketing URL tripping `exfiltration_language` (`https?://\S+`), "never a safety
score" and "Never spends" tripping `imperative_to_model` (`\bnever\b`), "for your assistant:"
tripping `fake_system_role` (`\bassistant[,:]`), "check a document for hidden text" tripping
`stealth_concealment` (`\bhidden\b`), and a *security-auditing* server (`com.opzyai/mcp`,
"secrets, .env exposure, git-history leaks, CVEs") tripping `sensitive_file_target`. The
maximum `suspicion_score` in the whole 7,766-row queue is only **4**, so there is no high-score
tail to lean on. This is informal triage, not the validation protocol — Brief 03 owns the
rubric and the numbers — but it is strong prior evidence that precision will be low and that
**no case study may be built from `analysis.csv` without manual validation** (AGENTS.md §2.3).

## 5. Limitations and anomalies

**5.1 Still a prefix, not a census.** The 200-page brake was reached with the cursor live
(probe page 201 returned 100 entries), so the registry holds **more than 20,000 per-version
entries** and 7,766 is a **lower bound** on unique servers. The page cap was pre-authorised at
200; continuing is a one-flag change (`--max-pages N`, ~1.5 s/page, $0) and needs a new
authorisation. Every claim must read "the first 20,000 registry entries (cursor order)".
The honest conclusion is that **the ecosystem is bigger than any previous estimate in this
repo**: 108 → 1,967 → 7,766 unique servers, each checkpoint still short of exhaustion.

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
(5 min 26 s for 200 pages) against a live, concurrently-updated collection. Keyset pagination
during inserts can in principle skip or duplicate entries; the crawl makes no attempt to
correct for that, and both snapshots are therefore "as observed", not point-in-time. The two
snapshots on disk (60-page and 200-page) permit a first drift check: the registry head was
byte-stable across the session (§1), but no per-server drift analysis has been done
(`FUTURE_WORK.md` item 3).

**5.6 Git stamp — resolved.** The working tree is now a git repository (initialised
2026-09-21 at the project root where `AGENTS.md` lives), so the AGENTS.md §2.6 git-status
stamp is satisfied: this crawl recorded `0429072-dirty` (checkpoint commit `0429072` plus the
uncommitted crawl artifacts). Raw API snapshots **are** version-controlled (19.0 MB + 6.2 MB),
so the dataset — not just the code — is reproducible from the repo.

**5.7 Dedupe rule.** For each name we keep `isLatest=true`; if no entry is flagged latest we
fall back to the lexicographically newest `version` string. That fallback fired exactly
**once** in 7,766 servers (`dev.eusend/eusend`, §2), so the rule is documented but not load-bearing.

**5.8 Version strings are not semver-compared,** which only matters for the fallback in §5.7.

**5.9 Rate/latency variance.** The registry intermittently slowed from ~1.5 s/page to ~11 s/page
with no HTTP errors and no retries, then recovered. Timing is therefore not a stable
reproducibility property; content is (see §6). If a future run appears stalled, check the log
before assuming a hang.

## 6. Reproducing these numbers

```bash
# from the repository root
sha256sum data/servers.jsonl     # expect 65022f3e…7b92d8
python3 /tmp/collection_stats.py                 # composition table in §3
python3 pilot/analyze.py --inp data/servers.jsonl --out data/analysis.csv   # §4 detector numbers
python3 pilot/crawl_registry.py --max-pages 2 --probe-pages 1 \
        --out /tmp/replay.jsonl --raw-dir /tmp/replay   # live re-crawl check
```

Determinism evidence: `pilot/analyze.py` was run twice over the frozen snapshot and both runs
produced byte-identical output (`7091455e2cec4f13068441c17dbf530c774514ab48ed47dc685545446450648f`).
Re-running the *crawl* is not expected to be byte-identical — the registry is live. Determinism
is therefore claimed **over the frozen snapshot**, which is exactly why `data/raw/` exists and
is committed.

## 7. Acceptance criteria — Brief 01

| Criterion | Status | Evidence |
|---|---|---|
| `data/servers.jsonl` ≥1,500 unique servers, or documents why fewer | ✅ **PASS** | **7,766** unique servers (§2), sha256 `65022f3e…7b92d8` |
| Raw snapshot on disk | ✅ **PASS** | `data/raw/registry/20260921T111907Z/` — 200 pages + probe + `crawl_meta.json`; byte-fidelity verified (§1) |
| Re-running analysis reproduces identical counts | ✅ **PASS** | two `analyze.py` runs → identical sha256 (§6); caveat: the crawl itself is not re-runnable against a live registry (§5.5) |
| Collection report committed | ✅ **PASS** | this file is under version control (repo initialised 2026-09-21, §5.6) |
| Don't add secondary registries | ✅ honored | official registry only (§5.2) |
| Don't hit any server endpoint — registry API only | ✅ honored | no `remotes[]` contacted; registry GETs only (§5.3) |

**Spend:** $0.00 against the $50 pilot cap (all crawls, probes and re-checks this session).
**Open item:** the 200-page brake (§5.1) — a true census needs another run with a higher cap.

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



