#!/usr/bin/env python3
"""Crawl the official MCP Registry into data/servers.jsonl.

API verified 2026-09-21: GET https://registry.modelcontextprotocol.io/v0/servers
  - params: limit (max entries/page; 100 accepted), cursor (from metadata.nextCursor)
  - entries are PER-VERSION: we dedupe by server name, keeping isLatest=true.
  - response shape: {"servers": [{"server": {...}, "_meta": {...}}],
                     "metadata": {"nextCursor": "<name>:<version>", "count": <n>}}

Reproducibility (AGENTS.md §2.6): every raw API page is written VERBATIM to
<raw-dir>/<UTC timestamp>/page-NNN.json before normalization, followed by a
crawl_meta.json provenance record (timestamp, git stamp, counts, output sha256).
Re-running analyze.py over that frozen snapshot reproduces identical counts;
re-running this crawl does NOT (the live registry mutates between runs).

Usage:
  python3 crawl_registry.py --max-pages 60 --probe-pages 1 \
      --out ../data/servers.jsonl --raw-dir ../data/raw/registry
"""
import argparse, hashlib, json, os, subprocess, sys, time
from datetime import datetime, timezone
import requests

BASE = "https://registry.modelcontextprotocol.io/v0/servers"
OFFICIAL_META = "io.modelcontextprotocol.registry/official"


def fetch_page(cursor=None, limit=100, retries=5):
    """One registry page -> (parsed_json, verbatim_response_text).

    Retries cover transient proxy/network faults (observed: a sandbox ProxyError that
    killed a 600-page run at page 273 when the budget was only 3 attempts).
    """
    params = {"limit": limit}
    if cursor:
        params["cursor"] = cursor
    for attempt in range(retries):
        try:
            r = requests.get(BASE, params=params, timeout=30)
            r.raise_for_status()
            return r.json(), r.text
        except (requests.RequestException, json.JSONDecodeError) as e:
            if attempt == retries - 1:
                raise
            wait = min(2 ** (attempt + 1), 30)
            print(f"  retry {attempt + 1}/{retries - 1} in {wait}s ({type(e).__name__})", file=sys.stderr)
            time.sleep(wait)


def utc_stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


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


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize(entry):
    sv = entry.get("server", {}) or {}
    meta = (entry.get("_meta", {}) or {}).get(OFFICIAL_META, {}) or {}
    repo = sv.get("repository") or {}
    return {
        "name": sv.get("name"),
        "title": sv.get("title"),
        "version": sv.get("version"),
        "description": sv.get("description") or "",
        "repository_url": repo.get("url"),
        "packages": [p.get("identifier") for p in sv.get("packages", []) if p.get("identifier")],
        "remotes": [r.get("url") for r in sv.get("remotes", []) if r.get("url")],
        "transport_types": [r.get("type") for r in sv.get("remotes", []) if r.get("type")],
        "is_latest": bool(meta.get("isLatest")),
        "status": meta.get("status"),
        "published_at": meta.get("publishedAt"),
        "updated_at": meta.get("updatedAt"),
    }


def crawl(max_pages=50, sleep=0.4, raw_dir=None, limit=100, probe_pages=0, retries=5,
          checkpoint=None, checkpoint_every=50):
    """Page through the registry; returns (records, meta).

    `meta` carries every provenance/scaling number the collection report needs.
    Raw pages are dumped verbatim BEFORE normalization (AGENTS.md §2.6).
    `probe_pages` fetches extra pages that are deliberately NOT normalized, to
    establish whether the cursor was actually exhausted at the page cap.
    """
    records, cursor, pages = {}, None, 0
    entries_seen = 0
    replaced_by_newer, dropped_non_latest = 0, 0
    statuses, anomalies = {}, []
    exhausted = False

    while pages < max_pages:
        data, raw_text = fetch_page(cursor, limit=limit, retries=retries)
        if raw_dir:
            with open(os.path.join(raw_dir, f"page-{pages + 1:03d}.json"), "w", encoding="utf-8") as f:
                f.write(raw_text)
        entries = data.get("servers", []) or []
        if not entries:
            exhausted = True
            break
        entries_seen += len(entries)
        for entry in entries:
            rec = normalize(entry)
            if not rec["name"]:
                anomalies.append(f"page {pages + 1}: entry without server.name")
                continue
            statuses[rec["status"]] = statuses.get(rec["status"], 0) + 1
            prev = records.get(rec["name"])
            # prefer isLatest=true; otherwise keep the lexicographically newest version
            if prev is None:
                records[rec["name"]] = rec
            elif rec["is_latest"] and not prev["is_latest"]:
                records[rec["name"]] = rec
                replaced_by_newer += 1
            elif rec["is_latest"] == prev["is_latest"] and (rec["version"] or "") > (prev["version"] or ""):
                records[rec["name"]] = rec
                replaced_by_newer += 1
            else:
                dropped_non_latest += 1
        pages += 1
        cursor = (data.get("metadata") or {}).get("nextCursor")
        print(f"page {pages}: {len(entries)} entries, {len(records)} unique servers so far", file=sys.stderr)
        if checkpoint and checkpoint_every and pages % checkpoint_every == 0:
            checkpoint(list(records.values()), pages)
            print(f"  [checkpoint] {len(records)} servers written after page {pages}", file=sys.stderr)
        if not cursor:
            exhausted = True
            break
        time.sleep(sleep)

    probe = {"requested": probe_pages, "pages_fetched": 0, "entries_seen": 0}
    for i in range(probe_pages):
        if exhausted or not cursor:
            break
        data, raw_text = fetch_page(cursor, limit=limit, retries=retries)
        if raw_dir:
            with open(os.path.join(raw_dir, f"probe-{i + 1:03d}.json"), "w", encoding="utf-8") as f:
                f.write(raw_text)
        entries = data.get("servers", []) or []
        probe["pages_fetched"] += 1
        probe["entries_seen"] += len(entries)
        print(f"exhaustion probe {i + 1}: {len(entries)} entries (not normalized)", file=sys.stderr)
        cursor = (data.get("metadata") or {}).get("nextCursor")
        if not entries or not cursor:
            exhausted = True
            break
        time.sleep(sleep)

    meta = {
        "pages_fetched": pages,
        "entries_seen": entries_seen,
        "unique_servers": len(records),
        "dedupe_replacements": replaced_by_newer,
        "dedupe_dropped": dropped_non_latest,
        "cursor_exhausted": exhausted,
        "probe": probe,
        "statuses": statuses,
        "anomalies": anomalies,
    }
    return list(records.values()), meta


def write_jsonl(path, records):
    """Write the normalized dataset: one JSON object per line, parents created."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-pages", type=int, default=50, help="safety cap on pages (100/page)")
    ap.add_argument("--limit", type=int, default=100, help="entries per page (100 is the observed API max)")
    ap.add_argument("--out", default="../data/servers.jsonl")
    ap.add_argument("--raw-dir", default="../data/raw/registry",
                    help="root for the verbatim API snapshot (one UTC-stamped subdir per run); '' disables")
    ap.add_argument("--probe-pages", type=int, default=0,
                    help="extra page fetches (saved raw, NOT normalized) to test cursor exhaustion")
    ap.add_argument("--sleep", type=float, default=0.4, help="politeness delay between requests (seconds)")
    ap.add_argument("--retries", type=int, default=5,
                    help="per-page retry budget for transient proxy/network faults (default 5, capped 30s backoff)")
    ap.add_argument("--checkpoint-every", type=int, default=50,
                    help="rewrite the output dataset every N pages so a long crawl survives a late failure")
    args = ap.parse_args()

    # AGENTS.md §2.5: print the spend/scope estimate BEFORE any external call.
    print(f"[budget] estimated external spend: $0.00 | up to {args.max_pages + args.probe_pages} "
          f"unauthenticated GETs to {BASE} ({args.limit}/page, {args.sleep}s apart). "
          f"No API key, no credential, no server endpoint contacted.", file=sys.stderr)

    raw_dir = None
    if args.raw_dir:
        raw_dir = os.path.join(args.raw_dir, utc_stamp())
        os.makedirs(raw_dir, exist_ok=True)
        print(f"[repro] verbatim API snapshot -> {raw_dir}", file=sys.stderr)

    started = datetime.now(timezone.utc).isoformat()

    def checkpoint(records, pages):
        write_jsonl(args.out, records)   # durability: one proxy blip must not lose the run

    completed = True
    try:
        servers, meta = crawl(max_pages=args.max_pages, sleep=args.sleep, raw_dir=raw_dir,
                              limit=args.limit, probe_pages=args.probe_pages,
                              retries=args.retries, checkpoint=checkpoint,
                              checkpoint_every=args.checkpoint_every)
    except (requests.RequestException, json.JSONDecodeError) as e:
        completed = False
        servers = []
        meta = {"error": f"{type(e).__name__}: {e}"}
        print(f"\n[fatal] crawl aborted after the retry budget: {type(e).__name__}: {e}", file=sys.stderr)
        print(f"[fatal] last checkpointed dataset (if any) is at {args.out}; raw pages kept in {raw_dir}",
              file=sys.stderr)

    if servers:
        write_jsonl(args.out, servers)

    meta.update({
        "completed": completed,
        "started_utc": started,
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "base_url": BASE,
        "limit": args.limit,
        "max_pages": args.max_pages,
        "out": os.path.abspath(args.out),
        "out_bytes": os.path.getsize(args.out),
        "out_sha256": sha256_file(args.out),
        "git": git_stamp(),
        "python": sys.version.split()[0],
    })
    if raw_dir:
        with open(os.path.join(raw_dir, "crawl_meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

    if not completed:
        sys.exit(2)

    print(f"\nSaved {len(servers)} unique latest-version servers -> {args.out}")
    print(f"entries seen: {meta['entries_seen']} | unique servers: {meta['unique_servers']} "
          f"({100.0 * meta['unique_servers'] / max(meta['entries_seen'], 1):.1f}% kept by isLatest dedupe)")
    print(f"pages fetched: {meta['pages_fetched']} | cursor exhausted: {meta['cursor_exhausted']} "
          f"| anomalies: {len(meta['anomalies'])}")
    if not meta["cursor_exhausted"]:
        print("NOTE: page cap reached with the registry cursor still live -> this snapshot is a "
              "PREFIX of the registry, not the whole thing. Raise --max-pages or report it as a limit.",
              file=sys.stderr)


if __name__ == "__main__":
    main()
