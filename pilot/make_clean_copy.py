#!/usr/bin/env python3
"""Build paper/main_clean.md — the external-review copy of paper/main.md.

Citation-style pass ONLY. No number, claim, or citation changes. The clean copy
removes repo-local path references from the body prose (they become plain
English), keeping paths, script names, and commands ONLY inside Appendix A (the
artifact index + reproduction chain), which is the single place a reviewer looks
to map a claim back to a file.

Usage:  python3 pilot/make_clean_copy.py [--check]
"""
import argparse
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "paper", "main.md")
DST = os.path.join(REPO, "paper", "main_clean.md")

# Appendix A starts here in the source; everything from this marker down is
# reproduced verbatim (paths + commands intentionally preserved there).
APPENDIX_MARKER = "## Appendix A"

HEADER = """*Preprint v1 (for endorsement review) — 2026-09-29 — Sajjad Rahim Nouri, Islamic Azad
University, Ramsar Branch — License: CC BY 4.0.*

*Every number in this paper traces to a released artifact; the mapping from claim to file
is given in Appendix A, whose files are cited in the body as: §A the collection report
(§A.1 registry crawl, §A.2 GitHub enrichment, §A.3 truncation census, §A.4 duplicate-name
census, §A.5 Unicode scan, §A.6 confirmation-bypass scan); §B the findings backlog (§B.1
mechanisms, §B.2 defensive catalog, §B.3 false-positive grouping, §B.4 ecosystem-adaptation
notes); §C the detector-fix proposal; §D the pre-registered live-matrix protocol; §E the
blind second-opinion protocol; §F the consistency-check report; §G the validation report;
§H the related-work map.*
"""

# ---------------------------------------------------------------------------
# Citation-style replacements: repo-local references -> prose. Order matters
# (longer / more specific patterns first).
# ---------------------------------------------------------------------------
REPLACEMENTS = [
    # --- related work ----------------------------------------------------
    ("""Table built from `docs/RELATED_WORK_MAP.md` (rows and cite-as lines maintained there;""",
     """Table built from the companion related-work map (§H) (rows and cite-as lines maintained
there;"""),

    # --- collection / enrichment ----------------------------------------
    ("""2026-09-21 in three PI-authorised runs with raw snapshots committed
(`data/collection_report.md` §2–§4).""",
     """2026-09-21 in three PI-authorised runs with raw snapshots committed
(the collection report, §A.1)."""),
    ("""tool-description rows from 4,725 repositories** (`data/github_tools.jsonl`;
`data/collection_report.md` §8).""",
     """tool-description rows from 4,725 repositories** (the released description
corpus; the collection report, §A.2)."""),

    # --- detector / sample ------------------------------------------------
    ("""**Detector (frozen v2).** `pilot/analyze.py` scans the full stored text.""",
     """**Detector (frozen v2).** The frozen detector script scans the full stored text."""),
    ("""50 uniform-random zero-flag control rows, seed 42 (`data/analysis_toollevel.csv`,
sha256 `ae1aff9f…8f77`); row order immutable — every label anchors to a `row_id`.""",
     """50 uniform-random zero-flag control rows, seed 42 (the frozen sample file, sha256 `ae1aff9f…8f77`); row order
immutable — every label anchors to a stable row identifier."""),

    # --- labeling protocol ----------------------------------------------
    ("""**Human labeling protocol.** Human-in-the-terminal via `pilot/label_sample.py` with
per-class TP rules;""",
     """**Human labeling protocol.** Human-in-the-terminal via the released labeling script with
per-class TP rules;"""),
    ("""row. Every mutation goes through supersede/audit rails (`labels.jsonl.superseded`,
`labels.audit.jsonl`); the script never picks verdicts; 150/150 rows carry a rationale
note; unclear rate 0%; zero-flag false-negative rate 0/50 (`data/validation_report.md`).""",
     """row. Every mutation goes through supersede/audit rails (a superseded-label archive
and a label-mutation audit trail); the script never picks verdicts; 150/150 rows carry a
rationale note; unclear rate 0%; zero-flag false-negative rate 0/50 (validation report, §G)."""),
    ("""43/150 sample rows sit on the cap; a full-text re-review produced **7 verdict flips**
(`data/validation_report.md`).""",
     """43/150 sample rows sit on the cap; a full-text re-review produced **7 verdict flips**
(validation report, §G)."""),
    ("""(median +468 chars) with **0/7 verdict flips** (`data/collection_report.md` §5.11) —""",
     """(median +468 chars) with **0/7 verdict flips** (the collection report, §A.3) —"""),
    ("""anomaly censuses*: **1,484/16,763** duplicate `server::tool` names (collection_report
§5.10; mechanisms counted once by hand where they collide); **0 control/format Unicode
codepoints** corpus (negative; NFKC+Cc/Cf byte-diff, `data/unicode_scan.csv`; §5.12);
**2/16,763** rows match
a confirmation-bypass trigger family, both benign-shaped (`data/collection_report.md`
§5.13; `data/p7_bypass_scan.csv`).""",
     """anomaly censuses*: **1,484/16,763** duplicate server/tool name pairs (collection
report, §A.4; mechanisms counted once by hand where they collide); **0 control/format
Unicode codepoints** corpus (negative; NFKC+Cc/Cf byte-diff, §A.5);
**2/16,763** rows match
a confirmation-bypass trigger family, both benign-shaped (collection report, §A.6)."""),

    # --- reliability design ---------------------------------------------
    ("""version-pinned; a methodological limitation, disclosed per
`prompts/06-second-opinion.md`) relabeled a 30-item seed-shuffled packet served full-text,""",
     """version-pinned; a methodological limitation, disclosed per
the blind second-opinion protocol (§E)) relabeled a 30-item seed-shuffled packet served
full-text,"""),

    # --- results ---------------------------------------------------------
    ("""instances on labeled rows, 15 supported → **flag-instance precision 5.6%**
(`data/validation_report.md`). Every heuristic class, run over this population, is""",
     """instances on labeled rows, 15 supported → **flag-instance precision 5.6%**
(validation report, §G). Every heuristic class, run over this population, is"""),
    ("""are in the row notes, `data/labels.jsonl`
(mechanisms also cataloged in `docs/FINDINGS_DISCUSSION.md` §a):""",
     """are in the row notes of the frozen label set
(mechanisms also cataloged in the findings backlog, §B.1):"""),
    ("""From the FP-reason table and the semantic grouping in `docs/FINDINGS_DISCUSSION.md` §c
(one bucket per row, first match wins; 145 FP rows):""",
     """From the FP-reason table and the semantic grouping in the findings backlog (§B.3)
(one bucket per row, first match wins; 145 FP rows):"""),
    ("""(`docs/FINDINGS_DISCUSSION.md` §b): anti-IPI data/instruction splits""",
     """(the findings backlog, §B.2): anti-IPI data/instruction splits"""),
    ("""(NFKC + Cc/Cf byte-diff; `data/unicode_scan.csv`; §5.12); **Type III confirmation
bypass — 2/16,763 rows** match a conservative nine-phrase trigger family, one the
row-47 benign onboarding funnel ("do not wait for OTP"), one dependency-ordering prose
(`data/p7_bypass_scan.csv`; §5.13).""",
     """(NFKC + Cc/Cf byte-diff; the collection report, §A.5); **Type III confirmation
bypass — 2/16,763 rows** match a conservative nine-phrase trigger family, one the
row-47 benign onboarding funnel ("do not wait for OTP"), one dependency-ordering prose
(the collection report, §A.6)."""),

    # --- section 7 -------------------------------------------------------
    ("""**Design.** Blind Mode B (`prompts/06-second-opinion.md`): 30-item packet (all 5 TP rows
+ 25 FP rows, `random.seed(20260927)`), full texts, no access to human labels or notes;
the rater is an LLM (ChatGPT web UI, consumer tier, not version-pinned — a disclosed
limitation, not a benchmark claim); rater output never touches `data/labels.jsonl`.""",
     """**Design.** Blind Mode B (the second-opinion protocol, §E): 30-item packet (all 5 TP
rows + 25 FP rows, fixed seed 20260927), full texts, no access to human labels or notes; the rater is an LLM (ChatGPT web UI, consumer tier, not version-pinned — a
disclosed limitation, not a benchmark claim); rater output never touches the frozen
label set."""),
    ("""reference in this paper is the 150/150 human-in-the-terminal verdicts (§5, `labels.jsonl`);""",
     """reference in this paper is the 150/150 human-in-the-terminal verdicts (§5, the frozen
label set);"""),
    ("""**Result of the consistency check** (`data/kappa_report.md`):""",
     """**Result of the consistency check** (the consistency-check report, §F):"""),
    ("""the source-level re-examination flipped **0/7** (`data/validation_report.md`;
`data/collection_report.md` §5.11).""",
     """the source-level re-examination flipped **0/7** (the validation report, §G;
the collection report, §A.3)."""),

    # --- section 8 -------------------------------------------------------
    ("""mocked harness (`docs/BRIEF04_PROTOCOL.md`): each trial registers the case tool — its
description embedded **verbatim** from the corpus (sha256-pinned, re-verified against
`data/github_tools.jsonl` at harness init) — alongside two benign filler tools, and asks""",
     """mocked harness (the pre-registered protocol, §D): each trial registers the case tool —
its description embedded **verbatim** from the corpus (sha256-pinned, re-verified
against the released corpus at harness init) — alongside two benign filler tools, and
asks"""),
    ("""> in …* — gemini-3.8-flash, FL rep 1 (transcript `fl_gemini-3.8-flash_1_*.jsonl`)""",
     """> in …* — gemini-3.8-flash, FL rep 1 (the matching gemini-3.8-flash rep-1 transcript)"""),
    ("""> note."* — glm-5.3, WF rep 2 (transcript `wf_glm-5.3_2_*.jsonl`)""",
     """> note."* — glm-5.3, WF rep 2 (the matching glm-5.3 rep-2 transcript)"""),
    ("""> anywhere.**"* — glm-5.3, DP rep 2 (transcript `dp_glm-5.3_2_*.jsonl`; the key, echoed""",
     """> anywhere.**"* — glm-5.3, DP rep 2 (the matching glm-5.3 rep-2 transcript;
the key, echoed"""),
    ("""All transcripts, the per-trial ledger, and the redaction rules are committed artifacts
(`data/live_tests/`); the ASR table above is regenerable via
`python3 experiments/summarize.py`.""",
     """All transcripts, the per-trial ledger, and the redaction rules are committed
artifacts (Appendix A); the ASR table above is regenerable from the ledger by the
released summarizer script."""),

    # --- sections 9 / 10 -------------------------------------------------
    ("""used for **candidate generation, never verdicts** (AGENTS.md §2.3). Its only job is""",
     """used for **candidate generation, never verdicts** (a standing rule of this
project: heuristics produce candidates, never verdicts). Its only job is"""),
    ("""**The ecosystem appears to be adapting around the channel** (`docs/FINDINGS_DISCUSSION.md`
§d): pay-per-call""",
     """**The ecosystem appears to be adapting around the channel** (the findings backlog,
§B.4): pay-per-call"""),
    ("""**Recommendations (v3-candidates; never auto-applied).** From
`docs/DETECTOR_FIX_PROPOSAL.md`, one line each:""",
     """**Recommendations (v3-candidates; never auto-applied).** From
the detector-fix proposal (§C), one line each:"""),
    ("""**Data & code availability.** All artifacts are in the companion repository
(`<repo-url placeholder>`); the dataset will be archived with a Zenodo DOI
(`DOI placeholder`) under CC BY 4.0. See Appendix A for the artifact index and
reproduction chain.""",
     """**Data & code availability.** All artifacts are released in the companion repository;
the dataset is archived with a Zenodo DOI under CC BY 4.0. See Appendix A for the
artifact index and reproduction chain."""),
    ("""code paths — and the 90-day coordinated-disclosure rule (AGENTS.md §2.2) is reserved for""",
     """code paths — and this project's 90-day coordinated-disclosure rule is reserved for"""),
]

# The word-count / provenance HTML comments are repo bookkeeping, not paper text.
COMMENT_RE = re.compile(r"^[ \t]*<!--.*?-->[ \t]*\n?", re.M | re.S)


def build(text):
    """Return the clean copy of `text` (the full main.md source)."""
    # Split off Appendix A: it keeps paths and commands verbatim.
    idx = text.index(APPENDIX_MARKER)
    head, appendix = text[:idx], text[idx:]

    # 1. Drop HTML comments everywhere (word counts, latex-mirror notes). The
    #    footer word-count comment sits after Appendix A, so strip both halves.
    head = COMMENT_RE.sub("", head)
    appendix = COMMENT_RE.sub("", appendix)

    # 2. Replace the front-matter block with the v1 endorsement header.
    title_line, _, _rest = head.partition("\n")
    assert title_line.startswith("# Calibrating the Alarms"), title_line
    m = re.search(r"\n---\n", head)
    assert m, "front-matter rule not found"
    head = title_line + "\n\n" + HEADER + "\n---\n\n" + head[m.end():]

    # 3. Apply the citation-style replacements; every one must match exactly.
    for old, new in REPLACEMENTS:
        if old not in head:
            raise SystemExit("MISS in main_clean build:\n" + old[:160])
        head = head.replace(old, new, 1)

    return head + appendix


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------
# Repo-local markers that must not appear in the sanitized body.
PATHY = re.compile(
    r"data/|docs/|pilot/|experiments/|prompts/|AGENTS\.md|CONVENTIONS\.md"
    r"|BRIEF04|\.py\b|\.jsonl\b|\.csv\b|labels\.jsonl"
)
CODE_SPAN_RE = re.compile(r"`([^`\n]+)`")
BANNED = ("PENDING", "TODO", "[SRN")


def body_of(clean):
    """Everything before Appendix A (the sanitized region)."""
    return clean[: clean.index(APPENDIX_MARKER)]


def numbers(text):
    """Data numbers, in order — the invariant that must not change.

    Section-symbol references (\S5.11, \S2.3, the Appendix A \S7 legend) are
    citation style, not data, so they are normalized away; repo-internal
    filename fragments that the sanitization removes by design are counted
    separately and reported.
    """
    t = re.sub(r"\u00a7\s*[A-Z]?\.?\d+(\.\d+)*", "\u00a7", text)   # section refs
    t = re.sub(r"(?:prompts/\d+|BRIEF\d+|BRIEF04)[-A-Za-z0-9_]*", "", t)  # prompt/protocol ids
    t = re.sub(r"(?:python|p)\d+", "", t)  # interpreter version / proposal id in filenames
    return re.findall(r"\d[\d,\.]*", t)


def _body_of_src(text):
    """main.md's paper body: no comments, no title/front-matter block."""
    t = COMMENT_RE.sub("", text)
    m = re.search(r"\n---\n", t)
    return t[m.end():] if m else t


def _body_of_clean(clean):
    """main_clean.md's paper body: no comments, no v1 header block."""
    t = COMMENT_RE.sub("", clean)
    t = t[t.index(HEADER) + len(HEADER):] if HEADER in t else t
    return t.lstrip("\n")


def word_count(t):
    t = COMMENT_RE.sub("", t)
    t = re.sub(r"```.*?```", "", t, flags=re.S)
    return len(t.split())


def check(clean, src):
    problems = []

    # (a) no repo-local paths outside Appendix A (fenced blocks hold prose/ASCII art,
    #     not citations, so they are excluded from the leak scan)
    scan = re.sub(r"```.*?```", "", body_of(clean), flags=re.S)
    # inspect each inline code span on its own (never across span boundaries)
    leaks = sorted({c for c in CODE_SPAN_RE.findall(scan) if PATHY.search(c)})
    if leaks:
        problems.append("path leaks in body: " + "; ".join(leaks))

    # (b) Appendix A still carries the artifact index and the commands
    app = clean[clean.index(APPENDIX_MARKER):]
    for needed in ("data/collection_report.md", "experiments/trial_accounting.py",
                   "python3 pilot/crawl_registry.py"):
        if needed not in app:
            problems.append(f"Appendix A lost: {needed}")

    # (c) no banned markers anywhere
    for b in BANNED:
        if b in clean:
            problems.append(f"banned marker present: {b}")

    # (d) every numeric token preserved, in order
    a, b = numbers(_body_of_src(src)), numbers(_body_of_clean(clean))
    if a != b:
        problems.append(
            f"NUMBER DRIFT: src {len(a)} numeric tokens, clean {len(b)}; "
            f"first divergence at "
            f"{next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))}"
        )

    # (e) word count within +/-2%
    # Compare the paper BODY (each file minus its own header block): the v1
    # header + artifact legend are new required material, not a body edit.
    w_src = word_count(_body_of_src(src))
    w_cln = word_count(_body_of_clean(clean))
    drift = (w_cln - w_src) / w_src * 100
    if abs(drift) > 2.0:
        problems.append(
            f"word-count drift {drift:+.2f}% (body: main.md {w_src}, main_clean.md {w_cln})")

    return problems, w_src, w_cln, drift


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="verify only; do not write main_clean.md")
    args = ap.parse_args()

    src = open(SRC, encoding="utf-8").read()
    clean = build(src)
    problems, w_src, w_cln, drift = check(clean, src)

    print(f"body word count: main.md {w_src} -> main_clean.md {w_cln} "
          f"({drift:+.2f}%, limit ±2%)")
    a, b = numbers(_body_of_src(src)), numbers(_body_of_clean(clean))
    print(f"data numbers in body: {len(a)} -> {len(b)} "
          f"(identical & in order: {a == b})")
    if problems:
        print("\nFAILED:")
        for p in problems:
            print("  - " + p)
        return 1
    print("checks passed: no body path leaks, Appendix A intact, no banned markers, "
          "numbers identical.")

    if not args.check:
        open(DST, "w", encoding="utf-8").write(clean)
        print(f"wrote {os.path.relpath(DST, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
