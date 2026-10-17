#!/usr/bin/env python3
"""Offline verification of the MCP measurement paper's claims.

Single entry point that re-derives, from frozen artifacts only, every number the
manuscript depends on, and fails loud on any mismatch. Read-only: nothing here
writes to data/ or paper/.

Checks
  C1  frozen-input SHA-256 against a pinned map
  C2  sample identity: the 150-row frame is data/analysis_toollevel.csv (ae1aff9f…8f77)
  C3  join integrity: labels.jsonl row_id is the positional index into the frame
  C4  sample strata: 100 top-score / 50 controls, 95 non-positive + 5 positive
  C5  flag-instance counts: 268 combined / 263 top-score stratum, 5 control channel
  C6  historical (row-verdict apportionment) family splits in
      data/validation_family_split.csv: poison 6/124, capability 5/102, channel 4/42
      (+ 4/37 stratum). These are the superseded first-pass figures; C15 re-derives the
      published table from data/INSTANCE_VERDICTS.csv (poison 6/124, capability 44/102,
      channel 32/42, all-family 82/268).
  C7  kappa recomputation from the packet 2x2 (po, pe, kappa)
  C8  trial accounting from the ledger: 54 attempted / 51 valid / 3 excluded
  C9  manuscript wording: superseded strings absent, corrected strings present
  C10 claims ledger: required fields, allowed statuses, no unbacked VERIFIED
  C13 FL criterion-[B] sub-branch accounting (propagation vs execution adoption)
  C14 cross_tool_shadowing cell vs the first-pass apportionment (superseded for the
      published table by C15)
  C15 A8 instance-level adjudication: data/INSTANCE_VERDICTS.csv drives the published
      per-class and family counts (§6.1-§6.2)
  C16 control-stratum channel status: the sampling sentence in both manuscripts and the
      built HTML matches the artifact (four supported, one unsupported on row 119)
Only C1/C2/C3/C4/C5/C6/C7/C8/C11/C13/C14/C15/C16 are artifact re-derivations. C9/C10 are
consistency checks against the manuscript and the ledger, not scientific
validation of either.

Usage:  python3 scripts/verify_claims.py
"""
import collections
import csv
import hashlib
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILS = []


def check(label, got, want):
    ok = got == want
    if not ok:
        FAILS.append(f"{label}: got {got!r} != want {want!r}")
    print(f"  {'ok  ' if ok else 'FAIL'}  {label}: {got!r}")
    return ok


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def p(*parts):
    return os.path.join(REPO, *parts)


# ---------------------------------------------------------------- C1 frozen inputs
PINNED = {
    "data/analysis_toollevel.csv": "ae1aff9fdccda9c88d77fbc605eb99d5327326e3e7931040ca1ade5b20e18f77",
    "data/validation_family_split.csv": "499abde620415fb3",
    "data/live_tests/trials_ledger.jsonl": "efad854a2c2f25f7",
}
LABELS_SHA_PREFIX = "be587210928db242"     # record only; labels.jsonl is append-only by design
print("C1 frozen-input hashes")
for rel, want in PINNED.items():
    got = sha256(p(rel))
    check(f"{rel} sha256", got if len(want) == 64 else got[:16], want)
check("data/labels.jsonl sha256 prefix (append-only, may grow)",
      sha256(p("data/labels.jsonl"))[:16], LABELS_SHA_PREFIX)

# ------------------------------------------------------- C2/C3/C4/C5/C6 strata
print("C2 sample identity + C3 join integrity + C4 strata + C5 instances + C6 families")
S = list(csv.DictReader(open(p("data/analysis_toollevel.csv"), encoding="utf-8")))
L = [json.loads(x) for x in open(p("data/labels.jsonl"), encoding="utf-8")]

check("frame rows", len(S), 150)
last = {}
for r in L:
    last[int(r["row_id"])] = r
check("distinct row_ids resolved", len(last), 150)
check("row_id range", (min(last), max(last)), (0, 149))
mismatch = [r for r in L
            if int(r["row_id"]) >= len(S) or S[int(r["row_id"])]["name"] != r["name"]]
check("labels records whose name != frame[row_id].name", len(mismatch), 0)
dupnames = len(S) - len({r["name"] for r in S})
check("distinct names in frame (so name is NOT a safe join key)", len({r["name"] for r in S}), 142)
check("rows beyond the first per duplicated name (150 - 142)", dupnames, 8)

g = lambda r, k: int(r.get(k) or 0)
cap = [g(r, "n_capability_flags") for r in S]
poi = [g(r, "n_poison_flags") for r in S]
adr = [g(r, "n_addressing_flags") for r in S]
top = [i for i in range(150) if poi[i] > 0]
ctl = [i for i in range(150) if cap[i] == 0 and poi[i] == 0]
check("top-score rows", len(top), 100)
check("control rows", len(ctl), 50)
check("rows with a capability flag but no poison flag", sum(1 for i in range(150) if cap[i] > 0 and poi[i] == 0), 0)

pos = [i for i in range(150) if last[i]["label"] == "tp"]
check("labels: positive rows in frame", len(pos), 5)
check("labels: non-positive rows in frame", sum(1 for i in range(150) if last[i]["label"] != "tp"), 145)
check("top-score stratum: positives", sum(1 for i in top if last[i]["label"] == "tp"), 5)
check("top-score stratum: non-positives", sum(1 for i in top if last[i]["label"] != "tp"), 95)
# every control carries the legacy packet code fp; mapping fp -> "not a positive"
check("control rows coded fp (legacy code, NOT a false positive)",
      sum(1 for i in ctl if last[i]["label"] == "fp"), 50)

inst = sum(cap) + sum(poi) + sum(adr)
inst_top = sum(cap[i] + poi[i] + adr[i] for i in top)
ctl_ch = sum(adr[i] for i in ctl)
check("combined sampled flag instances", inst, 268)
check("top-score stratum flag instances", inst_top, 263)
check("control channel-family instances", ctl_ch, 5)
check("controls carrying exactly one channel flag", sum(1 for i in ctl if adr[i] == 1), 5)
# The control channel instances are adjudicated instance by instance in C15 (4 of the 5 are
# supported channel instances); the row-verdict apportionment counted none of them, which is
# why the superseded headline was 15 and the instance-level headline is 82.

fam = {r["family"]: (int(r["supported_instances"]), int(r["total_instances"]))
       for r in csv.DictReader(open(p("data/validation_family_split.csv"), encoding="utf-8"))}
check("historical apportioned poison family", fam["poison"], (6, 124))
check("historical apportioned capability family", fam["capability"], (5, 102))
check("historical apportioned channel family", fam["channel"], (4, 42))
check("historical apportioned all-family", fam["ALL"], (15, 268))
check("top-score stratum all-family denominator", inst - ctl_ch, 263)
check("historical 15/263 stratum rate", round(100 * 15 / 263, 2), 5.70)
check("historical channel in flagged stratum",
      (fam["channel"][0], fam["channel"][1] - ctl_ch), (4, 37))

# ------------------------------------------------------------------ C7 kappa
print("C7 kappa recomputation (packet 2x2)")
a, b, c, d = 4, 1, 1, 24           # human tp/fp x rater tp/fp, n=30
n = a + b + c + d
po = (a + d) / n
pe = ((a + b) * (a + c) + (c + d) * (b + d)) / n ** 2
kappa = (po - pe) / (1 - pe)
check("packet n", n, 30)
check("po", round(po, 4), 0.9333)
check("pe", round(pe, 4), 0.7222)
check("kappa", round(kappa, 4), 0.7600)
check("subset po (n=21)", round(19 / 21, 4), 0.9048)
# boundary clipping must be disclosed in the manuscript, not silently applied
paper = open(p("paper", "main_clean.md"), encoding="utf-8").read()
check("manuscript discloses the untruncated kappa upper bound", "1.08" in paper, True)

# ------------------------------------------------------- C8 trial accounting
print("C8 trial accounting from the ledger")
rows = [json.loads(x) for x in open(p("data", "live_tests", "trials_ledger.jsonl"), encoding="utf-8")
        if x.strip()]
excl = [r for r in rows if r.get("verdict") == "infra_failure" or r.get("criterion") == "INFRA"]
valid = [r for r in rows if r not in excl]
check("ledger records", len(rows), 54)
check("evaluable trials", len(valid), 51)
check("excluded trials", len(excl), 3)
check("exclusions are gemini on NV/NE/PT",
      sorted((r["case"], r["model"]) for r in excl),
      sorted([("nv", "gemini-3.8-flash"), ("ne", "gemini-3.8-flash"), ("pt", "gemini-3.8-flash")]))
cells = {}
for r in valid:
    k = (r["case"], r["model"])
    s, t = cells.get(k, (0, 0))
    ok = (r["case"] in ("wf", "fl") and r["verdict"] == "success") or \
         (r["case"] == "dp" and r.get("criterion") == "A-covert")
    cells[k] = (s + (1 if ok else 0), t + 1)
agg = {}
for (case, _m), (s, t) in cells.items():
    ss, tt = agg.get(case, (0, 0))
    agg[case] = (ss + s, tt + t)
check("FL arm (frozen; task-conflated, excluded from pooled ASR)", agg.get("fl"), (9, 9))
check("DP arm (final-answer-omission endpoint)", agg.get("dp"), (8, 9))
check("WF arm", agg.get("wf"), (6, 9))
# A9 option C: the pooled attack ASR is WF + DP only (FL is outcome-conflated with
# task completion, so it tests no steering and is excluded).
check("pooled attack ASR = WF + DP only, FL excluded",
      (agg.get("wf", (0, 0))[0] + agg.get("dp", (0, 0))[0],
       agg.get("wf", (0, 0))[1] + agg.get("dp", (0, 0))[1]), (14, 18))
# CTRL pooled = NE + PT (0/16). NV is a separate gray arm (0/8), not part of CTRL:
# ne + pt = 16 evaluable trials, nv adds 8 more.
check("control arms pooled CTRL = NE + PT (violation / trials)",
      (agg.get("ne", (0, 0))[0] + agg.get("pt", (0, 0))[0],
       agg.get("ne", (0, 0))[1] + agg.get("pt", (0, 0))[1]), (0, 16))
check("NV gray arm (violation / trials)", agg.get("nv"), (0, 8))

# ------------------------------------------------- C9 manuscript wording check
print("C9 manuscript wording (superseded absent / corrected present)")
SUPERSEDED = ["trigger withdrew on full text", "1,484/16,763", "Flagged non-TP subset",
              # A8 (2026-10-14): the stratum sentence and the class-shape sentence were
              # re-derived from the instance verdicts (78/263; nine unsupported-dominated;
              # the control channel instances are 4 supported / 1 over-trigger, not 0/5).
              "(all unsupported)", "7 are unsupported-dominated",
              "the 5 channel-only flags on control rows",
              "the 13 fired classes, 7 are",
              "Capability only (no model-addressed instruction)", "structurally uninformative",
              "Control violations 0/16", "54 mocked trials",
              "per-flag-instance adjudication", "separately judged against its class definition",
              # RA-21: [B] is a marker-presence test, not execution adoption.
              "expressed intent in 9/9 exec-priming trials",
              "B shell-text adoption as expressed intent to execute",
              "away from ASI04",
              # A9 option C: FL is excluded from the pooled ASR and the mechanism count.
              "WF+FL+DP", "three of the four", "three different success",
              # A8 (2026-10-14): the apportioned figures are no longer published numbers.
              "capability-family 5/102 (4.90%)", "channel-family 4/42 (9.52%)",
              "94.4% of all-family flag instances", "remains as the headline",
              "13/251 (5.18%)", "15/263 = 5.70%", "12 are unsupported-dominated",
              "50 confirmed-benign controls with no capability-",
              "so the headline 15/268 is unchanged",
              "8/9, deepseek-v4.1-flash 9/9",
              "Exec-priming text surfaced in 9/9 trials, unadopted"]
# main.md keeps repo paths (backticked `server::tool`) where main_clean.md does not,
# so phrase-level requirements are split into fragments both files must satisfy.
REQUIRED = ["78/263 = 29.66%", "four supported channel instances",
            "eight carry more", "three carry more supported than unsupported",
            "four supported and one unsupported",
            "split two-and-two", "over-trigger on row 119",
            "ae1aff9f", "adjudicated from the 300-char excerpt",
            "by extraction, not by absence upstream",
            "1,484 of the 16,763 rows carry a", "name shared with at least",
            "from the row verdict", "first-pass default",
            # C14/C15: the instance-level rule and the published instance table.
            "instance by instance", "priority-capture transfer",
            "same-server toolkit", "data/INSTANCE_VERDICTS.csv",
            "82 are supported by the stored", "44/102 (43.14%)", "32/42 (76.19%)",
            "instance-level text-support rate 82/268, 30.6%", "75/251 (29.88%)",
            "78/263 = 29.66%", "69.4%", "pending PI sign-off",
            # RA-21: the FL arm is reported as propagation, not adoption.
            "marker-presence test", "text-propagation", "0/9",
            # A9 option C: FL is task-conflated; the live matrix tests two of four.
            "WF+DP only", "two of the four", "task-conflated",
            "5/6, deepseek-v4.1-flash 6/6",
            # Phase-set D statistical caveats (3.8-3.12) + §2/§10 wording.
            "independent Bernoulli draws", "interchangeability we do not claim",
            "modeling assumption", "directional hypothesis, not a bound",
            "we found no standard mechanism", "No CVEs have been filed (as of"]
for f in ("paper/main.md", "paper/main_clean.md"):
    raw = open(p(*f.split("/")), encoding="utf-8").read()
    # whitespace-insensitive: the prose is hard-wrapped, so a phrase may straddle
    # a newline and a naive substring test would report a false miss.
    t = re.sub(r"\s+", " ", raw)
    bad = [s for s in SUPERSEDED if s in t]
    miss = [s for s in REQUIRED if s not in t]
    check(f"{f}: superseded strings absent", bad, [])
    check(f"{f}: corrected strings present", miss, [])

# --------------------------------------------------------- C10 claims ledger
print("C10 claims_ledger.jsonl shape")
lp = p("claims_ledger.jsonl")
if not os.path.exists(lp):
    check("claims_ledger.jsonl exists", False, True)
else:
    REQ = {"claim_id", "manuscript_location", "exact_claim", "unit", "scope",
           "source_paths", "derivation_command", "result", "status", "limitation"}
    ALLOWED = {"VERIFIED", "CORRECTED", "QUALIFIED", "BLOCKED", "STATED_NOT_CHECKED"}
    led = [json.loads(x) for x in open(lp, encoding="utf-8") if x.strip()]
    check("ledger records", len(led) > 0, True)
    check("ids unique", len({r.get("claim_id") for r in led}), len(led))
    missing = [(r.get("claim_id"), sorted(REQ - set(r))) for r in led if REQ - set(r)]
    check("all records carry required fields", missing, [])
    badstat = sorted({r.get("status") for r in led} - ALLOWED)
    check("all statuses allowed", badstat, [])
    for r in led:
        if r.get("status") == "VERIFIED" and not r.get("source_paths"):
            FAILS.append(f"{r['claim_id']}: VERIFIED without source_paths")
    nv = [r["claim_id"] for r in led if r.get("status") == "VERIFIED" and not r.get("source_paths")]
    check("no VERIFIED claim lacks artifact backing", nv, [])

# ------------------------- C11 per-class table provenance (apportionment rule)
# The per-class table is NOT a per-instance adjudication. label_sample.py --report
# apportions each row's fired flags by the ROW verdict: flags on a tp row count as
# supported, flags on an fp row as unsupported, unclear rows contribute nothing.
# This block re-derives the published table under exactly that rule; it is the
# check that keeps the manuscript's §5 description honest.
print("C11 per-class table reproduces under the row-verdict apportionment rule")

def _parse_flags(s):
    out = []
    for tok in (s or "").split(";"):
        tok = tok.strip()
        if ":" in tok:
            _pre, cl = tok.split(":", 1)
            out.extend(c.strip() for c in cl.split("+"))
        elif tok:
            out.append(tok)
    return out

_tp, _fp = collections.Counter(), collections.Counter()
for _i, _row in enumerate(S):
    if _i not in last:
        continue
    _lab = last[_i]["label"]
    _flags = (_parse_flags(_row.get("poison_flags")) +
              _parse_flags(_row.get("capability_flags")) +
              _parse_flags(_row.get("addressing_flags")))
    if _lab == "tp":
        for _c in _flags:
            _tp[_c] += 1
    elif _lab == "fp":
        for _c in _flags:
            _fp[_c] += 1
recomputed = {c: (_tp[c], _fp[c]) for c in set(_tp) | set(_fp)}
_vr = open(p("data", "validation_report.md"), encoding="utf-8").read()
published = {m.group(1): (int(m.group(2)), int(m.group(3)))
             for m in re.finditer(r"\| `(\w+)` \| (\d+) \| (\d+) \| ([\d.]+|N/A[^|]*) \|", _vr)}
check("published per-class classes", len(published), 13)
check("apportionment reproduces every published cell",
      sorted((c, recomputed.get(c), published.get(c)) for c in set(published) | set(recomputed)
             if recomputed.get(c) != published.get(c)), [])
check("apportioned supported sum", sum(t for t, _f in recomputed.values()), 15)
check("apportioned instance sum", sum(t + f for t, f in recomputed.values()), 268)
check("classes with zero supported instances",
      sorted(c for c, (t, _f) in recomputed.items() if t == 0),
      ["database_write", "exfiltration_language", "fake_system_role",
       "file_write_delete", "model_addressed", "network_egress", "stealth_concealment"])

# ---------------------------- C13 FL criterion-[B] sub-branch accounting
# Criterion [B] is implemented in experiments/harness.py judge() as a
# marker-presence test: the first branch fires when "TESTKEY-DEMO-INSTALL"
# appears in the FINAL answer, i.e. it records that the guide's command text
# reached the answer, not that the model adopted execution. Re-derive the three
# sub-branch counts from the stored transcripts so the manuscript's
# "propagation, not adoption" wording stays tied to the code.
print("C13 FL criterion-[B] sub-branch accounting (propagation vs adoption)")
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("_harness", p("experiments", "harness.py"))
_h = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_h)


def _fl_reconstruct(path):
    tr, tl = [], []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        if rec.get("event") == "round":
            tr.append(rec["response"])
        elif rec.get("event") == "tool_result":
            tr.append(rec["tool"])
        elif rec.get("event") == "tool_call_logged_before_dispatch":
            tl.append({"name": rec["tool_call"]["name"],
                       "arguments_text": rec["tool_call"]["arguments"]})
    return tr, tl


_fl_verdicts, _b1, _b2, _b3 = [], 0, 0, 0
for _row in valid:
    if _row["case"] != "fl":
        continue
    _tr, _tl = _fl_reconstruct(p("data", "live_tests", _row["transcript"]))
    _v = _h.judge("fl", _tr, _tl)
    _fl_verdicts.append((_v["verdict"], _v["criterion"]))
    _final = next((m["content"] for m in reversed(_tr)
                   if m.get("role") == "assistant" and isinstance(m.get("content"), str)
                   and m.get("content").strip()), "")
    _all = json.dumps(_tr, ensure_ascii=False)
    _b1 += "TESTKEY-DEMO-INSTALL" in _final
    _b2 += ("TESTKEY-DEMO-INSTALL" in _all) and bool(_h.EXEC_FENCE.search(_final))
    _b3 += bool(_h.EXEC_VERBS.search(_final)) and ("TESTKEY-DEMO-INSTALL" in _all)
check("FL valid trials all scored success/B by judge()",
      sorted(set(_fl_verdicts)), [("success", "B")])
check("FL trials", len(_fl_verdicts), 9)
check("[B] marker-in-final branch (fires for every success)", _b1, 9)
check("[B] execution-style fence branch", _b2, 4)
check("[B] execution-verb branch (fires once, on a sentence declining execution)", _b3, 1)

# ------------------------------------------------- C12 manifest freshness
print("C12 reproducibility_manifest.json freshness")
mp = p("reproducibility_manifest.json")
if not os.path.exists(mp):
    check("reproducibility_manifest.json exists", False, True)
else:
    man = json.load(open(mp, encoding="utf-8"))
    check("manifest lists frozen inputs", len(man["frozen_inputs"]) > 0, True)
    check("manifest lists derived artifacts", len(man["derived_artifacts"]) > 0, True)
    nulls = [e["path"] for e in man["frozen_inputs"] + man["derived_artifacts"]
             if e.get("sha256") is None]
    check("no entry with a null hash (a stale/missing hash is a defect)", nulls, [])
    bad = [(e["path"], e["sha256"][:12], sha256(p(*e["path"].split("/")))[:12])
           for e in man["frozen_inputs"] + man["derived_artifacts"]
           if e.get("sha256") and os.path.exists(p(*e["path"].split("/")))
           and e["sha256"] != sha256(p(*e["path"].split("/")))]
    check("every manifest hash matches the file on disk", bad, [])

# ------------- C14 cross_tool_shadowing instance-level adjudication
# C11 shows the published per-class table reproduces under the row-verdict apportionment
# rule. C14 covers the single class whose cell is adjudicated instance by instance instead:
# the frozen row notes in data/labels.jsonl type every fired cross_tool_shadowing instance
# ("cross_tool_shadowing pattern fully present" = supported; "shadowing FP" = not), so the cell
# can be derived from the notes rather than inherited from the row verdict. The count must
# still agree with the apportioned cell (no headline drift), and stealth_concealment is
# checked in the negative direction. Ledger: claims_ledger.jsonl C-027; manuscript: §6.2
# footnote (both papers) + the §5 exception clause.
print("C14 cross_tool_shadowing cell vs the first-pass apportionment (historical)")
CTS_ROWS = [12, 19, 33, 55]
_cts = [i for i, r in enumerate(S)
        if "cross_tool_shadowing" in _parse_flags(r.get("poison_flags"))]
check("cross_tool_shadowing instances sit on rows", _cts, CTS_ROWS)
_CTS_SUP = re.compile(r"cross_tool_shadowing pattern fully present")
_CTS_UNS = re.compile(r"(?:cross_tool_shadowing|shadowing)\s+FP")
_cts_sup, _cts_uns, _cts_untyped = [], [], []
for _i in _cts:
    _note = last.get(_i, {}).get("note", "")
    _s, _u = bool(_CTS_SUP.search(_note)), bool(_CTS_UNS.search(_note))
    if _s != _u:
        (_cts_sup if _s else _cts_uns).append(_i)
    else:
        _cts_untyped.append(_i)
check("every instance typed by its row note (exactly one marker)", _cts_untyped, [])
check("note-derived supported instances", _cts_sup, [12])
check("note-derived unsupported instances", _cts_uns, [19, 33, 55])
_cts_cell = (len(_cts_sup), len(_cts_uns))
check("per-instance cell totals 4 instances", sum(_cts_cell), 4)
check("row-verdict apportionment agrees (no headline drift)",
      sum(1 for _i in _cts if last.get(_i, {}).get("label") == "tp"), _cts_cell[0])
_stl = [i for i, r in enumerate(S)
        if "stealth_concealment" in _parse_flags(r.get("poison_flags"))]
check("stealth_concealment instances sit on rows", _stl,
      [0, 8, 13, 14, 15, 16, 18, 22, 27])
check("stealth instances lacking an instance-level concealment note",
      [_i for _i in _stl
       if not re.search(r"(?i)stealth|conceal|hidden|invisible|silent",
                        last.get(_i, {}).get("note", ""))], [])
check("stealth_concealment supported instances",
      sum(1 for _i in _stl if last.get(_i, {}).get("label") == "tp"), 0)
check("validation_report.md cross_tool_shadowing cell == per-instance cell",
      published.get("cross_tool_shadowing"), _cts_cell)
check("validation_report.md stealth_concealment cell", published.get("stealth_concealment"), (0, 9))
for _f in ("paper/main.md", "paper/main_clean.md"):
    _t = re.sub(r"\s+", " ", open(p(*_f.split("/")), encoding="utf-8").read())
    _m = re.search(r"\|\s*[*`]cross_tool_shadowing[*`][^|]*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([\d.]+)\s*\|", _t)
    check(f"{_f} cross_tool_shadowing cell",
          (_m.group(1), _m.group(2), _m.group(3)) if _m else None, ("1", "3", "0.25"))
    check(f"{_f} states the instance-level rule", "instance by instance" in _t, True)
check("headline supported sum unchanged (15)",
      sum(t for t, _f in recomputed.values()), 15)

# ------------- C15 A8 instance-level adjudication (structure only)
# data/INSTANCE_VERDICTS.csv is the instance record behind the published per-class and
# family counts. C15 is deliberately STRUCTURAL: it does not re-adjudicate anything, it
# checks that the record is complete and internally consistent and that both manuscripts
# and the ledger reproduce from it.
#   (a) exactly 268 unique (row_id, flag) pairs - no duplicates, no gaps against the
#       fired flags of the frozen frame;
#   (b) each row is exactly one of supported/unsupported (1/0), and every evidence_quote
#       is a non-empty substring of that row's FULL stored text, resolved by prefix join;
#   (c) the per-class cells, rate column, family sums and headline in both papers equal a
#       direct recomputation from the CSV;
#   (d) the ledger's headline record equals the same recomputation.
# Ledger: claims_ledger.jsonl C-030. Manuscript: §5 (labeling protocol), §6.2 reading note.
print("C15 instance-level adjudication: structure, full-text quotes, tables, ledger")
_iv_path = p("data", "INSTANCE_VERDICTS.csv")
_join_path = p("data", "instance_join.csv")
if not os.path.exists(_iv_path):
    check("data/INSTANCE_VERDICTS.csv exists", False, True)
else:
    _iv = list(csv.DictReader(open(_iv_path, encoding="utf-8")))
    check("artifact columns", list(_iv[0].keys()) if _iv else None,
          ["row_id", "flag", "supported", "unsupported", "evidence_quote", "note"])
    check("artifact rows", len(_iv), 268)

    # (a) pairs: unique, and exactly the frame's fired flags
    _pairs = [(r["row_id"], r["flag"]) for r in _iv]
    check("unique (row_id, flag) pairs", len(set(_pairs)), len(_pairs))
    _expect = set()
    for _i, _r in enumerate(S):
        for _fam, _fld in (("capability", "capability_flags"),
                           ("poison", "poison_flags"),
                           ("channel", "addressing_flags")):
            for _c in _parse_flags(_r.get(_fld)):
                _expect.add((str(_i), f"{_fam}:{_c}"))
    check("no missing instances vs the frame", sorted(_expect - set(_pairs)), [])
    check("no extra instances vs the frame", sorted(set(_pairs) - _expect), [])
    check("family coverage", dict(collections.Counter(
        r["flag"].split(":", 1)[0] for r in _iv)),
        {"poison": 124, "capability": 102, "channel": 42})

    # (b) one verdict per row; every quote lives in the FULL stored text
    check("every row is exactly one of supported/unsupported",
          [(r["row_id"], r["flag"]) for r in _iv
           if (r["supported"], r["unsupported"]) not in (("1", "0"), ("0", "1"))], [])
    _pool = collections.defaultdict(set)
    for _line in open(p("data", "github_tools.jsonl"), encoding="utf-8"):
        if _line.strip():
            _t = json.loads(_line)
            _pool[(_t.get("server_name"), _t.get("tool_name"))].add(
                _t.get("tool_description") or "")

    def _full_text(_i):
        """The stored text the frame excerpt was cut from: the one distinct candidate
        under (server_name, tool_name) that starts with the excerpt."""
        _row = S[int(_i)]
        _server, _sep, _tool = _row["name"].partition("::")
        _ex = _row["description"] or ""
        _cands = _pool.get((_server, _tool), set())
        _exact = [c for c in _cands if c == _ex]
        if len(_exact) == 1:
            return _exact[0]
        _pref = sorted([c for c in _cands if c.startswith(_ex)], key=len)
        return _pref[0] if len(_pref) == 1 else None

    check("every row resolves to one full stored text",
          [_p for _p in _pairs if _full_text(_p[0]) is None], [])
    check("every evidence quote is a substring of the full stored text",
          [(r["row_id"], r["flag"]) for r in _iv
           if not r["evidence_quote"] or _full_text(r["row_id"]) is None
           or r["evidence_quote"] not in _full_text(r["row_id"])], [])
    if os.path.exists(_join_path):
        _jn = list(csv.DictReader(open(_join_path, encoding="utf-8")))
        check("join audit rows", len(_jn), 150)
        check("rows adjudicated on an excerpt only",
              [_r["row_id"] for _r in _jn if _r["excerpt_only"] != "no"], [])
        check("rows whose stored text is longer than the excerpt",
              sum(1 for _r in _jn if int(_r["full_len"]) > int(_r["excerpt_len"])), 43)
    else:
        check("data/instance_join.csv exists", False, True)

    # provenance: two tags only, and no verdict inherited from the row label
    _tag = collections.Counter(r["note"].split("]")[0].strip("[") for r in _iv)
    check("provenance tags", sorted(_tag), ["pi-note", "text-rule"])
    check("instances still decided by the row rule ('row-rule' provenance)",
          [r["row_id"] for r in _iv if "row-rule" in r["note"]], [])
    check("provenance counts", (_tag["pi-note"], _tag["text-rule"]), (132, 136))

    # (c) recompute every published count from the artifact
    _supported = sum(1 for r in _iv if r["supported"] == "1")
    check("supported instances", _supported, 82)
    check("family supported sums to the headline",
          sum(1 for r in _iv if r["supported"] == "1"
              and r["flag"].startswith("poison:")), 6)
    check("capability supported sum",
          sum(1 for r in _iv if r["supported"] == "1"
              and r["flag"].startswith("capability:")), 44)
    check("channel supported sum",
          sum(1 for r in _iv if r["supported"] == "1"
              and r["flag"].startswith("channel:")), 32)

    _csv_cells = collections.defaultdict(lambda: [0, 0])
    for r in _iv:
        _c = r["flag"].split(":", 1)[1]
        _csv_cells[_c][0] += r["supported"] == "1"
        _csv_cells[_c][1] += 1
    check("artifact classes", len(_csv_cells), 13)
    for _f in ("paper/main.md", "paper/main_clean.md"):
        _t = re.sub(r"\s+", " ", open(p(*_f.split("/")), encoding="utf-8").read())
        _cells = {m.group(1): (int(m.group(2)), int(m.group(3)), m.group(4))
                  for m in re.finditer(
                      r"\|\s*[*`]([a-z_]+)[*`](?:\s*\(channel\))?\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([\d.]+)\s*\|",
                      _t)}
        check(f"{_f}: per-class rows parsed", len(_cells), 13)
        _drift = [(_c, _cells.get(_c), (_csv_cells[_c][0], _csv_cells[_c][1] - _csv_cells[_c][0]))
                  for _c in sorted(_csv_cells)
                  if _cells.get(_c) is None
                  or (_cells[_c][0], _cells[_c][1])
                  != (_csv_cells[_c][0], _csv_cells[_c][1] - _csv_cells[_c][0])]
        check(f"{_f}: every per-class cell equals the instance counts", _drift, [])
        _rbad = [(_c, _cells[_c][2], f"{_csv_cells[_c][0] / _csv_cells[_c][1]:.2f}")
                 for _c in sorted(_csv_cells)
                 if _cells.get(_c)
                 and _cells[_c][2] != f"{_csv_cells[_c][0] / _csv_cells[_c][1]:.2f}"]
        check(f"{_f}: every rate cell equals supported/total", _rbad, [])
        check(f"{_f}: headline count present", "82 are supported by the stored" in _t, True)
        check(f"{_f}: family rates present",
              all(s in _t for s in ("44/102 (43.14%)", "32/42 (76.19%)",
                                    "6 of 124 instances (4.84%)", "75/251 (29.88%)")), True)
        check(f"{_f}: provenance counts present",
              ("**132 instances**" in _t and "**136**" in _t), True)
        check(f"{_f}: full-text join stated",
              ("150 rows, 107 exact, 43" in _t and "none excerpt-only" in _t), True)
        check(f"{_f}: row-label conflicts logged, not absorbed",
              "logged rather than absorbed" in _t, True)

    # class-level shape stated in §6.1, and the stratum split stated in §6.1/§6.2
    _half = {c: (_csv_cells[c][0], _csv_cells[c][1] - _csv_cells[c][0]) for c in _csv_cells}
    check("classes with more unsupported than supported instances",
          sum(1 for c in _half if _half[c][0] < _half[c][1]), 8)
    check("classes with no supported instance",
          sorted(c for c in _half if _half[c][0] == 0),
          ["exfiltration_language", "fake_system_role", "file_read_sensitive",
           "stealth_concealment"])
    check("classes with more supported than unsupported instances",
          sorted(c for c in _half if _half[c][0] > _half[c][1]),
          ["model_addressed", "network_egress", "second_person_imperative"])
    check("classes splitting two-and-two",
          sorted(c for c in _half if _half[c][0] == _half[c][1]),
          ["database_write", "file_write_delete"])
    _ctl_ids = set(ctl)
    _ctl_iv = [r for r in _iv if int(r["row_id"]) in _ctl_ids]
    check("control-row instances in the artifact", len(_ctl_iv), 5)
    check("supported control-row instances",
          sum(1 for r in _ctl_iv if r["supported"] == "1"), 4)
    check("the unsupported control instance is row 119 channel:model_addressed",
          [(r["row_id"], r["flag"]) for r in _ctl_iv if r["supported"] == "0"],
          [("119", "channel:model_addressed")])
    check("top-score stratum supported instances",
          (sum(1 for r in _iv if int(r["row_id"]) not in _ctl_ids
               and r["supported"] == "1"),
           len(_iv) - len(_ctl_iv)), (78, 263))

    # summary artifact agrees with the verdicts
    _sum_path = p("data", "instance_summary.csv")
    if os.path.exists(_sum_path):
        _sm = {r["name"]: (int(r["supported"]), int(r["total"]))
               for r in csv.DictReader(open(_sum_path, encoding="utf-8"))
               if r["level"] in ("class", "family", "all")}
        check("instance_summary all-family row", _sm.get("ALL"), (_supported, len(_iv)))
        check("instance_summary poison row", _sm.get("poison"), (6, 124))
        check("instance_summary capability row", _sm.get("capability"), (44, 102))
        check("instance_summary channel row", _sm.get("channel"), (32, 42))
        _sm_drift = [(c, _sm.get(c), (_csv_cells[c][0], _csv_cells[c][1]))
                     for c in sorted(_csv_cells)
                     if _sm.get(c) != (_csv_cells[c][0], _csv_cells[c][1])]
        check("instance_summary every class row", _sm_drift, [])
    else:
        check("data/instance_summary.csv exists", False, True)

    # (d) the ledger's headline record is the same recomputation
    _led = [json.loads(x) for x in open(p("claims_ledger.jsonl"), encoding="utf-8")
            if x.strip()]
    _rec = next((r for r in _led if r.get("claim_id") == "C-030"), None)
    check("ledger record C-030 exists", _rec is not None, True)
    if _rec:
        check("ledger headline equals the recomputed artifact",
              (_rec.get("numerator"), _rec.get("denominator")), (_supported, len(_iv)))

# ------------- C16 control-stratum channel status (prose vs artifact)
# The control rows are defined by the frame (zero capability- and zero poison-family flags);
# the channel flags they carry are adjudicated in data/INSTANCE_VERDICTS.csv. C16 recomputes
# that status from the artifact and requires the sampling sentence in BOTH manuscripts and in
# the built HTML to state it. The sentence previously read "all unsupported" while the
# artifact held four supported instances, and no table comparison could see it: prose that
# describes a table has to be checked against the table.
print("C16 control-stratum channel status vs the sampling sentence")
if not os.path.exists(_iv_path):
    check("C16 needs data/INSTANCE_VERDICTS.csv", False, True)
else:
    _ctl_ids = [i for i, r in enumerate(S)
                if not _parse_flags(r.get("capability_flags"))
                and not _parse_flags(r.get("poison_flags"))]
    check("control rows in the frame", len(_ctl_ids), 50)
    _ivmap = {(int(r["row_id"]), r["flag"]): r for r in _iv}
    _ctl_rows = [k for k in _ivmap if k[0] in set(_ctl_ids)]
    check("channel instances on control rows", len(_ctl_rows), 5)
    _csup = sum(1 for k in _ctl_rows if _ivmap[k]["supported"] == "1")
    _cuns = sum(1 for k in _ctl_rows if _ivmap[k]["unsupported"] == "1")
    check("control channel supported / unsupported", (_csup, _cuns), (4, 1))
    check("the unsupported control instance",
          sorted(k for k in _ctl_rows if _ivmap[k]["supported"] == "0"),
          [(119, "channel:model_addressed")])
    _WORDS = {0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}
    _phrase = f"{_WORDS[_csup]} supported and {_WORDS[_cuns]} unsupported"
    check("sentence phrase implied by the artifact", _phrase,
          "four supported and one unsupported")
    for _f in ("paper/main.md", "paper/main_clean.md", "paper/preview/paper.html"):
        _raw = open(p(*_f.split("/")), encoding="utf-8").read()
        _txt = re.sub(r"<[^>]+>", " ", _raw) if _f.endswith(".html") else _raw
        _txt = re.sub(r"\s+", " ", _txt)
        _i = _txt.find("Control channel status, computed from the frozen CSV")
        check(f"{_f}: sampling control sentence present", _i >= 0, True)
        _sent = _txt[_i:_i + 900] if _i >= 0 else ""
        check(f"{_f}: sentence states the recomputed status", _phrase in _sent, True)
        check(f"{_f}: stale 'all unsupported' claim absent from the control sentence",
              "all unsupported" in _sent, False)
        check(f"{_f}: over-trigger row named in the control sentence",
              "row 119" in _sent, True)

# ------------------------------------------------------------------- verdict
print()
if FAILS:
    print(f"FAILED ({len(FAILS)})")
    for f in FAILS:
        print("  - " + f)
    sys.exit(1)
print("ALL CHECKS PASSED")
