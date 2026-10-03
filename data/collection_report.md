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

- **ListTools `unnamed` family:** the `listtools:unnamed` extraction family includes tool
  descriptions harvested from live ListTools responses, with some argument-level text
  mixed in (validation-sample rows **103, 122, 133, 141, 148**). These are not necessarily
  standalone tool descriptions; the family is an extraction-provenance/data-quality caveat.
- **Registry metadata inconsistency:** validation-sample row **130** has registry server
  name `ecommerce-intelligence-mcp-server` but manifest name `redfin-mcp-server'`. Record identity
  cannot be assumed consistent across registry metadata and the fetched manifest.

**5.10 Duplicate-registration census — `server::tool` is not a unique key.** *(added 2026-09-27T11:50Z, commit `4d347fc`)*
In `data/github_tools.jsonl` (16,763 rows): **(a)** 1,484 distinct full names
(`server_name::tool_name`) appear on 2+ evidence rows; **(b)** 1,092 of those (73.6%) are
`generic:unnamed` registrations; **(c)** top-5 duplicated names: `com.smartbear/smartbear-mcp::readme:unnamed`
(20 rows), `com.files/python-mcp::generic:unnamed` (19), `com.keboola/mcp::generic:unnamed` (19),
`com.scanmalware.mcp/scanmalware-mcp::decorator:unnamed` (19), `io.github.aahl/mcp-notify::generic:unnamed`
(19); **(d)** descriptions **differ** across rows for 1,327 of the 1,484 duplicated names (89.3%),
are identical for 157. Example pair for `com.keboola/mcp::generic:unnamed`:
"Text of the answer to a documentation query." and
"List of URLs to the sources of the answer."
A full name alone cannot identify an evidence row. For sampled rows 21 and 33,
matching the sampled description resolves each to one evidence record; this is
not a uniqueness guarantee for the entire sample.

Computed 2026-09-27T11:50:05Z; git-status stamp: `4d347fc-clean` before this correction.

**5.11 Upstream (source-level) truncation — stored `tool_description` text that ends mid-sentence.** *(added 2026-09-28T06:38Z, after commit `eb8a84c`)*

**Definition and level.** This census measures a *different* truncation level from the
CSV-cap one: here the stored `tool_description` **inside `data/github_tools.jsonl` itself**
is cut — i.e. the loss already happened **upstream of every artifact built from that file**
(during Brief 02's extraction/assembly of the evidence rows). A flagged row therefore shows
`[FULL TEXT]` in `label_sample.py` while genuinely missing its ending; by contrast, the
150-row validation sample's CSV-cap census (43/150 labeled rows sitting exactly on
`analyze.py`'s 300-char `description` cap, reported in `data/validation_report.md` §Truncation)
compares a 300-char **CSV display excerpt** against the stored full text — recoverable,
per-row, from `github_tools.jsonl`. Three levels, in short: (1) CSV display cap
(recoverable, `label_sample.py` diagnoses it per row), (2) **upstream source-level cut in the
stored text (this census, unrecoverable from the repo alone)**, and (3) the terminal's 1,500-char
`DISPLAY_LIMIT` (cosmetic, text untouched on disk).

**Heuristic (a proxy, not a verdict — AGENTS.md §2.3).** A non-empty description whose last
non-space character is neither a letter nor one of the terminal marks `.! ?)]}"'` is flagged;
additionally, a description whose final word is a trailing function word (`until, and, or, to,
with, the, a, an, of, for, if, when, from, by, than, that, then, its, their, which, while,
into, via, per, before, after, between, through, without, within`) is flagged (spec-named
signals are `until/and/to/with`). Known false-positive buckets, disclosed up front: **52 rows
end in `。`** — a legitimate CJK sentence terminator the Latin-punctuation heuristic does not
know — so the CJK-adjusted count is the better estimate; a few rows end in digits/equations
(`0` 20, `6` 14, `4` 12), which are plausibly legitimate; and 2 rows end in `…` (self-marked
elision, arguably intentional). Conversely the function-word rule *misses* cuts that happen to
land on a complete-looking word (e.g. a dangling noun), so both directions of error exist and
the number is a **lower bound on true upstream cuts**.

**Census numbers** (over all 16,763 evidence rows; **0** empty descriptions):

| Metric | Value |
|---|---|
| Evidence rows (`github_tools.jsonl`) | 16,763 (distinct stored descriptions 15,832) |
| **Flagged rows (heuristic as specified)** | **1,082 (6.45%)** |
| Flagged **distinct descriptions** | 1,024 |
| Flagged after CJK-terminator carve-out (better estimate) | **1,030 (6.14%)** |
| Primary-signal bucket: non-terminal punctuation | 786 rows — `,` 276 · `\` 151 · `:` 99 · `(` 27 · `=` 18 · `—` 16 · `[` 16 · `;` 12 · digits 60 · other 111 |
| Additional-signal bucket: trailing function word | 296 rows — `the` 61 · `for` 38 · `a` 32 · `to` 25 · `and` 24 · `or` 13 · `by` 13 · `with` 11 · `of` 10 · rest 69 |
| Known-benign subsets (disclosed) | `。` 52 · digit/equation endings ~46 · `…` 2 |
| Length distribution (all 16,763) | min 9 · p25 60 · median 89 · p75 122 · p95 285 · max 1,547 chars |
| Length distribution (flagged 1,082) | min 9 · p25 48 · median 79 · p75 99 · p95 278 · max 949 chars — flagged text is shifted **shorter** than the population, and 832/1,082 (77%) sit ≤ 100 chars: short rows are cut as often as long ones, so "short description = complete description" is not a safe assumption |

**Examples.**

1. **Trailing function word, `until`** — `ai.wpconvert/mcp::wpconvert_convert_folder`
   (source `packages/mcp/src/server.mjs`, 635 chars), the **stored text behind
   validation-sample row 23** (`fp`; note records the artifact):
   "…Once you have a jobId, poll wpconvert_check_status **until**" — cut mid-imperative.
2. **Non-terminal punctuation, `,`** — `io.github.TomasLucasUTN/godot-mcp-bridge::get_guide`
   (source `mcp-server/src/meta-tools.ts`, 322 chars): "…testing a running game, choosing
   between the scene-editing tools**,**"
3. **Non-terminal punctuation, `\`** — `io.github.aistoragedepot-admin/aistoragedepot-mcp::search_library`
   (source `index.mjs`, 949 chars): "…Items marked **\\**" — a trailing backslash left by a
   line-based extractor.

**Cross-reference to the 150-row sample.** 7 of the 150 sample rows' recovered stored texts
are flagged by this heuristic (rows 23, 41, 53, 90, 96, 98, 120) — the row-23 `until` cut was
caught independently during closeout note fill and is recorded in its label note. These 7 rows
were labeled on descriptions that are missing their endings **at the source level**, a caveat
the CSV-cap census cannot see.

Producing command (verbatim; `python3`, stdlib only — AGENTS.md §2.7):

```bash
python3 - <<'PY'
import json
ALLOWED = set('.!?)]}"\'')
FUNC = {'until','and','or','to','with','the','a','an','of','for','if','when','from','by',
        'than','that','then','its','their','which','while','into','via','per','before',
        'after','between','through','without','within'}
def flag(d):
    core = d.rstrip()
    if not core: return None
    lc = core[-1]
    if not (lc.isalpha() or lc in ALLOWED):
        return ('punct', lc)
    words = core.split()
    if len(words) >= 2 and words[-1].lower() in FUNC:
        return ('funcword', words[-1].lower())
    return None
n = flagged = 0; buckets = {}
for line in open('data/github_tools.jsonl', encoding='utf-8'):
    if not line.strip(): continue
    d = json.loads(line).get('tool_description') or ''
    n += 1
    f = flag(d)
    if f: flagged += 1; buckets[f] = buckets.get(f, 0) + 1
print('rows', n, 'flagged', flagged, round(100*flagged/n, 2))
for k, v in sorted(buckets.items(), key=lambda x: -x[1]): print(k, v)
PY
```

**Re-extraction outcome (2026-09-28 validity pass).** All 7 sample rows flagged above were
re-judged on their **upstream-full** texts, recovered from the live public source files
(`raw.githubusercontent.com`, branch `main`, no token; HTTP 200 in 7/7 — the `master`
fallback never fired). Deltas vs the stored text: +28 (row 53), +50 (row 98), +62 (row 23),
+468 (row 120), +493 (row 90), +668 (row 96), +787 (row 41) — **median +468**. Three cut
mechanisms: (1) the extraction regex `[^"']{10,2000}` halting at the first embedded quote
(rows 23, 53, 96, 98 — visible cuts at `until`, `via`, `{status:`, `the`); (2) descriptions
authored as `+`-concatenated multi-fragment literals, truncated at the first fragment
boundary (rows 41, 90, 120); (3) extractor line residue (row 90's stored trailing `\`).
Every stored text matched its live-file anchor verbatim, so upstream drift is not a
confound for these 7. Verdicts: **0/7 flips — all 7 confirmed `fp` on the full text**
(row 120 is a zero-flag control and stays zero-flag); the sample's label counts are
unchanged. But the cuts demonstrably hid **material capability language** — row 41's
bot-detection evasion/impersonation parameters, row 98's deny-by-default WP-CLI allowlist,
row 90's anti-SSRF refusals — which is the materiality evidence for treating stored-cuts as
an evidence-quality defect rather than a cosmetic one (per-row judgments in
`data/labels.jsonl`; corpus-wide follow-up parked as `FUTURE_WORK.md` item 12).

Producing command (a)–(c):

```bash
python3 - <<'PY'
import json
from collections import defaultdict
names = defaultdict(list)
for line in open('data/github_tools.jsonl'):
    if line.strip():
        o = json.loads(line)
        names[f"{o['server_name']}::{o['tool_name']}"].append(o)
dups = {n: r for n, r in names.items() if len(r) > 1}
print('duplicated_names', len(dups))
print('generic_unnamed_duplicated_names', sum(1 for n in dups if n.endswith('::generic:unnamed')))
for n, r in sorted(dups.items(), key=lambda x: (-len(x[1]), x[0]))[:5]:
    print(f'{n} {len(r)}')
PY
```

Producing command (d):

```bash
python3 - <<'PY'
import json
from collections import defaultdict
desc = defaultdict(set)
for line in open('data/github_tools.jsonl'):
    if line.strip():
        o = json.loads(line)
        desc[f"{o['server_name']}::{o['tool_name']}"].add(o['tool_description'])
dups = {n: s for n, s in desc.items() if len(s) >= 2 or sum(1 for _ in s) >= 2}
dup_multi = {n: s for n, s in desc.items() if len([x for x in s]) >= 1 and len(s) >= 0}
rows = defaultdict(int)
for line in open('data/github_tools.jsonl'):
    if line.strip():
        o = json.loads(line)
        rows[f"{o['server_name']}::{o['tool_name']}"] += 1
dups = {n for n, c in rows.items() if c > 1}
print('descriptions_differ', sum(1 for n in dups if len(desc[n]) > 1))
print('descriptions_same', sum(1 for n in dups if len(desc[n]) == 1))
PY
```

**5.12 Unicode hidden-character scan — NFKC + Cc/Cf strip byte-diff over stored `tool_description`.** *(added 2026-09-28T13:10Z, at HEAD `69237e0`)*

Mirrors the hidden-character check (Type V in the AgentsID taxonomy) **on our own corpus**, so the paper can say "we also scanned" rather than citing the check from outside. Byte-level diff between the raw stored description and its NFKC-normalized form with Unicode category `Cc` (control) + `Cf` (format) characters removed — the codepoint classes that carry invisible payload (zero-width joiners, bidi overrides, soft hyphens, tag characters).

**Headline numbers (16,763 stored descriptions, `data/github_tools.jsonl`):**

- **Zero hidden characters found: 0 `Cc` and 0 `Cf` codepoints across the entire corpus** — the strip pipeline removes nothing, so no description-level concealment via control/format characters exists in the stored evidence base. Honest scope note: the extractor already collapses newlines (0 of 16,763 stored descriptions contain `\n`), so the one trivially-expected `Cc` class is absent **by extraction, not by absence upstream**; the finding is that *nothing beyond that* — no zero-width, bidi, soft-hyphen, or other format codepoint — hides in the stored text.
- **Byte delta (raw − normalized+stripped): 88 of 16,763 rows (0.52%) with a positive delta, totaling 436 B, max 20 B per description**; 0 rows show a negative delta (NFKC expansion). All 88 deltas come from **visible** fullwidth CJK punctuation folding (U+FF0C FULLWIDTH COMMA, U+FF08/U+FF09 FULLWIDTH PARENTHESES, U+FF1A FULLWIDTH COLON, U+FF1B FULLWIDTH SEMICOLON) — byte-length shrinks because the ASCII fold is narrower, not because anything was stripped.
- 119/16,763 rows are NFKC-changed at all; 31 of those with zero byte delta (exclusively U+2026 HORIZONTAL ELLIPSIS → `...`).

Top-10 rows by byte delta (per-codepoint detail in `data/unicode_scan.csv`):

| `server::tool` | delta | folded codepoints |
|---|---|---|
| `io.github.RollingGo-AI/hotelbooking::generic:unnamed` | 20 B | U+FF0C ×4, U+FF08 ×2, U+FF09 ×2, U+FF1A ×1 |
| `cn.pianam.mcp/devtools-mcp::decorator:unnamed` (4 evidence rows, §5.10 dup-key) | 18 B each | U+FF08/U+FF09 ×4, U+FF0C/U+FF1A/U+FF1B variants |
| `com.zhijipaipan/zhiji-bazi::bazi_compute` | 14 B | U+FF0C ×3, U+FF08, U+FF09, U+FF1A |
| `io.github.ascript-cn/ascript-mcp::listtools:unnamed` | 12 B | U+FF08 ×2, U+FF09 ×2, U+FF1A, U+FF0C |
| `cc.ssave/tiktok-instagram-downloader::generic:unnamed` | 10 B | U+FF08 ×2, U+FF09 ×2, U+FF0C |
| `cn.pianam.mcp/stock-mcp::decorator:unnamed` | 10 B | U+FF08 ×2, U+FF09 ×2, U+FF0C |
| `io.github.chenxiaofie/memory-mcp::listtools:unnamed` | 10 B | U+FF08 ×2, U+FF09 ×2, U+FF1A |

**Co-occurrence with our flags (150-row labeled sample only — detectors are NOT re-run corpus-wide):** 148/150 sample rows resolve via the exact `(server_name, tool_name)` + 300-char-prefix join (the 2 unresolved — `ca.swiftsign/mcp`, `com.frontiercrown.signer/nostr-signer` — are `generic:unnamed` name collisions, the §5.10 dup-key mechanism); 98/148 carry ≥1 detector flag; **exactly 1/148 sample rows has any byte delta — row 34 (`io.github.XZXZZX-Ai/bilibili-mcp::get_video_info`, the sample's only non-English row: 3× U+FF0C + 1× U+FF1A) — and it is a flagged row whose human label is `fp`** (the bilingual defensive guard, §5.9 / P6 seed). No hidden-byte co-occurrence with any human-confirmed TP row.

**Interpretation and caveats.** Negative result for the Type V mirror: in the official-registry population as stored, concealment-by-codepoint does not appear — in contrast to §5.11's upstream **truncation**, which demonstrably hides material capability language (a different mechanism: text absent from the stored view vs. text invisible within it). Scanner-blind classes stated honestly: visually confusable *letters* (Cyrillic homoglyphs, Mathematical Alphanumeric Symbols) are categories L/Sm, not Cc/Cf, and are **not** covered by this scan (detection-side question, parked with P6); and for the 1,082 §5.11-cut rows a hidden run upstream of the extractor's view cannot be ruled out — the corpus-wide re-extraction (FUTURE_WORK item 12) precedes any stronger claim.

Artifact: `data/unicode_scan.csv` (16,763 rows; columns `idx, server_name, tool_name, repo, raw_bytes, raw_chars, final_bytes, final_chars, byte_delta, char_delta, cc_stripped, cf_stripped, nfkc_changed, codepoints_stripped, has_hidden`), sha256 `4f9eccbb202e1e16efdfde2b8b31152b3edbd114d9954aee90bc4e46813da110`.

Producing command (a)+(b):

```bash
python3 - <<'PY'
import json, csv, unicodedata, hashlib
from collections import Counter

CC_CF = ('Cc', 'Cf')

scan, desc_by_idx = [], {}
with open('data/github_tools.jsonl') as f:
    for i, line in enumerate(f, 1):
        if not line.strip():
            continue
        o = json.loads(line)
        d = o.get('tool_description') or ''
        desc_by_idx[i] = d
        nf = unicodedata.normalize('NFKC', d)
        stripped = [c for c in nf if unicodedata.category(c) in CC_CF]
        keep = ''.join(c for c in nf if unicodedata.category(c) not in CC_CF)
        raw_b, final_b = len(d.encode('utf-8')), len(keep.encode('utf-8'))
        cc = sum(1 for c in stripped if unicodedata.category(c) == 'Cc')
        cps = Counter(f"U+{ord(c):04X}({unicodedata.category(c)})" for c in stripped)
        scan.append({
            'idx': i, 'server_name': o.get('server_name', ''), 'tool_name': o.get('tool_name', ''),
            'repo': o.get('repo', ''), 'raw_bytes': raw_b, 'raw_chars': len(d),
            'final_bytes': final_b, 'final_chars': len(keep), 'byte_delta': raw_b - final_b,
            'char_delta': len(d) - len(keep), 'cc_stripped': cc, 'cf_stripped': len(stripped) - cc,
            'nfkc_changed': nf != d, 'codepoints_stripped': ';'.join(f"{k}x{v}" for k, v in sorted(cps.items())),
            'has_hidden': raw_b > final_b,
        })

with open('data/unicode_scan.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(scan[0].keys()))
    w.writeheader()
    w.writerows(scan)
sha = hashlib.sha256(open('data/unicode_scan.csv', 'rb').read()).hexdigest()
print('rows_scanned', len(scan))
print('rows_hidden_byte_delta_gt0', sum(r['has_hidden'] for r in scan))
print('total_hidden_bytes', sum(r['byte_delta'] for r in scan))
print('unicode_scan_csv_sha256', sha)
PY
```

**5.13 P7 confirmation-bypass surface sizing — trigger-phrase scan + co-flag analysis.** *(added 2026-09-28T13:25Z, at HEAD `d7980b3`)*

Non-scoring sizing pass for the `confirmation_bypass` v3 candidate (P7 in `docs/DETECTOR_FIX_PROPOSAL.md`, seeded by AgentsID Toxic Flow Type III + the row 47 watch-item): the frozen corpus is scanned for the conservative 9-phrase literal trigger family (case-insensitive): `avoid redundant approv` · `skip verification` · `skip approv` · `not needed before` · `proceed without` · `do not wait for` · `without confirmation` · `no confirmation needed` · `unnecessary approval` (AgentsID's `unnecessary confirmation` variant is not in the family and was not scanned). Co-flagging is computed by **importing the frozen v2 detector** (`pilot/analyze.py::scan_text`) — rules are not re-implemented.

**Headline: 2 of 16,763 stored descriptions (0.012%) contain any trigger phrase — 2 distinct servers, 2 total hits.** Per-phrase row counts: `not needed before` 1 · `do not wait for` 1 · all seven others 0. Co-flag: **1 of the 2 rows carries an existing v2 flag**; 1 carries none. Both hits read benign:

- `[493] ai.novence/mcp::bootstrap` — *"Returns apiKey immediately — do not wait for OTP"* — co-flag `CAP:secret_env_access; POI:imperative_to_model` — this is the **row 47 evidence row itself** (human label `fp`, the vendor's verification-relaxed onboarding funnel).
- `[5682] finance.fibrous/fibx::generic:unnamed` — *"get_auth_status, get_balance, get_policy and get_quote are not needed before it"* — no existing flag — **dependency-ordering prose** (which API calls precede which), not gate suppression.

**Interpretation.** (1) Population contrast, mirroring §5.12's Type V result: confirmation-bypass phrasing is **effectively absent from the official-registry population** (2/16,763, both benign-shaped), where AgentsID reports Type III as "financially concentrated" with a top-6 CRITICAL rule (`security_bypass`, 482 findings) in its npm/PyPI corpus — different populations, honestly measured on both sides. (2) The proposed **confirmation-noun gate is measured-necessary**: the bare phrase `not needed before` fires on pure API sequencing (row 5682), so P7 without the noun requirement (`approval|confirmation|consent|OTP|2FA|verification|review` in-sentence) would add that FP; with the gate, row 5682 is suppressed. (3) With the gate, the class as specified fires on **exactly 1/16,763 stored descriptions — row 47, human-labeled `fp`** — so its measured precision prospect on this population is 0/1 at n=2, and its recall opportunity is equally ~0: the surface is too small to calibrate the class here. P7 therefore stays **non-scoring**, and its value is prospective (week-6 drift re-crawl; other populations) rather than cross-sectional. This measurement supersedes the earlier expectation that the class "stays silent on row 47 as stored" — it does not; see the corrected P7 (d).

Caveats: literal phrase family (no morphology beyond the `approv` stems), so paraphrases outside the family are unmeasured; stored-text caveat of §5.11 applies (cuts can hide continuations); `server::tool` is not a unique key (§5.10).

Artifact: `data/p7_bypass_scan.csv` (2 rows; columns `idx, server_name, tool_name, repo, phrases, n_phrase_hits, context, co_flag, rules_version, has_co_flag`), sha256 `c2a7903b04d1b5215ab5d944abb71aec95adce18251b1ee5d8ac2f2957e8650d`.

Producing command:

```bash
python3 - <<'PY'
import json, csv, re, hashlib, importlib.util
from collections import Counter

spec = importlib.util.spec_from_file_location('analyze', 'pilot/analyze.py')
analyze = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analyze)   # frozen v2 rules; imported, never re-implemented

PHRASES = ['avoid redundant approv', 'skip verification', 'skip approv', 'not needed before',
           'proceed without', 'do not wait for', 'without confirmation', 'no confirmation needed',
           'unnecessary approval']
rx = [(p, re.compile(re.escape(p), re.IGNORECASE)) for p in PHRASES]

rows, descs = [], []
with open('data/github_tools.jsonl') as f:
    for i, line in enumerate(f, 1):
        if not line.strip():
            continue
        o = json.loads(line)
        d = o.get('tool_description') or ''
        descs.append(d)
        hit = [(p, m.start()) for p, r in rx for m in r.finditer(d)]
        if hit:
            rows.append({
                'idx': i, 'server_name': o.get('server_name', ''), 'tool_name': o.get('tool_name', ''),
                'repo': o.get('repo', ''), 'phrases': ';'.join(p for p, _ in hit),
                'n_phrase_hits': len(hit),
                'context': d[max(0, hit[0][1] - 60):hit[0][1] + len(hit[0][0]) + 60].replace('\n', ' '),
                'co_flag': '', 'rules_version': 'v2 (imported pilot/analyze.py scan_text)',
                'has_co_flag': False,
            })

for r in rows:
    hits = analyze.scan_text(descs[r['idx'] - 1])
    cap = sorted(k.split(':', 1)[1] for k in hits if k.startswith('capability:'))
    poi = sorted(k.split(':', 1)[1] for k in hits if k.startswith('poison:'))
    adr = sorted(k.split(':', 1)[1] for k in hits if k.startswith('addressing:'))
    parts = []
    if cap: parts.append('CAP:' + ','.join(cap))
    if poi: parts.append('POI:' + ','.join(poi))
    if adr: parts.append('ADR:' + ','.join(adr))
    r['co_flag'] = '; '.join(parts)
    r['has_co_flag'] = bool(cap or poi or adr)

with open('data/p7_bypass_scan.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['idx', 'server_name', 'tool_name', 'repo', 'phrases',
                                      'n_phrase_hits', 'context', 'co_flag', 'rules_version', 'has_co_flag'])
    w.writeheader()
    w.writerows(rows)
sha = hashlib.sha256(open('data/p7_bypass_scan.csv', 'rb').read()).hexdigest()

per_phrase = Counter(p for r in rows for p in set(r['phrases'].split(';')))
print('rows_with_trigger_phrase', len(rows))
print('distinct_servers', len({r['server_name'] for r in rows}))
print('rows_with_co_existing_flag', sum(r['has_co_flag'] for r in rows))
for p in PHRASES:
    print(f"  {p!r}: {per_phrase.get(p, 0)}")
print('p7_bypass_scan_csv_sha256', sha)
PY
```

### 5.14 RQ1 candidate rate of the frozen detector (full corpus)

Producing command (frozen detector imported unchanged, stdlib only):

```bash
python3 pilot/derive_candidate_rate.py
```

The frozen v2 detector was re-run over **all 16,763 stored tool descriptions** (4,725
repositories) — the same population the 150-row validation sample was drawn from — to
answer RQ1's candidate-rate half directly. Headline results (persisted to
`data/candidate_rate_scan.csv`):

| Quantity | Value | Share of corpus |
|---|---|---|
| Rows with >=1 flag, any family | 4,128 | 24.63% |
| Rows with >=1 poison-family flag | 698 | 4.16% |
| Rows with >=1 capability-family flag | 1,892 | 11.29% |
| Rows with >=1 channel-family flag | 2,183 | 13.02% |
| Total flag instances (row, class) | 4,926 | — |

Largest classes by rows flagged: `model_addressed` 2,068 · `secret_env_access` 1,013 ·
`network_egress` 582 · `imperative_to_model` 436 · `exfiltration_language` 199. These are
the **candidate rate** the detector emits — an upper bound on triage work, not a claim
about poisoning prevalence. The validated text-support rate on the sampled candidates is
reported separately (`data/validation_family_split.csv`).

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

---

## 8. Tool-level delta (Mission Brief 02, 2026-09-22)

Brief 02 enrichment finished against `data/servers.jsonl` (sha256 `be197ec0…993c`).
Artifacts: `data/github_tools.jsonl` (16,763 tool-description rows),
`data/github_tools.jsonl.meta.json`, `data/github_tools.jsonl.visited.jsonl`.
Detector pass (rules v2, `level` column) was written to a side path so the frozen
server-level `data/analysis.csv` (sha256 `2d0a58c1…b76a`) was **not** touched:

```bash
cd pilot && python3 analyze.py \
  --inp ../data/servers.jsonl --tools ../data/github_tools.jsonl \
  --out /tmp/analysis_full.csv
```

All percentages below are over that output (17,167 server rows + 16,763 tool rows).
Detector outputs remain **candidates, not verdicts** (AGENTS.md §2.3).

### 8.0 Brief 02 acceptance checklist

| Item | Value | Producing command / source |
|---|---|---|
| Repos reached (distinct visited) | **6,330** | `python3 -c "…len({l.strip() for l in open('data/github_tools.jsonl.visited.jsonl')})"` → 6,330 (matches `meta.json` `visited_repos`) |
| Repos with ≥1 tool extracted | **4,725** | distinct `repo` in `data/github_tools.jsonl` |
| Yield among reached | **74.6%** (4,725/6,330) ≥ 60% criterion | as above |
| Yield among run-list (unique) | 53.0% (4,725/8,923) | `build_population()` unique repos = 8,923 (list len 9,339: 58 repos appear under multiple namespaces; max repeat `joeetdev/venture-estate` ×315) |
| Yield among all GitHub-linked repos | 48.3% (4,725/9,785) — below 60% → why-not arm §8.3 | `meta.json` `population.distinct_repos` |
| Median tools/repo (repos with tools) | **2** | `statistics.median` over per-repo tool counts in `github_tools.jsonl` |
| Mean tools/repo | 3.55 | same |
| Resume-integrity of visited log | **PASS (set semantics)** — 6,710 lines → 6,330 distinct (380 append-dup lines across 23 repos; dupes follow run-list multi-namespace repeats, not double-processing of distinct repos); every tool-repo ⊆ visited (0 leaks); `meta.visited_repos` == distinct set size | Counter over `.visited.jsonl`; set difference vs tool repos |
| Unvisited run-list repos (retryable) | **2,593** unique — ProxyError path deliberately does **not** mark visited (`fetch_github.py`) | `run_unique - visited`; this-run `meta.failures['http:ProxyError']=2600` (list-length accounting) |
| Quota at end | Unauthenticated `GET /rate_limit` now: limit **60**, remaining **60**, used 0 (fresh window; no token). During run: `meta.paused=null` → never hit `PAUSE_BELOW_REMAINING=500`. `api_calls_this_run=8458`. | `curl -sS https://api.github.com/rate_limit`; `meta.json` |
| API spend | **$0.00** | `meta.json` `spend_usd: 0.0` |
| Runtime (meta-recorded final run) | **17,665.5 s (4 h 54 m 26 s)** wall; `started_utc` 2026-09-22T05:21:58Z → `finished_utc` 2026-09-22T10:16:24Z | `meta.json` |
| Don'ts: no clone/execute; token env-only | honored | raw `raw.githubusercontent.com` reads only; token from `os.environ` |

### 8.1 (a) `model_addressed` prevalence — server vs tool

```bash
# from /tmp/analysis_full.csv (command in §8 header)
python3 -c "
import csv,collections
rows=list(csv.DictReader(open('/tmp/analysis_full.csv')))
for lvl in ('server','tool'):
    rs=[r for r in rows if r['level']==lvl]
    a=sum(1 for r in rs if int(r['n_addressing_flags'])>0)
    print(lvl, a, len(rs), round(100*a/len(rs),1))
"
```

| Level | ≥1 addressing flag | n | Share |
|---|---|---|---|
| Server | 3,390 | 17,167 | **19.7%** |
| Tool | 2,195 | 16,763 | **13.1%** |
| **Delta (tool − server)** | | | **−6.7 pp** |

Per-class: server `model_addressed` 3,371 + `second_person_imperative` 24;
tool `model_addressed` 2,080 + `second_person_imperative` 132.

**Finding:** the instruction channel is *less* open at tool level than server level
(−6.7 pp). Server-level marketing prose names the agent audience far more often than
functional tool docs; `second_person_imperative` is relatively richer on tools
(132 vs 24) — imperative tool text addresses *you* without always saying “agent”.
Channel-open still exceeds poison-flagged at both levels (19.7% vs 1.8% server;
13.1% vs 4.2% tool).

### 8.2 (b) Poisoning-pattern candidates at tool level

```bash
python3 -c "
import csv,collections
rows=[r for r in csv.DictReader(open('/tmp/analysis_full.csv')) if r['level']=='tool']
n=len(rows); c=collections.Counter()
any_=0
for r in rows:
    fs=[f for f in r['poison_flags'].split(';') if f]
    if fs: any_+=1
    for f in fs: c[f.split(':',1)[1]]+=1
print('any', any_, n, round(100*any_/n,1))
[print(k,v,round(100*v/n,2)) for k,v in c.most_common()]
"
```

| Class | Tool count | % of 16,763 tools |
|---|---|---|
| (≥1 poison flag) | **703** | **4.2%** |
| `imperative_to_model` | 438 | 2.61% |
| `exfiltration_language` | 202 | 1.21% |
| `cross_tool_shadowing` | 35 | 0.21% |
| `stealth_concealment` | 28 | 0.17% |
| `fake_system_role` | 17 | 0.10% |
| `sensitive_file_target` | 7 | 0.04% |

(Server comparison: 302/17,167 = 1.8% any-poison, §4.)

**Top-15 tool rows by `suspicion_score`** (from `/tmp/analysis_full.csv`, tool rows sorted score desc, name asc; description excerpt ≤160 chars):

| # | Score | name (`server::tool`) | repo | Flags (cap / poi) | Description excerpt |
|---|---|---|---|---|---|
| 1 | 10 | `io.github.coti-io/coti-private-messaging::send_message` | coti-io/coti-sdk-private-messaging | network_egress / exfil, imperative, stealth | Send a private encrypted message to another AI agent or wallet for private agent-to-agent messaging, encrypted communication between autonomous agents, hidden s… |
| 2 | 8 | `de.cernion/cernion-energy-tools::generic:unnamed` | energychain/cernion-energy-tools | network_egress, shell / exfil, imperative | Forwards a bounded process intent to the existing Cernion Process Intake action (prepareProcessIntent), which creates a pending_confirmation receipt only. Retur… |
| 3 | 7 | `ai.wiplash/wiplash::generic:unnamed` | Wiplash-ai/wiplash-mcp | shell / exfil, imperative | Read the public repository, issue, linked review, and test status for one Wiplash code-request post. Use get_post first to verify the category and understand th… |
| 4 | 7 | `co.workix/mcp::manifest:@workix/mcp` | facetoplace/Workix | secret_env / exfil, imperative | Remote jobs, freelance gigs and vacancies from 24 boards — Upwork, Freelancer.com, hh.ru, Kwork, RemoteOK, WeWorkRemotely, Adzuna and more — for AI agents over … |
| 5 | 7 | `com.mcpemails/emails::manifest:MCP Emails` | Albretsen/MCPEmails | secret_env / exfil, imperative | Hosted email for AI agents. Connect Gmail, Fastmail, iCloud, Yahoo, Zoho, Yandex or any IMAP/SMTP mailbox to Claude, Cursor and other MCP clients. Read, search,… |
| 6 | 7 | `io.github.SHREESHMAN/lineupify::generic:unnamed` | SHREESHMAN/lineupify | secret_env / exfil, imperative | Forget the saved Spotify login (deletes tokens.json). With purge: true also deletes everything Lineupify keeps on disk: config, caches, drafts and exports; purg… |
| 7 | 7 | `io.github.ariekogan/ateam-mcp::ateam_auth` | ariekogan/ateam-mcp | secret_env / exfil, imperative | Authenticate with A-Team. Required before any tenant-aware operation (reading solutions, deploying, testing, etc.). The user can get their API key at https://mc… |
| 8 | 6 | `ai.agenttrust/mcp-server::agenttrust_send` | agenttrust/mcp-server | — / exfil, imperative | Send a message to another agent via the AgentTrust A2A relay. Creates a new task or continues an existing one when taskId is provided. Use agenttrust_discover f… |
| 9 | 6 | `app.crawlio/crawlio-browser::list_profiles` | Crawlio-app/crawlio-browser | — / imperative, stealth | List the Chrome profiles that have connected to this server, marking which one currently holds the browser connection. A profile appears once its extension has … |
| 10 | 6 | `ar.com.muovi/mcp-server::generic:unnamed` | muovi-latam/mcp-server | — / exfil, imperative | Build the canonical Muovi deep-link that opens the on-platform task creation flow pre-filled with a specific professional and service. Returns a URL of the form… |
| 11 | 6 | `com.post-pulse/mcp-server::schedule_post` | PostPulse/mcp-server-postpulse | — / exfil, imperative | Schedule a social media post to a connected account. Supports Instagram (feed, reel, story), Facebook (feed, reel, story), YouTube, TikTok, Threads, LinkedIn, X… |
| 12 | 6 | `com.santismm/knowledge::manifest:santismm-knowledge-mcp` | santismm/santismm-knowledge-mcp | — / exfil, imperative | MCP server for the Santismm Knowledge Platform — core knowledge, first-party essays, Homeric Atlas datasets and epistemic claims. Ships the core corpus; the hos… |
| 13 | 6 | `com.webflow/mcp::generic:unnamed` | webflow/mcp-server | — / shadowing, imperative | Provides essential guidelines and best practices for effectively using the Webflow tools. Call this tool to understand recommended workflows and important consi… |
| 14 | 6 | `dev.tinify/mcp::crop_image` | Stianlars1/tinify-mcp | — / imperative, stealth | Crop a PNG, JPEG, WebP, or AVIF image with Tinify.dev to the given rectangle and write the result next to the original (or to output_path). The source image is … |
| 15 | 6 | `dev.tinify/mcp::resize_image` | Stianlars1/tinify-mcp | — / imperative, stealth | Resize a PNG, JPEG, WebP, or AVIF image with Tinify.dev by width, height, or scale, and write the result next to the original (or to output_path). At least one … |

Max tool-level `suspicion_score` = **10** (server-level queue max remains 5). Many top rows are again *plausible-benign* marketing (“for AI agents”, product URLs tripping `exfiltration_language`) — **Brief 03 must label before any case study** (AGENTS.md §2.3).

### 8.3 (c) Capability-class distribution at tool level

```bash
python3 -c "
import csv,collections
rows=[r for r in csv.DictReader(open('/tmp/analysis_full.csv')) if r['level']=='tool']
n=len(rows); c=collections.Counter()
any_=0
for r in rows:
    fs=[f for f in r['capability_flags'].split(';') if f]
    if fs: any_+=1
    for f in fs: c[f.split(':',1)[1]]+=1
print('any', any_, n, round(100*any_/n,1))
[print(k,v,round(100*v/n,2)) for k,v in c.most_common()]
"
```

| Class | Tool count | % of 16,763 |
|---|---|---|
| (≥1 capability flag) | **1,900** | **11.3%** |
| `secret_env_access` | 1,015 | 6.06% |
| `network_egress` | 588 | 3.51% |
| `shell_execution` | 196 | 1.17% |
| `database_write` | 99 | 0.59% |
| `file_read_sensitive` | 67 | 0.40% |
| `file_write_delete` | 37 | 0.22% |
| `package_install` | 11 | 0.07% |

(Server §4: 8.8% any-capability; `secret_env_access` still leads at both levels.)

### 8.4 (d) Why-not arm — repos with zero extractable tool definitions

Denominator: 9,785 distinct GitHub-linked repos (`meta.population.distinct_repos`).
Reached-with-tools = 4,725 (48.3%). The shortfall splits into three documented reasons:

| Reason | Count | Source |
|---|---|---|
| **1. Repository not found (HTTP 404)** — deleted, private, renamed, or never public | **1,572** this meta-run (`failures['repo-not-found']`) | `meta.json`; repo marked visited (deterministic, no retry value) |
| **2. Reachable but no tool definition extractable** — README/manifest/source had no match for `@mcp.tool` / `server.tool(` / `ListToolsResult` / description-at-tool / manifest patterns (empty-tree this run: 0) | **1,605** visited repos with zero tool rows overall (this-run `no-tools-found`=408 is the subset completed in the final run; balance from earlier resume legs of the same campaign) | `visited − tools_repos` set difference |
| **3. Transient network failure (`ProxyError`)** — not marked visited by design, so left as a retryable gap rather than a false negative | **2,593** unique run-list repos still unvisited (this-run `failures['http:ProxyError']=2600` in list-length units) | `run_unique − visited`; `fetch_github.py` ProxyError branch |

Also excluded by **namespace stratification** (PI amendment: >50-server namespaces capped at 25 repos, seed 42): **862** unique repos never entered the run list (9,785 − 8,923). Those are out-of-population by design, not extraction failures.

```bash
python3 - <<'PY'
import json,sys; sys.path.insert(0,'pilot')
from fetch_github import build_population
meta=json.load(open('data/github_tools.jsonl.meta.json'))
V={l.strip() for l in open('data/github_tools.jsonl.visited.jsonl') if l.strip()}
T={json.loads(l)['repo'] for l in open('data/github_tools.jsonl') if l.strip()}
run,st=build_population('data/servers.jsonl'); R={r['repo'] for r in run}
print('404', meta['failures']['repo-not-found'], 'zero-tool visited', len(V-T),
      'unvisited', len(R-V), 'stratified-out', st['distinct_repos']-len(R))
PY
```

### 8.5 Triage queue for Brief 03

`data/analysis_toollevel.csv` — **150 rows**, tool level only, sha256
`ae1aff9fccda9c88d77fbc605eb99d5327326e3e7931040ca1ade5b20e18f77`:

- top **100** tool rows by `suspicion_score` (scores 10…4 in this sample),
- **50** uniform-random zero-flag rows (zero capability + zero poison flags;
  addressing-only rows allowed; `random.Random(42)`),
- exact-duplicate analysis keys dropped before sampling (16,763 → 16,410 unique tool rows),
- frozen server-level `data/analysis.csv` **unchanged** (sha256 `2d0a58c1…b76a`).

Sample construction is Brief 03's input; labeling itself is human-in-the-terminal
(`pilot/label_sample.py`, not yet written).



