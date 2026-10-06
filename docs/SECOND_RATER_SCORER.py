#!/usr/bin/env python3
"""Score the second rater's answers: human-human Cohen's kappa (+ CI) vs the PI labels.

Usage:
    python3 docs/SECOND_RATER_SCORER.py second_rater_answers.csv

Inputs
    second_rater_answers.csv      columns: blind_id, label[, rationale]
                                  label in {tp, fp, unclear}
    pilot/second_rater_pack.csv   the blinded pack (sha256-verified)
    data/labels.jsonl             the PI's frozen verdicts (last-wins, human-owned)

Stdlib only. The blind -> row_id map is re-derived from the documented sampling recipe
(seed 2026, row_id tie-break) instead of being stored next to the pack, so the pack stays
blind; the pack's sha256 is verified first, so a drifted pack fails loudly.

Reports: n, observed agreement (po), chance agreement (pe), Cohen's kappa, a delta-method
95% interval for kappa (truncated to [-1, 1]), and the disagreement set with row_ids.

Dependence caveat printed with the result: duplicate-name rows (the same server::tool
registered more than once — e.g. rows 94/95 in the full sample; rows 79/82 inside this
pack) are not independent items, so kappa here is a descriptive consistency figure for
this pack, not an independent-trials estimate.
"""
import csv
import hashlib
import json
import math
import os
import random
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACK = os.path.join(REPO, "pilot", "second_rater_pack.csv")
LABELS = os.path.join(REPO, "data", "labels.jsonl")
PACK_SHA256 = "af27187869f749f69e95080b806ae4e5bd43ec771ca4226caece9b1d4124b77a"
SEED = 2026
Z = 1.959963984540054
VALID = {"tp", "fp", "unclear"}
# Duplicate-name rows: same server::tool appearing on more than one sample row
# (data/collection_report.md §5.10 census; rows 94/95 are the paper's canonical pair).
DUP_NAME_ROWS = {79, 82, 94, 95}


def blind_map():
    """blind_id -> row_id, re-derived from the documented recipe."""
    rng = random.Random(SEED)
    top = sorted(range(0, 100))
    ctrl = sorted(range(100, 150))
    pick = sorted(rng.sample(top, 32)) + sorted(rng.sample(ctrl, 8))
    rng.shuffle(pick)
    return {f"R{n:02d}": row for n, row in enumerate(pick, start=1)}


def verify_pack():
    data = open(PACK, "rb").read()
    got = hashlib.sha256(data).hexdigest()
    if got != PACK_SHA256:
        sys.exit(f"pack sha256 drift: {got} != recorded {PACK_SHA256}")
    rows = list(csv.DictReader(open(PACK, encoding="utf-8")))
    if len(rows) != 40:
        sys.exit(f"pack has {len(rows)} rows, expected 40")
    return rows


def human_labels():
    lab = {}
    for line in open(LABELS, encoding="utf-8"):
        line = line.strip()
        if line:
            r = json.loads(line)
            lab[int(r["row_id"])] = r["label"]
    return lab


def cohen_kappa(pairs):
    """(kappa, po, pe, se, n) from (human, rater) label pairs; delta-method SE."""
    n = len(pairs)
    if n == 0:
        return (None, None, None, None, 0)
    cats = sorted({a for a, _ in pairs} | {b for _, b in pairs})
    p = {}
    for a in cats:
        for b in cats:
            c = sum(1 for x, y in pairs if x == a and y == b)
            if c:
                p[(a, b)] = c / n
    a_m = {a: sum(v for (x, _), v in p.items() if x == a) for a in cats}
    b_m = {b: sum(v for (_, y), v in p.items() if y == b) for b in cats}
    po = sum(v for (x, y), v in p.items() if x == y)
    pe = sum(a_m[c] * b_m[c] for c in cats)
    if pe == 1:
        return (float("nan"), po, pe, None, n)
    kappa = (po - pe) / (1 - pe)
    grad = {}
    for (i, j) in p:
        delta = 1.0 if i == j else 0.0
        h = b_m[i] + a_m[j]
        grad[(i, j)] = ((delta - h) * (1 - pe) + (po - pe) * h) / (1 - pe) ** 2
    mean_g = sum(v * grad[c] for c, v in p.items())
    var = (sum(v * grad[c] ** 2 for c, v in p.items()) - mean_g ** 2) / n
    return (kappa, po, pe, math.sqrt(max(var, 0.0)), n)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    answers_path = sys.argv[1]
    pack_rows = verify_pack()
    bmap = blind_map()
    human = human_labels()

    answers = {}
    for r in csv.DictReader(open(answers_path, encoding="utf-8")):
        bid = (r.get("blind_id") or "").strip()
        lab = (r.get("label") or "").strip().lower()
        if not bid:
            continue
        if lab not in VALID:
            sys.exit(f"{bid}: label {lab!r} not in {sorted(VALID)}")
        answers[bid] = (lab, (r.get("rationale") or "").strip())

    missing = [row["blind_id"] for row in pack_rows if row["blind_id"] not in answers]
    extra = [b for b in answers if b not in bmap]
    if missing or extra:
        sys.exit(f"missing answers: {missing or 'none'}; unknown blind_ids: {extra or 'none'}")

    pairs, dis = [], []
    for row in pack_rows:
        bid = row["blind_id"]
        rid = bmap[bid]
        h = human.get(rid)
        if h is None:
            sys.exit(f"no PI label for row_id {rid}")
        a = answers[bid][0]
        # pack rows with no POI flag (classes_fired == 'none') cannot be 'tp'
        pairs.append((h, a))
        if h != a:
            dis.append((bid, rid, h, a, row["classes_fired"]))

    kappa, po, pe, se, n = cohen_kappa(pairs)
    print("=" * 68)
    print("Human-human consistency check (second-rater pack, seed 2026)")
    print("=" * 68)
    print(f"  n = {n}   po = {po:.4f}   pe = {pe:.4f}")
    if se is None:
        print("  kappa undefined (pe == 1)")
    else:
        lo, hi = kappa - Z * se, kappa + Z * se
        lo, hi = max(-1.0, lo), min(1.0, hi)
        print(f"  Cohen's kappa = {kappa:+.3f}   delta-method 95% CI "
              f"[{lo:+.2f}, {hi:+.2f}]   (SE {se:.3f})")
    print(f"  disagreements = {len(dis)}")
    for bid, rid, h, a, cls in dis:
        flag = "  [duplicate-name row: item independence reduced]" if rid in DUP_NAME_ROWS else ""
        print(f"    {bid}  row_id {rid:>3}  PI={h:<7} rater={a:<7} {cls}{flag}")
    if not dis:
        print("    (none)")
    print("\nNote: duplicate-name rows (same server::tool on more than one sample row —")
    print("rows 94/95 in the full sample, rows 79/82 in this pack) reduce item")
    print("independence, so kappa is a descriptive consistency figure for this pack.")
    print("Unclear answers are kept as a third category; the PI labels contain none.")


if __name__ == "__main__":
    main()
