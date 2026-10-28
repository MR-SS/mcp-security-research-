#!/usr/bin/env python3
"""Human sign-off workflow for A8's assistant-drafted instance verdicts.

This program never changes data/INSTANCE_VERDICTS.csv. It presents only rows whose
provenance is [text-rule], shows the full stored description and the proposed evidence,
and appends the PI's accept/override decision to data/instance_signoffs.jsonl. The
append-only sidecar is the human audit trail needed before describing the per-instance
table as human-reviewed.

Usage:
  python3 pilot/signoff_instances.py                 # interactive, resumes automatically
  python3 pilot/signoff_instances.py --limit 10      # review a small batch
  python3 pilot/signoff_instances.py --summary       # progress only; writes nothing
  python3 pilot/signoff_instances.py --export PATH   # write a read-only review packet
  python3 pilot/signoff_instances.py --revise ROW|FLAG  # revise one prior sign-off
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
DATA = HERE / "data"
VERDICTS = DATA / "INSTANCE_VERDICTS.csv"
SIGNOFFS = DATA / "instance_signoffs.jsonl"
FRAME = DATA / "analysis_toollevel.csv"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def instance_key(row: dict) -> str:
    return f"{row['row_id']}|{row['flag']}"


def proposed_supported(row: dict) -> bool:
    return row["supported"] == "1" and row["unsupported"] == "0"


def load_targets() -> list[dict]:
    rows = list(csv.DictReader(VERDICTS.open(encoding="utf-8")))
    targets = [r for r in rows if r["note"].startswith("[text-rule]")]
    if len(targets) != 136:
        raise SystemExit(f"expected 136 text-rule instances; found {len(targets)}")
    return targets


def load_last_signoffs() -> dict[str, dict]:
    last: dict[str, dict] = {}
    if not SIGNOFFS.exists():
        return last
    for line in SIGNOFFS.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rec = json.loads(line)
            last[rec["instance_key"]] = rec
    return last


def full_text_by_row() -> dict[int, str]:
    # Reuse the asserted prefix join from the A8 producer; do not identify text by
    # (server, tool) because that key is known to be non-unique in this corpus.
    import sys
    sys.path.insert(0, str(HERE / "pilot"))
    import adjudicate_instances as a8

    frame = list(csv.DictReader(FRAME.open(encoding="utf-8")))
    pool = a8.load_corpus()
    out: dict[int, str] = {}
    for row_id, row in enumerate(frame):
        text, _, _ = a8.resolve_full_text(row, pool)
        out[row_id] = text
    return out


def render(target: dict, text: str, position: int, total: int) -> None:
    proposal = "SUPPORTED" if proposed_supported(target) else "UNSUPPORTED"
    print("\n" + "=" * 88)
    print(f"[{position}/{total}] row {target['row_id']}  {target['flag']}")
    print(f"Proposed verdict: {proposal}")
    print("Proposed rationale:")
    print(textwrap.fill(target["note"].replace("[text-rule] ", ""), width=88))
    print("Evidence quote:")
    print(textwrap.fill(target["evidence_quote"], width=88))
    print("Full stored description:")
    print(textwrap.fill(text, width=88))
    print("Decision: [a]ccept proposal  [s]upported override  [u]nsupported override  [q]uit")


def append(record: dict) -> None:
    with SIGNOFFS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        fh.flush()


def export_packet(path: Path, targets: list[dict], texts: dict[int, str], signed: dict[str, dict]) -> None:
    lines = ["# A8 human sign-off packet", "",
             "Read the full text and choose whether you accept the proposed instance verdict.",
             "This packet is read-only; record decisions through signoff_instances.py.", ""]
    for n, target in enumerate(targets, start=1):
        key = instance_key(target)
        status = signed.get(key, {}).get("decision", "PENDING")
        proposal = "supported" if proposed_supported(target) else "unsupported"
        lines += [f"## {n}. `{key}` — {status}", f"Proposed: **{proposal}**", "",
                  f"Rationale: {target['note']}", "", f"Evidence: {target['evidence_quote']}",
                  "", "Full stored description:", "", texts[int(target["row_id"])], ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--export", type=Path)
    parser.add_argument("--revise", metavar="ROW|FLAG",
                        help="append a corrected decision for one already-signed instance")
    args = parser.parse_args()

    targets = load_targets()
    signed = load_last_signoffs()
    pending = [r for r in targets if instance_key(r) not in signed]
    accepted = sum(r.get("decision") == "accept" for r in signed.values())
    overridden = sum(r.get("decision") == "override" for r in signed.values())
    print(f"A8 sign-off progress: {len(signed)}/136 decided; "
          f"{accepted} accepted, {overridden} overridden, {len(pending)} pending.")
    if args.summary:
        return 0

    texts = full_text_by_row()
    if args.export:
        export_packet(args.export, targets, texts, signed)
        return 0

    if args.revise:
        target = next((r for r in targets if instance_key(r) == args.revise), None)
        if target is None:
            raise SystemExit(f"unknown text-rule instance {args.revise!r}")
        old = signed.get(args.revise)
        if old is None:
            raise SystemExit(f"{args.revise!r} is pending; use normal review instead")
        print(f"Revising {args.revise}: current last decision is "
              f"{'supported' if old['supported'] else 'unsupported'} ({old['decision']}).")
        render(target, texts[int(target["row_id"])], 1, 1)
        while True:
            choice = input("> ").strip().lower()
            if choice == "q":
                print("No change written.")
                return 0
            if choice in {"a", "s", "u"}:
                supported = proposed_supported(target) if choice == "a" else choice == "s"
                decision = "accept" if choice == "a" else "override"
                note = ("PI revised prior decision and accepted the proposed text-rule verdict "
                        "after reviewing full stored text." if choice == "a" else
                        input("Required one-line rationale for override: ").strip())
                if note:
                    break
                print("A rationale is required for an override.")
                continue
            print("Use a, s, u, or q.")
        append({
            "ts": utc_now(), "instance_key": args.revise, "row_id": int(target["row_id"]),
            "flag": target["flag"], "decision": decision, "supported": supported,
            "proposed_supported": proposed_supported(target), "note": note,
            "supersedes": old,
        })
        print(f"saved revision: {args.revise} → {'supported' if supported else 'unsupported'}")
        return 0

    if args.limit:
        pending = pending[:args.limit]
    for position, target in enumerate(pending, start=1):
        key = instance_key(target)
        render(target, texts[int(target["row_id"])], position, len(pending))
        while True:
            choice = input("> ").strip().lower()
            if choice == "q":
                print("Paused. Existing decisions are saved; rerun to resume.")
                return 0
            if choice == "a":
                decision = "accept"
                supported = proposed_supported(target)
                note = "PI accepted the proposed text-rule verdict after reviewing full stored text."
                break
            if choice in {"s", "u"}:
                decision = "override"
                supported = choice == "s"
                note = input("Required one-line rationale for override: ").strip()
                if note:
                    break
                print("A rationale is required for an override.")
                continue
            print("Use a, s, u, or q.")
        append({
            "ts": utc_now(), "instance_key": key, "row_id": int(target["row_id"]),
            "flag": target["flag"], "decision": decision, "supported": supported,
            "proposed_supported": proposed_supported(target), "note": note,
        })
        print(f"saved {key}: {'supported' if supported else 'unsupported'} ({decision})")
    print("Batch complete. Rerun to continue or use --summary for progress.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
