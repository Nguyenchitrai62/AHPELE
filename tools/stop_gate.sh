#!/usr/bin/env bash
# Stop the local OpenCode gate and wait until it has really exited.
set -euo pipefail
PID_FILE="$HOME/.cache/ahpele/gate.pid"
[ -f "$PID_FILE" ] || { echo "no gate pid file"; exit 0; }
pid="$(cat "$PID_FILE")"
if kill -0 "$pid" 2>/dev/null; then
  kill "$pid"
  for _ in $(seq 50); do kill -0 "$pid" 2>/dev/null || break; sleep 0.2; done
fi
pkill -f 'tools/opencode_gate.py' 2>/dev/null || true
for _ in $(seq 50); do pgrep -f 'tools/opencode_gate.py' >/dev/null || break; sleep 0.2; done
rm -f "$PID_FILE"
echo "gate stopped"
