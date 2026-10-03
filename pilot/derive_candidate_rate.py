#!/usr/bin/env python3
"""R5 PHASE 1B - RQ1 candidate rate of the FROZEN detector over the full corpus.

Runs the frozen v2 detector (pilot/analyze.py::scan_text, imported unchanged)
over every stored tool description in data/github_tools.jsonl, i.e. the same
16,763-row population the validation sample was drawn from.

Reports, for the RQ1 "what candidate rate does the detector produce" question:
  * rows with >=1 flag of any family, corpus-wide
  * rows with >=1 poison-family flag
  * per-class row and instance counts
  * total flag instances corpus-wide

Output: data/candidate_rate_scan.csv (per-class) + a summary block printed for
the collection report. Stdlib only; the detector is imported, never modified.
"""
import collections
import csv
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(REPO, "data", "github_tools.jsonl")
ANALYZE = os.path.join(REPO, "pilot", "analyze.py")
OUT = os.path.join(REPO, "data", "candidate_rate_scan.csv")

EXPECTED_ROWS = 16763

sys.path.insert(0, os.path.join(REPO, "pilot"))
import analyze  # noqa: E402  (the frozen detector, imported unmodified)


def main():
    rows = 0
    row_any = 0
    row_poison = 0
    row_capability = 0
    row_channel = 0
    inst_any = 0
    inst_by_class = collections.Counter()
    rows_by_class = collections.Counter()
    repos = set()

    with open(CORPUS, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            rows += 1
            if r.get("repo"):
                repos.add(r["repo"])
            text = r.get("tool_description") or ""
            hits = analyze.scan_text(text)
            if not hits:
                continue
            row_any += 1
            inst_any += len(hits)
            fams = {k.split(":", 1)[0] for k in hits}
            if "poison" in fams:
                row_poison += 1
            if "capability" in fams:
                row_capability += 1
            if "addressing" in fams:
                row_channel += 1
            for cls in hits:
                rows_by_class[cls] += 1
                inst_by_class[cls] += len(hits[cls])

    assert rows == EXPECTED_ROWS, f"corpus rows {rows} != {EXPECTED_ROWS}"

    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["class", "family", "rows_flagged", "instances"])
        for cls in sorted(rows_by_class):
            w.writerow([cls, cls.split(":", 1)[0], rows_by_class[cls], inst_by_class[cls]])
        w.writerow(["__TOTAL__", "all", row_any, inst_any])

    print(f"corpus rows scanned            : {rows}")
    print(f"repositories                   : {len(repos)}")
    print(f"rows with >=1 flag (any family): {row_any}  "
          f"({row_any / rows:.4%} of the corpus)")
    print(f"rows with >=1 poison flag      : {row_poison}  "
          f"({row_poison / rows:.4%})")
    print(f"rows with >=1 capability flag  : {row_capability}  "
          f"({row_capability / rows:.4%})")
    print(f"rows with >=1 channel flag     : {row_channel}  "
          f"({row_channel / rows:.4%})")
    print(f"total flag instances (corpus)  : {inst_any}")
    print()
    print("per-class (rows flagged / instances):")
    for cls in sorted(rows_by_class, key=lambda c: -rows_by_class[c]):
        print(f"  {cls:<42} {rows_by_class[cls]:>6}  {inst_by_class[cls]:>6}")
    print()
    print(f"wrote {os.path.relpath(OUT, REPO)}")


if __name__ == "__main__":
    main()