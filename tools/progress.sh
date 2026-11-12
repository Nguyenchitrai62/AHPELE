#!/usr/bin/env bash
# Overview of local dev runs (LOCAL DEV ONLY).
#   tools/progress.sh            # runs touched in the last 24 h
#   tools/progress.sh 6          # runs touched in the last 6 h
#   watch -n 60 tools/progress.sh  # refresh every minute (Ctrl+C to stop)
set -uo pipefail
HOURS="${1:-24}"
KIT="${PLE_KIT:-/home/ttlab/src/ple}"
ENTRY="$(cd "$(dirname "$0")/.." && pwd)"
UV="${UV:-$HOME/.local/bin/uv}"

echo "=== $(date -u '+%Y-%m-%d %H:%M UTC')  runs touched in the last ${HOURS} h"
mapfile -t RUNS < <(find "$KIT/runs" -mindepth 1 -maxdepth 1 -type d -mmin -$((HOURS * 60)) -printf '%T@ %p\n' 2>/dev/null | sort -n | cut -d' ' -f2-)
if [ ${#RUNS[@]} -eq 0 ]; then echo "(no runs)"; else
  "$UV" run --quiet --project "$KIT" python "$ENTRY/tools/run_status.py" "${RUNS[@]}" 2>/dev/null
fi

echo
echo "=== model calls through the gate (last 15 min)"
python3 - "$HOME/.cache/ahpele/gate-usage.jsonl" <<'EOF'
import json, sys, time, collections
try:
    rows = [json.loads(l) for l in open(sys.argv[1])]
except FileNotFoundError:
    print("(no gate log)"); sys.exit()
now = time.time()
ends = [r for r in rows if r.get("event", "end") == "end" and r["ts"] > now - 900]
starts = [r for r in rows if r.get("event") == "start" and r["ts"] > now - 900]
by = collections.defaultdict(list)
for r in ends:
    by[r["model"]].append(r)
for m, rs in sorted(by.items()):
    s = sorted(r["secs"] for r in rs)
    err = sum(1 for r in rs if r["status"] != 200)
    cost = sum(r.get("list_cost") or 0 for r in rs)
    print(f"  {m:<28} {len(rs):>4} calls, median {s[len(s)//2]:>5.0f}s, errors {err}, list cost ${cost:.3f}")
open_calls = len(starts) - len(ends)
print(f"  calls in flight (approx): {max(open_calls, 0)}")
total = sum(r.get("list_cost") or 0 for r in rows if r.get("event", "end") == "end")
print(f"  total list cost since the gate started: ${total:.2f}")
EOF

echo
echo "=== machine"
free -g | awk 'NR==2{print "  RAM available: "$7" GB of "$2" GB"}'
df -h / | awk 'NR==2{print "  disk free: "$4" ("$5" used)"}'
echo "  task containers running: $(docker ps --format '{{.Names}}' | grep -c -- '__env-main')"
if [ -f "$HOME/.cache/ahpele/gate.pid" ] && kill -0 "$(cat "$HOME/.cache/ahpele/gate.pid")" 2>/dev/null; then
  echo "  gate: running"
else
  echo "  gate: NOT running (start: tools/start_gate.sh)"
fi
