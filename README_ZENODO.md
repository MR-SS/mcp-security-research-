# Zenodo release — Calibrating the Alarms (v1.0.0)
Registry-grounded, human-validated measurement of poisoning detectors on 16,763 MCP tool descriptions; code + data snapshot for citation via DOI.
Frozen artifacts: `data/` (crawl, `github_tools.jsonl`, `labels.jsonl`, `analysis_toollevel.csv`, instance verdicts, live-test ledger), `claims_ledger.jsonl`, `reproducibility_manifest.json`, `paper/main_clean.md`, `paper/FACTS_VERIFIED.md`, `docs/`, `scripts/`, `experiments/` — hashes in the manifest; do not edit.
Re-derive: `python3 scripts/gate_battery.py` (4/4) · `python3 scripts/verify_claims.py` (all claims) · `python3 experiments/trial_accounting.py --check` (54|54|51|3).
Disclaimer: public metadata and public source only, no third-party server code executed; detector outputs are *candidates*, not verdicts, precision is sample-scoped; all genuine findings go through 90-day coordinated disclosure — contact the author before reuse.
Snapshot pre-paper (arXiv pending); license MIT for code and data, manuscript CC BY 4.0.
