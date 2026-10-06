#!/usr/bin/env python3
"""Rebuild paper/preview/paper.html from paper/main_clean.md.

One pandoc pass (markdown -> html5, standalone, --embed-resources) with the
committed stylesheet and title header, then the three reviewer figures are
injected as base64 <img> at fixed anchors. Do NOT re-encode the result with a
second pandoc pass: that silently drops the embedded stylesheet and header
(how the previously committed copy lost them).

Anchors are pandoc-generated ids/first-lines from main_clean.md; the script
fails loud if any anchor is missing or duplicated.
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

FIGURES = [
    # (figure id, anchor regex to insert before, png, alt, caption)
    ("fig-1",
     r'<h2 id="results">',
     "fig-1-funnel.png", "Denominator funnel",
     "Figure 1 — Denominator funnel (each stage annotated against its own "
     "denominator): 60,000 per-version entries → 17,167 isLatest servers "
     "(28.6%) → 11,370 with a repository reference (66.2% of servers; "
     "11,288 GitHub-linked, 65.8%) → GitHub-linked extraction yield: 16,763 "
     "tool-description rows from 4,725 repositories → 4,128 any-flag rows "
     "(24.6%) → 698 poison-flag rows (4.2%) → 150 reviewed rows → 268 flag "
     "instances → 15 supported (5.6%) → 5 poison-positive rows. Stage "
     "numerators from the collection report (§A.1, §A.2); scan rates from "
     "data/candidate_rate_scan.csv and data/validation_family_split.csv."),
    ("fig-2",
     r'<h3 id="the-five-tp-rows-and-four-mechanisms">',
     "fig-2-perclass.png", "Per-class text-support rate",
     "Reviewer figure (not a numbered paper figure) — Per-class text-support "
     "rate, paper §6.2: supported/instances for each of the 13 fired classes "
     "from data/validation_report.md; poison family 6/124 = 4.8% (dashed), "
     "all-family 15/268 = 5.6% (dotted). Colors: capability orange, poison "
     "blue, channel green."),
    ("fig-3",
     r"<p>Pooled attack ASR",
     "fig-3-trials.png", "Mocked harness results",
     "Reviewer figure (not a numbered paper figure) — Mocked-harness results, "
     "paper §8: success/total per arm × model cell and 95% compatibility "
     "intervals for the pooled arms — FL [0.70, 1.00], DP [0.57, 0.98], "
     "WF [0.35, 0.88], CTRL [0.00, 0.19] — recomputed from "
     "data/live_tests/trials_ledger.jsonl (fully mocked harness, synthetic "
     "data only)."),
]


def fail(msg):
    print("BUILD FAIL: " + msg, file=sys.stderr)
    sys.exit(1)


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
    html = html.replace("<title>main_clean</title>",
                        "<title>" + TITLE + "</title>")

    # 2. -H parks the title block in <head> (invalid); move it to top of body.
    m = re.search(r'<div class="title-block">.*?</div>\s*(?=</head>)',
                  html, re.S)
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

    # 4. inject the three figures as base64 <img> before their anchors.
    for fid, anchor, png, alt, caption in FIGURES:
        if html.count(anchor) != 1:
            fail(f"anchor {anchor!r} occurs {html.count(anchor)} times (want 1)")
        png_path = os.path.join(PREVIEW, "figs", png)
        if not os.path.exists(png_path):
            fail("missing figure " + png_path)
        b64 = base64.b64encode(open(png_path, "rb").read()).decode("ascii")
        fig = (f'<figure id="{fid}">\n'
               f'<img src="data:image/png;base64,{b64}" role="img" '
               f'aria-label="{alt}" alt="{alt}" />\n'
               f'<figcaption>{caption}</figcaption>\n'
               f'</figure>\n')
        html = html.replace(anchor, fig + anchor, 1)

    if html.count("data:image/png;base64") != 3:
        fail("expected exactly 3 embedded figures")
    open(OUT, "w", encoding="utf-8").write(html)
    print(f"Wrote {OUT} ({os.path.getsize(OUT)} bytes, 3 figures embedded)")


if __name__ == "__main__":
    main()
