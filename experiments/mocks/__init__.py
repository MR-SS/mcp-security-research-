"""Brief 04 mock tool servers (Stage 2).

Offline only: every tool is answered from canned synthetic data per
docs/BRIEF04_PROTOCOL.md §2 — no sockets, no subprocess, no filesystem writes.
Tool descriptions are embedded VERBATIM from the §0 fixture table and are
sha-checked against data/github_tools.jsonl at harness init (fail loudly on
mismatch).
"""
from .fixtures import FIXTURES, CASES, verify_against_corpus, FixturesMismatchError
from .fillers import FILLER_TOOLS

__all__ = [
    "FIXTURES",
    "CASES",
    "FILLER_TOOLS",
    "verify_against_corpus",
    "FixturesMismatchError",
]
