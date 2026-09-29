"""Shared helpers for Brief 04 mock tools (offline, synthetic-only)."""
from __future__ import annotations

import re
from typing import Any, Callable, Dict, NamedTuple

# Strings that must never appear in a canned response (defense in depth; the
# canned data is authored synthetic, this is a tripwire, not a filter).
REAL_KEY_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9]{10,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"eyJ[A-Za-z0-9_-]{20,}"),  # JWT-shaped
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
)


class SyntheticDataLeak(AssertionError):
    """A canned response contained credential-shaped material."""


def assert_synthetic(payload: Any) -> None:
    """Tripwire: canned responses carry only TESTKEY-style synthetic strings."""
    import json

    text = json.dumps(payload, ensure_ascii=False)
    for pattern in REAL_KEY_PATTERNS:
        hit = pattern.search(text)
        if hit:
            raise SyntheticDataLeak(
                f"canned response matched real-credential pattern {pattern.pattern!r}"
            )


class MockTool(NamedTuple):
    """One registered tool: OpenAI schema + canned dispatcher."""

    name: str
    schema: dict                 # OpenAI "function" tool definition
    dispatch: Callable[[dict], Dict[str, Any]]  # args dict -> JSON-serialisable result


def tool_schema(name: str, description: str, parameters: dict) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": parameters,
        },
    }


def ok(result: Dict[str, Any]) -> Dict[str, Any]:
    return {"status": "ok", "result": result}


def err(message: str) -> Dict[str, Any]:
    return {"status": "error", "error": message}
