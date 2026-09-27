#!/usr/bin/env python3
"""Mission Brief 03 — interactive manual labeling CLI.

Usage:
  python3 label_sample.py                        # interactive labeling
  python3 label_sample.py --dry-run 2            # test with 2 rows, then abort
  python3 label_sample.py --report               # compute precision, write report

Repair modes (added 2026-09-26 — mechanics only, the human still labels):
  python3 label_sample.py --review-unclear               # re-review every row labeled u
  python3 label_sample.py --review-unclear --no-prompt   # inventory only (no prompts)
  python3 label_sample.py --review-truncated             # re-review labeled rows whose
                                                         # 300-char CSV excerpt hid text
  python3 label_sample.py --review-truncated --no-prompt # inventory only (no prompts)
  python3 label_sample.py --note 4 "single-line note"     # enrich an existing FP row
  python3 label_sample.py --set-note 12 "single-line note" # repair a note on ANY row
  python3 label_sample.py --verdict 3 fp "single-line note" # record a PI verdict + its
                                                           # rationale on an already-labeled
                                                           # row; MAY change the label

`--verdict` is the only non-interactive path that may change a label: the human supplies
both the label and its single-line rationale on the command line (e.g. when a full-text
re-review was written up offline), and an empty note is refused, so no label can be flipped
without a stated reason. The script still never picks a verdict itself.

Evidence display (all labeling, from 2026-09-26): every row is rendered from the FULL
text in `data/github_tools.jsonl`, never from the 300-char CSV excerpt, and every
description carries an explicit terminal marker:
  [FULL TEXT]             the complete server-authored description
  [TRUNCATED-AT-SOURCE]   the stored text is itself cut — analyze.py's 300-char cap
                          and no github_tools.jsonl row to recover the text from
  [TRUNCATED-AT-DISPLAY]  the full text exists but exceeds DISPLAY_LIMIT chars, so
                          only the first DISPLAY_LIMIT are printed (see TOOLS for
                          the rest) — this is a terminal limit, NOT a data problem

File-mutation contract (auditable, never destructive):
  * `data/labels.jsonl` is APPEND-ONLY. A repair appends the corrected record; reads
    are last-wins per row_id (`load_labels`), so the newest record always wins.
  * Every replaced record is copied verbatim to `data/labels.jsonl.superseded`.
  * Every mutation also appends a JSON line to `data/labels.audit.jsonl`
    (ts, action, row_id, old, new).
  * Notes are single-line. A pasted multi-line block is JOINED with spaces rather
    than silently truncated: `input()` asks Python's buffered reader for a line and
    happily swallows a whole pasted block, storing line 1 and leaking the rest into
    LATER prompts (this is what truncated row 12's note at 2026-09-26T09:06Z).
    Notes now go through `_prompt_line()`, which reads one byte at a time off the
    TTY, then drains whatever else the paste left buffered. A note that still ends
    in a truncation signature (`:`, `,`, `;`, `-`, `...`) or carries fewer than four
    words triggers a confirm prompt before it is stored.

Labels are written immediately (resumable). Detector rules (v2) are frozen;
FP-derived regex fixes go to data/validation_report.md as a proposal diff only.
This script NEVER calls a model API and never auto-labels — it only displays
evidence and records the human's keystroke.
"""
import argparse, builtins, csv, json, os, re, select, sys, textwrap, datetime, collections
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
DATA = HERE / "data"
SAMPLE = DATA / "analysis_toollevel.csv"
LABELS = DATA / "labels.jsonl"
REPORT = DATA / "validation_report.md"
# Repair-mode sidecars (audit trail for every mutation).
TOOLS = DATA / "github_tools.jsonl"
SUPERSEDED = DATA / "labels.jsonl.superseded"
AUDIT = DATA / "labels.audit.jsonl"
# analyze.py truncates the CSV `description` column to this many chars; the
# excerpt-vs-full comparison below needs the same constant to stay honest.
CSV_DESC_LIMIT = 300
# Labels that mean "human could not decide with the evidence shown".
UNCLEAR_LABELS = ("u", "unclear")
# Every label `--verdict` may write (the interactive CLI's t/f/u/fn/s keys).
VALID_LABELS = ("tp", "fp", "u", "unclear", "fn", "skip")
# Hard display limit: never flood the terminal with a 20 KB description. Anything
# longer is printed as its first DISPLAY_LIMIT chars and marked [TRUNCATED-AT-DISPLAY];
# the untouched text stays available in `github_tools.jsonl`.
DISPLAY_LIMIT = 1500

# Per-class one-line TP rules (mirrors LABELING_RUBRIC.md).
RULES = {
    "shell_execution": "TP only if the description explicitly says the tool can RUN a shell, execute commands, invoke bash/cmd, or spawn a subprocess — not merely references shell-related words in passing.",
    "file_write_delete": "TP only if the description states the tool CREATES, MODIFIES, or REMOVES files on disk at the caller's direction — not a metaphorical 'write up a report'.",
    "file_read_sensitive": "TP only if the description states the tool READS files or filesystem content (including globbing) — not a reference to reading data generally.",
    "secret_env_access": "TP only if the description states the tool READS, WRITES, or DEPENDS ON environment variables, tokens, API keys, secrets, or credentials — not just the words in a list of what it protects against.",
    "network_egress": "TP only if the description states the tool MAKES outbound HTTP requests, fetches URLs, posts to webhooks, downloads/uploads, or scrapes — not merely that it connects to a remote server conceptually.",
    "database_write": "TP only if the description states the tool QUERIES, INSERTS, or UPDATES a database — not just the word 'query' used in a non-SQL sense.",
    "package_install": "TP only if the description states the tool INSTALLS packages or dependencies (pip, npm, etc.) — not just lists dependencies as output.",
    "imperative_to_model": "TP only if the description TELLS THE MODEL what it must/should/never do in an imperative directed at the agent — not marketing copy that happens to use 'never' or 'always' about a product feature.",
    "stealth_concealment": "TP only if it tells the agent to HIDE actions, results, or reasoning from the user (e.g., 'do not disclose', 'silently', 'without the user's knowledge') — not a description of a hidden/internal feature.",
    "important_tags": "TP only if the description CONTAINS or SIMULATES injection-style markup tags (<IMPORTANT>, <SYSTEM>, [INST], <<SYS>>) designed to manipulate model behavior — not a product name containing those words.",
    "cross_tool_shadowing": "TP only if the description INSTRUCTS THE AGENT to alter its use of OTHER tools or servers (e.g., 'when emailing, always CC…') — not a standalone tool description.",
    "exfiltration_language": "TP only if the description DESCRIBES SENDING DATA to an external endpoint or address (URL, webhook, email CC, transmission) — not a product URL or marketing link in the description.",
    "sensitive_file_target": "TP only if the description EXPLICITLY NAMES a sensitive file or path (.ssh, id_rsa, .env, .aws/credentials, .kube, /etc/passwd, .npmrc, .pypirc) AS A TARGET the tool operates on — not as a file the tool helps you avoid.",
    "fake_system_role": "TP only if the description ASSIGNS a fake system role or instructs the model to ignore prior instructions (e.g., 'system prompt', 'ignore previous', 'new instructions') — not a legitimate product description.",
    "model_addressed": "CHANNEL measurement (not malice): TP if the description names an agent, model, LLM, bot, or assistant as its intended audience.",
    "second_person_imperative": "CHANNEL measurement (not malice): TP if the description uses 'you'/'your' plus an imperative.",
}

FLAG_RE = re.compile(r'^([a-z_]+):([a-z_]+)$')


def parse_flags(flag_str):
    out = []
    for f in flag_str.split(';'):
        f = f.strip()
        if not f:
            continue
        m = FLAG_RE.match(f)
        if m:
            out.append((m.group(1), m.group(2)))
    return out


def flag_summary(row):
    parts = []
    for col, label in [('capability_flags', 'CAP'), ('poison_flags', 'POI'),
                       ('addressing_flags', 'ADR')]:
        fl = parse_flags(row.get(col, '') or '')
        if fl:
            parts.append(f"{label}:{';'.join(c for g, c in fl)}")
    return '; '.join(parts) if parts else '(none)'


def rule_for_class(cls):
    return RULES.get(cls, f"NO RULE for {cls}")


def rules_for_row(row):
    seen = set(); lines = []
    for col, label in [('capability_flags', 'CAPABILITY'), ('poison_flags', 'POISON'),
                        ('addressing_flags', 'ADDRESSING')]:
        for g, c in parse_flags(row.get(col, '') or ''):
            if c in seen:
                continue
            seen.add(c)
            lines.append(f"  [{c}] {rule_for_class(c)}")
    return lines


def load_labels():
    labels = {}
    if LABELS.exists():
        for line in open(LABELS, encoding='utf-8'):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
                labels[str(r['row_id'])] = r
            except (json.JSONDecodeError, KeyError):
                pass
    return labels


def verify_sample():
    rows = list(csv.DictReader(open(SAMPLE, newline='', encoding='utf-8')))
    if len(rows) != 150:
        print(f"ABORT: analysis_toollevel.csv has {len(rows)} rows, expected exactly 150.", file=sys.stderr)
        sys.exit(1)
    scores = [int(r['suspicion_score']) for r in rows]
    if any(int(r['suspicion_score']) <= 0 for r in rows[:100]):
        print("ABORT: top-100 rows must all have suspicion_score > 0.", file=sys.stderr)
        sys.exit(1)
    if any(int(r['suspicion_score']) != 0 for r in rows[100:]):
        print("ABORT: last-50 rows must all have suspicion_score == 0.", file=sys.stderr)
        sys.exit(1)
    if scores[:100] != sorted(scores[:100], reverse=True):
        print("ABORT: top-100 rows are not sorted by suspicion_score descending.", file=sys.stderr)
        sys.exit(1)
    print(f"OK: {len(rows)} rows verified (top-100 scores {scores[0]}…{scores[99]}, last-50 zero-flag).")
    return rows


def wrap(text, width=72):
    return textwrap.fill(text or '', width=width)


def display_row(row, k, total, index=None):
    """Render one sample row: header, per-class TP rules, then the FULL text.

    Never shows the 300-char CSV excerpt as evidence — `display_full_text` pulls the
    complete description from github_tools.jsonl and labels what it is showing.
    """
    if index is None:
        index = load_tool_rows()
    print(f"\n{'='*72}")
    print(f"[{k}/{total}]  score={row['suspicion_score']}")
    print(f"  name : {row['name']}")
    print(f"  repo : {row['repo']}")
    print(f"  flags: {flag_summary(row)}")
    print(f"{'='*72}")
    for line in rules_for_row(row):
        print(line)
    display_full_text(row, index, header=False)


def prompt_label(row, idx, labels, disp_text=None):
    """Loop until valid keypress. Returns (label, note) or (None, None) if quit."""
    already = labels.get(str(idx))
    if already:
        print(f"  [already labeled: {already['label']}]")
    disp = disp_text or f"{idx + 1}/150"
    while True:
        has_fn = idx >= 100
        keys = 't/f/u/' + ('fn ' if has_fn else '') + 's/q'
        try:
            key = input(f"  [{disp}] {keys} > ").strip().lower()
        except EOFError:
            print()
            return None, None
        if key == 'q':
            return None, None
        if key == 's':
            return 'skip', ''
        if key in ('t', 'u'):
            try:
                note = prompt_note('tp' if key == 't' else 'unclear')
            except EOFError:
                print("\n  stdin closed while entering the note — quitting.")
                return None, None
            return ('tp' if key == 't' else 'u'), note
        if key == 'f':
            try:
                note = prompt_note('fp', required=False)
            except EOFError:
                print("\n  stdin closed while entering the note — quitting.")
                return None, None
            return 'fp', note
        if key == 'fn':
            if has_fn:
                return 'fn', ''
            print("  fn only available for zero-flag rows (display 101-150).")
            continue
        print(f"  unknown key '{key}' — use {keys}")


def _utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def append_line(path, rec):
    """Append one JSON record and flush immediately (crash-safe, resumable)."""
    with open(path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')
        f.flush()


def log_mutation(action, row_id, old, new):
    """Append an audit entry for every file mutation (AGENTS.md: log mutations)."""
    append_line(AUDIT, {"ts": _utc(), "action": action, "row_id": str(row_id),
                        "file": LABELS.name, "old": old, "new": new})


def supersede(old_rec, new_rec, action):
    """Auditable replacement: old record -> .superseded, new record -> labels.jsonl.

    labels.jsonl stays append-only; load_labels() is last-wins per row_id, so the
    new record takes effect without deleting any history.
    """
    append_line(SUPERSEDED, old_rec)
    append_line(LABELS, new_rec)
    log_mutation(action, new_rec["row_id"], old_rec, new_rec)


def write_label(idx, name, repo, flags, label, note):
    rec = {"row_id": str(idx), "name": name, "repo": repo, "flags": flags,
           "label": label, "note": note, "ts": _utc()}
    append_line(LABELS, rec)


# ---------- note hygiene (single-line enforcement) ----------

def _collapse(note):
    """Collapse newlines/tabs/runs of spaces so a pasted block fits one line."""
    return ' '.join((note or '').split())


def note_profile(note):
    """Flag the truncation signature left behind by a multi-line paste."""
    n = (note or '').rstrip()
    if not n:
        return None
    if n.endswith((':', ',', ';', '-', '—', '...', '(')):
        return f"ends with {n[-1]!r} — looks cut off mid-sentence"
    if len(n.split()) < 4:
        return "only a few words — a note must state the reasoning"
    return None


# A pasted block arrives from the terminal in one burst; wait this long for the
# rest of it after the first line lands (a human typist adds ~0 ms of delay, so
# this costs nothing in normal use).
PASTE_SETTLE = 0.05


def _genuine_input():
    """True when `input` is Python's builtin and not a scripted/substituted stub.

    Test and automation drivers commonly replace `builtins.input` with a function
    that returns queued keystrokes (the Brief 03 sandbox suite does). If we ignored
    that stub and read the terminal ourselves the driver would deadlock waiting for
    input it already handed us — so a stub always wins, and we fall back to the
    plain `input()` path (i.e. the pre-2026-09-26 behaviour).
    """
    try:
        return getattr(builtins.input, '__module__', None) == 'builtins'
    except Exception:                      # exotic stub without __module__
        return False


def _tty_available():
    """True when stdin is a real terminal we can safely read byte-wise."""
    if not _genuine_input():
        return False
    try:
        return sys.stdin is not None and sys.stdin.isatty()
    except (AttributeError, ValueError):   # detached / closed stdin
        return False


def _read_tty_line(fd):
    """Read exactly ONE line from a TTY, one byte at a time.

    `input()` cannot be used for free text: it asks the buffered reader for a line,
    the reader fills its 8 KB buffer from the tty, and a pasted block therefore
    loses every line after the first (which then leak into the next prompts).
    Reading the raw fd byte-by-byte can never over-read.

    Raises EOFError when the line starts at end-of-input, so callers can quit the
    way they do on `input()`; a line that ends without a trailing newline is
    returned as-is.
    """
    buf = bytearray()
    while True:
        try:
            b = os.read(fd, 1)
        except OSError:                    # tty hung up
            if not buf:
                raise EOFError("stdin closed")
            break
        if not b:                          # end-of-input
            if not buf:
                raise EOFError("stdin closed")
            break
        if b in (b'\n', b'\r'):
            break
        buf += b
    enc = (getattr(sys.stdin, 'encoding', None) or 'utf-8')
    return buf.decode(enc, 'replace')


def _drain_pasted_lines(fd):
    """Return any further lines the TTY already has buffered (rest of a paste)."""
    extra, timeout = [], PASTE_SETTLE
    while select.select([fd], [], [], timeout)[0]:
        extra.append(_read_tty_line(fd))
        timeout = 0.0                      # keep only while data keeps arriving
    return extra


def _prompt_line(prompt):
    """`input()` for free text, without its paste over-read on a TTY."""
    sys.stdout.write(prompt)
    sys.stdout.flush()
    if _tty_available():
        return _read_tty_line(sys.stdin.fileno())
    return input()                         # piped/non-tty (tests, fixtures)


def prompt_note(purpose, required=True):
    """Read ONE note; a pasted block is joined, never silently truncated."""
    prompt = ("  note (single line; paste OK, required for "
              f"{purpose}): ") if required else "  note (optional, Enter to skip): "
    while True:
        first = _prompt_line(prompt)
        extra = _drain_pasted_lines(sys.stdin.fileno()) if _tty_available() else []
        raw = '\n'.join([first] + extra)
        note = _collapse(raw)
        if not note:
            if required:
                print("  NOTE REQUIRED — write something.")
                continue
            return ''
        if extra:
            print(f"  NOTE JOINED to one line ({len(extra) + 1} pasted lines — "
                  f"{len(note)} chars kept, nothing dropped).")
        warn = note_profile(note) if required else None
        if warn:
            print(f"  WARNING: {warn}")
            print(f"  -> would store: {note!r}")
            if _prompt_line("  accept as-is? [y/N] > ").strip().lower() != 'y':
                continue
        return note


# ---------- full-description lookup (repair mode) ----------

def load_tool_rows():
    """Load data/github_tools.jsonl into a (server_name, tool_name) index."""
    idx = collections.defaultdict(list)
    if not TOOLS.exists():
        return idx
    with open(TOOLS, encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                t = json.loads(line)
            except json.JSONDecodeError:
                continue
            idx[(t.get('server_name', ''), t.get('tool_name', ''))].append(t)
    return idx


def reference_descriptions(row, index):
    """Resolve the FULL text(s) behind one CSV row.

    Returns (refs, warnings); each ref is {'source_file', 'full', 'kind'} where
    kind is 'exact' (a github_tools row whose 300-char excerpt reproduces the CSV
    text), 'sibling' (same server+tool name, different excerpt) or 'csv' (no
    source row found — the excerpt itself is then the only evidence and may
    already be truncated).
    """
    warnings, refs = [], []
    name = row.get('name', '')
    server, sep, tool = name.partition('::')
    excerpt = row.get('description', '') or ''
    cands = index.get((server, tool), []) if sep else []
    if not cands and sep:
        # Fallback 1: tool_name only (server_name drifts between snapshots).
        cands = [t for k, v in index.items() if k[1] == tool for t in v]
        if cands:
            warnings.append(f"no row for server_name={server!r}; matched "
                            f"tool_name={tool!r} only ({len(cands)} candidate(s))")
    if not cands:
        warnings.append(f"NOT FOUND in {TOOLS.name} — falling back to the CSV "
                        f"excerpt (itself capped at {CSV_DESC_LIMIT} chars)")
        return [{'source_file': '(csv)', 'full': excerpt, 'kind': 'csv'}], warnings
    exact, siblings = [], []
    for t in cands:
        full = (t.get('tool_description') or '').replace('\n', ' ')
        (exact if full[:CSV_DESC_LIMIT] == excerpt else siblings).append((t, full))
    if len(exact) > 1:
        warnings.append(f"{len(exact)} rows reproduce the excerpt exactly; showing all")
    for t, full in exact:
        refs.append({'source_file': t.get('source_file', '?'), 'full': full,
                     'kind': 'exact'})
    if not exact:
        warnings.append(f"no exact excerpt match among {len(cands)} candidate(s) for "
                        f"{name!r} — showing candidates longest-first")
        siblings.sort(key=lambda p: -len(p[1]))
        for t, full in siblings[:3]:
            refs.append({'source_file': t.get('source_file', '?'), 'full': full,
                         'kind': 'sibling'})
    return refs, warnings


def display_full_text(row, index, header=True):
    """Print the FULL description(s) behind a CSV row, with explicit markers.

    Evidence rule (AGENTS.md §2.3 — detector honesty): the human must always know
    whether the text on screen is the whole server-authored description or a
    cut-down view, and *why* it is cut down.

    Returns verdicts: list of (kind, full_len, verdict_text, marker).
    """
    excerpt = row.get('description', '') or ''
    refs, warnings = reference_descriptions(row, index)
    if header:
        at_cap = '  <- AT CAP, the display was truncated' if len(excerpt) >= CSV_DESC_LIMIT else ''
        print(f"\n{'='*72}")
        print(f"  name : {row.get('name', '')}")
        print(f"  repo : {row.get('repo', '')}")
        print(f"  flags: {flag_summary(row)}")
        print(f"  CSV excerpt: {len(excerpt)} chars (CSV cap = {CSV_DESC_LIMIT}){at_cap}")
        print(f"{'='*72}")
    for w in warnings:
        print(f"  [warn] {w}")
    verdicts = []
    for r in refs:
        full = r['full']
        marker = full_text_marker(r['kind'], len(full))
        if r['kind'] == 'csv':
            verdict = "N/A (no source row found)"
        elif len(full) > len(excerpt):
            verdict = (f"LONGER by {len(full) - len(excerpt)} chars — "
                       f"the label was made on a truncated view")
        elif len(full) == len(excerpt):
            verdict = "IDENTICAL — no truncation, the excerpt is the complete text"
        else:
            verdict = "SHORTER (candidate is not the excerpt source)"
        verdicts.append((r['kind'], len(full), verdict, marker))
        print(f"{'-'*72}")
        print(f"  {marker}  full_len={len(full)}  source={r['source_file']}  [{r['kind']}]")
        print(f"  VERDICT: {verdict}")
        if marker == '[TRUNCATED-AT-SOURCE]':
            print(f"  (stored text is capped at {CSV_DESC_LIMIT} chars by analyze.py and no")
            print(f"   {TOOLS.name} row was found to recover the rest)")
        elif marker == '[TRUNCATED-AT-DISPLAY]':
            print(f"  (showing first {DISPLAY_LIMIT} of {len(full)} chars — terminal limit;")
            print(f"   the untouched text is in {TOOLS.name})")
        print(f"{'-'*72}")
        print(wrap(full[:DISPLAY_LIMIT], 72))
    print(f"{'-'*72}")
    return verdicts


def full_text_marker(kind, length):
    """Terminal marker for one description block (see module docstring).

    'csv' means no github_tools.jsonl row was found, so the 300-char-capped CSV
    excerpt is the only evidence we hold — at exactly the cap we cannot tell what
    analyze.py cut off, hence [TRUNCATED-AT-SOURCE] rather than [FULL TEXT].
    """
    if kind == 'csv':
        return '[TRUNCATED-AT-SOURCE]' if length >= CSV_DESC_LIMIT else '[FULL TEXT]'
    return '[TRUNCATED-AT-DISPLAY]' if length > DISPLAY_LIMIT else '[FULL TEXT]'


def _best_ref(refs):
    """Prefer an exact excerpt match; else the longest same-server/tool candidate."""
    real = [r for r in refs if r['kind'] != 'csv']
    if not real:
        return None
    return max([r for r in real if r['kind'] == 'exact'] or real,
               key=lambda r: len(r['full']))


def truncation_status(row, index):
    """Was this row's label made on a truncated view of its description?

    Returns excerpt_len, full_len, delta, kind, source_file and two booleans:
      truncated   verified — the recovered full text is longer than the CSV excerpt;
      csv_capped  unverifiable — the excerpt sits exactly on analyze.py's 300-char
                  cap and no source row exists to check what was cut.
    """
    excerpt = row.get('description', '') or ''
    refs, warnings = reference_descriptions(row, index)
    ref = _best_ref(refs)
    st = {'excerpt_len': len(excerpt), 'full_len': len(excerpt), 'delta': 0,
          'kind': 'csv', 'source_file': '(csv)', 'truncated': False,
          'csv_capped': len(excerpt) >= CSV_DESC_LIMIT, 'warnings': warnings}
    if ref is not None:
        full = ref['full']
        st.update({'full_len': len(full), 'delta': max(0, len(full) - len(excerpt)),
                   'kind': ref['kind'], 'source_file': ref['source_file'],
                   'truncated': len(full) > len(excerpt), 'csv_capped': False})
    return st


def truncated_labeled_rows(labels, rows, index, exclude_unclear=True):
    """The --review-truncated set: labeled rows whose evidence was cut down.

    Rows currently labeled u/unclear are excluded by default because --review-unclear
    already shows them the same full text (overlap would double-count in the report).
    """
    out = []
    for rid in sorted(int(k) for k in labels):
        v = labels[str(rid)]
        if exclude_unclear and v['label'] in UNCLEAR_LABELS:
            continue
        st = truncation_status(rows[rid], index)
        if st['truncated'] or st['csv_capped']:
            st.update({'row_id': rid, 'label': v['label'],
                       'name': rows[rid]['name'], 'repo': rows[rid]['repo']})
            out.append(st)
    return out


def audit_events(actions=None):
    """Read the mutation audit log into a list (newest last)."""
    events = []
    if not AUDIT.exists():
        return events
    for line in open(AUDIT, encoding='utf-8'):
        if not line.strip():
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if actions and e.get('action') not in actions:
            continue
        events.append(e)
    return events


def unclear_row_ids(labels):
    """row_ids currently labeled u/unclear, ascending."""
    return sorted(int(k) for k, v in labels.items() if v['label'] in UNCLEAR_LABELS)


def interactive():
    rows = verify_sample()
    labels = load_labels()
    index = load_tool_rows()
    done = sum(1 for k in range(len(rows)) if str(k) in labels)
    print(f"{SAMPLE}: {len(rows)} rows | labeled: {done}")
    if TOOLS.exists():
        print(f"evidence: FULL text from {TOOLS.name} "
              f"({len(index)} (server, tool) keys), display cap {DISPLAY_LIMIT} chars")
    else:
        print(f"  [warn] {TOOLS.name} missing — falling back to the {CSV_DESC_LIMIT}-char"
              f" CSV excerpt")
    for i, row in enumerate(rows):
        if str(i) in labels:
            continue
        display_row(row, i + 1, len(rows), index=index)
        label, note = prompt_label(row, i, labels)
        if label is None:
            print(f"\nQUIT. Resumable — rerun to continue from display {i+2}.")
            break
        if label == 'skip':
            continue
        flags = flag_summary(row)
        write_label(i, row['name'], row['repo'], flags, label, note)
        n_lab = sum(1 for k in range(len(rows)) if str(k) in load_labels())
        print(f"  -> {label} written. Progress: {n_lab}/{len(rows)}.")
    print(f"\nDONE. Labels: {LABELS}")


# ---------- repair commands (added 2026-09-26) ----------

def _review_rows(title, action, ids_fn, no_prompt=False):
    """Shared mechanic behind --review-unclear and --review-truncated.

    Shows every selected row's FULL source text (with markers), its per-class TP
    rules and a truncation diagnosis, then re-prompts with the normal t/f/u/s/q keys.
    Nothing is written until the human presses a key; t/u require a single-line note;
    every replacement is archived to labels.jsonl.superseded and logged to
    labels.audit.jsonl. `ids_fn(labels, rows, index) -> (ids, prelude, hints)`.
    """
    rows = verify_sample()
    labels = load_labels()
    index = load_tool_rows() if TOOLS.exists() else {}
    ids, prelude, hints = ids_fn(labels, rows, index)
    counts = collections.Counter(v['label'] for v in labels.values())
    print(f"\n=== {title} ===  source: {SAMPLE.name}")
    print(f"labeled rows: {len(labels)}/{len(rows)}  "
          f"(tp={counts['tp']}, fp={counts['fp']}, "
          f"u={counts['u'] + counts['unclear']}, skip={counts['skip']})")
    if prelude:
        print(prelude)
    if not ids:
        print("Nothing to review — no rows match this repair mode.")
        return
    print(f"rows to review ({len(ids)}): {', '.join(str(i) for i in ids)}")
    for rid in ids:
        if hints and rid in hints:
            print(f"  row {rid}: {hints[rid]}")
    if not TOOLS.exists():
        print(f"  [warn] {TOOLS} missing — falling back to the CSV excerpt for every row")
    if no_prompt:
        print("INVENTORY ONLY (--no-prompt): full text shown, NO labels written.")
    for rid in ids:
        row, v = rows[rid], labels[str(rid)]
        print(f"\n{'#'*72}")
        print(f"# row {rid} — currently '{v['label']}'  (old note: {v.get('note', '')!r})")
        print(f"{'#'*72}")
        verdicts = display_full_text(row, index, header=True)
        excerpt_len = len(row.get('description', '') or '')
        longer = any(k in ('exact', 'sibling') and ln > excerpt_len
                     for k, ln, _, _ in verdicts)
        print(f"  DIAGNOSIS: {'the original display WAS truncated (mechanical)' if longer else 'no truncation found (judgment call)'}")
        for line in rules_for_row(row):
            print(line)
        print(f"{'-'*72}")
        if no_prompt:
            continue
        label, note = prompt_label(row, rid, labels, disp_text=f"row {rid}")
        if label is None:
            print(f"\nQUIT at row {rid}. Labels already written are on disk.")
            return
        if label == 'skip':
            print(f"  row {rid} left as '{v['label']}' (skipped).")
            continue
        new_rec = {"row_id": str(rid), "name": row['name'], "repo": row['repo'],
                   "flags": flag_summary(row), "label": label, "note": note,
                   "ts": _utc(),
                   "supersedes": {"label": v['label'], "note": v.get('note', ''),
                                  "ts": v.get('ts')}}
        supersede(v, new_rec, action=action)
        print(f"  -> row {rid}: '{v['label']}' superseded by '{label}'.")
    print(f"\nDONE. labels={LABELS.name}  superseded={SUPERSEDED.name}  audit={AUDIT.name}")


def _unclear_ids(labels, rows, index):
    ids = unclear_row_ids(labels)
    return ids, f"{len(ids)} row(s) labeled u/unclear", None


def _truncated_ids(labels, rows, index):
    """Truncation-affected labeled rows, minus the u-rows (--review-unclear's set)."""
    affected = truncated_labeled_rows(labels, rows, index, exclude_unclear=True)
    ids = [a['row_id'] for a in affected]
    prelude = (f"{len(ids)} labeled row(s) whose CSV excerpt is shorter than the full "
               f"source text (analyze.py caps the column at {CSV_DESC_LIMIT} chars, but "
               f"the detector scanned the full text)")
    hints = {a['row_id']: f"truncated: excerpt {a['excerpt_len']} -> full {a['full_len']} "
                          f"(+{a['delta']} chars) via {a['source_file']}"
             for a in affected}
    seen = set()
    # 'verdict' counts too: a full-text verdict also writes the row's note, and the
    # re-reviewer needs the same "already decided by hand, press s" signal for it.
    for e in audit_events(('set-note', 'note', 'verdict')):
        try:
            rid = int(e['row_id'])
        except (KeyError, TypeError, ValueError):
            continue
        if rid in hints and rid not in seen:
            seen.add(rid)          # once per row, however many note/verdict edits it has
            hints[rid] += "  [note already hand-repaired 2026-09-26 — press s to keep it]"
    return ids, prelude, hints


def review_unclear(no_prompt=False):
    """Re-review every row labeled u, showing its FULL source text.

    The mechanic answers the only question the human cannot answer from the CSV:
    was the display truncated (mechanical) or is this a genuine judgment call?
    """
    _review_rows('--review-unclear', 'review-unclear', _unclear_ids,
                 no_prompt=no_prompt)


def review_truncated(no_prompt=False):
    """Re-review labeled rows whose label rests on analyze.py's 300-char excerpt.

    analyze.py caps the CSV `description` column (CSV_DESC_LIMIT) while the detector
    scanned the FULL text, so any label on a capped row was made on less evidence
    than the detector saw. This pass shows the full text and lets the human confirm
    or flip the label. Rows labeled u are excluded — --review-unclear covers those.
    """
    _review_rows('--review-truncated', 'review-truncated', _truncated_ids,
                 no_prompt=no_prompt)


def set_note(rid, note, require_fp=False):
    """Replace the note on an existing row WITHOUT changing its label. Audited."""
    rows = verify_sample()
    labels = load_labels()
    if str(rid) not in labels:
        print(f"ABORT: row {rid} has no label yet — nothing to annotate.", file=sys.stderr)
        sys.exit(1)
    v = labels[str(rid)]
    if require_fp and v['label'] != 'fp':
        print(f"ABORT: row {rid} is '{v['label']}', not 'fp' — "
              f"use --set-note for repairs on non-fp rows.", file=sys.stderr)
        sys.exit(1)
    note = _collapse(note)          # joining is lossless: pasted blocks become one line
    if not note:
        print("ABORT: note is empty after whitespace collapse.", file=sys.stderr)
        sys.exit(1)
    warn = note_profile(note)
    if warn:
        print(f"  [warn] {warn}")
    new_rec = dict(v)
    new_rec.update({"note": note, "ts": _utc(),
                    "supersedes": {"label": v['label'], "note": v.get('note', ''),
                                   "ts": v.get('ts')}})
    supersede(v, new_rec, action='note' if require_fp else 'set-note')
    print(f"row {rid} [{v['label']}] note replaced")
    print(f"  old: {v.get('note', '')!r}")
    print(f"  new: {note!r}")
    print(f"  audit: {AUDIT.name}  superseded: {SUPERSEDED.name}")


def set_verdict(rid, label, note):
    """Record a PI verdict AND its rationale on an already-labeled row. Label MAY change.

    Used when the human has already re-decided a row on its FULL source text offline
    (e.g. the written-up answers to the `--review-unclear` queue). Both the label the
    statistics use and the rationale that justifies it are written atomically through
    `supersede`, so the previous record stays recoverable in `labels.jsonl.superseded`
    and the change is logged with old/new to `labels.audit.jsonl`.

    An empty note is refused: a label change without a stated reason is exactly what
    this project's labeling provenance rules exist to prevent.
    """
    rows = verify_sample()
    labels = load_labels()
    if str(rid) not in labels:
        print(f"ABORT: row {rid} has no label yet — label it interactively first.",
              file=sys.stderr)
        sys.exit(1)
    if label not in VALID_LABELS:
        print(f"ABORT: label {label!r} is not one of "
              f"{'/'.join(sorted(VALID_LABELS))}.", file=sys.stderr)
        sys.exit(1)
    v = labels[str(rid)]
    note = _collapse(note)          # joining is lossless: pasted blocks become one line
    if not note:
        print("ABORT: note is empty — a verdict needs its rationale.", file=sys.stderr)
        sys.exit(1)
    warn = note_profile(note)
    if warn:
        print(f"  [warn] {warn}")
    row = rows[rid]
    st = truncation_status(row, index=load_tool_rows() if TOOLS.exists() else {})
    new_rec = {"row_id": str(rid), "name": row['name'], "repo": row['repo'],
               "flags": flag_summary(row), "label": label, "note": note, "ts": _utc(),
               "supersedes": {"label": v['label'], "note": v.get('note', ''),
                              "ts": v.get('ts')}}
    supersede(v, new_rec, action='verdict')
    moved = label != v['label']
    print(f"row {rid} [{v['label']} -> {label}]"
          f"{' FLIP' if moved else ' (label unchanged)'} verdict recorded")
    print(f"  evidence: excerpt {st['excerpt_len']} -> full {st['full_len']} chars "
          f"({'+' if st['delta'] else ''}{st['delta']} hidden)  "
          f"{'truncated' if st['truncated'] else 'not truncated'}")
    print(f"  old note: {v.get('note', '')!r}")
    print(f"  new note: {note!r}")
    print(f"  audit: {AUDIT.name}  superseded: {SUPERSEDED.name}")
    return moved


def report():
    if not LABELS.exists():
        print("No labels.jsonl yet. Label some rows first.", file=sys.stderr)
        sys.exit(1)
    labels = load_labels()
    rows = list(csv.DictReader(open(SAMPLE, newline='', encoding='utf-8')))
    total = len(rows)
    labeled = {int(v['row_id']) for v in labels.values()}

    tp = collections.Counter(); fp = collections.Counter()
    tp_rows = fp_rows = 0                       # row counts (the counters above
    unclear = 0; fn = 0; skip = 0               # tally flag INSTANCES per class)
    fp_reasons = collections.Counter()
    tp_examples = collections.defaultdict(list)
    fn_examples = []

    for i, row in enumerate(rows):
        rid = str(i)
        if rid not in labels:
            continue
        v = labels[rid]; lab = v['label']; note = v.get('note', '')
        flags = parse_flags(row.get('poison_flags', '') or '') + \
                parse_flags(row.get('capability_flags', '') or '') + \
                parse_flags(row.get('addressing_flags', '') or '')
        if lab == 'tp':
            tp_rows += 1
            for _, c in flags:
                tp[c] += 1
                if len(tp_examples[c]) < 3:
                    tp_examples[c].append({'name': row['name'], 'note': note})
        elif lab == 'fp':
            fp_rows += 1
            for _, c in flags:
                fp[c] += 1
            # One taxonomy entry per ROW — a row carrying N flag classes is ONE
            # reason. (Classifying inside the loop above multiplied every
            # note-derived reason by the row's flag count, which misreported a
            # reason shared by one row as if several rows shared it.)
            lower = note.lower()
            if any(w in lower for w in ['marketing', 'product', 'feature']):
                fp_reasons['marketing/product language'] += 1
            elif any(w in lower for w in ['benign', 'legitimate', 'normal']):
                fp_reasons['benign legitimate use'] += 1
            elif any(w in lower for w in ['url', 'link', 'http']):
                fp_reasons['bare URL/link'] += 1
            elif not note.strip():
                fp_reasons['no note given'] += 1
            else:
                fp_reasons[note[:60]] += 1
        elif lab in UNCLEAR_LABELS:
            unclear += 1
        elif lab == 'fn':
            fn += 1; fn_examples.append({'name': row['name'], 'note': note})
        elif lab == 'skip':
            skip += 1

    lines = []
    lines.append("# Brief 03 — Validation Report\n")
    lines.append(f"> Generated {datetime.datetime.now(datetime.timezone.utc).isoformat()} from `{LABELS}` over `{SAMPLE}`.\n")
    lines.append("## Summary\n")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    labeled_count = len(labels)
    lines.append(f"| Total rows in sample | {total} |")
    lines.append(f"| Labeled rows | {labeled_count} |")
    lines.append(f"| Unlabeled rows | {total - labeled_count} |")
    lines.append(f"| Skip | {skip} |")
    lines.append(f"| TP rows | {tp_rows} |")
    lines.append(f"| FP rows | {fp_rows} |")
    lines.append(f"| Unclear rows | {unclear} |")
    lines.append(f"| False-negative (zero-flag) rows | {fn} |")
    lines.append(f"| Flag instances on TP rows | {sum(tp.values())} |")
    lines.append(f"| Flag instances on FP rows | {sum(fp.values())} |")
    lines.append("\n*Rows count rows. Flag instances count (row, class) pairs across "
                 "those rows: one row can carry several classes, so flag instances on "
                 "FP rows exceed FP rows. Precision below uses the per-class instance "
                 "counts.*\n")
    lines.append(f"\n## Per-class precision (TP / (TP+FP), unclear excluded)\n")
    all_classes = sorted(set(list(tp.keys()) + list(fp.keys())))
    lines.append("| Class | TP | FP | Precision |")
    lines.append("|---|---|---|---|")
    for c in all_classes:
        t, f = tp[c], fp[c]
        if t + f:
            lines.append(f"| `{c}` | {t} | {f} | {t/(t+f):.2f} |")
        else:
            lines.append(f"| `{c}` | {t} | {f} | N/A (no FPs) |")
    lines.append(f"\n## Unclear rate\n")
    unc_rate = unclear / max(labeled_count, 1)
    lines.append(f"Unclear / all labeled: {unclear}/{labeled_count} = {unc_rate:.2%}")
    lines.append(f"\n## False-negative rate (zero-flag rows only)\n")
    zero_count = sum(1 for r in rows if int(r['suspicion_score']) == 0)
    fn_rate = fn / max(zero_count, 1)
    lines.append(f"FN / zero-flag rows: {fn}/{zero_count} = {fn_rate:.2%}")
    if fn_examples:
        lines.append("\nFN examples:\n")
        for e in fn_examples[:5]:
            lines.append(f"- `{e['name']}` — {e['note']}")
    # ---- truncation-validity bookkeeping (added 2026-09-26) -------------------
    index = load_tool_rows() if TOOLS.exists() else {}
    affected = truncated_labeled_rows(labels, rows, index, exclude_unclear=False)
    aff_unclear = sorted(a['row_id'] for a in affected if a['label'] in UNCLEAR_LABELS)
    aff_reviewable = [a for a in affected if a['label'] not in UNCLEAR_LABELS]
    queue_ids = {str(a['row_id']) for a in aff_reviewable}
    # A full-text re-review reaches disk two ways: the --review-truncated queue
    # (action 'review-truncated') and a written-up verdict recorded with --verdict.
    # Both mean "a human re-decided this row on its full text", so both count here —
    # otherwise the u -> fp flips that truncation caused would be invisible.
    review_ev = audit_events(('review-truncated', 'verdict'))
    verdict_rows = sorted({str(e.get('row_id')) for e in review_ev
                           if e.get('action') == 'verdict'})
    def _changed(e):
        return (e.get('old') or {}).get('label') != (e.get('new') or {}).get('label')
    last_ev = {}
    flipped_by_row = {}
    for e in review_ev:
        rid = str(e.get('row_id'))
        if rid in queue_ids:
            last_ev[rid] = e            # only queued rows feed the queue column
        if _changed(e):
            flipped_by_row[rid] = e     # every full-text review that moved a label
    flipped = sorted(flipped_by_row, key=int)
    capped = sum(1 for r in rows if len(r.get('description', '') or '') >= CSV_DESC_LIMIT)

    lines.append(f"\n## Truncation-validity check (added 2026-09-26)\n")
    lines.append(
        f"`analyze.py` writes the CSV `description` column truncated to {CSV_DESC_LIMIT} "
        f"chars (`CSV_DESC_LIMIT`; lines 176 and 212), while the detector scanned the "
        f"**full** text from `{TOOLS.name}`. The initial labeling pass therefore showed "
        f"the human a {CSV_DESC_LIMIT}-char excerpt, so labels on capped rows rest on "
        f"less evidence than the detector saw — {capped}/{total} sample rows sit exactly "
        f"on the cap.\n")
    lines.append(f"* Cap-affected labeled rows: **{len(affected)} of {labeled_count}** "
                 f"labeled ({len(affected)/max(labeled_count, 1):.0%}).\n"
                 f"* Of these, {len(aff_unclear)} carry a `u` label and are covered by "
                 f"`--review-unclear`: {', '.join(str(i) for i in aff_unclear) or 'none'}.\n"
                 f"* The remaining **{len(aff_reviewable)}** are the `--review-truncated` "
                 f"queue: "
                 f"{', '.join(str(a['row_id']) for a in aff_reviewable) or 'none'}.\n"
                 f"* Re-review is done on full text in `{TOOLS.name}`; every replacement "
                 f"is archived to `{SUPERSEDED.name}` and logged to `{AUDIT.name}`.\n"
                 f"* **Labels flipped after full-text re-review: {len(flipped)}** — "
                 f"{len(last_ev)} of {len(aff_reviewable)} queued rows re-reviewed so far; "
                 f"{len(verdict_rows)} row(s) were decided through `--verdict` (written-up "
                 f"answers to `--review-unclear`, which the queue cannot carry because it "
                 f"excludes `u` rows).\n")
    if flipped:
        lines.append("* Flips: " + ', '.join(
            f"row {rid} `{(flipped_by_row[rid].get('old') or {}).get('label', '?')}` → "
            f"`{(flipped_by_row[rid].get('new') or {}).get('label', '?')}`"
            for rid in flipped) + ".\n")
    if aff_reviewable:
        lines.append("")
        lines.append("| row_id | label now | excerpt | full | hidden | source_file | "
                     "re-reviewed | outcome |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for a in aff_reviewable:
            e = last_ev.get(str(a['row_id']))
            if e is None:
                status, outcome = 'no', 'pending PI pass'
            else:
                old_l = (e.get('old') or {}).get('label', '?')
                new_l = (e.get('new') or {}).get('label', '?')
                status = 'yes'
                outcome = f'FLIPPED {old_l} -> {new_l}' if old_l != new_l \
                    else f'confirmed {new_l}'
            lines.append(f"| {a['row_id']} | `{a['label']}` | {a['excerpt_len']} | "
                         f"{a['full_len']} | +{a['delta']} | `{a['source_file']}` | "
                         f"{status} | {outcome} |")
        lines.append("")

    lines.append(f"\n## FP-reason taxonomy\n")
    lines.append("One entry per FP ROW; the first matching bucket wins "
                 "(marketing/product language → benign legitimate use → bare URL/link → "
                 "no note given → first 60 chars of the note).\n")
    lines.append("| Reason | Count |")
    lines.append("|---|---|")
    for reason, cnt in fp_reasons.most_common():
        lines.append(f"| {reason} | {cnt} |")
    lines.append(f"\n## TP examples by class\n")
    for c in sorted(tp_examples):
        lines.append(f"### `{c}` ({len(tp_examples[c])} examples)\n")
        for e in tp_examples[c]:
            lines.append(f"- `{e['name']}` — note: {e['note']}")
    lines.append(f"\n## Detector status\n")
    lines.append("Detector rules (v2) are **frozen**. Any regex fix proposals derived from")
    lines.append("these FP patterns must be filed as a **separate proposal diff** —")
    lines.append("never auto-applied to `pilot/analyze.py`.\n")

    text = '\n'.join(lines)
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Report written to {REPORT}")
    print(f"Labeled: {labeled_count}/{total} rows | TP:{tp_rows} FP:{fp_rows} "
          f"Unclear:{unclear} FN:{fn} rows | flag instances TP:{sum(tp.values())} "
          f"FP:{sum(fp.values())}")
    print(f"Truncation-validity: {len(affected)}/{labeled_count} labeled rows cap-affected | "
          f"{len(last_ev)}/{len(aff_reviewable)} queued rows re-reviewed on full text | "
          f"{len(flipped)} label(s) flipped after full-text re-review "
          f"({len(verdict_rows)} --verdict record(s), {len(review_ev)} review event(s))")
    for c in all_classes:
        t, f = tp[c], fp[c]
        if t + f:
            print(f"  {c}: precision {t/(t+f):.2f} (TP={t}, FP={f})")


def dry_run(n=2):
    rows = verify_sample()[:n]
    index = load_tool_rows()
    print(f"DRY-RUN: {n} rows. No labels written.")
    for i, row in enumerate(rows):
        display_row(row, i + 1, len(rows), index=index)
        has_fn = i >= 100
        print(f"  [DRY-RUN] would prompt here. Keys: t=tp f=fp u=unclear {'fn ' if has_fn else ''}s=skip q=quit")
    print("\nDRY-RUN complete. Use `python3 label_sample.py` for real labeling.")


def main():
    ap = argparse.ArgumentParser(description="Brief 03 interactive manual labeling CLI.")
    ap.add_argument("--dry-run", type=int, default=0, help="test with N rows, then abort")
    ap.add_argument("--report", action="store_true", help="compute precision, write validation_report.md")
    ap.add_argument("--review-unclear", action="store_true",
                    help="re-review every row labeled u, showing its FULL source description")
    ap.add_argument("--review-truncated", action="store_true",
                    help="re-review labeled rows whose 300-char CSV excerpt hid text")
    ap.add_argument("--no-prompt", action="store_true",
                    help="with --review-unclear/--review-truncated: inventory only, "
                         "write no labels")
    ap.add_argument("--note", nargs=2, metavar=("ROW_ID", "NOTE"), action="append",
                    help="append a note to an existing FP row (label unchanged)")
    ap.add_argument("--set-note", nargs=2, metavar=("ROW_ID", "NOTE"), action="append",
                    help="replace the note on ANY labeled row (label unchanged)")
    ap.add_argument("--verdict", nargs=3, metavar=("ROW_ID", "LABEL", "NOTE"),
                    action="append",
                    help="record a PI verdict (tp/fp/u/fn/skip) and its single-line "
                         "rationale on an already-labeled row; the label MAY change")
    args = ap.parse_args()
    if args.no_prompt and not (args.review_unclear or args.review_truncated):
        ap.error("--no-prompt is only meaningful together with --review-unclear "
                 "or --review-truncated")
    if args.review_unclear:
        review_unclear(no_prompt=args.no_prompt)
    elif args.review_truncated:
        review_truncated(no_prompt=args.no_prompt)
    elif args.verdict:
        flips = 0
        for rid, label, note in args.verdict:
            flips += set_verdict(int(rid), label.strip().lower(), note)
        print(f"\nDONE. {len(args.verdict)} verdict(s) recorded, {flips} label(s) flipped.")
    elif args.note:
        for rid, note in args.note:
            set_note(int(rid), note, require_fp=True)
    elif args.set_note:
        for rid, note in args.set_note:
            set_note(int(rid), note, require_fp=False)
    elif args.report:
        report()
    elif args.dry_run:
        dry_run(args.dry_run)
    else:
        interactive()


if __name__ == "__main__":
    main()
