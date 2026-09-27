# Mission Brief 04 — Live Model Experiments (`experiments/`)

**Context:** Read `AGENTS.md` first. Budget: ≤$50 this brief. Goal of the section: *do descriptions found in the wild actually fool current models?* — 20–40 tests, not a benchmark.

**Goal:** Convert 5 manually-confirmed suspicious descriptions (from Brief 03 labels) into test cases and measure ASR/RR on 2–3 models.

**Tasks**
1. Setup `experiments/` with a minimal tool-calling harness: a mock tool (logs calls, executes nothing), a real suspicious description attached to one tool, user task unrelated to the attack (MCPTox-style).
2. Per confirmed case: 4 variants (verbatim / lightly-paraphrased / template-adapted / control-benign) → 20+ cases total. Redact any un-disclosed specifics; use synthetic equivalents (fake key material, `example.com` endpoints).
3. Models: one frontier API model + one open model (whatever the human's budget keys cover — ask before spending). Log full transcripts to `experiments/runs/<timestamp>/`.
4. Output `experiments/results.md`: per-model ASR, RR, covert/overt split, 3 anonymized trajectory excerpts for the paper.

**Acceptance criteria**
- [ ] Spend printed and approved before calls; final spend ≤ $50 logged
- [ ] ASR/RR per model per variant in one table
- [ ] No real target data anywhere in transcripts (synthetic only)

**Don'ts**
- Don't contact any real third-party server; tools are mocks
- Don't run more than ~40 cases — marginal cases belong in `FUTURE_WORK.md`
- Don't include verbatim data about unpatched specific servers in any artifact (Ethics rule)
