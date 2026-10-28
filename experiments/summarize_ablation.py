#!/usr/bin/env python3
"""Recompute the matched WF/DP description-ablation counts from its ledger.

The ledger is append-only because infrastructure-failure cells receive one
end-of-batch retry.  The last record for each scheduled cell is authoritative.
This script intentionally reports raw counts only: the three replications per
cell are a fixed mocked-harness panel, not independent population samples.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "live_tests" / "ablation_trials_ledger.jsonl"
CASES = ("wf", "dp")
VARIANTS = ("source", "neutral")
MODELS = ("glm-5.3", "deepseek-v4.1-flash", "gemini-3.8-flash")
REPS = (1, 2, 3)


def main() -> None:
    rows = [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines()
            if line.strip()]
    last = {}
    for row in rows:
        key = (row["case"], row["variant"], row["model"], row["rep"])
        last[key] = row
    expected = {(c, v, m, r) for c in CASES for v in VARIANTS
                for m in MODELS for r in REPS}
    if set(last) != expected:
        raise SystemExit(f"ledger cells differ from the frozen 36-cell design: "
                         f"missing={sorted(expected - set(last))}; extra={sorted(set(last) - expected)}")
    if any(row["verdict"] == "infra_failure" for row in last.values()):
        raise SystemExit("final ledger still has an infra_failure cell")

    print(f"attempts={len(rows)} final_cells={len(last)}")
    for case in CASES:
        for variant in VARIANTS:
            cells = [last[(case, variant, model, rep)] for model in MODELS for rep in REPS]
            k = sum(row["verdict"] == "success" for row in cells)
            print(f"{case.upper()} {variant}: {k}/{len(cells)}")
            for model in MODELS:
                model_rows = [last[(case, variant, model, rep)] for rep in REPS]
                print(f"  {model}: {sum(r['verdict'] == 'success' for r in model_rows)}/3")
    print("final verdicts=" + json.dumps(dict(Counter(r["verdict"] for r in last.values())), sort_keys=True))


if __name__ == "__main__":
    main()
