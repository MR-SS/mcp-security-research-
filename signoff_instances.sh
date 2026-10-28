#!/usr/bin/env bash
# Human review launcher for the 136 A8 text-rule instance verdicts.
# Run from any directory: bash signoff_instances.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

MODE="${1:-review}"
case "$MODE" in
  review)
    exec python3 pilot/signoff_instances.py
    ;;
  batch)
    COUNT="${2:-10}"
    exec python3 pilot/signoff_instances.py --limit "$COUNT"
    ;;
  status)
    exec python3 pilot/signoff_instances.py --summary
    ;;
  packet)
    exec python3 pilot/signoff_instances.py --export data/instance_signoff_packet.md
    ;;
  revise)
    KEY="${2:-}"
    if [[ -z "$KEY" ]]; then
      echo "Usage: bash signoff_instances.sh revise 'ROW|FLAG'" >&2
      exit 2
    fi
    exec python3 pilot/signoff_instances.py --revise "$KEY"
    ;;
  *)
    cat <<'USAGE'
Usage:
  bash signoff_instances.sh            # resume pending items until you quit
  bash signoff_instances.sh batch 10   # review exactly 10 pending items
  bash signoff_instances.sh status     # show completed / pending counts
  bash signoff_instances.sh packet     # regenerate the read-only review packet
  bash signoff_instances.sh revise '3|channel:model_addressed'

Keys during review:
  a = accept the proposed verdict
  s = override to supported (rationale required)
  u = override to unsupported (rationale required)
  q = save progress and quit
USAGE
    exit 2
    ;;
esac
