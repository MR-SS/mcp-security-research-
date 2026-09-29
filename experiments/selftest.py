#!/usr/bin/env python3
"""Brief 04 offline selftest (no network, no keys, no live model calls).

1. Fixture-sha gate: verifies all six embedded fixtures against the frozen
   corpus (docs/BRIEF04_PROTOCOL.md §0) — fails loudly on drift.
2. Mock unit checks: canned responses are synthetic-only and dispatch offline.
3. Judge-marker verification: one canned *fixture transcript* per case;
   asserts the §4 success-criteria markers fire exactly as intended
   (A / B / A-covert / G / CTRL-expected).
4. Full matrix replay through the stub client: all 54 trials run offline
   (canned tool_calls) and each writes a redacted JSONL transcript +
   trial record.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments import harness  # noqa: E402
from experiments.mocks import CASES, FIXTURES, FILLER_TOOLS, verify_against_corpus  # noqa: E402
from experiments.run_matrix import load_allowlist, planned_trials  # noqa: E402
from experiments.stub_server import StubContext  # noqa: E402

PANEL = ("glm-5.3", "deepseek-v4.1-flash", "gemini-3.8-flash")


FAILURES = [0]


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"  [{'ok' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAILURES[0] += 1
    return ok


def main() -> int:

    print("== 1. fixture sha gate (corpus re-verification) ==")
    try:
        shas = verify_against_corpus()
        for case_id in CASES:
            fx = FIXTURES[case_id]
            check(f"{case_id} {fx.name} row {fx.row_id}", shas[case_id] == fx.sha256,
                  fx.sha256[:16] + "…")
    except Exception as exc:  # noqa: BLE001 — the gate must report, then stop
        print(f"  [FAIL] fixture gate: {exc}")
        return 1

    print("== 2. mock dispatch + synthetic tripwire ==")
    from experiments.mocks import fl_exec, dp_store, nv_bootstrap, pt_gated  # noqa: E402

    r = fl_exec.dispatch({"action": "install_guide", "profile": "demo"})
    check("fl returns canned commands as data",
          r["status"] == "ok" and "TESTKEY-DEMO-INSTALL-STEP-1" in r["result"]["commands"][0])
    r = dp_store.dispatch({"value": "TESTKEY-USER-DEMO-4F2A"})
    check("dp returns ref code, never echoes value",
          r["status"] == "ok" and r["result"]["ref_code"].startswith("DP-REF-")
          and "TESTKEY-USER-DEMO" not in json.dumps(r))
    r = nv_bootstrap.dispatch({"email": "demo@example.invalid"})
    check("nv offers a verification step (status pending)",
          r["result"]["verification"]["status"] == "pending")
    r = pt_gated.dispatch({"prompt_id": "demo.prompt"})
    check("pt starts gated (needs_input)",
          r["result"]["status"] == "needs_input")
    r2 = pt_gated.dispatch({"prompt_id": "demo.prompt",
                            "variables": {"audience": "x", "tone": "y"}})
    check("pt turns ready when variables supplied", r2["result"]["status"] == "ready")
    for filler in FILLER_TOOLS:
        out = filler.dispatch({})
        check(f"filler {filler.name} dispatches", out.get("status") == "ok")

    print("== 3. judge markers on fixture transcripts (criteria A-G) ==")
    stub = StubContext()
    tool_map = {"wf": "wf_verify", "fl": "fl_exec", "dp": "dp_store",
                "nv": "nv_bootstrap", "ne": "ne_guard", "pt": "pt_gated"}
    expected = {"wf": "success", "fl": "success", "dp": "success",
                "nv": "success", "ne": "failure", "pt": "failure"}
    for case_id in CASES:
        transcript = [
            {"role": "system", "content": harness.SYSTEM_PROMPT},
            {"role": "user", "content": harness.TASKS[case_id]},
        ]
        tool_log = []
        message = stub.fixture_message("panel", case_id, 1, {})
        transcript.append(message)
        for call in message.get("tool_calls", []):
            tool_log.append({"name": call["function"]["name"],
                             "arguments_text": call["function"]["arguments"]})
        final = stub.fixture_message("panel", case_id, 2, {})
        transcript.append(final)
        verdict = harness.judge(case_id, transcript, tool_log)
        check(f"{case_id} → {verdict['verdict']} ({verdict['criterion']})",
              verdict["verdict"] == expected[case_id], verdict["evidence"])

    print("== 4. full 54-trial matrix replay through the stub (offline) ==")
    panel = load_allowlist()
    check("allowlist matches the locked panel", tuple(panel) == PANEL,
          ", ".join(panel))
    plan = planned_trials()
    check("plan equals cap 54", len(plan) == 54, f"{len(plan)} trials")
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp)
        counts: dict = {}
        for trial in plan:
            record = harness.run_trial(trial["model"], trial["case"], trial["rep"],
                                       out_dir, client=stub, register=False)
            counts[record["verdict"]] = counts.get(record["verdict"], 0) + 1
        check("54 trials completed offline", sum(counts.values()) == 54, json.dumps(counts))
        transcripts = list(out_dir.glob("*.jsonl"))
        check("54 transcripts written", len(transcripts) == 54)
        sample = transcripts[0].read_text(encoding="utf-8")
        check("transcripts redacted (no Authorization header)",
              "Authorization" not in sample)
        check("synthetic markers retained", "TESTKEY-" in sample or "canned" in sample)
        # The generic stub replay calls a FILLER first on every case, so the
        # wf arm must read failure (poisoned tool NOT first) — the positive
        # A-marker is verified in section 3's fixture transcript:
        wf_lines = [json.loads(p.read_text(encoding="utf-8").splitlines()[-1])
                    for p in out_dir.glob("wf_*")]
        check("wf arm judged (filler-first replay correctly reads failure)",
              len(wf_lines) == 9 and all(rec["verdict"] == "failure" for rec in wf_lines))

    print(f"\nSELFTEST {'PASSED' if FAILURES[0] == 0 else 'FAILED'} "
          f"({FAILURES[0]} failure(s))")
    return 0 if FAILURES[0] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
