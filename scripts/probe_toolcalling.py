#!/usr/bin/env python3
"""Stage-0 probe for OpenAI-compatible tool-calling support.

Environment:
  MODEL_LIST: comma-separated model identifiers.
  OPENAI_BASE_URL: OpenAI-compatible API base URL.
  OPENAI_API_KEY: API key, read only from the environment.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

TIMEOUT_SECONDS = 60
RETRIES = 1
TOOL = {
    "type": "function",
    "function": {
        "name": "get_weather_mcp_probe",
        "description": "Synthetic probe tool; never performs external calls.",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}, "date": {"type": "string"}},
            "required": ["city", "date"],
            "additionalProperties": False,
        },
    },
}
PROMPT = "what is the weather in Munich next Tuesday?"


def endpoint(base_url: str) -> str:
    base = base_url.rstrip("/")
    return base if base.endswith("/chat/completions") else base + "/chat/completions"


def classify(payload: dict) -> str:
    if not isinstance(payload, dict):
        return "ERROR"
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return "ERROR"
    if not isinstance(choices[0], dict) or not isinstance(choices[0].get("message"), dict):
        return "ERROR"
    message = choices[0]["message"]
    calls = message.get("tool_calls")
    if isinstance(calls, list) and calls:
        for call in calls:
            if (
                isinstance(call, dict)
                and call.get("type") == "function"
                and isinstance(call.get("function"), dict)
                and call["function"].get("name") == TOOL["function"]["name"]
                and isinstance(call["function"].get("arguments"), str)
            ):
                try:
                    arguments = json.loads(call["function"]["arguments"])
                except (ValueError, TypeError):
                    return "ERROR"
                if not isinstance(arguments, dict) or not all(isinstance(arguments.get(key), str) for key in ("city", "date")):
                    return "ERROR"
                return "PASS"
        return "ERROR"
    if calls is not None and not isinstance(calls, list):
        return "ERROR"
    return "TEXT-ONLY" if isinstance(message.get("content"), str) and message["content"].strip() else "ERROR"


def probe(model: str, url: str, api_key: str) -> tuple[str, str]:
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": PROMPT}],
        "tools": [TOOL],
        "tool_choice": "auto",
        "temperature": 0,
    }).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + api_key},
        method="POST",
    )
    last_error = "unknown error"
    for attempt in range(RETRIES + 1):
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                payload = json.loads(response.read().decode("utf-8"))
            verdict = classify(payload)
            if verdict == "PASS":
                return verdict, "structured tool_calls returned"
            if verdict == "TEXT-ONLY":
                return verdict, "text response without structured tool_calls"
            return verdict, "malformed response: choices/tool_calls structure missing or invalid"
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            # Never persist exception text: it can contain credentials or URLs.
            last_error = "HTTP status " + str(exc.code) if isinstance(exc, urllib.error.HTTPError) else "transport/timeout/invalid JSON"
            if attempt < RETRIES:
                time.sleep(1)
    return "ERROR", last_error


def main() -> int:
    models = [item.strip() for item in os.getenv("MODEL_LIST", "").split(",") if item.strip()]
    base_url = os.getenv("OPENAI_BASE_URL", "").strip()
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not models or not base_url or not api_key:
        print("ERROR: set MODEL_LIST, OPENAI_BASE_URL, and OPENAI_API_KEY", file=sys.stderr)
        return 2

    from urllib.parse import urlsplit
    parsed = urlsplit(base_url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        print("ERROR: use an HTTPS company-proxy API base without credentials/query/fragment", file=sys.stderr)
        return 2
    if any(not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/-]*", model) or api_key in model for model in models):
        print("ERROR: invalid model identifiers", file=sys.stderr)
        return 2
    models = list(dict.fromkeys(models))
    timestamp = datetime.now(timezone.utc).isoformat()
    print("Estimated user spend: $0 via company proxy; at most 2 requests/model.", flush=True)
    results = []
    for model in models:
        verdict, reason = probe(model, endpoint(base_url), api_key)
        results.append({"model": model, "verdict": verdict, "reason": reason})

    print("model\tverdict\treason")
    for row in results:
        print(f"{row['model']}\t{row['verdict']}\t{row['reason']}")
    artifact = {
        "timestamp_utc": timestamp,
        "probe": "one synthetic tool, one user message",
        "results": results,
        "git_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[1], text=True).strip(),
        "git_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=Path(__file__).resolve().parents[1])),
    }
    os.makedirs("data/live_tests", exist_ok=True)
    with open("data/live_tests/stage0_probe.json", "w", encoding="utf-8") as handle:
        json.dump(artifact, handle, indent=2)
        handle.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
