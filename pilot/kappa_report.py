#!/usr/bin/env python3
"""Brief 06 Mode B phase 2 — Cohen's kappa between the blind LLM rater and the human labels.

Protocol (prompts/06-second-opinion.md, Mode B): 30 items (5 tp-stratum rows 12/35/60/94/95
+ 25 fp rows, random.seed(20260927)) were relabeled blind by an LLM rater from
`data/kappa_packet.md`. The rater's verdicts arrive as `data/labels_llm.jsonl` — either
JSON records {Q-id, verdict} or the raw BATCH MODE lines
    QXX | VERDICT: tp|fp|unclear | one-line reason ...
parsing is deliberately weatherproof (case, spacing, '*' emphasis, '|' vs ':' separators).
The join to human labels goes through `data/kappa_sample_map.json` (LOCAL-ONLY Q->row_id).

HARD RULE (Mode B): the rater's opinions NEVER touch `data/labels.jsonl`. This script only
reads both sides and reports agreement. It writes `data/kappa_report.md` — and nothing else —
and only when all 30 items parsed cleanly. If `data/labels_llm.jsonl` is absent: prints
`awaiting rater output`, exits 2, writes nothing.

Usage:
  python3 pilot/kappa_report.py                 # compute + write data/kappa_report.md
  python3 pilot/kappa_report.py --selftest      # synthetic-data checks, no real files touched

Exit codes: 0 ok · 1 parse/validation failure (loud) · 2 awaiting rater output.
Stdlib only (AGENTS.md §2.7). Detector/artifact rules are untouched (AGENTS.md §2.9).
"""
import argparse, csv, json, math, re, sys, datetime, hashlib
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
DATA = HERE / "data"
SAMPLE = DATA / "analysis_toollevel.csv"
LABELS = DATA / "labels.jsonl"
MAP = DATA / "kappa_sample_map.json"
LLM = DATA / "labels_llm.jsonl"
REPORT = DATA / "kappa_report.md"

EXPECTED_N = 30
VALID_VERDICTS = ("tp", "fp", "unclear")
VERDICT_ALIASES = {"u": "unclear", "unc": "unclear"}
CATS_3 = ("tp", "fp", "unclear")


class ParseAbort(Exception):
    """Loud, fatal input problem — the report must not be written."""


# ---------------------------------------------------------------- parsing (weatherproof)

_QID_RE = re.compile(r"\bQ\s*[-–—]?\s*0*(\d{1,2})\b", re.IGNORECASE)
_VERDICT_MARKED_RE = re.compile(
    r"(?:VERDICT|verdict|label|LABEL)\s*\**\s*[:=]\s*\**\s*(tp|fp|unclear|u|unc)\b",
    re.IGNORECASE)
_VERDICT_BARE_RE = re.compile(r"\b(tp|fp|unclear|u|unc)\b[\s\]|:.]*$", re.IGNORECASE)

_QID_JSON_KEYS = {"q", "qid", "q_id", "q-id", "id", "item", "item_id", "item-id", "number"}
_VERDICT_JSON_KEYS = {"verdict", "label", "rating", "decision"}


def _norm_verdict(token):
    v = (token or "").strip().strip("*'\"").strip().lower()
    v = VERDICT_ALIASES.get(v, v)
    if v in VALID_VERDICTS:
        return v
    return None


def _norm_qid(num):
    q = int(num)
    if not (1 <= q <= 99):
        return None
    return f"Q{q:02d}"


def parse_llm_line(line):
    """Return (qid, verdict) for one rater line, or None if the line is not an item.

    Raises ParseAbort for a line that looks like an item but carries an unusable id or
    verdict (loud failure beats silent skipping)."""
    s = line.strip()
    if not s or s.startswith("#"):
        return None

    # 1) JSON record path
    if s.startswith("{"):
        try:
            obj = json.loads(s)
        except json.JSONDecodeError:
            obj = None
        if isinstance(obj, dict):
            low = {str(k).strip().lower(): v for k, v in obj.items()}
            qkey = next((k for k in low if k in _QID_JSON_KEYS), None)
            vkey = next((k for k in low if k in _VERDICT_JSON_KEYS), None)
            if qkey is None or vkey is None:
                raise ParseAbort(f"JSON record without Q-id/verdict keys: {s[:80]!r}")
            m = re.search(r"0*(\d{1,2})", str(low[qkey]))
            qid = _norm_qid(m.group(1)) if m else None
            verdict = _norm_verdict(str(low[vkey]))
            if qid is None or verdict is None:
                raise ParseAbort(f"JSON record with unusable Q-id/verdict: {s[:80]!r}")
            return qid, verdict
        raise ParseAbort(f"unparseable JSON line: {s[:80]!r}")

    # 2) raw BATCH MODE line path: 'QXX | VERDICT: tp | reason ...'
    mq = _QID_RE.search(s)
    if not mq:
        return None                      # prose line without any Q-id: ignore quietly
    qid = _norm_qid(mq.group(1))
    if qid is None:
        raise ParseAbort(f"Q-id out of range 1..99: {s[:80]!r}")
    mv = _VERDICT_MARKED_RE.search(s) or _VERDICT_BARE_RE.search(s)
    if not mv:
        item_shaped = re.match(r"\s*\**\s*[Qq]\s*\d", s)
        if item_shaped:
            raise ParseAbort(f"Q-id present but no parsable verdict: {s[:80]!r}")
        return None                      # Q-id mentioned mid-prose, no verdict: inert
    verdict = _norm_verdict(mv.group(1))
    if verdict is None:
        raise ParseAbort(f"unknown verdict token: {s[:80]!r}")
    return qid, verdict


def parse_llm_file(path):
    """Parse the whole rater file. Returns (items, warnings).

    Weatherproof to formatting drift; loud on duplicates/unmatched/unknown verdicts."""
    raw = Path(path).read_text(encoding="utf-8")
    items, warnings, order = {}, [], []
    for lineno, line in enumerate(raw.splitlines(), 1):
        try:
            parsed = parse_llm_line(line)
        except ParseAbort as e:
            raise ParseAbort(f"line {lineno}: {e}")
        if parsed is None:
            continue
        qid, verdict = parsed
        if qid in items:
            if items[qid][0] == verdict:
                warnings.append(f"line {lineno}: duplicate {qid} (same verdict {verdict}) "
                                f"— first occurrence kept")
                continue
            raise ParseAbort(f"line {lineno}: conflicting duplicate {qid}: "
                             f"{items[qid][0]} vs {verdict} — resolve before computing")
        items[qid] = (verdict, lineno)
        order.append(qid)
    return items, warnings, order


def validate_items(items, expected_qids):
    """Loud validation: exactly the expected 30, no extras. Returns the parsed subset."""
    missing = sorted(set(expected_qids) - set(items))
    unmatched = sorted(set(items) - set(expected_qids))
    if missing:
        raise ParseAbort(f"missing rater verdicts for {len(missing)} item(s): "
                         f"{', '.join(missing)}")
    if unmatched:
        raise ParseAbort(f"rater produced {len(unmatched)} item(s) outside the packet: "
                         f"{', '.join(unmatched)}")
    return {q: items[q][0] for q in sorted(expected_qids)}


# ---------------------------------------------------------------- inputs

def load_human_labels(path=LABELS):
    """Last-wins per row_id (same read rule as label_sample.load_labels)."""
    labels = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
                labels[str(r["row_id"])] = r
            except (json.JSONDecodeError, KeyError):
                pass
    return labels


def load_map(path=MAP):
    m = json.loads(Path(path).read_text(encoding="utf-8"))
    qmap = {q: str(rid) for q, rid in m["map"].items()}
    return qmap, m


def load_poi_sets(sample_path=SAMPLE):
    """row_id -> bool: does the sampled row carry >=1 poison flag?"""
    poi = {}
    with open(sample_path, newline="", encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f)):
            flags = [p for p in (row.get("poison_flags", "") or "").split(";") if p.strip()]
            poi[str(i)] = bool(flags)
    return poi


def human_label_of(labels, row_id):
    rec = labels.get(row_id)
    if rec is None:
        raise ParseAbort(f"row {row_id} has no human label in labels.jsonl — "
                         f"the map and the label file disagree")
    lab = (rec.get("label") or "").strip().lower()
    lab = VERDICT_ALIASES.get(lab, lab)
    if lab in ("skip", "fn"):
        raise ParseAbort(f"row {row_id} carries human label '{lab}' — kappa over this "
                         f"stratum design (tp/fp/unclear) is undefined for it")
    if lab not in VALID_VERDICTS:
        raise ParseAbort(f"row {row_id} carries unknown human label '{lab}'")
    return lab


# ---------------------------------------------------------------- statistics

def kappa_from_counts(counts, cats):
    """counts[(human, llm)] -> (po, pe, kappa, matrix) over `cats`."""
    n = sum(counts.values())
    if n == 0:
        return 0.0, 0.0, None, {}
    matrix = {(h, l): counts.get((h, l), 0) for h in cats for l in cats}
    po = sum(matrix[(c, c)] for c in cats) / n
    h_marg = {h: sum(matrix[(h, l)] for l in cats) for h in cats}
    l_marg = {l: sum(matrix[(h, l)] for h in cats) for l in cats}
    pe = sum(h_marg[c] * l_marg[c] for c in cats) / (n * n)
    kappa = None if math.isclose(1.0 - pe, 0.0) else (po - pe) / (1.0 - pe)
    return po, pe, kappa, matrix


def binarize(pairs):
    """tp vs not-tp."""
    return Counter(("tp" if h == "tp" else "not-tp", "tp" if l == "tp" else "not-tp")
                   for h, l in pairs)


# ---------------------------------------------------------------- report assembly

def _fmt_kappa(k):
    return "undefined (degenerate marginals)" if k is None else f"{k:+.3f}"


def build_report(pairs, poi_flags, strata, qmap, meta_lines):
    """pairs: list of (qid, row_id, human, llm). Returns the full markdown report string."""
    lines = []
    lines.append("# Mode B inter-rater reliability — Cohen's kappa (phase 2)")
    lines.append("")
    lines.extend(meta_lines)
    lines.append("")

    # --- 3-class over all 30
    c3 = Counter((h, l) for _, _, h, l in pairs)
    po3, pe3, k3, m3 = kappa_from_counts(c3, CATS_3)
    lines.append("## All 30 items — 3-class (tp / fp / unclear)")
    lines.append("")
    lines.append(f"- observed agreement (po): **{po3:.4f}** ({po3*100:.1f}%)")
    lines.append(f"- expected agreement by chance (pe): **{pe3:.4f}** ({pe3*100:.1f}%)")
    lines.append(f"- Cohen's kappa: **{_fmt_kappa(k3)}**")
    lines.append("")
    lines.append("| human \\ llm | tp | fp | unclear | total |")
    lines.append("|---|---|---|---|---|")
    for h in CATS_3:
        row = [m3[(h, l)] for l in CATS_3]
        lines.append(f"| **{h}** | " + " | ".join(str(x) for x in row) +
                     f" | {sum(row)} |")
    coltot = [sum(m3[(h, l)] for h in CATS_3) for l in CATS_3]
    lines.append("| **total** | " + " | ".join(str(x) for x in coltot) +
                 f" | {sum(coltot)} |")
    lines.append("")

    # --- 2-class over all 30
    c2 = binarize([(h, l) for _, _, h, l in pairs])
    po2, pe2, k2, m2 = kappa_from_counts(c2, ("tp", "not-tp"))
    lines.append("## All 30 items — 2-class (tp / not-tp)")
    lines.append("")
    lines.append(f"- observed agreement: **{po2:.4f}** ({po2*100:.1f}%) · expected: "
                 f"**{pe2:.4f}** · kappa: **{_fmt_kappa(k2)}**")
    lines.append("")
    lines.append("| human \\ llm | tp | not-tp | total |")
    lines.append("|---|---|---|---|")
    for h in ("tp", "not-tp"):
        row = [m2[(h, l)] for l in ("tp", "not-tp")]
        lines.append(f"| **{h}** | " + " | ".join(str(x) for x in row) + f" | {sum(row)} |")
    lines.append("")

    # --- POI-only variant (items that actually carry >=1 poison flag)
    poi_pairs = [(q, rid, h, l) for q, rid, h, l in pairs if poi_flags.get(rid)]
    lines.append(f"## POI-flag-carrying items only (n = {len(poi_pairs)} of {len(pairs)})")
    lines.append("")
    if poi_pairs:
        cp3 = Counter((h, l) for _, _, h, l in poi_pairs)
        p_po3, p_pe3, p_k3, _ = kappa_from_counts(cp3, CATS_3)
        cp2 = binarize([(h, l) for _, _, h, l in poi_pairs])
        p_po2, p_pe2, p_k2, _ = kappa_from_counts(cp2, ("tp", "not-tp"))
        lines.append(f"- 3-class: po **{p_po3:.4f}** · pe **{p_pe3:.4f}** · "
                     f"kappa **{_fmt_kappa(p_k3)}**")
        lines.append(f"- 2-class (tp / not-tp): po **{p_po2:.4f}** · pe **{p_pe2:.4f}** · "
                     f"kappa **{_fmt_kappa(p_k2)}**")
        poi_zeros = len(pairs) - len(poi_pairs)
        lines.append(f"- excluded: {poi_zeros} item(s) with zero poison flags "
                     f"(capability/addressing-only or zero-flag controls)")
    else:
        lines.append("- no POI-flag-carrying items in this sample — variant undefined")
    lines.append("")

    # --- per-stratum agreement
    lines.append("## Per-stratum agreement")
    lines.append("")
    lines.append("| stratum | n | agree | agreement |")
    lines.append("|---|---|---|---|")
    for name, qids in strata.items():
        sub = [(q, rid, h, l) for q, rid, h, l in pairs if q in qids]
        agr = sum(1 for _, _, h, l in sub if h == l)
        pct = f"{100*agr/len(sub):.1f}%" if sub else "n/a"
        lines.append(f"| {name} | {len(sub)} | {agr} | {pct} |")
    lines.append("")

    # --- disagreements, resolved to row_ids
    dis = [(q, rid, h, l) for q, rid, h, l in pairs if h != l]
    lines.append(f"## Disagreements ({len(dis)})")
    lines.append("")
    if dis:
        lines.append("| item | row_id | human | llm rater |")
        lines.append("|---|---|---|---|")
        for q, rid, h, l in dis:
            lines.append(f"| {q} | {rid} | {h} | {l} |")
    else:
        lines.append("None — perfect agreement on this packet.")
    lines.append("")

    # --- interpretation note (fixed, rule-bound; never a verdict)
    lines.append("*Interpretation convention (Landis & Koch): <0 poor · 0.01–0.20 slight · "
                 "0.21–0.40 fair · 0.41–0.60 moderate · 0.61–0.80 substantial · 0.81–1.00 "
                 "almost perfect. The blind rater's opinions never modify "
                 "`data/labels.jsonl` (Mode B hard rule).*")
    lines.append("")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- main paths

def run(llm_path, map_path=MAP, labels_path=LABELS, sample_path=SAMPLE,
        out_path=REPORT):
    """Full real-data run. Returns exit code (0 ok, 2 awaiting, raises ParseAbort on bad input)."""
    if not Path(llm_path).exists():
        print("awaiting rater output")
        print(f"  (expected {llm_path}; nothing written)")
        return 2
    qmap, mapmeta = load_map(map_path)
    expected = set(qmap)
    if len(qmap) != EXPECTED_N:
        raise ParseAbort(f"map has {len(qmap)} items, expected {EXPECTED_N}")
    items, warnings, _ = parse_llm_file(llm_path)
    verdicts = validate_items(items, expected)

    labels = load_human_labels(labels_path)
    poi_flags = load_poi_sets(sample_path)

    pairs = []
    for q in sorted(qmap):
        rid = qmap[q]
        pairs.append((q, rid, human_label_of(labels, rid), verdicts[q]))

    strata = {"tp stratum (all 5)": set(), "fp stratum (25)": set()}
    tp_ids = {str(x) for x in mapmeta.get("strata", {}).get("tp_all", [])}
    for q, rid, _, _ in pairs:
        strata["tp stratum (all 5)" if rid in tp_ids else "fp stratum (25)"].add(q)

    sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()[:16]
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    meta = [
        f"> Generated {stamp} by `pilot/kappa_report.py` (stdlib only). Mode B hard rule: "
        "the blind rater never modifies `data/labels.jsonl`.",
        f"> Inputs: `{Path(map_path).name}` (sha256 {sha(map_path)}…), "
        f"`{Path(labels_path).name}` (sha256 {sha(labels_path)}…), "
        f"`{Path(llm_path).name}` (sha256 {sha(llm_path)}…), seed "
        f"{mapmeta.get('seed')} · base_commit {mapmeta.get('base_commit')}.",
    ]
    if warnings:
        meta.append(f"> Parser warnings: " + " · ".join(warnings))
    report = build_report(pairs, poi_flags, strata, qmap, meta)
    Path(out_path).write_text(report, encoding="utf-8")
    print(f"kappa report written to {out_path}")
    c3 = Counter((h, l) for _, _, h, l in pairs)
    po3, pe3, k3, _ = kappa_from_counts(c3, CATS_3)
    print(f"n=30 · po={po3:.4f} pe={pe3:.4f} kappa(3-class)={_fmt_kappa(k3)}")
    c2 = binarize([(h, l) for _, _, h, l in pairs])
    po2, pe2, k2, _ = kappa_from_counts(c2, ("tp", "not-tp"))
    print(f"        po={po2:.4f} pe={pe2:.4f} kappa(2-class)={_fmt_kappa(k2)}")
    return 0


# ---------------------------------------------------------------- selftest

def _selftest():
    """Synthetic-data checks. Touches NO real data file; tmp files live in /tmp."""
    import tempfile, os

    # -- statistics: perfect agreement -> kappa == 1
    pairs = ([("tp", "tp")] * 5 + [("fp", "fp")] * 25)
    c3 = Counter(pairs)
    po, pe, k, _ = kappa_from_counts(c3, CATS_3)
    assert abs(po - 1) < 1e-12 and abs(pe - (5*5 + 25*25)/900) < 1e-12, (po, pe)
    assert k is not None and abs(k - 1.0) < 1e-9, k
    c2 = binarize(pairs)
    po2, pe2, k2, _ = kappa_from_counts(c2, ("tp", "not-tp"))
    assert abs(k2 - 1.0) < 1e-9 and abs(po2 - 1.0) < 1e-12

    # -- statistics: constructed near-chance agreement -> kappa ~ 0
    #    human: rows 1-5 tp, 6-30 fp; llm: tp on rows 5,6,7,8,9 only
    hum = ["tp"]*5 + ["fp"]*25
    llm = ["fp"]*4 + ["tp"]*1 + ["tp"]*4 + ["fp"]*21
    pairs_c = list(zip(hum, llm))
    c3c = Counter(pairs_c)
    po, pe, k, _ = kappa_from_counts(c3c, CATS_3)
    # diag = 1 (row5 tp/tp) + 21 (fp/fp) = 22/30
    assert abs(po - 22/30) < 1e-12, po
    assert abs(k) < 0.05, k                      # chance-level sanity

    # -- degenerate marginals: single category everywhere -> kappa undefined, not a crash
    _, _, kd, _ = kappa_from_counts(Counter({("fp", "fp"): 30}), CATS_3)
    assert kd is None

    # -- parser: formatting drift accepted
    drift = [
        'Q01 | VERDICT: tp | reason here',
        'q02 **verdict:** FP — something',
        '{"qid": "Q03", "verdict": "unclear"}',
        '{"Q": 4, "label": "tp"}',
        'Q05:fp',
        'Q06|VERDICT:  unclear | spaced',
        'Q07 | fp',
        'Q08: unclear.',
        'Some prose mentioning Q09 without a verdict stays inert.',
    ]
    got = {}
    for ln in drift:
        p = parse_llm_line(ln)
        if p:
            got[p[0]] = p[1]
    assert got == {"Q01": "tp", "Q02": "fp", "Q03": "unclear", "Q04": "tp",
                   "Q05": "fp", "Q06": "unclear", "Q07": "fp", "Q08": "unclear"}, got

    # -- parser: loud failures (per-line)
    for bad in ('Q00 | VERDICT: tp', 'Q01 | VERDICT: banana', '{"qid": "Q01"}',
                'Q01 | but no verdict given', 'Q02 VERDICT: maybe'):
        try:
            parse_llm_line(bad)
            raise AssertionError(f"expected ParseAbort for {bad!r}")
        except ParseAbort:
            pass

    # -- end-to-end: absent llm file -> exit 2, nothing written
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "should_not_exist.md")
        code = run(llm_path=os.path.join(td, "labels_llm.jsonl"),
                   map_path=MAP, labels_path=LABELS,
                   sample_path=SAMPLE, out_path=out)
        assert code == 2, code
        assert not os.path.exists(out), "absent-input guard wrote a file!"

    # -- end-to-end: happy path on tmp files (synthetic 30, real-format map)
    with tempfile.TemporaryDirectory() as td:
        qmap = {f"Q{i:02d}": 100 + i for i in range(1, 31)}
        mapjson = {"seed": 1, "base_commit": "selftest", "strata": {"tp_all": [101, 102]},
                   "map": qmap}
        mp, lp, llp, op = (os.path.join(td, n) for n in
                           ("m.json", "lab.jsonl", "llm.jsonl", "rep.md"))
        open(mp, "w").write(json.dumps(mapjson))
        with open(lp, "w") as f:
            for i in range(1, 31):
                lab = "tp" if 101 <= 100 + i <= 102 else "fp"
                f.write(json.dumps({"row_id": str(100 + i), "label": lab, "note": ""}) + "\n")
        with open(llp, "w") as f:
            for i in range(1, 31):
                v = "tp" if 101 <= 100 + i <= 102 else "fp"
                f.write(f"Q{i:02d} | VERDICT: {v} | synthetic\n")
        code = run(llm_path=llp, map_path=mp, labels_path=lp,
                   sample_path=SAMPLE, out_path=op)
        assert code == 0, code
        txt = open(op, encoding="utf-8").read()
        assert "kappa" in txt and "| **total** |" in txt
        # duplicate-conflict abort (file level)
        with open(llp, "a") as f:
            f.write("Q01 | VERDICT: fp | contradiction\n")
        try:
            run(llm_path=llp, map_path=mp, labels_path=lp,
                sample_path=SAMPLE, out_path=op)
            raise AssertionError("expected ParseAbort for conflicting duplicate")
        except ParseAbort:
            pass
        # unmatched item abort (file level): rewrite file, add an out-of-packet id
        with open(llp, "w") as f:
            for i in range(1, 31):
                f.write(f"Q{i:02d} | VERDICT: fp | x\n")
            f.write("Q31 | VERDICT: tp | outside the packet\n")
        try:
            run(llm_path=llp, map_path=mp, labels_path=lp,
                sample_path=SAMPLE, out_path=op)
            raise AssertionError("expected ParseAbort for unmatched Q-id")
        except ParseAbort as e:
            assert "outside the packet" in str(e), e
        # missing-item abort (file level): drop one line
        with open(llp, "w") as f:
            for i in range(1, 30):
                f.write(f"Q{i:02d} | VERDICT: fp | x\n")
        try:
            run(llm_path=llp, map_path=mp, labels_path=lp,
                sample_path=SAMPLE, out_path=op)
            raise AssertionError("expected ParseAbort for missing item")
        except ParseAbort as e:
            assert "missing rater verdicts" in str(e), e

    print("selftest OK: kappa=1 at perfect agreement, kappa~0 at chance level, "
          "degenerate-safe, parser drift-tolerant, loud aborts, exit-2 guard writes nothing")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Mode B phase 2: Cohen's kappa report "
                                             "(blind LLM rater vs human labels).")
    ap.add_argument("--selftest", action="store_true",
                    help="synthetic-data checks; real data files untouched")
    ap.add_argument("--llm", default=str(LLM),
                    help="rater verdict file (JSONL records or raw BATCH MODE lines)")
    ap.add_argument("--map", default=str(MAP), help="LOCAL-ONLY Q->row_id map")
    ap.add_argument("--labels", default=str(LABELS), help="human labels (last-wins)")
    ap.add_argument("--out", default=str(REPORT), help="report destination (markdown)")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(_selftest())
    try:
        sys.exit(run(args.llm, args.map, args.labels, SAMPLE, args.out))
    except ParseAbort as e:
        print(f"ABORT: {e}", file=sys.stderr)
        print("nothing written", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
