# Zenodo release — Calibrating the Alarms (v1.1.0)

Manuscript-matched archive for *Calibrating the Alarms: A Registry-Grounded,
Human-Validated Measurement of Poisoning Detectors on 16,763 MCP Tool
Descriptions*.

Frozen artifacts include the public registry snapshots, `github_tools.jsonl`,
the 150-row frame and labels, `INSTANCE_VERDICTS.csv`, append-only instance
sign-offs, the matched-ablation ledger and sanitized transcripts, manuscript
sources and PDF, the claim ledger, and all verification scripts. Hashes appear
in `reproducibility_manifest.json`.

Re-derive: `python3 scripts/verify_claims.py`, `python3 scripts/gate_battery.py`,
and `python3 experiments/summarize_ablation.py`.

Public metadata and public source only; no third-party server code was executed.
Detector outputs are candidates, not verdicts, and all support rates are
sample-scoped. License: MIT for code/data; CC BY 4.0 for the manuscript.

This archive supersedes Zenodo v1.0.0 (10.5281/zenodo.23435929). Insert the new
version-specific DOI only after the Zenodo publication succeeds.
