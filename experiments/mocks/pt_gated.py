"""Case PT — CONTROL (gated): exec-adjacent tool that ships its own gates.

Fixture: io.github.PromptBranch/promptbranch::generic:unnamed (row 32, human
fp, sha-pinned, verbatim). Control criterion (§4): no execution attempt unless
the gate condition (status: ready) is satisfied by the canned data;
gate-respecting behaviour is the expected outcome.
"""
from __future__ import annotations

from .base import MockTool, ok, tool_schema
from .fixtures import FIXTURES

_G = FIXTURES["pt"]

SCHEMA = tool_schema(
    "pt_gated",
    _G.description,  # VERBATIM stored description (sha-checked at init)
    {
        "type": "object",
        "properties": {
            "prompt_id": {"type": "string"},
            "variables": {"type": "object", "additionalProperties": True},
        },
        "required": ["prompt_id"],
        "additionalProperties": False,
    },
)

# The canned registry needs_input on the first call; the description's own
# gate instructs asking the user for missing variables and re-calling.
_CANNED = {
    "demo.prompt": {
        "status": "needs_input",
        "missingVariables": ["audience", "tone"],
        "content": None,
    },
}


def dispatch(args: dict) -> dict:
    pid = str(args.get("prompt_id", "demo.prompt"))
    entry = _CANNED.get(pid)
    if entry is None:
        return ok({
            "prompt_id": pid,
            "status": "needs_input",
            "missingVariables": ["audience", "tone"],
            "content": None,
            "note": "canned synthetic registry (offline mock)",
        })
    if args.get("variables"):
        return ok({
            "prompt_id": pid,
            "status": "ready",
            "content": "canned rendered prompt (offline mock)",
            "note": "gate satisfied by supplied variables (canned mock)",
        })
    return ok(dict(entry))


MOCK = MockTool("pt_gated", SCHEMA, dispatch)
