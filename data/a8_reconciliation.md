# A8 reconciliation record

- Rule version: **A8-r3**
- Adjudication date: **2026-10-17**
- Inputs: `data/analysis_toollevel.csv` (frame), `data/labels.jsonl` (labels and row notes), `data/github_tools.jsonl` (full stored text). None is written here.
- Join: each frame excerpt resolves to the one distinct stored text that starts with it (`data/instance_join.csv`). 107 exact, 43 prefix, 43 rows where the full text is longer than the 300-character excerpt, 0 excerpt-only.

## Row-label conflicts

The instance verdict is never bent toward the frozen row label. Entries below are poison instances whose verdict disagrees with the label of the row they sit on. The five TP row labels are untouched.

**None.** No poison instance on a TP row was judged unsupported, and no poison instance on an FP row was judged supported.

## Denominator framing

`cross_tool_shadowing` rows 19, 33 and 55 are **same-server** false-positive instances. They stay in the class denominator (`4` instances, `1` supported) and are counted unsupported; their verdicts are instance-derived, not apportioned. Nothing is moved out of the denominator.

## Near-misses considered and rejected

| Row | Flag | Why it was considered | Why it is not support |
|---|---|---|---|
| 61 | `imperative_to_model` | the tagline *"use secrets blind ..., never in context"* is directive in form | compressed product doctrine, not an executable instruction; the mechanism is row 60's deposit clause |
| 78 | `imperative_to_model` | *"THIS IS THE PREFERRED FIRST TOOL"* captures priority | scoped to that server's own composite and primitives, the rows 19/33 precedent |
| 0 | `stealth_concealment` | the channel is marketed for content that *"should not appear in the public user conversation"* | channel privacy stated openly; no directive to hide the tool's own actions (gray zone, Discussion) |
| 29 | `imperative_to_model` | *"Use immediately before a decision"* is a directive | timing guidance for this tool's declared function |

## Provenance

- `pi-note`: 132 instances typed by the PI's own frozen row note.
- `text-rule`: 136 assistant-drafted, text-bound adjudications against the full stored text.
- **Human sign-off closed 2026-10-28:** the PI reviewed and accepted all 136 `text-rule` verdicts in the append-only `data/instance_signoffs.jsonl`; no final sign-off differs from the frozen table.
- The AI-assisted pass supplied drafts, not an independent human rater. The completed sign-off is not an inter-rater reliability measurement and must not be reported as one.
