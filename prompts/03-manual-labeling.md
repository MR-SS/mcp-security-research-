# Mission Brief 03 — Validation Sample & Detector Precision (`pilot/label_sample.py`)

**Context:** Read `AGENTS.md` first. Detectors emit *candidates*; the paper needs validated precision to be credible.

**Goal:** A reproducible manual-labeling workflow over the top-100 triage queue plus 50 random negatives, ending in precision/recall numbers per detector class.

**Tasks**
1. Create `pilot/label_sample.py`: CLI that walks the human through records (name, level, description, flags hit), stores labels in `data/labels.jsonl` (`{row_id, flag_class, label: tp|fp|unclear, notes}`), resumable mid-way.
2. Sampling: top-100 by `suspicion_score` + 50 uniform random rows with zero flags (for catch-rate sanity).
3. After labeling: compute per-class TP/FP, precision; mark `unclear` separately; write `data/validation_report.md` with the numbers + a short "where heuristics failed" analysis.
4. Propose (don't apply silently) 2–3 regex fixes to `analyze.py` based on FP patterns; keep the original rules versioned for the paper's methods section.

**Acceptance criteria**
- [ ] 150 labels collected; precision per class computed and reported
- [ ] Detector fixes proposed as a diff with rationale, not auto-merged
- [ ] Labeled sample published alongside the dataset (it's a contribution)

**Don'ts**
- Don't let the labeling script import model APIs — labeling is human-in-the-terminal
- Don't silently redefine what counts as TP mid-process; if the rubric needs changing, version it (v1/v2) and note it
