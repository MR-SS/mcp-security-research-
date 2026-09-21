#!/usr/bin/env python3
"""Static heuristic analysis of MCP server metadata -> data/analysis.csv + summary stats.

IMPORTANT (methodology): detectors produce CANDIDATES, not verdicts.
Report validated precision from the manual sample; phrase findings as
"patterns consistent with X", never "X% of servers are malicious".

Rule versions:
  v1 (frozen) — CAPABILITY_PATTERNS + POISON_PATTERNS, recoverable at git commit 6cca247.
                The suspicion_score definition stays v1 (caps + 3*poisons) so the triage
                queue remains comparable across runs.
  v2 (current) — adds ADDRESSING_PATTERNS ("model_addressed": is the description addressed
                to an agent/model at all?). This is an instruction-channel measurement,
                reported SEPARATELY from poisoning classes and NOT summed into any
                poisoning statistic or into suspicion_score.
"""
import argparse, base64, csv, hashlib, json, os, re, subprocess, sys
from urllib.parse import urlparse

# ---------- 1. Dangerous capability surface (ASI02/ASI05 relevance) ----------
CAPABILITY_PATTERNS = {
    "shell_execution":    [r"\bexec(ute)?\b", r"\bshell\b", r"\bsubprocess\b", r"\bterminal\b",
                           r"\brun (a |any )?(command|script|code)\b", r"\bbash\b", r"\bcmd\b"],
    "file_write_delete":  [r"\bwrite(s|ing)?\b.{0,30}\bfiles?\b", r"\bdelete(s|ing)?\b.{0,30}\bfiles?\b",
                           r"\bremove(s|ing)?\b.{0,30}\bfiles?\b", r"\bmodify\b.{0,20}\bfiles?\b",
                           r"\boverwrite\b"],
    "file_read_sensitive":[r"\bread(s|ing)?\b.{0,30}\b(files?|disk)\b", r"\bfilesystem\b", r"\bglob\b"],
    "secret_env_access":  [r"\benv(ironment)? variables?\b", r"\btokens?\b", r"\bapi[- ]?keys?\b",
                           r"\bsecrets?\b", r"\bcredentials?\b"],
    "network_egress":     [r"\bfetch\b", r"\bhttp requests?\b", r"\bwebhook\b", r"\bposts? data\b",
                           r"\bscrap(e|ing)\b", r"\bdownload\b", r"\bupload\b"],
    "database_write":     [r"\bsql\b", r"\bquery\b.{0,30}\bdatabase\b", r"\binsert\b", r"\bupdate\b.{0,20}\brows?\b"],
    "package_install":    [r"\binstall(s|ing)?\b.{0,30}\b(packages?|dependencies)\b", r"\bpip\b", r"\bnpm install\b"],
}

# ---------- 2. Tool-description poisoning patterns (ASI04 relevance) ----------
POISON_PATTERNS = {
    "imperative_to_model":   [r"\byou (must|shall|should|need to|have to)\b", r"\balways\b",
                              r"\bnever\b", r"\bdo not\b", r"\bit is (critical|important|required)\b",
                              r"\bmandatory\b"],
    "stealth_concealment":   [r"\bdo not (tell|mention|inform|reveal|disclose)\b",
                              r"\bwithout (the )?us?er'?s? (knowledge|consent|awareness)\b",
                              r"\binvisib(le|ility)\b", r"\bsilently\b", r"\bhidden\b"],
    "important_tags":        [r"<IMPORTANT>", r"<important>", r"^IMPORTANT:", r"<SYSTEM>",
                              r"\[INST\]", r"<<SYS>>"],
    "cross_tool_shadowing":  [r"\b(before|after|when|whenever) (using|calling|invoking) (the|any|other)\b",
                              r"\bother tools?\b", r"\bany tool\b"],
    "exfiltration_language": [r"\b(send|post|transmit|forward|exfiltrate|report)\b.{0,50}\b(to|http|url|endpoint|webhook|server)\b",
                              r"\bcc\b.{0,30}@", r"https?://\S+"],
    "sensitive_file_target": [r"~/\.ssh", r"id_rsa", r"\.env\b", r"\.aws/credentials", r"\.kube",
                              r"\bknown_hosts\b", r"/etc/passwd", r"\.npmrc", r"\.pypirc"],
    "fake_system_role":      [r"\bsystem prompt\b", r"\bassistant[,:]", r"\bignore (previous|all|prior)\b",
                              r"\bnew instructions?\b"],
}

# ---------- 3. Instruction-channel measurement (v2) — NOT a poisoning verdict ----------
# Answers "is this description *addressed to* an agent/model at all?", i.e. is the
# instruction channel in use. Benign servers trip it constantly ("For AI agents",
# "your agent never sees the plaintext"), so it must never be reported as malice and
# never summed with poison counts. Known over-trigger to watch in validation:
# LLM-serving servers describe themselves in model vocabulary ("run any AI model"),
# which matches the audience rule although no agent is being addressed.
RULES_VERSION = "v2"

ADDRESSING_PATTERNS = {
    "agent_audience": [
        r"\b(a|an|any|the|your|our|other|every)\s+(ai\s+)?(agent|assistant|model|llm|bot)s?\b",
        r"\bfor\s+(ai\s+)?(agents?|assistants?|models?|llms?|bots?)\b",
        r"\bai\s+(agents?|assistants?|models?|coders?|clients?)\b",
        r"\bagentic\b",
    ],
}

# Used ONLY in the compound rule in scan_text(): a bare imperative ("never", "always")
# is not instruction-channel evidence unless the text also addresses a reader.
IMPERATIVE_PATTERNS = [
    r"\byou (must|shall|should|need to|have to)\b", r"\balways\b", r"\bnever\b",
    r"\bdo not\b", r"\bmust not\b",
]

ZERO_WIDTH = "".join(["​", "‌", "‍", "⁠", "﻿"])
B64_RE = re.compile(r"\b[A-Za-z0-9+/]{40,}={0,2}\b")  # long base64-ish blob


def b64_decodes_to_text(blob):
    try:
        decoded = base64.b64decode(blob, validate=True)
        return sum(32 <= b < 127 or b in (9, 10, 13) for b in decoded) / max(len(decoded), 1) > 0.85
    except Exception:
        return False


def scan_text(text):
    """Return {class: [matched_regex,...]} for one text blob."""
    hits = {}
    for group, table in (("capability", CAPABILITY_PATTERNS), ("poison", POISON_PATTERNS),
                         ("addressing", ADDRESSING_PATTERNS)):
        for cls, patterns in table.items():
            for p in patterns:
                if re.search(p, text, re.IGNORECASE | re.MULTILINE):
                    hits.setdefault(f"{group}:{cls}", []).append(p)
    # v2 compound rule: a behavioural imperative counts as instruction-channel use only when
    # the text also addresses a reader ("you"/"your"). Bare "never"/"always" in human-facing
    # marketing prose ("never a safety score") stays unflagged by design.
    if re.search(r"\byou(r)?\b", text, re.IGNORECASE) and any(
            re.search(p, text, re.IGNORECASE | re.MULTILINE) for p in IMPERATIVE_PATTERNS):
        hits.setdefault("addressing:second_person_imperative", []).append("you(r) + imperative")
    if any(ch in text for ch in ZERO_WIDTH):
        hits.setdefault("poison:zero_width_chars", []).append("zero-width unicode present")
    for blob in B64_RE.findall(text):
        if b64_decodes_to_text(blob):
            hits.setdefault("poison:base64_blob", []).append(blob[:24] + "...")
            break
    return hits


def github_slug(url):
    if not url or "github.com" not in url:
        return None
    parts = urlparse(url).path.strip("/").split("/")
    return "/".join(parts[:2]) if len(parts) >= 2 else None


def git_stamp():
    """Short SHA (+'-dirty') or an honest 'unavailable' marker — AGENTS.md §2.6."""
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=here,
                             capture_output=True, text=True, timeout=10)
        if sha.returncode != 0:
            return "unavailable (not a git repository)"
        dirty = subprocess.run(["git", "status", "--porcelain"], cwd=here,
                               capture_output=True, text=True, timeout=10)
        return sha.stdout.strip() + ("-dirty" if dirty.stdout.strip() else "")
    except (OSError, subprocess.SubprocessError):
        return "unavailable (git not runnable)"


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inp", default="../data/servers.jsonl")
    ap.add_argument("--out", default="../data/analysis.csv")
    args = ap.parse_args()

    servers = [json.loads(l) for l in open(args.inp, encoding="utf-8") if l.strip()]
    rows, any_cap, any_poison, any_addr, gh = [], 0, 0, 0, 0
    for s in servers:
        text = "\n".join(filter(None, [s.get("title"), s.get("description")]))
        hits = scan_text(text)
        caps = sorted(h for h in hits if h.startswith("capability:"))
        pois = sorted(h for h in hits if h.startswith("poison:"))
        addrs = sorted(h for h in hits if h.startswith("addressing:"))
        rows.append({
            "name": s["name"], "version": s["version"],
            "repo": s.get("repository_url") or "",
            "github": github_slug(s.get("repository_url")) or "",
            "n_capability_flags": len(caps), "capability_flags": ";".join(caps),
            "n_poison_flags": len(pois), "poison_flags": ";".join(pois),
            # v2 instruction-channel fields — kept out of suspicion_score (v1 definition)
            # so the triage queue stays comparable with v1 output.
            "n_addressing_flags": len(addrs), "addressing_flags": ";".join(addrs),
            "suspicion_score": len(caps) + 3 * len(pois),  # triage only, not a finding
            "rules_version": RULES_VERSION,
            "description": (s.get("description") or "").replace("\n", " ")[:300],
        })
        any_cap += bool(caps); any_poison += bool(pois); any_addr += bool(addrs)
        gh += bool(rows[-1]["github"])

    rows.sort(key=lambda r: -r["suspicion_score"])
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    # Provenance on stderr only, so the CSV itself stays byte-stable across re-runs.
    print(f"[repro] inp={os.path.abspath(args.inp)} sha256={file_sha256(args.inp)} "
          f"| out={os.path.abspath(args.out)} sha256={file_sha256(args.out)} "
          f"| git={git_stamp()}", file=sys.stderr)

    n = len(servers)
    print(f"\n=== Summary over {n} servers ===   [rules {RULES_VERSION}; v1 rules frozen at commit 6cca247]")
    print(f"servers with >=1 dangerous-capability pattern : {any_cap:4d} ({100*any_cap/n:.1f}%)")
    print(f"servers with >=1 poisoning-pattern flag       : {any_poison:4d} ({100*any_poison/n:.1f}%)")
    print(f"servers linked to GitHub repos                : {gh:4d} ({100*gh/n:.1f}%)")
    print("\nCapability class prevalence:")
    cap_counts, poi_counts, addr_counts = {}, {}, {}
    for r in rows:
        for c in r["capability_flags"].split(";"):
            if c: cap_counts[c.split(":")[1]] = cap_counts.get(c.split(":")[1], 0) + 1
        for p in r["poison_flags"].split(";"):
            if p: poi_counts[p.split(":")[1]] = poi_counts.get(p.split(":")[1], 0) + 1
        for a in r["addressing_flags"].split(";"):
            if a: addr_counts[a.split(":")[1]] = addr_counts.get(a.split(":")[1], 0) + 1
    for k, v in sorted(cap_counts.items(), key=lambda x: -x[1]):
        print(f"  {k:22s} {v:4d} ({100*v/n:.1f}%)")
    print("\nPoisoning-pattern prevalence (CANDIDATES — validate manually!):")
    for k, v in sorted(poi_counts.items(), key=lambda x: -x[1]):
        print(f"  {k:22s} {v:4d} ({100*v/n:.1f}%)")
    print("\nInstruction-channel measurement (v2 — NOT a poisoning verdict, reported separately):")
    print(f"servers describing themselves as addressed to an agent/model : {any_addr:4d} ({100*any_addr/n:.1f}%)")
    for k, v in sorted(addr_counts.items(), key=lambda x: -x[1]):
        print(f"  {k:22s} {v:4d} ({100*v/n:.1f}%)")
    print("  (measures whether the instruction channel is in use, independently of intent)")
    print(f"\nTop suspicious triage queue written to {args.out} (rows sorted by suspicion_score)")
    print("Next steps: (1) manually label top-100 rows for precision; (2) fetch READMEs/tools from GitHub; (3) 90-day disclosure before any public case study.")


if __name__ == "__main__":
    main()
