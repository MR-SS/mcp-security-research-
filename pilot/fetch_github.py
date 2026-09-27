#!/usr/bin/env python3
"""Brief 02 — GitHub enrichment: repo trees + raw file reads -> tool descriptions.

Reads GITHUB_TOKEN from the environment ONLY (never printed, logged, written,
or embedded in any artifact — AGENTS.md rule 8). GitHub REST API (<=1 req/s,
rate-limit headers logged) is used ONLY for repo tree listings (+ default-branch
fallback); file CONTENT comes from raw.githubusercontent.com (no API quota).
Checkpoints every 500 repos; resumable; pauses cleanly if quota < 500 remaining.

Population (PI amendment): full run over GitHub-linked repos EXCEPT registry-name
namespaces with >50 GitHub-linked servers, capped at 25 repos each (uniform
sample, seed 42, flagged stratified=true). Full-population and namespace-adjusted
stats are reported SEPARATELY downstream — mass-publishers must not dominate.
"""
import argparse
import collections
import json
import os
import random
import re
import sys
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests

API = "https://api.github.com"
RAW = "https://raw.githubusercontent.com"
BIG_NS_THRESHOLD = 50
BIG_NS_SAMPLE = 25
SEED = 42
MAX_TOOLS_PER_REPO = 20
MAX_SOURCE_FILES = 10
MAX_FILE_BYTES = 2_000_000
SOURCE_EXTS = (".py", ".ts", ".js", ".tsx", ".jsx", ".mjs", ".cjs",
               ".go", ".rs", ".java", ".rb")
PAUSE_BELOW_REMAINING = 500


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def github_slug(url):
    if not url or "github.com" not in url:
        return None
    parts = urlparse(url).path.strip("/").split("/")
    return "/".join(parts[:2]) if len(parts) >= 2 else None


def build_population(servers_path):
    """Return (run_list, stats) where run_list = [(server, repo, stratified)]."""
    servers = [json.loads(l) for l in open(servers_path, encoding="utf-8")
               if l.strip()]
    repo_servers = collections.defaultdict(list)
    for s in servers:
        g = github_slug(s.get("repository_url"))
        if g:
            repo_servers[g].append(s["name"])
    ns_servers = collections.Counter()
    ns_repos = collections.defaultdict(set)
    for repo, members in repo_servers.items():
        for m in members:
            ns = m.split("/")[0]
            ns_servers[ns] += 1
            ns_repos[ns].add(repo)
    big = sorted(ns for ns, c in ns_servers.items() if c > BIG_NS_THRESHOLD)
    rng = random.Random(SEED)
    run, big_repos = [], {}
    for ns in sorted(ns_repos):
        repos = sorted(ns_repos[ns])
        if ns in big:
            repos = sorted(rng.sample(repos, min(BIG_NS_SAMPLE, len(repos))))
            big_repos[ns] = repos
        for repo in repos:
            run.append({"server": sorted(repo_servers[repo])[0],
                        "servers": sorted(repo_servers[repo]),
                        "repo": repo, "stratified": ns in big,
                        "namespace": ns})
    stats = {"github_linked_servers": sum(len(v) for v in repo_servers.values()),
             "distinct_repos": len(repo_servers),
             "big_namespaces": {ns: {"servers": ns_servers[ns],
                                     "repos_total": len(ns_repos[ns]),
                                     "repos_sampled": len(big_repos[ns])}
                                for ns in big},
             "run_repos": len(run)}
    return run, stats

API_CALLS = 0
_LAST_API_TS = 0.0


class QuotaPause(Exception):
    pass


def _pace_api():
    """Enforce <=1 REST req/s: sleep only the gap since the last API call."""
    global _LAST_API_TS
    now = time.monotonic()
    gap = now - _LAST_API_TS
    if gap < 1.0:
        time.sleep(1.0 - gap)
    _LAST_API_TS = time.monotonic()


def api_get(session, path, token_present):
    """GET a GitHub REST path. Logs rate-limit headers. Raises QuotaPause."""
    global API_CALLS
    url = API + path
    for attempt in range(4):
        _pace_api()  # the ONLY pacing sleep: <=1 REST req/s, no dead time
        r = session.get(url, timeout=30)
        API_CALLS += 1
        rem = r.headers.get("X-RateLimit-Remaining", "?")
        lim = r.headers.get("X-RateLimit-Limit", "?")
        print(f"  [api] {path} -> {r.status_code} "
              f"(limit={lim} remaining={rem})", file=sys.stderr)
        try:
            remaining = int(rem)
        except (TypeError, ValueError):
            remaining = None
        if remaining is not None and remaining < PAUSE_BELOW_REMAINING:
            reset = r.headers.get("X-RateLimit-Reset", "?")
            raise QuotaPause(
                f"quota remaining={remaining} < {PAUSE_BELOW_REMAINING} "
                f"(reset epoch {reset}); pausing cleanly")
        if r.status_code == 200:
            return r.json()
        if r.status_code in (403, 429) and attempt < 3:
            time.sleep(min(2 ** (attempt + 2), 30))
            continue
        if r.status_code == 404:
            return None
        r.raise_for_status()
    raise RuntimeError(f"API GET failed after retries: {path}")


def raw_get(session, repo, branch, path):
    """Fetch file content via raw.githubusercontent.com (no API quota)."""
    url = f"{RAW}/{repo}/{branch}/{path}"
    r = session.get(url, timeout=30)
    if r.status_code == 200:
        return r.text
    return None


def repo_default_branch(session, repo, token_present):
    meta = api_get(session, f"/repos/{repo}", token_present)
    if meta:
        return meta.get("default_branch", "main")
    return None


def repo_tree(session, repo, branch, token_present):
    tree = api_get(session, f"/repos/{repo}/git/trees/{branch}?recursive=1",
                   token_present)
    if not tree or tree.get("truncated"):
        if tree and tree.get("truncated"):
            print(f"  [warn] tree truncated for {repo}", file=sys.stderr)
        if not tree:
            return None
    return [t["path"] for t in tree.get("tree", [])
            if t.get("type") == "blob"]


def pick_files(paths):
    """README + manifests first, then the most tool-plausible source files."""
    by_lower = {p.lower(): p for p in paths}
    picks, seen = [], set()

    def take(p):
        if p and p not in seen:
            seen.add(p)
            picks.append(p)

    for cand in ("readme.md", "readme", "readme.markdown", "readme.rst",
                 "package.json", "pyproject.toml", "server.json",
                 "lhm.plugin.json"):
        take(by_lower.get(cand))
        for p in paths:
            if p.lower().endswith("/" + cand) and len(picks) < 6:
                take(p)
    scored = []
    for p in paths:
        if p in seen:
            continue
        pl = p.lower()
        if pl.endswith(SOURCE_EXTS):
            if "/test" in pl or "/node_modules/" in p:
                continue
        elif pl.rsplit("/", 1)[-1] in ("server.json", "server.yaml",
                                       "server.yml", "mcp.json", ".mcp.json",
                                       "manifest.json", "lhm.plugin.json"):
            pass  # registry manifests: tool surface for hosted servers
        else:
            continue
        low = p.lower()
        score = (3 if "tool" in low else 0) + (2 if "server" in low else 0) \
            + (1 if "mcp" in low else 0)
        scored.append((score, len(p), p))
    scored.sort(key=lambda t: (-t[0], t[1]))
    for _, _, p in scored:
        if len(picks) >= MAX_SOURCE_FILES:
            break
        take(p)
    return picks

# ---------- extraction ----------
TOOL_DECORATOR = re.compile(
    r'@(?:mcp\.)?tool\s*\(\s*(?:["\']([^"\']+)["\']\s*,\s*)?'
    r'(?:description\s*=\s*["\']([^"\']+)["\'])?',
    re.IGNORECASE)
FUNC_TOOL = re.compile(
    r'(?:server\.tool|app\.tool|mcp\.tool)\s*\(\s*["\']([^"\']+)["\']',
    re.IGNORECASE)
LISTTOOLS_NAME = re.compile(
    r'["\']name["\']\s*:\s*["\']([A-Za-z0-9_\-]{2,64})["\']',
    re.IGNORECASE)
LISTTOOLS_DESC = re.compile(
    r'["\']description["\']\s*:\s*["\']([^"\']{10,2000})["\']',
    re.IGNORECASE | re.DOTALL)
GENERIC_DESC = re.compile(
    r'description\s*[=:]\s*["\']([^"\']{10,2000})["\']',
    re.IGNORECASE | re.DOTALL)


def clip(text, limit=2000):
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:limit]


def extract_tools(filename, text):
    """Return [(tool_name, description, confidence)] capped per repo later.

    Priority order (brief amendment 3): README prose -> package manifests ->
    tool-registration blocks. Manifests capture the server.json-registered tool
    surface (common in hosted/remote servers with no in-repo tool code);
    registration blocks cover @mcp.tool / server.tool( / FastMCP /
    ListToolsResult plus Rust fn description() and JS Tool objects.
    """
    found = []
    low = filename.lower()
    base = low.rsplit("/", 1)[-1]
    if base in ("readme.md", "readme", "readme.markdown", "readme.rst"):
        for m in LISTTOOLS_DESC.finditer(text):
            found.append(("readme:unnamed", clip(m.group(1)), "low"))
        return found
    if base in ("server.json", "server.yaml", "server.yml", "mcp.json",
                ".mcp.json", "manifest.json", "lhm.plugin.json",
                "package.json", "pyproject.toml"):
        name_m = re.search(
            r'["\']name["\']\s*[:=]\s*["\']([^"\']{2,128})["\']', text)
        desc_m = re.search(
            r'["\']description["\']\s*[:=]\s*["\']([^"\']{10,2000})["\']',
            text, re.DOTALL)
        sname = (name_m.group(1) if name_m else "manifest:unnamed")
        if desc_m:
            found.append(("manifest:" + sname, clip(desc_m.group(1)), "low"))
        return found
    for m in TOOL_DECORATOR.finditer(text):
        name, desc = m.group(1), m.group(2)
        if desc:
            found.append((name or "decorator:unnamed", clip(desc), "high"))
        elif name:
            window = text[m.end():m.end() + 1500]
            d = re.search(r'description\s*=\s*["\']([^"\']{10,2000})["\']',
                          window, re.IGNORECASE | re.DOTALL)
            if d:
                found.append((name, clip(d.group(1)), "medium"))
    for m in FUNC_TOOL.finditer(text):
        window = text[m.end():m.end() + 1500]
        d = re.search(r'description\s*[:=]\s*["\']([^"\']{10,2000})["\']',
                      window, re.IGNORECASE | re.DOTALL)
        if d:
            found.append((m.group(1), clip(d.group(1)), "medium"))
    if "ListToolsResult" in text or "list_tools" in text:
        names = LISTTOOLS_NAME.findall(text)
        descs = LISTTOOLS_DESC.findall(text)
        for i, d in enumerate(descs[:8]):
            n = names[i] if i < len(names) else "listtools:unnamed"
            found.append((n, clip(d), "medium"))
    # Rust: fn name()/fn description() pairs (e.g. Tandem operator_tools.rs)
    rust_names = re.findall(
        r'fn\s+name\s*\(\s*self\s*\)[^{]*\{[^}]{0,600}?["\']([a-z_][a-z0-9_]{2,64})["\']',
        text)
    rust_descs = re.findall(
        r'fn\s+description\s*\(\s*self\s*\)[^{]*\{[^}]{0,2000}?["\']([^"\']{10,2000})["\']',
        text, re.DOTALL)
    if rust_descs:
        for i, d in enumerate(rust_descs[:8]):
            n = rust_names[i] if i < len(rust_names) else "rust:unnamed"
            found.append((n, clip(d), "medium"))
    # JS/TS Tool objects: { name: 'x', ..., description: '...' }
    if not found:
        for m in re.finditer(
                r'name\s*:\s*["\']([A-Za-z0-9_\-]{2,64})["\']'
                r'[^}]{0,800}?description\s*:\s*["\']([^"\']{10,2000})["\']',
                text, re.DOTALL):
            w = text[max(0, m.start() - 200):m.start()].lower()
            if "tool" in w or "mcp" in w:
                found.append((m.group(1), clip(m.group(2)), "medium"))
                if len(found) >= 6:
                    break
    if not found:
        for m in GENERIC_DESC.finditer(text):
            window_before = text[max(0, m.start() - 400):m.start()].lower()
            if "tool" in window_before:
                found.append(("generic:unnamed", clip(m.group(1)), "low"))
                if len(found) >= 4:
                    break
    return found


def load_checkpoint(path):
    done, rows = set(), []
    if path and os.path.exists(path):
        for l in open(path, encoding="utf-8"):
            if l.strip():
                try:
                    r = json.loads(l)
                    done.add(r["repo"])
                    rows.append(r)
                except (json.JSONDecodeError, KeyError):
                    continue
    return done, rows


TOKEN_SHAPES = [
    re.compile(r'ghp_[A-Za-z0-9]{20,}'),
    re.compile(r'github_pat_[A-Za-z0-9_]{20,}'),
    re.compile(r'gho_[A-Za-z0-9]{20,}'),
    re.compile(r'sk-(live|test)-[A-Za-z0-9]{10,}'),
    re.compile(r'AKIA[0-9A-Z]{16}'),
    re.compile(r'xox[baprs]-[A-Za-z0-9-]{10,}'),
]


def token_hygiene_fail(rows):
    """Stop-and-report gate: any token-shaped string in artifacts."""
    for r in rows:
        blob = json.dumps(r)
        for pat in TOKEN_SHAPES:
            m = pat.search(blob)
            if m:
                # pre-cleared documentation prose (collection_report scan):
                if m.group(0).startswith("xoxb-") and "starting with xoxb-" in blob:
                    continue
                return r["repo"], m.group(0)[:12] + "..."
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--servers", default="../data/servers.jsonl")
    ap.add_argument("--out", default="../data/github_tools.jsonl")
    ap.add_argument("--meta", default=None)  # defaults to <out>.meta.json
    ap.add_argument("--max-repos", type=int, default=None)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--visited", default=None)  # defaults to <out>.visited.jsonl
    args = ap.parse_args()
    meta_path = args.meta or (args.out + ".meta.json")
    visited_path = args.visited or (args.out + ".visited.jsonl")

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN is not set. Export a public-read-only, short-lived "
              "fine-grained PAT in this shell, e.g.\n"
              "  export GITHUB_TOKEN=<paste-token-here>\n"
              "The script reads it from the environment at runtime only and never "
              "prints, logs, writes, or commits it.", file=sys.stderr)
        sys.exit(2)
    token_present = True

    run, pop_stats = build_population(args.servers)
    if args.max_repos:
        run = run[:args.max_repos]
    done, rows = load_checkpoint(args.out if args.resume else None)
    # Visited log: repos fully processed (incl. tool-less/404) so resume
    # never re-spends API quota on them. Seeded from this run's meta on
    # first resumed invocation.
    visited = set()
    if args.resume and os.path.exists(visited_path):
        visited = {l.strip() for l in open(visited_path, encoding="utf-8")
                   if l.strip()}
    visited_f = open(visited_path, "a" if args.resume else "w",
                     encoding="utf-8")
    todo = [r for r in run if r["repo"] not in done and r["repo"] not in visited]
    print(f"population: {pop_stats['distinct_repos']} repos; "
          f"run list: {len(run)}; resume-skipped: {len(done)}; "
          f"todo: {len(todo)}", file=sys.stderr)

    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {token}",
                            "Accept": "application/vnd.github+json",
                            "User-Agent": "mcp-security-research-brief02"})
    token = None  # drop from local scope once the header is set
    raw_session = requests.Session()
    raw_session.headers.update(
        {"User-Agent": "mcp-security-research-brief02"})

    started = utcnow()
    api_before = API_CALLS
    repos_ok = repos_tools = 0
    tools_total = 0
    failures = collections.Counter()
    paused = None
    t0 = time.time()
    out_f = open(args.out, "a" if args.resume else "w", encoding="utf-8")
    try:
        for i, item in enumerate(todo):
            repo = item["repo"]
            try:
                branch = repo_default_branch(session, repo, token_present)
                if not branch:
                    failures["repo-not-found"] += 1
                    visited.add(repo)  # deterministic: no retry value
                    visited_f.write(repo + "\n")
                    visited_f.flush()
                    continue
                paths = repo_tree(session, repo, branch, token_present)
                if not paths:
                    failures["empty-tree"] += 1
                    visited.add(repo)  # deterministic: no retry value
                    visited_f.write(repo + "\n")
                    visited_f.flush()
                    continue
                files = pick_files(paths)
                tools = []
                for f in files:
                    if len(tools) >= MAX_TOOLS_PER_REPO:
                        break
                    text = raw_get(raw_session, repo, branch, f)
                    if not text or len(text) > MAX_FILE_BYTES:
                        continue
                    for name, desc, conf in extract_tools(f, text):
                        if len(tools) >= MAX_TOOLS_PER_REPO:
                            break
                        tools.append({"server_name": item["server"],
                                      "servers": item["servers"],
                                      "repo": repo, "namespace": item["namespace"],
                                      "stratified": item["stratified"],
                                      "tool_name": name, "tool_description": desc,
                                      "source_file": f, "branch": branch,
                                      "extraction_confidence": conf})
                repos_ok += 1
                if tools:
                    repos_tools += 1
                    tools_total += len(tools)
                    for t in tools:
                        out_f.write(json.dumps(t) + "\n")
                    out_f.flush()
                else:
                    failures["no-tools-found"] += 1
                visited.add(repo)
                visited_f.write(repo + "\n")
                visited_f.flush()
            except QuotaPause as e:
                paused = str(e)
                print(f"PAUSED: {e}", file=sys.stderr)
                break
            except requests.RequestException as e:
                failures[f"http:{type(e).__name__}"] += 1
                if isinstance(e, requests.exceptions.ProxyError):
                    # Transient: NOT marked visited -> retried next resume.
                    visited_f.flush()
                    continue
            processed = len(done) + len(visited) + (i + 1)
            if processed % 500 == 0:
                out_f.flush()
                visited_f.flush()
                hit = token_hygiene_fail(rows)
                if hit:
                    print(f"TOKEN-HYGIENE STOP: token-shaped string in rows "
                          f"from {hit[0]}; refusing to write further. "
                          f"Inspect before resuming.", file=sys.stderr)
                    sys.exit(3)
                print(f"[checkpoint] {processed} repos, {tools_total} tools, "
                      f"api_calls={API_CALLS}", file=sys.stderr)
            # NOTE: no sleep here — pacing lives in _pace_api() (API calls
            # only); raw reads and failures cost zero waiting time.
    finally:
        out_f.close()
        visited_f.close()
    hit = token_hygiene_fail(rows)
    if hit:
        print(f"TOKEN-HYGIENE STOP after run: suspect string in {hit[0]}. "
              f"Inspect before committing.", file=sys.stderr)
        sys.exit(3)
    meta = {"started_utc": started, "finished_utc": utcnow(),
            "wall_seconds": round(time.time() - t0, 1),
            "population": pop_stats, "todo": len(todo),
            "repos_reached": repos_ok, "repos_with_tools": repos_tools,
            "tools_total": tools_total,
            "failures": dict(failures), "paused": paused,
            "visited_repos": len(visited),
            "api_calls_this_run": API_CALLS - api_before,
            "spend_usd": 0.0,
            "git": None, "seed": SEED,
            "big_ns_threshold": BIG_NS_THRESHOLD,
            "big_ns_sample": BIG_NS_SAMPLE,
            "max_tools_per_repo": MAX_TOOLS_PER_REPO}
    json.dump(meta, open(meta_path, "w", encoding="utf-8"), indent=1)
    print(f"done: reached={repos_ok} with_tools={repos_tools} "
          f"tools={tools_total} api_calls={API_CALLS - api_before} "
          f"paused={bool(paused)}", file=sys.stderr)


if __name__ == "__main__":
    main()
