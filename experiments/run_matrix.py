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
LEDGER = REPO_ROOT / "data" / "live_tests" / "trials_ledger.jsonl"
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


def planned_trials(cases: List[str] | None = None) -> List[dict]:
    """The frozen 54-trial plan, ARM-MAJOR (case outer, panel inner) so each
    arm completes across all three models before the next arm starts.
    """
    panel = load_allowlist()
    plan: List[dict] = []
    for case in (list(cases) if cases else list(CASES)):
        for model in panel:
            for rep in range(1, REPS + 1):
                plan.append({"model": model, "case": case, "rep": rep})
    if len(plan) > CAP_TOTAL:
        raise SystemExit(f"REFUSED: plan has {len(plan)} trials; cap is {CAP_TOTAL}")
    return plan


def load_ledger(path: Path = LEDGER) -> List[dict]:
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def done_set(records: List[dict]) -> set:
    return {(r["model"], r["case"], r["rep"]) for r in records}


def main(argv: List[str]) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Brief 04 matrix runner (stage-gated).")
    parser.add_argument("--stub", action="store_true",
                        help="run the matrix against the offline stub (no network)")
    parser.add_argument("--live", action="store_true",
                        help="run the real matrix (requires Stage-3 PI 'go' below)")
    parser.add_argument("--go", action="store_true",
                        help="PI Stage-3 authorization token for --live")
    parser.add_argument("--dry-plan", action="store_true",
                        help="print the trial plan and exit")
    parser.add_argument("--cases", default="",
                        help="comma-separated subset of arms (default: all six)")
    parser.add_argument("--skip-done", action="store_true",
                        help="skip (model, case, rep) trials already in the ledger")
    args = parser.parse_args(argv)

    cases = [c.strip() for c in args.cases.split(",") if c.strip()] if args.cases else None
    for case in (cases or []):
        if case not in CASES:
            raise SystemExit(f"REFUSED: unknown case {case!r}; known: {', '.join(CASES)}")
    plan = planned_trials(cases)
    ledger_records = load_ledger()
    done = done_set(ledger_records)
    if args.skip_done:
        plan = [t for t in plan if (t["model"], t["case"], t["rep"]) not in done]
    total_with_done = len(done | {(t["model"], t["case"], t["rep"]) for t in plan})
    if total_with_done > CAP_TOTAL:
        raise SystemExit(f"REFUSED: {total_with_done} total trials would exceed cap {CAP_TOTAL}")
    if args.dry_plan:
        print(json.dumps({"cap_total": CAP_TOTAL, "trials": len(plan),
                          "panel": load_allowlist(), "plan": plan}, indent=1))
        return 0

    from experiments.harness import Context, run_trial  # noqa: E402

    done = 0
    if args.stub:
        import tempfile

        from experiments.stub_server import StubContext  # noqa: E402

        client = StubContext()
        out_dir = Path(tempfile.mkdtemp(prefix="brief04_stub_"))
        print(f"STUB matrix: {len(plan)} trials (no network, canned tool_calls; "
              f"scratch dir {out_dir})")
    elif args.live:
        if not args.go:
            print("REFUSED: --live needs --go (Stage-3 PI authorization), "
                  "docs/BRIEF04_PROTOCOL.md §9")
            return 2
        client = Context.from_env()
        out_dir = REPO_ROOT / "data" / "live_tests"
        print(f"LIVE matrix: {len(plan)} trials via {client.base_url} "
              f"(key env-only)")
    else:
        print("Nothing to do: pass --dry-plan, --stub, or --live --go "
              "(Stage-3 PI authorization).")
        return 0

    tallies: dict = {}
    halted_models: set = set()
    done_n = 0
    for trial in plan:
        if trial["model"] in halted_models:
            continue
        from experiments.harness import ModelHalt  # noqa: E402

        try:
            record = run_trial(trial["model"], trial["case"], trial["rep"], out_dir,
                               client=client, register=not args.stub)
        except ModelHalt as exc:
            halted_models.add(trial["model"])
            print(f"HALT: {trial['model']} — {exc}; remaining trials for this "
                  f"model are skipped (§6), other models continue")
            continue
        done_n += 1
        arm = tallies.setdefault(record["case"], {})
        per = arm.setdefault(record["model"], {"success": 0, "trials": 0})
        per["trials"] += 1
        per["success"] += record["verdict"] == "success"
        print(f"[{done_n:02d}/{len(plan)}] {record['model']} {record['case']} "
              f"rep{record['rep']}: {record['verdict']} ({record['criterion']}) "
              f"\u2013 {record['evidence']}")
        remaining_cases = {t["case"] for t in plan[done_n:]}
        if record["case"] not in remaining_cases:
            print(f"--- ARM {record['case'].upper()} COMPLETE "
                  f"(running tallies: " + "; ".join(
                      f"{m}:{v['success']}/{v['trials']}"
                      for m, v in arm.items()) + ") ---")
    print(f"completed {done_n}/{len(plan)} trials this run; ledger: "
          f"{out_dir / 'trials_ledger.jsonl'}")
    from experiments import summarize  # noqa: E402
    print(summarize.asr_table(load_ledger()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
