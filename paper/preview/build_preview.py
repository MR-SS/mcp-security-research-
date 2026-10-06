#!/usr/bin/env python3
"""Rebuild paper/preview/paper.html from paper/main_clean.md (content frozen).

One pandoc pass (markdown -> html5, standalone, --embed-resources) with the
committed stylesheet and title header, then a presentation-only pass:

  1. document <title> metadata + title-block relocation + duplicate-H1 removal
  2. the three reviewer PNGs embedded as base64 <img>, each anchored next to the
     text that refers to it (Figure 1's frozen caption in §5 is NOT restated --
     that would duplicate the caption)
  3. a numbered References section (USENIX style) built from citation metadata
     that is already verified in docs/RELATED_WORK_MAP.md -- no new lookups
  4. first-use citation wiring: [N] superscript anchors in prose only, and only
     where the anchor string is unique in prose

Do NOT re-encode the result with a second pandoc pass: that silently drops the
embedded stylesheet and header. Every step fails loud.
"""
import base64
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PREVIEW = os.path.join(REPO, "paper", "preview")
MD = os.path.join(REPO, "paper", "main_clean.md")
OUT = os.path.join(PREVIEW, "paper.html")
TITLE = ("Calibrating the Alarms: A Registry-Grounded, Human-Validated "
         "Measurement of Poisoning Detectors on 16,763 MCP Tool Descriptions")

# --- Figure 1: the paper's own frozen caption is the text paragraph in §5, so
# --- this figure carries a source line only (no restated caption).
FIG_FUNNEL = {
    "id": "fig-1",
    # end of the frozen "Figure 1 - Denominator funnel ..." paragraph in §5
    "anchor": "(the collection\nreport, §A.1, §A.2).</p>",
    "png": "fig-1-funnel.png",
    "alt": "Denominator funnel from 60,000 registry version-entries to 5 poison-positive rows",
    "caption": ('<span class="src">Source: data/collection_report.md §2–§4 and §A.1–§A.2; '
                'data/candidate_rate_scan.csv; data/validation_family_split.csv '
                '(assert-verified).</span>'),
    "before": False,
}

FIGURES = [
    FIG_FUNNEL,
    {
        "id": "fig-2",
        # end of §6.2 (the per-class section ends where §6.3 begins)
        "anchor": '<h3 id="the-five-tp-rows-and-four-mechanisms">',
        "png": "fig-2-perclass.png",
        "alt": "Sorted per-class text-support rates with family reference lines",
        "caption": ('Reviewer figure R1 (not a numbered paper figure). Colors: capability '
                    'orange, poison blue, channel green. Dashed vertical line: poison family '
                    '6/124 = 4.8%; dotted: all-family 15/268 = 5.6%. Whiskers mark each '
                    'class\'s n. <span class="src">Source: data/validation_report.md '
                    '(§6.2 per-class table) (assert-verified).</span>'),
        "before": True,
    },
    {
        "id": "fig-3",
        "anchor": "<p>Pooled attack ASR",
        "png": "fig-3-trials.png",
        "alt": "Mocked-harness per-cell success over total, with pooled compatibility intervals",
        "caption": ('Reviewer figure R2 (not a numbered paper figure). Per-cell success/total; '
                    'lower panel gives 95% compatibility intervals for the pooled arms — '
                    'FL [0.70, 1.00], DP [0.57, 0.98], WF [0.35, 0.88], CTRL [0.00, 0.19]. '
                    'Fully mocked harness, synthetic data only. <span class="src">Source: '
                    'data/live_tests/trials_ledger.jsonl (assert-verified).</span>'),
        "before": True,
    },
]

# ---------------------------------------------------------------------------
# References: every field below is already verified in
# docs/RELATED_WORK_MAP.md §2 ("Cite-as lines"); nothing is looked up here.
# Where the map records no author/title metadata (MCPTox, MSB, Breaking the
# Protocol) its own cite-as short name fills the slot rather than inventing one.
# ---------------------------------------------------------------------------
def _e(authors, title, venue, year, url):
    return (f'{authors}, &ldquo;{title},&rdquo; <span class="ref-venue">{venue}</span> '
            f'{year}. <a href="{url}">{url}</a>')

REFS = [
    (_e("AgentsID Security Research", "Weaponized-by-Design",
        "industry census (vendor research, non-peer-reviewed)", "April 2026",
        "https://agentsid.dev/research"), ["Weaponized-by-Design"]),
    (_e("Hasan et al.", "MCP at First Glance", "arXiv preprint",
        "arXiv:2506.13538 [cs.SE], 2025 (v5 2026-04)", "https://arxiv.org/abs/2506.13538"),
     ["2506.13538", "Hasan"]),
    (_e("MCPTox", "MCPTox", "arXiv preprint",
        "arXiv:2508.14925 [cs.CR], August 2025", "https://arxiv.org/abs/2508.14925"),
     ["MCPTox"]),
    (_e("MSB", "MSB", "arXiv preprint; ICLR 2026",
        "arXiv:2510.15994 [cs.CR], October 2025", "https://arxiv.org/abs/2510.15994"),
     ["MSB"]),
    (_e("Breaking the Protocol", "Breaking the Protocol", "arXiv preprint",
        "arXiv:2601.17549 [cs.CR], January 2026", "https://arxiv.org/abs/2601.17549"),
     ["Breaking the Protocol"]),
    (_e("Hou et al.", "MCP Landscape", "arXiv preprint",
        "arXiv:2503.23278 [cs.CR], March 2025", "https://arxiv.org/abs/2503.23278"),
     ["Hou et al."]),
    (_e("Radosevich &amp; Halloran", "MCP Safety Audit", "arXiv preprint",
        "arXiv:2504.03767, April 2025", "https://arxiv.org/abs/2504.03767"),
     ["MCP Safety Audit"]),
    (_e("Errico", "Securing MCP", "arXiv preprint",
        "arXiv:2511.20920 [cs.CR], November 2025", "https://arxiv.org/abs/2511.20920"),
     ["Errico"]),
    (_e("Chen et al.",
        "Rethinking MCP Security: A Large-Scale Study of Runtime MCP Servers and "
        "Security Scanner Reliability (MCPZoo)", "arXiv preprint",
        "arXiv:2607.11086 [cs.CR], 13 July 2026", "https://arxiv.org/abs/2607.11086"),
     ["arXiv 2607.11086"]),
    (_e("Liu et al.",
        "When the Manual Lies: A Realistic Benchmark to Evaluate MCP Poisoning Attacks "
        "for LLM Agents (MCP-TDP)", "arXiv preprint",
        "arXiv:2605.24069 [cs.CR; cs.AI], 22 May 2026", "https://arxiv.org/abs/2605.24069"),
     ["When the Manual Lies"]),
    (_e("Stein", "How are AI agents used? Evidence from 177,000 MCP tools",
        "arXiv preprint", "arXiv:2603.23802 [cs.CY], 25 March 2026",
        "https://arxiv.org/abs/2603.23802"), ["Stein"]),
    (_e("Song et al.",
        "Beyond the Protocol: Unveiling Attack Vectors in the Model Context Protocol "
        "(MCP) Ecosystem", "IEEE Trans. Softw. Eng.", "52(8):2410–2426, 2026",
        "https://doi.org/10.1109/TSE.2026.3694876"), ["Song et al."]),
]

TABLE_RE = re.compile(r"<table\b.*?</table>", re.S)
REFS_RE = re.compile(r'<ol class="references">.*?</ol>', re.S)
APPENDIX_RE = re.compile(r'<h2 id="appendix-a-data-code-availability">')


def fail(msg):
    print("BUILD FAIL: " + msg, file=sys.stderr)
    sys.exit(1)


def references_html():
    items = "\n".join(f'  <li id="ref-{i}">{html}</li>' for i, (html, _) in enumerate(REFS, 1))
    return ('<h2 id="references">References</h2>\n'
            '<ol class="references">\n' + items + "\n</ol>\n")


def wire_citations(html):
    """Add [N] superscript anchors at first use in prose. Prose only, unique only."""
    blanked = TABLE_RE.sub(lambda m: "\x00" * len(m.group(0)), html)
    blanked = REFS_RE.sub(lambda m: "\x00" * len(m.group(0)), blanked)
    edits, used = [], []
    for n, (_, anchors) in enumerate(REFS, 1):
        for a in anchors:
            pat = re.compile(r"(?<![A-Za-z0-9])" + re.escape(a) + r"(?![A-Za-z0-9])")
            hits = list(pat.finditer(blanked))
            if len(hits) == 1:
                edits.append((hits[0].end(), n))
                used.append((n, a))
                break
    for pos, n in sorted(edits, reverse=True):
        html = (html[:pos] + f'<sup class="cite"><a href="#ref-{n}">[{n}]</a></sup>'
                + html[pos:])
    return html, used


def main():
    tmp = os.path.join(PREVIEW, ".paper-build-tmp.html")
    cmd = ["pandoc", MD, "-f", "markdown", "-t", "html5", "--standalone",
           "--embed-resources",
           "--css", os.path.join("paper", "preview", "paper-style.css"),
           "-H", os.path.join("paper", "preview", "title-header.html"),
           "-o", tmp]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    if r.returncode != 0:
        fail("pandoc: " + (r.stderr or "").strip())
    html = open(tmp, encoding="utf-8").read()
    os.unlink(tmp)

    # 1. document title metadata (pandoc falls back to the file stem).
    if "<title>main_clean</title>" not in html:
        fail("expected <title>main_clean</title> placeholder not found")
    html = html.replace("<title>main_clean</title>", "<title>" + TITLE + "</title>")

    # 2. -H parks the title block in <head> (invalid); move it to top of body.
    m = re.search(r'<div class="title-block">.*?</div>\s*(?=</head>)', html, re.S)
    if not m:
        fail("title-block div not found in head")
    block = m.group(0).rstrip()
    html = html[:m.start()] + html[m.end():]
    if html.count("<body>") != 1:
        fail("expected exactly one <body>")
    html = html.replace("<body>", "<body>\n" + block, 1)

    # 3. the title block supersedes the document's own H1 (same text).
    m = re.search(r'<h1 id="calibrating-the-alarms[^>]*>.*?</h1>\n', html, re.S)
    if not m:
        fail("document H1 not found")
    html = html[:m.start()] + html[m.end():]

    # 4. References section, inserted before Appendix A.
    if len(APPENDIX_RE.findall(html)) != 1:
        fail("Appendix A heading not found or duplicated")
    html = APPENDIX_RE.sub(lambda m: references_html() + m.group(0), html, 1)

    # 5. inject the three figures next to the text that refers to them.
    for fig in FIGURES:
        if html.count(fig["anchor"]) != 1:
            fail(f'anchor {fig["anchor"]!r} occurs {html.count(fig["anchor"])} times (want 1)')
        png_path = os.path.join(PREVIEW, "figs", fig["png"])
        if not os.path.exists(png_path):
            fail("missing figure " + png_path)
        b64 = base64.b64encode(open(png_path, "rb").read()).decode("ascii")
        block_html = ('<figure id="' + fig["id"] + '">\n'
                      '<img src="data:image/png;base64,' + b64 + '" role="img" '
                      'aria-label="' + fig["alt"] + '" alt="' + fig["alt"] + '" />\n'
                      '<figcaption>' + fig["caption"] + '</figcaption>\n</figure>\n')
        if fig["before"]:
            html = html.replace(fig["anchor"], block_html + fig["anchor"], 1)
        else:
            html = html.replace(fig["anchor"], fig["anchor"] + "\n" + block_html, 1)

    # 6. first-use citation wiring.
    html, used = wire_citations(html)

    # 7. verified invariants.
    if html.count("data:image/png;base64") != 3:
        fail("expected exactly 3 embedded figures")
    if html.count("Figure 1 — Denominator funnel") != 1:
        fail("Figure 1 caption duplicated: " +
             str(html.count("Figure 1 — Denominator funnel")))
    if html.count('<ol class="references">') != 1:
        fail("references list not found or duplicated")
    if html.count('<li id="ref-') != len(REFS):
        fail(f"expected {len(REFS)} reference entries")
    open(OUT, "w", encoding="utf-8").write(html)
    print(f"Wrote {OUT} ({os.path.getsize(OUT)} bytes, 3 figures embedded, "
          f"{len(REFS)} references)")
    print("citation superscripts wired: " + ", ".join(f"[{n}]<-{a!r}" for n, a in used))
    missing = [n for n in range(1, len(REFS) + 1) if n not in [u[0] for u in used]]
    print(f"left unwired (no unique prose anchor): {missing}")


if __name__ == "__main__":
    main()
