"""Live per-task status of a PLE dev run (LOCAL DEV ONLY).

eval/run.py prints its summary table only after every task in the run has
finished, but Harbor writes each trial's result.json as soon as that task is
graded. This reads those files and scores them with the kit's own logic.

Usage (from anywhere):
  uv run --project /home/ttlab/src/ple python tools/run_status.py <run dir> [<run dir> ...]
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import time

KIT = pathlib.Path(os.environ.get("PLE_KIT", "/home/ttlab/src/ple"))
sys.path.insert(0, str(KIT / "eval"))
import run as kit_run  # noqa: E402  (the kit's eval/run.py)


def trials(run_dir: pathlib.Path):
    for attempt in sorted(run_dir.glob("attempt*")):
        for trial in sorted((attempt / "jobs").glob("*/*__*")):
            if trial.is_dir():
                yield attempt.name, trial


def status(run_dir: pathlib.Path) -> None:
    print(f"== {run_dir}")
    rows = []
    for attempt, trial in trials(run_dir):
        task_id = trial.name.split("__")[0]
        task = run_dir / "tasks" / task_id
        started = trial.stat().st_mtime
        if not (trial / "result.json").is_file():
            age = (time.time() - (trial / "config.json").stat().st_mtime) / 60 if (trial / "config.json").exists() else 0
            rows.append((task_id, attempt, "running", "", f"{age:.0f} min so far", ""))
            continue
        r = kit_run.outcome(task_id, task, trial)  # the kit's own grading rules
        mins = f"{r.seconds / 60:.0f} min" if r.seconds else ""
        tok = ""
        if r.tokens:
            tok = " ".join(f"{k}={v / 1e6:.1f}M" for k, v in r.tokens.items())
        score = "" if r.score is None else f"{r.score:.3f}"
        rows.append((task_id, attempt, r.status, score, mins, tok))
    if not rows:
        print("  (no trials yet)")
    for row in rows:
        print("  {:<36} {:<9} {:<28} score={:<6} {:<10} {}".format(*row))
    done = [float(r[3]) for r in rows if r[3]]
    if done:
        print(f"  finished {len(done)}/{len(rows)}, mean score of finished = {sum(done) / len(done):.3f}")


if __name__ == "__main__":
    for arg in sys.argv[1:] or ["."]:
        status(pathlib.Path(arg).resolve())
