#!/usr/bin/env bash
# Start the local OpenCode Go gate (LOCAL DEV ONLY; see tools/opencode_gate.py).
# Reads OPENCODE_API_KEY from the entry's .env and GATE_KEY from the kit's local.env
# (creating local.env with a fresh GATE_KEY and judge settings on first run).
set -euo pipefail

ENTRY="$(cd "$(dirname "$0")/.." && pwd)"
KIT="${PLE_KIT:-/home/ttlab/src/ple}"
LOCAL_ENV="$KIT/local.env"
LOG_DIR="$HOME/.cache/ahpele"
PORT="${GATE_PORT:-8090}"
mkdir -p "$LOG_DIR"

if [ ! -f "$LOCAL_ENV" ]; then
  key="$(openssl rand -hex 24)"
  umask 077
  cat > "$LOCAL_ENV" <<EOF
# Local runs only (kit --env-file). Never commit. Created by AHPELE/tools/start_gate.sh
MODEL_API_KEY=$key
JUDGE_BASE_URL=http://localhost:$PORT/v1
JUDGE_API_KEY=$key
JUDGE_MODEL=deepseek-v4.1-flash
EOF
fi

GATE_KEY="$(grep '^MODEL_API_KEY=' "$LOCAL_ENV" | cut -d= -f2-)"
OPENCODE_API_KEY="$(grep '^OPENCODE_API_KEY=' "$ENTRY/.env" | cut -d= -f2-)"
export GATE_KEY OPENCODE_API_KEY GATE_PORT="$PORT"

if [ -f "$LOG_DIR/gate.pid" ] && kill -0 "$(cat "$LOG_DIR/gate.pid")" 2>/dev/null; then
  echo "gate already running (pid $(cat "$LOG_DIR/gate.pid"))"
  exit 0
fi

nohup "${UV:-$HOME/.local/bin/uv}" run --quiet --script "$ENTRY/tools/opencode_gate.py" \
  >> "$LOG_DIR/gate.log" 2>&1 &
echo $! > "$LOG_DIR/gate.pid"
sleep 3
tail -n 2 "$LOG_DIR/gate.log"
