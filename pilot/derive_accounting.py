#!/usr/bin/env python3
"""Re-derive the frozen-sample label accounting from source data (R4 FIX 2).

Authoritative sources:
  data/analysis_toollevel.csv  -- the frozen 150-row stratified sample
  data/labels.jsonl            -- human labels, last-wins by row_id (0-based ordinal)

Prints the TP / FP / TN split and the flagged-benign stratum used to rebuild the
section 6.4 false-positive taxonomy. Nothing here is hand-entered.
"""
import collections
import csv
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE = os.path.join(REPO, "data", "analysis_toollevel.csv")
LABELS = os.path.join(REPO, "data", "labels.jsonl")


def load_labels():
    """Last-wins label per row_id."""
    lab = {}
    for line in open(LABELS, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        lab[int(r["row_id"])] = r["label"]
    return lab


def load_sample():
    return list(csv.DictReader(open(SAMPLE, encoding="utf-8")))


def is_zero_flag(row):
    """Zero-flag == suspicion_score 0 (the definition label_sample.py uses:
    'fn only available for zero-flag rows (display 101-150)')."""
    return row["suspicion_score"] == "0"


def main():
    sample = load_sample()
    lab = load_labels()
    n = len(sample)
    zero = [i for i, r in enumerate(sample) if is_zero_flag(r)]
    flagged = [i for i, r in enumerate(sample) if not is_zero_flag(r)]

    tp = [i for i in range(n) if lab.get(i) == "tp"]
    fp_flagged = [i for i in flagged if lab.get(i) == "fp"]
    fp_zero = [i for i in zero if lab.get(i) == "fp"]
    unclear = [i for i in range(n) if lab.get(i) == "u"]

    print(f"frozen sample rows: {n}")
    print(f"  top-scored (flagged) rows : {len(flagged)}")
    print(f"  zero-flag control rows    : {len(zero)}")
    print()
    print("RESTRUCTURED ACCOUNTING (R4 FIX 2)")
    print(f"  TP  (flagged, judge TP)   : {len(tp)}  {tp}")
    print(f"  FP  (flagged, judge FP)   : {len(fp_flagged)}")
    print(f"  TN  (zero-flag, confirmed benign): {len(fp_zero)}")
    print(f"  unclear                   : {len(unclear)}")
    print(f"  SUM                      : {len(tp)+len(fp_flagged)+len(fp_zero)+len(unclear)}"
          f"  (must equal {n})")
    print()
    # flag instances, re-derived
    inst = 0
    for r in sample:
        for col in ("capability_flags", "poison_flags", "addressing_flags"):
            v = r[col]
            if v:
                inst += len([x for x in v.split(";") if x])
    print(f"  total flag instances over the sample: {inst}")
    tp_inst = sum(
        len([x for x in r[col].split(";") if x])
        for i in tp for r in [sample[i]]
        for col in ("capability_flags", "poison_flags", "addressing_flags")
    )
    print(f"  flag instances on TP rows : {tp_inst}")
    print(f"  flag instances on FP rows : {inst - tp_inst}")
    print()
    print("  TP physical rows:")
    for i in tp:
        print(f"    row {i}: {sample[i]['name']}")

    print()
    print("R4 FIX 3 CHECK — do rows 60/61/94/95 carry TP text, and how are they labeled?")
    for i in (12, 35, 60, 61, 94, 95):
        if i >= len(sample):
            print(f"    row {i}: OUT OF SAMPLE RANGE")
            continue
        r = sample[i]
        print(f"    row {i}: label={lab.get(i)!r} score={r['suspicion_score']} "
              f"name={r['name']}")
        desc = " ".join(r["description"].split())
        print(f"            text: {desc[:230]}")

    print()
    print("Human notes for the TP rows and row 61:")
    notes = {}
    for line in open(LABELS, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        notes[int(r["row_id"])] = r.get("note", "")
    for i in (12, 35, 60, 61, 94, 95):
        print(f"    row {i} note: {notes.get(i, '(none)')[:200]}")

    print()
    print("Duplicate-name check across the sample (R4 FIX 3 / section 5.10 rule):")
    names = collections.Counter(r["name"] for r in sample)
    for nm, c in names.items():
        if c > 1:
            ids = [i for i, r in enumerate(sample) if r["name"] == nm]
            print(f"    x{c} {nm}  rows {ids}  labels {[lab.get(i) for i in ids]}")


if __name__ == "__main__":
    main()
