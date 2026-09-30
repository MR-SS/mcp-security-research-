#!/usr/bin/env python3
"""Trial accounting for the live matrix (Appendix A table).

Regenerates the per-arm scheduled / completed / valid / infra-excluded counts
directly from data/live_tests/trials_ledger.jsonl and asserts the totals the
paper quotes (54 | 54 | 51 | 3). Stdlib only.

Usage:
    python3 experiments/trial_accounting.py            # print Markdown table
    python3 experiments/trial_accounting.py --check    # assert only (exit 1 on drift)
"""
import argparse
import collections
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(REPO, "data", "live_tests", "trials_ledger.jsonl")

# Arm order as it appears in the paper's ASR table and Appendix A.
ARMS = [
    ("wf", "WF -- unconditional priority capture"),
    ("fl", "FL -- exec-priming"),
    ("dp", "DP -- credential funnel"),
    ("nv", "NV -- gate-suppression (gray, never pooled)"),
    ("ne", "NE -- defensive guard (control)"),
    ("pt", "PT -- gated execution (control)"),
]

# Quoted in paper/main.md (abstract, section 8) and asserted below.
EXPECTED_TOTALS = {"scheduled": 54, "completed": 54, "valid": 51, "infra_excluded": 3}
SCHEDULED_PER_ARM = 9  # 3 models x 3 reps, per docs/BRIEF04_PROTOCOL.md


def load_ledger(path=LEDGER):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def account(rows):
    """Return {arm: {scheduled, completed, valid, infra_excluded}}.

    scheduled       = trial slots the pre-registered matrix called for
    completed       = ledger records present for the arm (transcript written)
    valid           = completed minus infra-excluded; these are the ASR denominators
    infra_excluded  = ledger records whose verdict is infra_failure (criterion INFRA)
    """
    per = collections.defaultdict(
        lambda: {"scheduled": 0, "completed": 0, "valid": 0, "infra_excluded": 0}
    )
    for code, _label in ARMS:
        per[code]["scheduled"] = SCHEDULED_PER_ARM
    for row in rows:
        cell = per[row["case"]]
        cell["completed"] += 1
        if row["verdict"] == "infra_failure" or row.get("criterion") == "INFRA":
            cell["infra_excluded"] += 1
        else:
            cell["valid"] += 1
    return per


def totals(per):
    keys = ("scheduled", "completed", "valid", "infra_excluded")
    return {k: sum(per[c][k] for c, _ in ARMS) for k in keys}


def check(per):
    """Return True when the ledger reproduces every number the paper quotes."""
    got = totals(per)
    problems = []
    for key, want in EXPECTED_TOTALS.items():
        if got[key] != want:
            problems.append(f"  {key}: expected {want}, ledger gives {got[key]}")
    for code, label in ARMS:
        cell = per[code]
        if cell["completed"] != cell["scheduled"]:
            problems.append(
                f"  {code} ({label}): scheduled {cell['scheduled']} != "
                f"completed {cell['completed']} (unfinished trial slot)"
            )
        if cell["valid"] + cell["infra_excluded"] != cell["completed"]:
            problems.append(f"  {code}: valid + infra_excluded != completed")
    if problems:
        print("TRIAL ACCOUNTING DRIFT:", file=sys.stderr)
        print("\n".join(problems), file=sys.stderr)
        return False
    return True


def markdown(per):
    lines = [
        "| Arm | Scheduled | Completed | Valid | Infra-excluded |",
        "|---|---|---|---|---|",
    ]
    for code, label in ARMS:
        c = per[code]
        lines.append(
            f"| {label} | {c['scheduled']} | {c['completed']} | {c['valid']} "
            f"| {c['infra_excluded']} |"
        )
    t = totals(per)
    lines.append(
        f"| **Total** | **{t['scheduled']}** | **{t['completed']}** | "
        f"**{t['valid']}** | **{t['infra_excluded']}** |"
    )
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="assert only, no table output")
    args = ap.parse_args()

    per = account(load_ledger())
    ok = check(per)
    if not args.check:
        print(markdown(per))
        if ok:
            print("\nassertions passed: totals and per-arm invariants match the paper.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
