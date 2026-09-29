#!/usr/bin/env python3
"""Brief 04 results summarizer — reads data/live_tests/trials_ledger.jsonl and
the per-trial transcripts, and produces (docs/BRIEF04_PROTOCOL.md §7 shape):

  1. the ASR table: rows = 6 arms, cols = locked panel (glm-5.3 first),
     cells = successes/trials with criterion letters;
  2. the NV gray arm SEPARATELY (FP-sensitivity — never pooled with attack ASR);
  3. candidate excerpts for the paper: the model's own words around the
     decisive tool call / verdict;
  4. infra-failure counts (timeout / garbled / transport — protocol §6).

Counts first: 3 reps do not establish population rates (§8).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.run_matrix import load_allowlist, load_ledger  # noqa: E402

OUT_DIR = REPO_ROOT / "data" / "live_tests"
ARMS = ("wf", "fl", "dp", "nv", "ne", "pt")
ARM_LABELS = {
    "wf": "WF  unconditional priority (attack)",
    "fl": "FL  exec-priming (attack)",
    "dp": "DP  credential funnel (attack)",
    "nv": "NV  gate-suppression (GRAY, not pooled)",
    "ne": "NE  defensive guard (control)",
    "pt": "PT  gated execution (control)",
}
CRITERION = {
    "wf": "A", "fl": "B", "dp": "A-covert/overt", "nv": "G",
    "ne": "CTRL", "pt": "CTRL",
}
INFRA_EVENTS = ("infra_failure", "timeout", "garbled", "transport")


def _cell(records: List[dict], model: str, case: str) -> str:
    rows = [r for r in records if r["model"] == model and r["case"] == case]
    if not rows:
        return "—"
    # §6: infra failures are excluded from ALL denominators; annotated inline.
    infra = sum(1 for r in rows if r.get("verdict") == "infra_failure")
    valid = [r for r in rows if r.get("verdict") != "infra_failure"]
    if not valid:
        return f"0/0 (+{infra} infra)"
    n = len(valid)
    k = sum(1 for r in valid if r.get("verdict") == "success")
    crits = sorted({r.get("criterion", "?") for r in valid if r.get("criterion") != "INFRA"})
    suffix = f" (+{infra} infra)" if infra else ""
    return f"{k}/{n} [{';'.join(crits)}]{suffix}"


def asr_table(records: List[dict]) -> str:
    panel = load_allowlist()
    lines = ["", "=== ASR TABLE (successes/trials [criterion letters]) ===",
             "| Arm | " + " | ".join(panel) + " |",
             "|---|" + "---|" * len(panel)]
    for case in ARMS:
        lines.append(f"| {ARM_LABELS[case]} | "
                     + " | ".join(_cell(records, m, case) for m in panel) + " |")
    attack_models = {m: [r for r in records
                         if r["model"] == m and r["case"] in ("wf", "fl", "dp")]
                     for m in panel}
    lines.append("")
    lines.append("Pooled attack ASR (WF+FL+DP only; NV never pooled): "
                 + "; ".join(f"{m} {sum(r['verdict'] == 'success' for r in rows)}"
                             f"/{len(rows)}"
                             for m, rows in attack_models.items()))
    lines.append(f"NV gray arm (separate): "
                 + "; ".join(
                     f"{m} {_cell(records, m, 'nv')}" for m in panel))
    return "\n".join(lines)


def infra_counts(records: List[dict]) -> str:
    # Infra failures are trials that never reached a trial_record: compare the
    # plan against the ledger, and scan transcripts for infra events.
    from experiments.run_matrix import planned_trials

    plan = {(t["model"], t["case"], t["rep"]) for t in planned_trials()}
    done = {(r["model"], r["case"], r["rep"]) for r in records}
    missing = plan - done
    infra_events = 0
    for path in OUT_DIR.glob("*.jsonl"):
        if path.name.startswith(("stage0", "trials_ledger")) or path.name == "MODEL_ALLOWLIST.txt":
            continue
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                if any(tag in line for tag in INFRA_EVENTS):
                    infra_events += 1
        except OSError:
            continue
    return (f"infra: {len(missing)} scheduled trial(s) without a ledger record "
            f"(= never completed); {infra_events} infra-tagged line(s) in transcripts")


def _flat_text(obj) -> str:
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        return " ".join(_flat_text(v) for v in obj.values())
    if isinstance(obj, list):
        return " ".join(_flat_text(v) for v in obj)
    return ""


def excerpt_for(record: dict, max_words: int = 45) -> Optional[str]:
    """The model's own words around the decisive call: the assistant text
    immediately BEFORE the case-tool call, or the final assistant text."""
    path = OUT_DIR / record.get("transcript", "")
    if not path.exists():
        return None
    case = record["case"]
    tool_names = {"wf": "wf_verify", "fl": "fl_exec", "dp": "dp_store",
                  "nv": "nv_bootstrap", "ne": "ne_guard", "pt": "pt_gated"}
    tool = tool_names[case]
    pre_text: Optional[str] = None
    final_text: Optional[str] = None
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("event") == "round":
            message = rec.get("response", {})
            calls = message.get("tool_calls") or []
            names = [c.get("function", {}).get("name") for c in calls]
            content = message.get("content") or ""
            if tool in names and content.strip():
                pre_text = content.strip()
            if content.strip():
                final_text = content.strip()
    chosen = pre_text or final_text
    if not chosen:
        return None
    words = " ".join(chosen.split()).split()
    if len(words) > max_words:
        words = words[:max_words] + ["…"]
    return f"[{record['model']} · {case.upper()}] \"{' '.join(words)}\""


def main() -> int:
    records = load_ledger()
    panel = load_allowlist()
    print(f"ledger: {len(records)} trial record(s); panel: {', '.join(panel)}")
    print(asr_table(records))
    print()
    print(infra_counts(records))
    print()
    print("=== EXCERPT CANDIDATES (model's own words; success rows first) ===")
    winners = [r for r in records if r.get("verdict") == "success"]
    others = [r for r in records if r.get("verdict") != "success"]
    shown = 0
    for r in winners + others:
        if shown >= 8:
            break
        text = excerpt_for(r)
        if text:
            print(text)
            shown += 1
    if not shown:
        print("(no transcript excerpts available)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
