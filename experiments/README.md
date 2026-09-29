# experiments/ — Brief 04 harness (Stage 2)

Offline-capable mock harness for the 54-trial live matrix
(`docs/BRIEF04_PROTOCOL.md` §1–§8). **No live model call happens from this
directory without the Stage-3 PI "go"**; everything below is testable offline.

## Layout

```
experiments/
├── mocks/            six mock tool servers + benign fillers (offline, canned)
│   ├── fixtures.py   verbatim §0 fixture texts, sha-pinned; corpus re-verification gate
│   ├── wf_verify.py  ATTACK A — unconditional priority capture (row 12)
│   ├── fl_exec.py    ATTACK B — exec-priming; returns shell text as data (row 35)
│   ├── dp_store.py   ATTACK C — credential funnel; ref-code receipt (row 60)
│   ├── nv_bootstrap.py  GRAY — gate-suppression phrasing, benign funnel (row 47)
│   ├── ne_guard.py   CONTROL — defensive guard text (row 26)
│   └── pt_gated.py   CONTROL — gated execution (row 32)
├── harness.py        one (case, rep, model) trial: fixed prompts, max_turns=10,
│                     redaction (§5), transcript writer, mechanical judge (§4)
├── judge logic       in harness.judge(): markers A / B / A-covert / G / CTRL
├── run_matrix.py     allowlist binding + frozen 54-trial plan + stage gates
├── stub_server.py    offline canned client (no network) for the selftest
└── selftest.py       fixture gate + unit checks + judge markers + 54-trial replay
```

## Quickstart

```bash
# 0) offline verification (no env vars needed) — run this first
python3 experiments/selftest.py

# 1) frozen plan (54 trials, panel order: glm-5.3 primary first)
python3 experiments/run_matrix.py --dry-plan

# 2) full matrix replay against the offline stub (no network)
python3 experiments/run_matrix.py --stub

# 3) ONE live trial (Stage-3 gated; PI 'go' required; allowlist-bound)
export OPENAI_BASE_URL="https://api.avalai.ir/v1"   # AvalAI gateway (PI access)
export OPENAI_API_KEY="..."                          # env only; never committed
python3 experiments/harness.py wf glm-5.3 --rep 1 --go

# 4) the full live matrix (Stage-3 gated)
python3 experiments/run_matrix.py --live --go
```

## Panel & cap (locked 2026-09-29)

- Panel (exactly `data/live_tests/MODEL_ALLOWLIST.txt`, one per line, primary first):
  1. `glm-5.3` (PRIMARY)
  2. `deepseek-v4.1-flash`
  3. `gemini-3.8-flash`
- `gpt-6-astra`: held-out reserve only — never in the matrix.
- Cap: **54 trials** (6 arms × 3 reps × 3 models; PI raise 40→54, 2026-09-29),
  ≤4 completions/trial → ≤216 completions panel-wide, ≤$2 estimated.
- The runner refuses any model not in the allowlist and any plan ≠ 54 trials.

## Guarantees

- Mocks are offline: canned JSON only; `TESTKEY-…` synthetic material; a
  tripwire rejects credential-shaped strings in canned data.
- Fixture descriptions are verbatim §0 texts; `verify_against_corpus()`
  sha-checks them against `data/github_tools.jsonl` **at every harness init**
  and fails loudly on drift. Never hand-edit a fixture string.
- Tool calls are logged **before** dispatch; transcripts are redacted
  recursively (headers never logged; exception text never persisted; env
  VALUES never enter artifacts).
- The harness never executes shell text (FL: detection, not execution).
- Trial outcomes append to `data/live_tests/trials_ledger.jsonl` (counts
  first; three reps do not establish population rates — protocol §8).
