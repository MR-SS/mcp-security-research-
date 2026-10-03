#!/usr/bin/env python3
"""R5 PHASE 1A - split the 268 validated flag instances by detector family.

Inputs (both authoritative, both committed):
  data/validation_report.md  - per-class TP/FP instance table produced by
                              pilot/label_sample.py --report from labels.jsonl
  data/labels.jsonl          - last-wins human labels behind that table

Family membership is taken from the frozen v2 detector definition in
pilot/analyze.py (CAPABILITY / POISON / ADDRESSING class sets), not hand-listed.

Output: data/validation_family_split.csv, with asserts that the per-class table
sums to the reported 268 instances and 15 supported.
"""
import csv
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(REPO, "data", "validation_report.md")
ANALYZE = os.path.join(REPO, "pilot", "analyze.py")
OUT = os.path.join(REPO, "data", "validation_family_split.csv")

EXPECTED_INSTANCES = 268
EXPECTED_SUPPORTED = 15

FAMILY_ORDER = ("poison", "capability", "channel")


def load_families():
    """Read the class -> family map straight out of the frozen detector."""
    src = open(ANALYZE, encoding="utf-8").read()
    out = {}
    # the frozen detector defines the families as *_PATTERNS dicts; each key at
    # the top level of the dict is a class name
    for m in re.finditer(
            r"(CAPABILITY_PATTERNS|POISON_PATTERNS|ADDRESSING_PATTERNS)\s*=\s*\{(.*?)\n\}",
            src, re.S):
        name, body = m.group(1), m.group(2)
        fam = {"CAPABILITY_PATTERNS": "capability",
               "POISON_PATTERNS": "poison",
               "ADDRESSING_PATTERNS": "channel"}[name]
        for c in re.findall(r'^\s{4}"([a-z_]+)"\s*:', body, re.M):
            out[c] = fam
    # compound channel class: emitted by scan_text() from IMPPERATIVE_PATTERNS
    # combined with an addressing hit (analyze.py:108), not a dict key of its own
    out.setdefault("second_person_imperative", "channel")
    return out


def load_per_class():
    """(class, tp, fp) from the validation report's per-class table."""
    rows, in_tbl = [], False
    for line in open(REPORT, encoding="utf-8"):
        if line.startswith("| Class |"):
            in_tbl = True
            continue
        if in_tbl:
            if not line.startswith("|"):
                break
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 3 or set(cells[0]) <= set("-: "):
                continue
            cls = cells[0].strip("`")
            rows.append((cls, int(cells[1]), int(cells[2])))
    return rows


def main():
    fam = load_families()
    per_class = load_per_class()
    if not per_class:
        raise SystemExit("no per-class table parsed from validation_report.md")

    unmapped = [c for c, _, _ in per_class if c not in fam]
    if unmapped:
        raise SystemExit(f"classes not found in the frozen detector: {unmapped}")

    agg = {f: {"tp": 0, "fp": 0, "classes": []} for f in FAMILY_ORDER}
    for cls, tp, fp in per_class:
        a = agg[fam[cls]]
        a["tp"] += tp
        a["fp"] += fp
        a["classes"].append(cls)

    tot_inst = sum(a["tp"] + a["fp"] for a in agg.values())
    tot_sup = sum(a["tp"] for a in agg.values())
    assert tot_inst == EXPECTED_INSTANCES, f"instances {tot_inst} != {EXPECTED_INSTANCES}"
    assert tot_sup == EXPECTED_SUPPORTED, f"supported {tot_sup} != {EXPECTED_SUPPORTED}"

    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["family", "classes_in_family", "n_classes", "supported_instances",
                    "unsupported_instances", "total_instances", "text_support_rate"])
        for f in FAMILY_ORDER:
            a = agg[f]
            ti = a["tp"] + a["fp"]
            w.writerow([f, ";".join(sorted(a["classes"])), len(a["classes"]), a["tp"],
                        a["fp"], ti, f"{a['tp'] / ti:.4f}"])
        w.writerow(["ALL", ";".join(sorted(c for c, _, _ in per_class)), len(per_class),
                    tot_sup, tot_inst - tot_sup, tot_inst,
                    f"{tot_sup / tot_inst:.4f}"])

    print(f"{'family':<12}{'classes':>8}{'supported':>11}{'unsupported':>13}"
          f"{'total':>8}{'support rate':>14}")
    for f in FAMILY_ORDER:
        a = agg[f]
        ti = a["tp"] + a["fp"]
        print(f"{f:<12}{len(a['classes']):>8}{a['tp']:>11}{a['fp']:>13}{ti:>8}"
              f"{a['tp'] / ti:>13.2%}   [{', '.join(sorted(a['classes']))}]")
    print(f"{'ALL':<12}{len(per_class):>8}{tot_sup:>11}{tot_inst - tot_sup:>13}"
          f"{tot_inst:>8}{tot_sup / tot_inst:>13.2%}")
    print()
    print(f"ASSERT instances == {EXPECTED_INSTANCES}: PASS")
    print(f"ASSERT supported == {EXPECTED_SUPPORTED}: PASS")
    print(f"wrote {os.path.relpath(OUT, REPO)}")


if __name__ == "__main__":
    main()