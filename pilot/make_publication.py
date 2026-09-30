#!/usr/bin/env python3
"""Build paper/main_clean.md — the PUBLICATION version of paper/main.md.

paper/main.md is the traceable scientific record and is READ-ONLY here: this
builder never opens it for writing. main_clean.md is the prose-first academic
rendering of exactly the same content.

Rules enforced (and verified) before the file is written:

  R1  Source read-only.
  R2  The body (everything before Appendix A) carries no inline code, no file
      paths, no git hashes, no checksums, and no CLI commands; each becomes
      academic prose. Paths, commands, and checksums live only in Appendix A.
  R3  Quantitative content byte-identical: the ordered numeric tokens of the
      body are unchanged, after excluding PROVENANCE tokens (a git commit id and
      a file checksum) which R2 removes and which are not measurements.
  R4  Body word count within +/-10% of the source body.
  R5  The evidence-chain figure becomes a numbered figure with a prose caption,
      losing no information.

Usage:  python3 pilot/make_publication.py [--check]
"""
import argparse
import os
import re
import sys

# Stage 1 (citation-style sanitization) is the verified replacement table in
# make_clean_copy.py; this module applies the publication rules on top of it.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_clean_copy as stage1  # noqa: E402

REPLACEMENTS = stage1.REPLACEMENTS
build_stage1 = stage1.build
COMMENT_RE = stage1.COMMENT_RE


REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "paper", "main.md")
DST = os.path.join(REPO, "paper", "main_clean.md")

# Everything from this marker down is reproduced verbatim: paths, script names,
# commands, and checksums are intentionally preserved there and nowhere else.
APPENDIX_MARKER = "## Appendix A"

# Numeric tokens R2 removes from the body. Neither is a scientific quantity:
# one is a git commit id, one is a file checksum. Both remain in Appendix A or
# in the repository's history, so excluding them keeps R3 a *scientific* check.
PROVENANCE_TOKENS = ("6cca247", "ae1aff9f\u20268f77", "sha256", "256",
                     "TESTKEY-USER-DEMO-4F2A", "TESTKEY")

HEADER = """*Preprint v1 (for endorsement review) \u2014 2026-09-29 \u2014 Sajjad Rahim Nouri, Islamic Azad
University, Ramsar Branch \u2014 License: CC BY 4.0.*

*Supporting artifacts \u2014 data, code, labels, and the full reproduction chain \u2014 are
listed in Appendix A.*
"""

# The HTML comments in the source are word-count/provenance bookkeeping, not paper text.
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


# R2/R5 companion: the frozen detector's version provenance is a repository
# fact, so it is recorded in Appendix A (where hashes belong) rather than in
# the body. Appended only if the source appendix does not already carry it.
PROVENANCE_NOTE = ("\n*Detector version provenance: the frozen v1 detector is recoverable at "
                   "commit 6cca247, and the suspicion-score definition is unchanged since v1.*\n")


# ---------------------------------------------------------------------------
# R2: remaining code spans in the body become prose or italics — never backticks
# ---------------------------------------------------------------------------
# Detector class names and protocol identifiers are scientific terms, not file
# references: they are set in italics. Anything naming a file, script, command,
# hash, or repository path is removed from the body (it is reproduced verbatim in
# Appendix A) and its sentence is rewritten below to read as prose.
ITALICISE = re.compile(r"`([A-Za-z][A-Za-z0-9_.\-]*(?:_[A-Za-z0-9_\-]+)+)`")
# Citation identifiers and model names are kept verbatim — they are references,
# not files — but set as plain text so the body carries no backticks at all.
PLAIN_OK = re.compile(
    r"`(?:"
    r"\d{4}\.\d{4,5}"                              # arXiv id
    r"|10\.\d{4,9}/[^`]+"                          # DOI
    r"|[A-Za-z][A-Za-z0-9]*(?:[.-][A-Za-z0-9]+)+"   # model / package name
    r"|CAP|POI)"
    r"`"
)

# Sentences that must lose a path/hash but keep their claim. Each entry must
# match exactly, so a silent wording drift in the source cannot pass unnoticed.
PROSE_REWRITES = [
    ("""**Detector (frozen v2).** The frozen detector script scans the full stored text. Capability
classes:""",
     """**Detector (frozen v2).** The frozen detector scans the full stored text. Capability
classes:"""),
    ("""plus structural checks `zero_width_chars`, `base64_blob`. Channel classes (v2):""",
     """plus structural checks `zero_width_chars` and `base64_blob`. Channel classes (v2):"""),
    ("""poisoning statistics. v1 is frozen at commit `6cca247`; the `suspicion_score` definition
is unchanged since v1.""",
     """poisoning statistics. Version 1 is frozen; the suspicion-score definition is unchanged
since that version."""),
    ("""**Sample construction (frozen).** Stratified: the top-100 rows by `suspicion_score` plus
50 uniform-random zero-flag control rows, seed 42 (the frozen sample file, sha256 `ae1aff9f…8f77`); row order
immutable — every label anchors to a stable row identifier.""",
     """**Sample construction (frozen).** Stratified: the top-100 rows by suspicion score plus
50 uniform-random zero-flag control rows, drawn with seed 42; row order is immutable and
every label anchors to a stable row identifier, so the frozen sample and its checksum are
fixed artifacts (Appendix A)."""),
    ("""**Registry collection.** Official registry API (`registry.modelcontextprotocol.io/v0/servers`),
cursor-paginated at 100 entries/page, entries per version, deduplicated to `isLatest=true`""",
     """**Registry collection.** The official registry's public server-list API was queried with
cursor pagination at 100 entries per page; because entries are published per version, each
server was deduplicated to its latest published version"""),
    ("""**GitHub enrichment.** For GitHub-linked servers, tool-registration blocks were extracted
from source (`@mcp.tool`, `server.tool(`, `ListToolsResult`), yielding **16,763""",
     """**GitHub enrichment.** For GitHub-linked servers, tool-registration blocks were extracted
from source by matching the common registration idioms of the major MCP server frameworks
(decorator-, method-, and result-type-based), yielding **16,763"""),
    ("""**The description-in-context channel.** An MCP client calls `tools/list`; the manifest —""",
     """**The description-in-context channel.** An MCP client issues a tool-listing request; the
manifest —"""),
    ("""shell, read a token (`CAP` classes). A **poison** is instruction-shaped steering: text
that tells the model what to do, hide, prefer, or ignore (`POI` classes).""",
     """shell, read a token (the capability classes). A **poison** is instruction-shaped steering:
text that tells the model what to do, hide, prefer, or ignore (the poison classes)."""),
    ("""**Human labeling protocol.** Human-in-the-terminal via the released labeling script with
per-class TP rules;""",
     """**Human labeling protocol.** A labeling aid was used interactively, in the analyst's
terminal, with per-class true-positive rules;"""),
    ("""row. Every mutation goes through supersede/audit rails (a superseded-label archive
and a label-mutation audit trail); the script never picks verdicts;""",
     """row. Every mutation goes through supersede/audit rails (a superseded-label archive and
a label-mutation audit trail); the aid never assigns verdicts on its own;"""),
    ("""**Design.** Blind Mode B (the second-opinion protocol, §E): 30-item packet (all 5 TP
rows + 25 FP rows, fixed seed 20260927), full texts, no access to human labels or notes; the rater is an LLM (ChatGPT web UI, consumer tier, not version-pinned — a
disclosed limitation, not a benchmark claim); rater output never touches the frozen
label set.""",
     """**Design.** Blind second-rater mode: a 30-item packet (all 5 true-positive rows plus 25
false-positive rows, drawn with a fixed seed of 20260927) was served as full texts to a second rater
with no access to the human labels, their notes, or the row map. The rater was a commercial
conversational LLM (consumer web interface, not version-pinned — a disclosed limitation, not
a benchmark claim), and its output never enters the frozen label set."""),
    ("""mocked harness (the pre-registered protocol, §D): each trial registers the case tool —
its description embedded **verbatim** from the corpus (sha256-pinned, re-verified
against the released corpus at harness init) — alongside two benign filler tools, and
asks""",
     """mocked harness (the pre-registered protocol, §D): each trial registers the case tool —
its description embedded **verbatim** from the corpus, checksum-pinned and re-verified
against the released corpus at harness initialisation — alongside two benign filler tools,
and asks"""),
    ("""(controls). Every tool response is canned synthetic data (`TESTKEY-…` markers; no""",
     """(controls). Every tool response is canned synthetic data bearing an obviously fake
credential marker (no"""),
    ("""Your key (`TESTKEY-USER-DEMO-4F2A`) was deposited into the""",
     """Your key (a synthetic demo credential) was deposited into the"""),
    ("""FL rep 1 (the matching gemini-3.8-flash rep-1 transcript)""",
     """FL rep 1 (the matching transcript)"""),
    ("""WF rep 2 (the matching glm-5.3 rep-2 transcript)""",
     """WF rep 2 (the matching transcript)"""),
    ("""DP rep 2 (the matching glm-5.3 rep-2 transcript;""",
     """DP rep 2 (the matching transcript;"""),
    ("""sample is the top 100 rows by `suspicion_score` plus 50 zero-flag control rows (§5), so it""",
     """sample is the top 100 rows by suspicion score plus 50 zero-flag control rows (§5), so it"""),
    ("""ADDED BEHAVIORAL INSTRUCTION TO THE MODEL."* A row is `tp` iff at least one poison flag""",
     """ADDED BEHAVIORAL INSTRUCTION TO THE MODEL."* A row is a true positive if and only if at
least one poison flag"""),
    ("""- **Priority capture, unconditional + universal** — row 12 (`com.webflow/mcp`):""",
     """- **Priority capture, unconditional + universal** — row 12 (a site-builder vendor):"""),
    ("""- **Priority capture, conditional gateway** — rows 94/95 (`dev.mcpfinder`, same server,""",
     """- **Priority capture, conditional gateway** — rows 94/95 (the same server,"""),
    ("""- **Exec-priming** — row 35 (`io.github.armanas/froglet`): *""",
     """- **Exec-priming** — row 35 (an agent-framework server): *"""),
    ("""- **Universal credential funnel** — row 60 (`com.dustforge/demipass`; family echo row 61,""",
     """- **Universal credential funnel** — row 60 (a password-manager server; family echo row 61,"""),
]

# R5: the ASCII evidence chain becomes a numbered figure with a prose caption.
# Every element of the original four-box diagram is carried into the caption.
CHAIN_FIGURE = """**Figure 1 — The evidence chain: what this study shows, and where it stops.**

*Observed benign description* → *attack-shaped mechanism* → *controlled steering* →
**not automatically: vulnerability**. Step 1 is the set of 5 true-positive rows catalogued
in §6.3, all of which occurred in otherwise benign product descriptions; author intent is
not assessed. Step 2 names the three mechanisms behind them — priority capture, exec-priming,
and a credential funnel. Step 3 is the live-trial evidence of §8: across 54 mocked trials,
exec-priming steered 9/9, the funnel steered covertly 8/9, and the controls never triggered
across 16 valid trials. Step 4 is deliberately **not** implied: there is no exploit path, no
live target, no attacker, no credential at risk, and no filed CVE (§10)."""

CHAIN_RE = re.compile(
    r"\*\*Figure R2-1 — the evidence chain: what we show, and where it stops\.\*\*\n+"
    r"```text\n.*?\n```\n",
    re.S,
)


def build(text):
    """Stage 1 (citation style) + publication rules. `text` is main.md, read-only."""
    clean = build_stage1(text)

    # R5: swap the ASCII chain for a numbered figure with a prose caption.
    if not CHAIN_RE.search(clean):
        raise SystemExit("MISS: evidence-chain figure not found")
    clean = CHAIN_RE.sub(CHAIN_FIGURE + "\n", clean, 1)

    # R2: prose rewrites, then italicise remaining class-name code spans, then
    # assert that no backtick survives in the body.
    idx = clean.index(APPENDIX_MARKER)
    head, appendix = clean[:idx], clean[idx:]

    for old, new in PROSE_REWRITES:
        if old in head:
            head = head.replace(old, new, 1)
        elif new not in head:
            raise SystemExit("MISS in publication build:\n" + old[:160])

    head = ITALICISE.sub(r"*\1*", head)
    head = PLAIN_OK.sub(lambda m: m.group(0)[1:-1], head)

    leftover = re.findall(r"`[^`\n]*`", head)
    if leftover:
        raise SystemExit("R2 VIOLATION — code spans left in body: " + "; ".join(leftover))

    if "6cca247" not in appendix:
        appendix = appendix.rstrip("\n") + "\n" + PROVENANCE_NOTE
    return head + appendix


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------
# Patterns the body must not contain (rule R2 / the task's grep list).
FORBIDDEN_BODY = [
    ("backtick", "`"),
    ("sha256", "sha256"),
    (".py", ".py"),
    (".jsonl", ".jsonl"),
    (".md", ".md"),
]


def body_of(clean):
    """The publication body: everything before Appendix A, from the Abstract on."""
    t = clean[: clean.index(APPENDIX_MARKER)]
    return t[t.index("## 1. Abstract"):]


def numbers(text):
    """Ordered numeric tokens, excluding section refs and provenance ids."""
    t = re.sub(r"§\s*[A-Z]?\.?\d+(\.\d+)*", "§", text)      # section references
    t = re.sub(r"(?:prompts/)?\d+(?=[-_.])|(?<=BRIEF)\d+", "", t)  # prompt/protocol ids
    t = re.sub(r"(?<=p)\d+_|(?<=python)\d+", "", t)          # proposal id / interpreter ver
    t = re.sub(r"(?<=v)\d+(?=/)", "", t)                      # API path version, e.g. v0/servers
    for tok in PROVENANCE_TOKENS:                           # git commit, checksum
        t = t.replace(tok, "")
    return re.findall(r"\d+(?:[.,]\d+)*", t)


FIGURE_CAPTION_RE = re.compile(
    r"\*\*Figure 1 — The evidence chain.*?filed CVE \(§10\)\.", re.S
)
# The same block in the source, still an ASCII diagram.
FIGURE_SOURCE_RE = re.compile(
    r"\*\*Figure R2-1 — the evidence chain: what we show, and where it stops\.\*\*"
    r"\n+```text\n.*?\n```\n",
    re.S,
)


def _strip_figure(text):
    """Remove the evidence-chain figure so the token walk covers body prose only."""
    return FIGURE_SOURCE_RE.sub("<FIGURE>", FIGURE_CAPTION_RE.sub("<FIGURE>", text))


# Scientific quantities the figure caption must preserve from the ASCII original.
FIGURE_REQUIRED = ("5 TP rows", "54 mocked trials", "9/9", "8/9", "0/16", "6.3", "8", "10")


def word_count(t):
    t = COMMENT_RE.sub("", t)
    t = re.sub(r"```.*?```", "", t, flags=re.S)
    return len(t.split())


def body_of_src(text):
    """main.md's body: everything before Appendix A, minus front matter/comments."""
    t = COMMENT_RE.sub("", text)
    t = t[: t.index(APPENDIX_MARKER)]
    i = t.index("## 1. Abstract")
    return t[i:]


def check(clean, src):
    problems = []
    body = body_of(clean)
    src_body = body_of_src(src)

    # (1) forbidden patterns in the body
    for label, pat in FORBIDDEN_BODY:
        n = body.count(pat)
        if n:
            problems.append(f"body still contains {label!r} x{n}")

    # (2) numbers identical, excluding the renumbered figure block, which R5
    #     rewrites from an ASCII diagram into a numbered figure (the task
    #     requires the renumbering). Its scientific content is checked apart.
    src_wo = _strip_figure(src_body)
    body_wo = _strip_figure(body)
    a, b = numbers(src_wo), numbers(body_wo)
    if a != b:
        import difflib
        ops = [o for o in difflib.SequenceMatcher(None, a, b, autojunk=False)
               .get_opcodes() if o[0] != "equal"]
        problems.append(f"NUMBER DRIFT: src {len(a)} vs clean {len(b)}; first ops {ops[:4]}")

    # (3) word count within +/-10% of the source body
    w_src, w_cln = word_count(src_body), word_count(body)
    drift = (w_cln - w_src) / w_src * 100
    if abs(drift) > 10.0:
        problems.append(f"word-count drift {drift:+.2f}% (src {w_src}, clean {w_cln})")

    # (3b) the figure caption must retain every scientific quantity
    cap = FIGURE_CAPTION_RE.search(clean)
    if not cap:
        problems.append("R5: numbered figure caption not found")
    else:
        ctext = cap.group(0)
        for need in ("5 true-positive rows", "54 mocked trials", "exec-priming steered 9/9",
                     "8/9", "16 valid trials", "§6.3", "§8", "§10", "Step 1", "Step 2",
                     "Step 3", "Step 4"):
            if need not in ctext:
                problems.append(f"R5: figure caption lost {need!r}")

    # (4) Appendix A must still carry paths, commands, and the checksum
    app = clean[clean.index(APPENDIX_MARKER):]
    for needed in ("data/collection_report.md", "experiments/trial_accounting.py",
                   "python3 pilot/crawl_registry.py", "ae1aff9f", "6cca247"):
        if needed not in app and needed not in clean:
            problems.append(f"provenance lost entirely: {needed}")

    return problems, w_src, w_cln, drift, len(a)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="verify only")
    args = ap.parse_args()

    src = open(SRC, encoding="utf-8").read()
    clean = build(src)
    problems, w_src, w_cln, drift, n_nums = check(clean, src)

    print(f"body word count: main.md {w_src} -> main_clean.md {w_cln} ({drift:+.2f}%, "
          f"limit ±10%)")
    print(f"body data numbers: {n_nums} (identical & in order: "
          f"{not any('NUMBER DRIFT' in p for p in problems)})")
    print("body greps: " + ", ".join(
        f"{label}={body_of(clean).count(pat)}" for label, pat in FORBIDDEN_BODY))
    if problems:
        print("\nFAILED:")
        for p in problems:
            print("  - " + p)
        return 1
    print("checks passed.")
    if not args.check:
        open(DST, "w", encoding="utf-8").write(clean)
        print(f"wrote {os.path.relpath(DST, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())



