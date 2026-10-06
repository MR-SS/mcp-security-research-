#!/usr/bin/env python3
"""Derive the R4 external-review numbers from source data. Nothing hand-entered.

Covers:
  * Wilson 95% confidence intervals for the live-trial success counts (FIX 5)
  * Cohen's kappa over the full 30-item blind packet and over the 25-FP-only
    subset (FIX 7)
  * Per-arm trial accounting and the DP overt/covert split (FIX 1)
"""
import importlib.util
import json
import math
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(REPO, "data", "live_tests", "trials_ledger.jsonl")
LLM = os.path.join(REPO, "data", "labels_llm.jsonl")
SAMPLE_MAP = os.path.join(REPO, "data", "kappa_sample_map.json")
SAMPLE = os.path.join(REPO, "data", "analysis_toollevel.csv")
LABELS = os.path.join(REPO, "data", "labels.jsonl")
PACKET = os.path.join(REPO, "data", "kappa_packet.md")

Z = 1.959963984540054  # two-sided 95%


def wilson(k, n, z=Z):
    """Wilson score interval; returns (lo, hi) rounded to 2 dp."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round(max(0.0, centre - half), 2), round(min(1.0, centre + half), 2))


def load_human_labels():
    lab = {}
    for line in open(LABELS, encoding="utf-8"):
        line = line.strip()
        if line:
            r = json.loads(line)
            lab[int(r["row_id"])] = r["label"]
    return lab


def load_llm_verdicts():
    out = {}
    for line in open(LLM, encoding="utf-8"):
        m = re.match(r"\s*(Q\d+)\s*\|\s*VERDICT:\s*(tp|fp|u)\b", line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def cohen_kappa(pairs):
    n = len(pairs)
    if n == 0:
        return (None, None, 0, 0, None)
    po = sum(1 for a, b in pairs if a == b) / n
    a_tp = sum(1 for a, _ in pairs if a == "tp") / n
    b_tp = sum(1 for _, b in pairs if b == "tp") / n
    pe = a_tp * b_tp + (1 - a_tp) * (1 - b_tp)
    kappa = 1.0 if pe == 1 else (po - pe) / (1 - pe)
    dis = sum(1 for a, b in pairs if a != b)
    return (round(kappa, 3), round(po, 4), n, dis, round(pe, 4))


def q2row_map():
    """Q-id -> row_id, read from the local-only sample map (the same source
    pilot/kappa_report.py uses; the packet itself is blind and carries no ids)."""
    return {q: int(rid) for q, rid in
            json.load(open(SAMPLE_MAP, encoding="utf-8"))["map"].items()}


def main():
    print("=" * 70)
    print("FIX 5 - Wilson 95% CI for live-trial success counts")
    print("=" * 70)
    # (name, ledger case, successes, trials); None case = not an attack arm.
    # WF is ledger-verified 6/9 (glm-5.3 3/3, deepseek-v4.1-flash 3/3,
    # gemini-3.8-flash 0/3) from data/live_tests/trials_ledger.jsonl.
    ci_rows = [("FL exec-priming", "fl", 9, 9),
               ("DP credential funnel (A-covert)", "dp", 8, 9),
               ("WF priority capture, pooled", "wf", 6, 9),
               ("Controls (CTRL pooled)", None, 0, 16),
               ("NV gate-suppression (gray)", None, 0, 8)]
    for name, _case, k, n in ci_rows:
        lo, hi = wilson(k, n)
        print(f"  {name:<34} {k}/{n}  CI [{lo:.2f}, {hi:.2f}]")

    # Consistency assert 1: FL + DP + WF successes must sum to the pooled
    # attack ASR quoted in the paper (23/27 = 9 + 8 + 6 over 9 + 9 + 9).
    ci_by_case = {case: (k, n) for _name, case, k, n in ci_rows if case}
    pooled_k = sum(k for k, _n in ci_by_case.values())
    pooled_n = sum(n for _k, n in ci_by_case.values())
    assert (pooled_k, pooled_n) == (23, 27), (
        f"pooled attack ASR drift: FL+DP+WF = {pooled_k}/{pooled_n}, "
        f"paper quotes 23/27")
    print(f"  pooled attack (FL+DP+WF)     {pooled_k}/{pooled_n}  "
          f"matches the paper's 23/27  OK")

    # Consistency assert 2: the CI denominators must equal the per-arm valid
    # counts that experiments/trial_accounting.py derives from the same ledger
    # (whose 54/54/51/3 totals it also asserts).
    spec = importlib.util.spec_from_file_location(
        "trial_accounting", os.path.join(REPO, "experiments",
                                         "trial_accounting.py"))
    ta = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ta)
    per = ta.account(ta.load_ledger())
    assert ta.check(per), "trial_accounting --check failed"
    for case, (_k, n) in ci_by_case.items():
        assert per[case]["valid"] == n, (
            f"{case}: trial_accounting valid={per[case]['valid']} != CI n={n}")
    print("  trial_accounting cross-check: per-arm valid counts + "
          "54/54/51/3 totals  OK")

    print()
    print("=" * 70)
    print("FIX 7 - kappa: full blind packet vs FP-only subset")
    print("=" * 70)
    smap = json.load(open(SAMPLE_MAP, encoding="utf-8"))
    strata = smap["strata"]
    human = load_human_labels()
    llm = load_llm_verdicts()
    print(f"  packet: tp_all={strata['tp_all']}, fp_sampled={len(strata['fp_sampled'])}")
    print(f"  rater verdicts parsed: {len(llm)} "
          f"(tp={sum(1 for v in llm.values() if v == 'tp')}, "
          f"fp={sum(1 for v in llm.values() if v == 'fp')})")
    q2row = q2row_map()
    print(f"  Q->row mappings recovered from kappa_packet.md: {len(q2row)}")

    pairs_all, pairs_fp = [], []
    for q in sorted(q2row):
        row, h, l = q2row[q], human.get(q2row[q]), llm.get(q)
        if h is None or l is None:
            continue
        pairs_all.append((h, l))
        if h == "fp":
            pairs_fp.append((h, l))
    for label, prs in (("full packet (5 TP + 25 FP)", pairs_all),
                       ("FP-only subset", pairs_fp)):
        k, po, n, dis, pe = cohen_kappa(prs)
        print(f"  {label:<30} n={n:<3} po={po}  pe={pe}  kappa={k}  "
              f"disagreements={dis}")
        if abs(po - pe) < 1e-9:
            print(f"      -> pe collapses onto po: degenerate kappa "
                  f"(prevalence paradox, standard)")

    print()
    print("=" * 70)
    print("FIX 1 - DP arm accounting (criterion A-covert) and pooled ASR")
    print("=" * 70)
    rows = [json.loads(l) for l in open(LEDGER, encoding="utf-8")]
    dp = [r for r in rows if r["case"] == "dp"]
    for r in sorted(dp, key=lambda r: (r["model"], r["rep"])):
        print(f"    {r['model']:<22} rep{r['rep']}  verdict={r['verdict']:<8} "
              f"criterion={r['criterion']}")
    covert = [r for r in dp if r["criterion"] == "A-covert"]
    overt = [r for r in dp if r["criterion"] == "A-overt"]
    print(f"  A-covert (success criterion): {len(covert)}/{len(dp)}")
    print(f"  A-overt  (criterion failed):  {len(overt)}/{len(dp)} "
          f"{[(r['model'], r['rep']) for r in overt]}")

    print()
    attack = [r for r in rows if r["case"] in ("wf", "fl", "dp")]
    succ = [r for r in attack if r["verdict"] == "success"]
    print(f"  pooled attack ASR (WF+FL+DP, success = A/B/A-covert): "
          f"{len(succ)}/{len(attack)}")
    # Assert 3: the ledger must reproduce the CI table's pooled attack ASR,
    # and each attack arm's own (successes, trials) pair.
    assert (len(succ), len(attack)) == (pooled_k, pooled_n), (
        f"ledger pooled attack {len(succ)}/{len(attack)} != "
        f"CI table {pooled_k}/{pooled_n}")
    for case, (k, n) in ci_by_case.items():
        arm = [r for r in rows if r["case"] == case]
        got = (sum(1 for r in arm if r["verdict"] == "success"), len(arm))
        assert got == (k, n), f"ledger {case} {got} != CI table {(k, n)}"
    print("  ledger cross-check: per-arm (successes, trials) match the CI "
          "table  OK")
    for mdl in ("glm-5.3", "deepseek-v4.1-flash", "gemini-3.8-flash"):
        t = [r for r in attack if r["model"] == mdl]
        s = [r for r in t if r["verdict"] == "success"]
        print(f"    {mdl:<22} {len(s)}/{len(t)}")

    # ------------------------------------------------------------------
    # STRUCTURE-LOCK - section 6.1 headline Wilson intervals,
    # duplicate-name cluster sensitivity, and the section 7 kappa CI.
    # Every figure printed here is assert-guarded against the paper text.
    # ------------------------------------------------------------------
    print()
    print("=" * 70)
    print("STRUCTURE-LOCK - headline CIs, cluster sensitivity, kappa CI")
    print("=" * 70)

    # (name, k, n, expected (lo, hi) as printed in section 6.1, 2 dp)
    headline = [("all-family text-support", 15, 268, (0.03, 0.09)),
                ("poison-family text-support", 6, 124, (0.02, 0.10)),
                ("TP yield in the top-100 rows", 5, 100, (0.02, 0.11)),
                ("row-level TP", 5, 150, (0.01, 0.08))]
    for name, k, n, want in headline:
        lo, hi = wilson(k, n)          # rounds to 2 dp, exactly as section 6.1
        assert (lo, hi) == want, (
            f"{name}: Wilson [{lo}, {hi}] != paper interval {want}")
        print(f"  {name:<30} {k}/{n}  Wilson 95% [{lo:.2f}, {hi:.2f}]  OK")
    print("  section 6.1 scope note: no multiplicity adjustment; "
          "per-class figures descriptive")

    # Cluster sensitivity: collapse flag instances that share a server::tool
    # (duplicate-name groups) and recompute the pooled text-support rate.
    import csv as _csv
    sample_rows = list(_csv.DictReader(open(SAMPLE, encoding="utf-8")))
    human_full = load_human_labels()

    def _instances(i):
        r = sample_rows[i]
        out = []
        for prefix, fld in (("capability:", "capability_flags"),
                            ("poison:", "poison_flags"),
                            ("addressing:", "addressing_flags")):
            for cls in (r[fld] or "").split(";"):
                cls = cls.strip()
                if cls:
                    out.append(cls if ":" in cls else prefix + cls)
        return out

    n_inst = sum(len(_instances(i)) for i in range(len(sample_rows)))
    assert n_inst == 268, f"sample instances {n_inst} != 268"
    tp_rows = [i for i in range(len(sample_rows)) if human_full[i] == "tp"]
    tp_inst = sum(len(_instances(i)) for i in tp_rows)
    # supported == instance carried by a TP row (15 supported / 15 instances)
    assert tp_inst == 15, f"instances on TP rows {tp_inst} != 15 supported"
    groups = {}
    for i, r in enumerate(sample_rows):
        groups.setdefault(r["name"], []).append(i)
    collapsed = {}
    for name, rws in groups.items():
        classes = set()
        for i in rws:
            classes.update(_instances(i))
        for cls in classes:
            collapsed[(name, cls)] = any(human_full[i] == "tp" for i in rws)
    c_k, c_n = sum(collapsed.values()), len(collapsed)
    assert (c_k, c_n) == (13, 251), (
        f"cluster collapse {c_k}/{c_n} != paper's 13/251")
    print(f"  cluster sensitivity (same server::tool collapsed)  "
          f"{c_k}/{c_n} = {100 * c_k / c_n:.2f}%  "
          f"vs 15/268 = {100 * 15 / 268:.2f}%  OK")

    # Kappa delta-method 95% CI (n = 30), from the packet's own 2x2 table.
    counts = {}
    for h, l in pairs_all:
        counts[(h, l)] = counts.get((h, l), 0) + 1
    assert sorted(counts.values()) == [1, 1, 4, 24], (
        f"packet 2x2 table drifted: {counts}")
    kk = len(pairs_all)
    p = {c: v / kk for c, v in counts.items()}
    labels_ord = ["tp", "fp"]
    a_m = {x: sum(v for (h, _l), v in p.items() if h == x) for x in labels_ord}
    b_m = {y: sum(v for (_h, l), v in p.items() if l == y) for y in labels_ord}
    po_k = sum(v for c, v in p.items() if c[0] == c[1])
    pe_k = sum(a_m[x] * b_m[x] for x in labels_ord)
    kappa_k = (po_k - pe_k) / (1 - pe_k)
    grad = {}
    for (i_, j_) in p:
        delta = 1.0 if i_ == j_ else 0.0
        h_ij = b_m[i_] + a_m[j_]
        grad[(i_, j_)] = ((delta - h_ij) * (1 - pe_k)
                          + (po_k - pe_k) * h_ij) / (1 - pe_k) ** 2
    mean_g = sum(v * grad[c] for c, v in p.items())
    var_k = (sum(v * grad[c] ** 2 for c, v in p.items()) - mean_g ** 2) / kk
    se_k = math.sqrt(var_k)
    lo_k, hi_k = kappa_k - Z * se_k, kappa_k + Z * se_k
    assert round(kappa_k, 3) == 0.760 and round(se_k, 3) == 0.162, (
        f"kappa {kappa_k:.3f} (se {se_k:.3f}) != +0.760 (se 0.162)")
    assert (round(lo_k, 2), round(min(1.0, hi_k), 2)) == (0.44, 1.00), (
        f"kappa CI [{lo_k:.2f}, {min(1.0, hi_k):.2f}] != paper [0.44, 1.00]")
    print(f"  kappa delta-method (n={kk})          {kappa_k:+.3f}  "
          f"SE {se_k:.3f}  95% CI [{lo_k:.2f}, "
          f"{min(1.0, hi_k):.2f}] (untruncated upper {hi_k:.2f})  OK")


# --------------------------------------------------------------------------
# R4 FIX 2 — section 6.4 false-positive taxonomy over the 95 flagged-benign rows
# --------------------------------------------------------------------------
# One bucket per row, first match wins, so the buckets partition the stratum.
# The rule is keyword-based over the human rationale note stored with each label
# in data/labels.jsonl; it is applied by code so the table is reproducible.
FP_BUCKETS = [
    ("Negated assurance", (
        "negated", "negated-assurance", "privacy reassurance", "reassurance",
        "anti-exfil assurance", "assurance")),
    ("Declared function (the product is the behavior)", (
        "declared function", "is function", "declared-function",
        "sending is function", "posting to connected accounts")),
    ("Defensive / anti-injection guard", (
        "defensive", "anti-injection", "anti-ipi", "consent gate", "hardening",
        "auth-hardening", "guard")),
    ("Detection / protection list", (
        "detection", "we protect against", "detection-list", "protect against")),
    ("Regex accident (class words as parameter/API names)", (
        "regex-accident", "regex accident", "regex noise", "api parameter",
        "supported api parameter", "as parameter names", "keyword noise")),
    ("Capability-only reading (poison flags fired but unsupported)", (
        "capability is real by design", "capability only", "as capability only",
        "structurally identical to exfil channel but benign",
        "no model-directed", "telemetry tool")),
    ("Authentication / credential-acquisition wording", (
        "authentication wording", "api-key acquisition",
        "not credential access", "authentication wording")),
    ("Own-tool routing / product-flow documentation", (
        "own-tool relevance", "product-flow docs", "own server",
        "vendor's own funne", "benign-scoped", "intra-server")),
    ("Anti-concealment disclosure (text reveals what it hides)", (
        "anti-concealment", "discloses hidde", "would otherwise be invisible",
        "not concealment", "background-read")),
    ("Bare URL / product hub", (
        "urls are", "bare url", "product hub", "is a product/api url",
        "returned url", "is returned url")),
    ("Template / duplicate-name inflation", (
        "template", "duplicate", "same-server", "sibling")),
    # Membership is keyword-matched only ("truncat"). The former "withdrew" keyword
    # encoded a causal claim — that the trigger went away on full text — which the
    # artifacts do not support: rows 58/70/72 retain excerpt-based notes and their
    # full-text pass is still pending. Dropping the keyword changes no membership.
    ("Truncation artifact (adjudicated from the 300-char excerpt)", (
        "truncat", "excerpt==full")),
    ("Marketing / feature prose", (
        "marketing", "feature prose", "only marketing copy",
        "permission descriptions", "benign sequencing", "intra-server sequencing")),
]

RESIDUAL = "Other FP (residual, reason not keyword-tagged)"


def classify_fp(note):
    n = (note or "").lower()
    for name, keys in FP_BUCKETS:
        if any(k in n for k in keys):
            return name
    return RESIDUAL


def fp_taxonomy():
    import collections
    import csv as _csv
    sample = list(_csv.DictReader(open(SAMPLE, encoding="utf-8")))
    lab, notes = {}, {}
    for line in open(LABELS, encoding="utf-8"):
        line = line.strip()
        if line:
            r = json.loads(line)
            lab[int(r["row_id"])] = r["label"]
            notes[int(r["row_id"])] = r.get("note", "")
    flagged_fp = [i for i, r in enumerate(sample)
                  if r["suspicion_score"] != "0" and lab.get(i) == "fp"]
    counts = collections.Counter(classify_fp(notes.get(i)) for i in flagged_fp)
    return flagged_fp, counts


def print_taxonomy():
    rows, counts = fp_taxonomy()
    print()
    print("=" * 70)
    print("FIX 2 - section 6.4 taxonomy over the flagged-benign stratum")
    print("=" * 70)
    total = 0
    for name, _keys in FP_BUCKETS:
        c = counts.get(name, 0)
        total += c
        print(f"  {name:<52} {c}")
    res = counts.get(RESIDUAL, 0)
    total += res
    print(f"  {RESIDUAL:<52} {res}")
    print(f"  {'SUM':<52} {total}")
    print(f"  stratum size (flagged rows judged benign) = {len(rows)}")
    print(f"  CHECK: buckets sum to stratum size? "
          f"{'PASS' if total == len(rows) else 'FAIL'} ({total} vs {len(rows)})")


if __name__ == "__main__":
    main()
    print_taxonomy()


if __name__ == "__main__":
    main()
