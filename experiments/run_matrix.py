#!/usr/bin/env python3
"""Brief 04 matrix runner (Stage 2; stage-gated).

Binds every run to data/live_tests/MODEL_ALLOWLIST.txt (exactly the locked
panel; the harness refuses to run on mismatch) and enforces the frozen matrix:
6 arms × 3 reps × 3 models = 54 trials (PI-authorized cap raise 40→54,
2026-09-29). Live execution requires --go (Stage-3 PI authorization);
--stub runs the same matrix end-to-end against the offline stub server and
writes nothing outside data/live_tests/.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.mocks import CASES  # noqa: E402

ALLOWLIST = REPO_ROOT / "data" / "live_tests" / "MODEL_ALLOWLIST.txt"
REPS = 3
CAP_TOTAL = 54  # 6 arms × 3 reps × 3 models (PI raise 40→54, 2026-09-29)


def load_allowlist(path: Path = ALLOWLIST) -> List[str]:
    lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()
             if ln.strip()]
    if len(lines) != 3:
        raise SystemExit(f"REFUSED: {path} must contain exactly 3 model lines "
                         f"(got {len(lines)})")
    if len(set(lines)) != 3:
        raise SystemExit(f"REFUSED: {path} contains duplicate model ids")
    return lines


def ensure_model_allowed(model: str, path: Path = ALLOWLIST) -> None:
    allowed = load_allowlist(path)
    if model not in allowed:
        raise SystemExit(
            f"REFUSED: model {model!r} is not in {path} (panel: {', '.join(allowed)}). "
            f"Panel changes require a new PI authorization.")


def planned_trials() -> List[dict]:
    """The frozen 54-trial plan, in panel order (glm-5.3 primary first)."""
    plan: List[dict] = []
    for model in load_allowlist():
        for case in CASES:
            for rep in range(1, REPS + 1):
                plan.append({"model": model, "case": case, "rep": rep})
    if len(plan) != CAP_TOTAL:
        raise SystemExit(f"REFUSED: plan has {len(plan)} trials; cap is {CAP_TOTAL}")
    return plan


def main(argv: List[str]) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Brief 04 matrix runner (stage-gated).")
    parser.add_argument("--stub", action="store_true",
                        help="run the full matrix against the offline stub (no network)")
    parser.add_argument("--live", action="store_true",
                        help="run the real matrix (requires Stage-3 PI 'go' below)")
    parser.add_argument("--go", action="store_true",
                        help="PI Stage-3 authorization token for --live")
    parser.add_argument("--dry-plan", action="store_true",
                        help="print the 54-trial plan and exit")
    args = parser.parse_args(argv)

    plan = planned_trials()
    if args.dry_plan:
        print(json.dumps({"cap_total": CAP_TOTAL, "trials": len(plan),
                          "panel": load_allowlist(), "plan": plan}, indent=1))
        return 0

    from experiments.harness import Context, run_trial  # noqa: E402

    out_dir = REPO_ROOT / "data" / "live_tests"
    done = 0
    if args.stub:
        from experiments.stub_server import StubContext  # noqa: E402

        client = StubContext()
        print(f"STUB matrix: {len(plan)} trials (no network, canned tool_calls)")
    elif args.live:
        if not args.go:
            print("REFUSED: --live needs --go (Stage-3 PI authorization), "
                  "docs/BRIEF04_PROTOCOL.md §9")
            return 2
        client = Context.from_env()
        print(f"LIVE matrix: {len(plan)} trials via {client.base_url} "
              f"(key env-only)")
    else:
        print("Nothing to do: pass --dry-plan, --stub, or --live --go "
              "(Stage-3 PI authorization).")
        return 0

    for trial in plan:
        record = run_trial(trial["model"], trial["case"], trial["rep"], out_dir,
                           client=client, register=True)
        done += 1
        print(f"[{done:02d}/{len(plan)}] {record['model']} {record['case']} "
              f"rep{record['rep']}: {record['verdict']} ({record['criterion']}) "
              f"– {record['evidence']}")
    print(f"completed {done}/{len(plan)} trials; ledger: "
          f"{out_dir / 'trials_ledger.jsonl'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
