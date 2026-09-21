# Collection Report — Official MCP Registry Crawl (Mission Brief 01)

> Produced by `pilot/crawl_registry.py` (extended for this brief). Every number below is
> computed from the frozen snapshot named in §1 — nothing is estimated or recalled
> (AGENTS.md §2.1). Detector outputs elsewhere in `data/` are **candidates, not verdicts**
> (AGENTS.md §2.3). This snapshot is a **prefix** of the registry, not a census — see §5.1.

## 1. Provenance

| | |
|---|---|
| Run started (UTC) | `2026-09-21T11:12:17.996634+00:00` |
| Run finished (UTC) | `2026-09-21T11:13:53.196421+00:00` |
| Command | `python3 pilot/crawl_registry.py --max-pages 60 --probe-pages 1 --out data/servers.jsonl --raw-dir data/raw/registry` |
| Endpoint | `GET https://registry.modelcontextprotocol.io/v0/servers` — params `limit=100`, `cursor` from `metadata.nextCursor` |
| Raw snapshot | `data/raw/registry/20260921T111217Z/` — 60 × `page-NNN.json` (verbatim bodies) + 1 × `probe-001.json` + `crawl_meta.json` |
| `data/servers.jsonl` | 925,222 bytes · sha256 `06dfa656544721d8e32a03d5629c8fc64a0ef7d87382c97553a02968852aafe5` |
| `data/analysis.csv` | sha256 `bf5d5f49938ef81cba58804ac5625c7c6bd1b7fe0882f56ac4f59bee46683afa` |
| Python / deps | CPython 3.11.11 · `requests` 2.34.2 (stdlib + `requests` only, AGENTS.md §2.7) |
| Git stamp | `unavailable (not a git repository)` — the working tree is not under version control (§5.6) |
| **External spend** | **$0.00** — 61 unauthenticated GETs, no API key, no credential, no third-party server endpoint contacted |

Raw-page fidelity was verified byte-for-byte: the saved `page-001.json` (sha256
`69f471324a5fb032b4e09a249350094cbd40efd8b0b023b60681816a6a21ca80`) is identical to a
fresh live `GET ?limit=100` of the same page.

## 2. Collection scale

| Metric | Value |
|---|---|
| Pages fetched | **60** (100 entries/page) |
| Entries seen (per-version, pre-dedupe) | **6,000** |
| **Unique servers after `isLatest` dedupe** | **1,967** |
| Kept by dedupe | **32.8%** of entries |
| Entries that replaced an earlier same-name record | 3,494 |
| Entries dropped as non-latest older versions | 539 |
| Structural anomalies | **0** — every entry carried `server.name`; no malformed pages, no retries needed |
| Exhaustion probe (page 61) | 100 entries returned → **cursor still live** |

Reconciliation: 1,967 + 3,494 + 539 = **6,000** entries ✓

**Why 6,000 entries become 1,967 servers.** The registry paginates **per version**
(`metadata.nextCursor` is a `<name>:<version>` key), so the stream interleaves releases of
the same server. This is not a rounding detail — it is a 3.05× inflation factor for anyone
who counts entries instead of deduping. The effect is uneven: pages 5–12 delivered 1,200
consecutive entries without adding a single new server name (190 servers at both ends of that
block), while pages 33–41 added 474 new names (886 → 1,360). Methods section should state the
dedupe rule explicitly.

## 3. Composition of the 1,967 unique servers

| Property | Servers | Share |
|---|---|---|
| `repository.url` present | 1,009 | **51.3%** |
| … of those, `github.com` | 1,005 | **51.1%** |
| Package-based (`packages[]` non-empty) | 287 | 14.6% |
| Remote-based (`remotes[]` non-empty) | 1,764 | **89.7%** |
| Both package and remote | 91 | 4.6% |
| Neither (metadata-only listing) | 7 | 0.4% |

Remote transport types (a server may expose several remotes): `streamable-http` **1,770**,
`sse` **52**. So the ecosystem is overwhelmingly **remote/HTTP**, not package-install —
which matters for the threat model: a remote server's tool descriptions can change at any
time without any install-time signal (rug-pull / description-drift exposure), and the
`repository.url` we rely on for GitHub enrichment covers only about half of it.

`status` among unique servers: `active` 1,950 (99.1%), `deprecated` 17.
Across all 6,000 raw entries: `active` 5,940, `deprecated` 60.

Namespace labels (first segment of the reverse-DNS name): `ai` 1,495 · `app` 456 ·
`agency` 6 · `ac` 3 · `al` 2 — i.e. 76.0% of the snapshot lives under `ai.*`, which is a
naming convention, not a quality signal.

## 4. Pilot (n=108) vs full prefix (n=1,967)

| Metric | Pilot (first 2 pages) | Full prefix (60 pages) |
|---|---|---|
| Unique servers | 108 | 1,967 |
| ≥1 dangerous-capability pattern | 18.5% | **7.1%** |
| ≥1 poisoning-pattern candidate | 1.9% | **4.2%** |
| GitHub-linked | 46.3% | **51.1%** |

⚠️ **The headline number moved in the wrong direction for the pilot's success criterion.**
PLAN.md §3 ticked "≥15% servers with dangerous capabilities → the story exists" on the
strength of the 108-server head-of-cursor sample; over 1,967 servers the same detectors flag
**7.1%**. The two samples are not equivalent (the pilot was a non-random head of the cursor
order, and the dangerous-capability rate clearly varies along that order), so the pilot
figure should not be quoted as an ecosystem estimate. This is a framing decision for the
human, not something the crawler should paper over; it is flagged in PLAN.md §3/§5.

The refreshed triage queue is `data/analysis.csv` (1,967 rows, sorted by `suspicion_score`).
Top capability classes: `secret_env_access` 73 (3.7%), `network_egress` 50 (2.5%),
`shell_execution` 12 (0.6%), `database_write` 5 (0.3%), `file_read_sensitive` 2 (0.1%),
`file_write_delete` 1 (0.1%). Poisoning-pattern candidates: `imperative_to_model` 56 (2.8%),
`exfiltration_language` 14 (0.7%), `fake_system_role` 10 (0.5%), `stealth_concealment` 3
(0.2%). These remain **candidates pending Brief 03 manual validation**.

## 5. Limitations and anomalies

**5.1 This is a prefix, not a census.** The exhaustion probe (page 61) returned another
100 per-version entries, so `cursor_exhausted = false`: the registry holds **more than
6,000 per-version entries**, and 1,967 is a **lower bound** on the number of unique servers.
Brief 01 specifies `--max-pages 60`, so the crawl stopped there by design. Any paper claim
must therefore read "the first 6,000 registry entries (cursor order)" — not "the registry".
Raising the cap is a one-flag change (`--max-pages N`) costing $0 and ~1.4 s/page; it was
**not** done unilaterally, because the page cap is an explicit brief/scope decision
(AGENTS.md §2.4).

**5.2 No secondary registries, by design.** PulseMCP / mcp.so / Smithery were not touched
(brief `Don'ts`; PLAN.md §2). Coverage is official-registry-only, so any server published
only elsewhere is invisible here. Parked in `FUTURE_WORK.md`.

**5.3 Registry API only.** No `remotes[]` endpoint was contacted and no server code was
executed (AGENTS.md §2.2). Consequently this dataset contains **no tool descriptions** — only
server-level metadata. The tool-level poisoning surface is Brief 02's job
(`pilot/fetch_github.py`).

**5.4 Detectors are heuristics.** The §4 percentages say "patterns consistent with", not
"these servers are malicious". Several capability patterns are deliberately broad
(`\btokens?\b`, `\bfetch\b`), so expect false positives until Brief 03 reports precision —
the `imperative_to_model` class fires on ordinary English ("never a safety score"), visible
in the top rows of `data/analysis.csv`.

**5.5 Single snapshot.** Rug-pull / description drift (taxonomy item 4) cannot be observed in
one crawl. The UTC-stamped raw snapshots are the substrate for a future diff-based
measurement (`FUTURE_WORK.md` item 3).

**5.6 No git repository.** `git rev-parse` fails in this working tree, so every artifact is
stamped `git: unavailable (not a git repository)` and "committed" here means "written to
`data/`", not "in a VCS". AGENTS.md §2.6 asks for a git-status stamp; that requirement is
**not satisfied** and needs a human decision (initialise a repo, or amend the rule). The
timestamp + input/output sha256 stamps do work and are recorded in
`data/raw/registry/20260921T111217Z/crawl_meta.json`.

**5.7 Dedupe rule.** For each name we keep `isLatest=true`; if no entry is flagged latest we
fall back to the lexicographically newest `version` string. All 1,967 retained servers carry
`is_latest=true`, so the fallback path decided nothing in this run.

## 6. Reproducing these numbers

```bash
# from the repository root
sha256sum data/servers.jsonl            # expect 06dfa656…52aafe5
python3 /tmp/collection_stats.py        # composition table in §3 (verbatim source: Appendix A)
python3 pilot/analyze.py --inp data/servers.jsonl --out data/analysis.csv   # §4 detector numbers
python3 pilot/crawl_registry.py --max-pages 2 --probe-pages 1 \
        --out /tmp/replay.jsonl --raw-dir /tmp/replay   # re-crawl check (the live registry will have moved)
```

Determinism evidence: `pilot/analyze.py` was run twice over the frozen snapshot and both runs
produced byte-identical output (`bf5d5f49938ef81cba58804ac5625c7c6bd1b7fe0882f56ac4f59bee46683afa`).
Re-running the *crawl* is not expected to be byte-identical — the registry is live. The
2-page smoke test did reproduce the previously committed pilot `data/servers.jsonl`
byte-for-byte (`7ace596c4f7ce618dcb8ecdad0864cf835a606d48d4f340be08fc23998d097ed`), which
confirms the modified script is behaviour-preserving. Determinism is therefore claimed **over
the frozen snapshot**, which is exactly why `data/raw/` exists.

## 7. Acceptance criteria — Brief 01

| Criterion | Status | Evidence |
|---|---|---|
| `data/servers.jsonl` ≥1,500 unique servers, or documents why fewer | ✅ **PASS** | **1,967** unique servers (§2), sha256 `06dfa656…52aafe5` |
| Raw snapshot on disk | ✅ **PASS** | `data/raw/registry/20260921T111217Z/` — 60 pages + probe + `crawl_meta.json`; byte-fidelity verified (§1) |
| Re-running analysis reproduces identical counts | ✅ **PASS** | two `analyze.py` runs → identical sha256 (§6); caveat: the crawl itself is not re-runnable against a live registry (§5.5, §6) |
| Collection report committed | ✅ **PASS (caveat)** | this file; "committed" = present in `data/`, since no VCS exists (§5.6) |
| Don't add secondary registries | ✅ honored | official registry only (§5.2) |
| Don't hit any server endpoint — registry API only | ✅ honored | no `remotes[]` contacted; 61 GETs to `registry.modelcontextprotocol.io` only (§5.3) |

**Spend:** $0.00 of the $50 pilot cap. **Brief 01 outcome:** the ≥1,500-server bar is met, so
the brief passes; the two items needing human attention are the §4 rate revision
(18.5% → 7.1%) and the §5.1 prefix limitation.

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

The output of this snippet plus the `pilot/analyze.py` run is what populates §2–§4; the same
file is kept at `/tmp/collection_stats.py` for the duration of this session.

