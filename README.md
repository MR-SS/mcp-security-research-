# Calibrating the Alarms

This repository accompanies *Calibrating the Alarms: A Registry-Grounded,
Human-Validated Measurement of Poisoning Detectors on 16,763 MCP Tool
Descriptions*.

The study measures detector output, not malicious prevalence. It analyzes a
cursor-bounded prefix of the public Official MCP Registry, extracts 16,763 tool
descriptions from 4,725 GitHub-linked repositories, audits a frozen 150-row
purposive frame, and reports a matched source--neutral description ablation in
a fully mocked harness. Detector matches are candidates, never vulnerability
verdicts.

## Release status

`v1.1.0` is the release candidate corresponding to the current manuscript and
its final sign-off and ablation artifacts. It supersedes the older Zenodo
`v1.0.0` pre-paper snapshot (DOI: [10.5281/zenodo.23435929](https://doi.org/10.5281/zenodo.23435929)).
The version-specific DOI for `v1.1.0` is added here, to `CITATION.cff`, and to
the submission PDF only after Zenodo publishes the archived tag. Do not cite
the v1.0.0 DOI as the artifact backing the current manuscript.

## Scope and key limits

- Registry collection stopped at a pre-authorized 600-page cursor boundary;
  this is not a registry census.
- The review frame contains the 100 highest-score rows and 50 zero-capability /
  zero-poison controls. Its rates are not population precision or prevalence
  estimates; the controls do not estimate recall or false negatives.
- The primary poison-family result is 6 supported instances among 124 reviewed
  poison flags in the purposive discovery stratum.
- The matched WF source--neutral contrast is 6/9 versus 0/9 inside the mocked
  harness. DP is 9/9 in both conditions and is task-confounded.
- The study analyzes public registry metadata and public source only. It does
  not execute third-party server code or contact third-party MCP endpoints.

## Reproduce the release checks

Run these from the repository root with Python 3.10+:

```bash
python3 scripts/verify_claims.py
python3 scripts/gate_battery.py
python3 experiments/summarize_ablation.py
```

The first two commands validate the manuscript's frozen inputs, sample identity,
instance adjudication, original-trial accounting, matched-ablation ledger, and
manifest hashes. The third reports the append-only ablation ledger with a
last-attempt-wins rule for retried transport failures.

## Repository map

| Path | Contents |
|---|---|
| `data/raw/` | Verbatim public registry snapshots |
| `data/github_tools.jsonl` | Source-extracted tool-description corpus |
| `data/analysis_toollevel.csv` | Frozen 150-row review frame |
| `data/INSTANCE_VERDICTS.csv` | Full-text, instance-level adjudication |
| `data/instance_signoffs.jsonl` | Append-only PI sign-off for text-rule drafts |
| `data/live_tests/` | Sanitized mocked-harness ledgers and transcripts |
| `paper/submission.md` | Focused submission manuscript and source for the PDF |
| `paper/main_clean.md` | Full audit manuscript |
| `reproducibility_manifest.json` | Hashes for tracked research artifacts |

## Ethics and disclosure

The repository contains no third-party executable server code and no real
credentials. It does not identify a reviewed server as malicious or publish an
unpatched exploit path. Any genuine finding requiring disclosure follows a
90-day coordinated-disclosure process.

## Licence and citation

Code and data are released under the repository's MIT license. The manuscript
is CC BY 4.0. Cite the version-specific Zenodo DOI once the `v1.1.0` archive is
published; `CITATION.cff` carries the current citation metadata.
