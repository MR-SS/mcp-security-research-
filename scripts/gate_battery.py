#!/usr/bin/env python3
"""The PI's standard gate battery, run at every phase-set commit.

Gates (all four must pass):
  G1  pilot/derive_r4_numbers.py                -> exit 0
  G2  experiments/trial_accounting.py --check   -> exit 0
  G3  abstract word count <= 180                -> both manuscript sources
  G4  number parity main.md <-> main_clean.md   -> 5 non-equal opcodes
      (HEAD historical baseline; the 5 ops are pre-existing provenance deletes,
       not editorial drift)

G4 uses the retired builder's tokenizer via import. The builders were retired at
commit c981c9a and cannot be run as scripts (their REPO path predates the move to
pilot/legacy/), but `numbers()`/`body_of*`/`_strip_figure` remain the project's
definition of "the same data numbers, in order", so the parity gate is computed
with them rather than reimplemented.

Usage:  python3 scripts/gate_battery.py
"""
import difflib
import importlib.util
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARITY_BASELINE = 5
ABSTRACT_CAP = 180
RESULTS = []


def record(gate, detail, ok):
    RESULTS.append((gate, detail, ok))
    print(f"  {'PASS' if ok else 'FAIL'}  {gate}: {detail}")
    return ok


def run(cmd):
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True).returncode


def load_legacy():
    path = os.path.join(REPO, "pilot", "legacy", "make_publication.py")
    spec = importlib.util.spec_from_file_location("legacy_make_publication", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def abstract_words(path):
    t = open(path, encoding="utf-8").read()
    m = re.search(r"## 1\. Abstract\s*\n(.*?)\n## ", t, re.S)
    if not m:
        return None
    return len(re.sub(r"<!--.*?-->", "", m.group(1), flags=re.S).strip().split())


def main():
    print("GATE BATTERY")

    g1 = run([sys.executable, os.path.join("pilot", "derive_r4_numbers.py")])
    record("G1 derive_r4_numbers", f"exit {g1}", g1 == 0)

    g2 = run([sys.executable, os.path.join("experiments", "trial_accounting.py"), "--check"])
    record("G2 trial_accounting", f"exit {g2}", g2 == 0)

    counts = {f: abstract_words(os.path.join(REPO, f))
              for f in ("paper/main.md", "paper/main_clean.md")}
    norm = [c for c in counts.values() if c is not None]
    ok3 = len(norm) == 2 and all(c <= ABSTRACT_CAP for c in norm)
    record("G3 abstract cap", f"main.md {counts['paper/main.md']} / "
                              f"main_clean.md {counts['paper/main_clean.md']} "
                              f"(cap {ABSTRACT_CAP})", ok3)

    mp = load_legacy()
    src = open(os.path.join(REPO, "paper", "main.md"), encoding="utf-8").read()
    cln = open(os.path.join(REPO, "paper", "main_clean.md"), encoding="utf-8").read()
    a = mp.numbers(mp._strip_figure(mp.body_of_src(src)))
    b = mp.numbers(mp._strip_figure(mp.body_of(cln)))
    ops = [o for o in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
           if o[0] != "equal"]
    ok4 = len(ops) == PARITY_BASELINE
    record("G4 number parity",
           f"{len(ops)} non-equal opcodes (src {len(a)} / clean {len(b)} tokens; "
           f"HEAD baseline {PARITY_BASELINE})", ok4)

    failed = [g for g, _, ok in RESULTS if not ok]
    print()
    if failed:
        print(f"BATTERY FAILED: {', '.join(failed)}")
        return 1
    print(f"BATTERY PASSED ({len(RESULTS)}/{len(RESULTS)} gates)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
