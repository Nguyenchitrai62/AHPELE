# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Pi coding agent harness (`@earendil-works/pi-coding-agent`).

Runs one headless Pi session per task. Pi runs in the serve container while the
task's files live in the task container. `task-tools.ts` replaces Pi's built-in
`read`, `write`, `edit`, and `bash` tools with versions that operate on the task
container through `taskbridge.Relay`, and the task's MCP servers are proxied
through the same relay. Pi's agent loop handles model calls, tool execution,
retries, and conversation compaction, returning its last response as the final
message.

The model is configured from the environment variables set by the evaluator in
`models.json` for each task. Claude and Gemini models use their native APIs
under Pi's built-in provider names (`anthropic` and `google`) so Pi's catalog
supplies their limits, thinking support, and image input capabilities. Any other
model uses the OpenAI-compatible `MODEL_BASE_URL` and `MODEL_API_KEY` under a
custom `model` provider with `UNKNOWN_MODEL` limits.
"""

from __future__ import annotations

import asyncio
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import time
from typing import Any

import taskbridge

HERE = pathlib.Path(__file__).resolve().parent
# npm ci, from package-lock.json
PI = shutil.which("pi") or str(HERE / "node_modules" / ".bin" / "pi")
# pi's --thinking level: off, minimal, low, medium, high, xhigh or max
THINKING = "max"
# stop pi this long before the deadline (less on short tasks) so its answer
# arrives
STOP_BEFORE_SEC = 90
CATALOG_TIMEOUT_SEC = 30
# Pi settings: retry failed requests up to 8 times with exponential backoff
# from 2 s to 60 s (~4 minutes total, versus Pi's 14 s default), set a 1-hour
# HTTP idle timeout so long max-effort thinking is not cut off at 5 minutes,
# and keep `streaming` cache warming so Pi refreshes Claude's prompt cache
# during long commands.
SETTINGS = {
    "defaultProjectTrust": "never",
    "quietStartup": True,
    "cacheWarming": "streaming",
    "retry": {"maxRetries": 8, "baseDelayMs": 2000, "maxAgentDelayMs": 60000},
    "httpIdleTimeoutMs": 3_600_000,
}
# Request features the Google Cloud route for Claude refuses. pi leaves them
# out, and the Anthropic API works without them too.
COMPAT = {
    "supportsStrictTools": False,
    "supportsMidConvoEffort": False,
    "supportsMidConvoSystemMessages": False,
    "supportsMidConvoToolChanges": False,
}
# A model pi's catalog does not know gets these limits; tune them for yours.
UNKNOWN_MODEL = {"input": ["text"], "contextWindow": 128000, "maxTokens": 16384}
# AHPELE: per-model settings for models missing from pi 1.1.0's catalog under
# the provider we use. Each entry may set `api` (the provider's API), `thinking`
# (pi's --thinking level for this model) and `model` (the models.json entry,
# replacing UNKNOWN_MODEL). Values for the local test models come from pi's own
# opencode-go catalog; Gemini 4 Argon follows the kit's pi-opus README (no
# `reasoning`, since pi would send a thinking budget that Argon rejects with 400).
MODEL_PROFILES: dict[str, dict[str, Any]] = {
    # Local test model (OpenCode Go, Chat Completions). Not submittable.
    "deepseek-v4.1-flash": {
        "api": "openai-completions",
        "model": {
            "input": ["text", "image"],
            "contextWindow": 1_000_000,
            "maxTokens": 32_000,
            "reasoning": True,
            "thinkingLevelMap": {"off": None, "minimal": None, "low": "low",
                                 "medium": None, "high": "high",
                                 "xhigh": None, "max": "max"},
            "compat": {"supportsStore": False,
                       "supportsDeveloperRole": False,
                       "maxTokensField": "max_tokens",
                       "requiresReasoningContentOnAssistantMessages": True,
                       "thinkingFormat": "deepseek"},
        },
    },
    # Local test model (OpenCode Go, Responses API only). Not submittable.
    "muse-spark-1.3-contributor": {
        "api": "openai-responses",
        "thinking": "xhigh",  # its highest level; it has no "max"
        "model": {
            "input": ["text", "image"],
            "contextWindow": 1_048_576,
            "maxTokens": 32_000,
            "reasoning": True,
            "thinkingLevelMap": {"off": None, "minimal": "minimal",
                                 "low": "low", "medium": "medium",
                                 "high": "high", "xhigh": "xhigh",
                                 "max": None},
        },
    },
    # Submission model (google provider, not in pi 1.1.0's catalog).
    "gemini-4-argon": {
        "model": {"input": ["text", "image"], "contextWindow": 1_048_576,
                  "maxTokens": 65_536},
    },
}


def profile(model: str) -> dict[str, Any]:
  """Returns the AHPELE settings for `model` (empty if it has none)."""
  return MODEL_PROFILES.get(model, {})
NOTE = (
    "You are working on an engineering task. Your tools act on the task's Linux"
    " container, whose working directory is {workdir}; it has no internet"
    " access. Read the whole instruction and the files it points to, put every"
    " deliverable exactly where and in the format the instruction asks, and"
    " check what you wrote. When you are done, reply with a short summary of"
    " what you delivered and where."
)
# AHPELE RC-0007: requirements-first working method (generic, never
# task-specific). Set AHPELE_REQ_WORKFLOW=0 to leave it out (ablations).
WORKFLOW = (
    "\n\nWorking method:\n"
    "1. Read the whole instruction first. Write the exact list of deliverables"
    " (paths, file names, formats, required columns, fields and tokens) and"
    " any scoring rules it states to /tmp/ahpele/checklist.md, and re-read"
    " that file before you finish.\n"
    "2. Inventory the project documents: note each one's revision and status."
    " Identify superseded, cancelled, draft or non-adopted documents and the"
    " RFIs, site instructions and correspondence that change requirements;"
    " the governing specification usually says which documents apply. Never"
    " cite or apply a superseded or cancelled document.\n"
    "3. Before you design anything, extract every hard requirement (safety and"
    " code limits, standard clauses, permit or authorisation limits,"
    " capacities, schedule milestones, resource caps) with its document,"
    " clause and numeric value into a requirements table at"
    " /tmp/ahpele/requirements.csv. If the deliverable includes a constraint"
    " or requirement register, build it from this table.\n"
    "4. Write a check script that recomputes the key numbers from your own"
    " deliverable and tests it against every row of the requirements table and"
    " every schema rule in the checklist. Fix every failure. Improve the"
    " objective (cost, performance) only while all hard checks keep passing,"
    " and re-run the checks after every change."
)
# AHPELE H1: document toolbox. Before pi starts, toolbox/ahpele_index.py is
# copied into the task container and run on the workdir; it writes a text
# corpus, rendered scanned pages and an inventory under /tmp/ahpele. Set
# AHPELE_TOOLBOX=0 to skip it (ablations).
TOOLBOX_SRC = HERE / "toolbox" / "ahpele_index.py"
TOOLBOX_DST = "/tmp/ahpele/bin/ahpele_index.py"
TOOLBOX_BUDGET_SEC = 300
INVENTORY_CHARS = 6000
TOOLBOX_NOTE = (
    "\n\nA document index was built before you started:\n"
    "- /tmp/ahpele/inventory.md lists every project file with its type,"
    " pages, scanned pages, revision, status words in its file name, and"
    " possible revision families (the same document under several revisions)."
    " Words found inside a document's text often refer to other documents.\n"
    "- /tmp/ahpele/corpus/<path>.txt holds the extracted text of each file"
    " (PDF pages, DOCX paragraphs and tables, XLSX cells with formulas, DXF"
    " text, dimensions and blocks, emails). Search it with grep -ril.\n"
    "- Scanned pages are already rendered as PNG under /tmp/ahpele/pages/;"
    " read one only when you need what is on it.\n"
    "- To re-run it on another folder: python3 " + TOOLBOX_DST + " --root"
    " <dir> --out <dir>.\n"
    "The index is a convenience: confirm every number you rely on against the"
    " original file.\n"
)
TIME_NOTE = (
    " You have about {minutes} minutes in all; leave time to finish the"
    " deliverables."
)


async def build_index(session: taskbridge.Session) -> str:
  """Runs the document toolbox in the task container (H1).

  Returns the system-prompt text describing the index (with the start of the
  inventory), or "" when the toolbox is disabled or anything fails. Never
  raises: a failed index must not cost the task.
  """
  if os.environ.get("AHPELE_TOOLBOX", "1") == "0" or not TOOLBOX_SRC.exists():
    return ""
  try:
    await session.write_file(TOOLBOX_DST, TOOLBOX_SRC.read_bytes())
    workdir = session.workdir or "/"
    res = await session.exec(
        f"command -v python3 >/dev/null || exit 3; cd / && python3 {TOOLBOX_DST}"
        f" --root '{workdir}' --out /tmp/ahpele --budget {TOOLBOX_BUDGET_SEC}"
        " 2>&1 | tail -n 3",
        timeout_sec=TOOLBOX_BUDGET_SEC + 60,
    )
    output = str(res.get("output", "")).strip()
    await session.log(f"ahpele: toolbox exit={res.get('exit_code')} {output[-300:]}")
    if res.get("exit_code") != 0 or "indexed" not in output:
      return ""
    inventory = (await session.read_file("/tmp/ahpele/inventory.md")).decode(
        "utf-8", "replace"
    )
    if len(inventory) > INVENTORY_CHARS:
      inventory = (
          inventory[:INVENTORY_CHARS]
          + "\n... (truncated: read /tmp/ahpele/inventory.md for the rest)\n"
      )
    return TOOLBOX_NOTE + "\nIndex summary: " + output.splitlines()[-1] + "\n\n" + inventory
  except Exception as exc:  # noqa: BLE001  pylint: disable=broad-exception-caught
    await session.log(f"ahpele: toolbox skipped: {type(exc).__name__}: {exc}")
    return ""


def note(session: taskbridge.Session) -> str:
  """Returns the text appended to Pi's system prompt for a task.

  Pi is stopped `STOP_BEFORE_SEC` before the deadline, so the prompt note
  reports the remaining time available before that cutoff.

  Args:
    session: Active task session.

  Returns:
    `NOTE` for the task's workdir, plus `TIME_NOTE` when the task has a limit.
  """
  left = session.time_left()
  text = NOTE.format(workdir=session.workdir)
  if os.environ.get("AHPELE_REQ_WORKFLOW", "1") != "0":
    text += WORKFLOW
  if left is None:
    return text
  return text + TIME_NOTE.format(minutes=int(left // 60))


def provider() -> tuple[str, dict[str, Any]]:
  """Returns the Pi provider name and its `models.json` entry.

  Returns:
    A tuple of `(provider_name, provider_config)`.
  """
  if os.environ.get("ANTHROPIC_BASE_URL"):
    return "anthropic", {
        "baseUrl": os.environ["ANTHROPIC_BASE_URL"],
        "api": "anthropic-messages",
        "apiKey": "$ANTHROPIC_API_KEY",
        "compat": COMPAT,
    }
  if os.environ.get("GOOGLE_GEMINI_BASE_URL"):
    return "google", {
        "baseUrl": os.environ["GOOGLE_GEMINI_BASE_URL"] + "/v1beta",
        "api": "google-generative-ai",
        "apiKey": "$GEMINI_API_KEY",
    }
  return "model", {
      "baseUrl": os.environ["MODEL_BASE_URL"],
      "api": profile(os.environ["MODEL_NAME"]).get("api", "openai-completions"),
      "apiKey": "$MODEL_API_KEY",
  }


def in_catalog(name: str, model: str, env: dict[str, str]) -> bool:
  """Checks whether Pi's built-in model catalog recognizes `model`.

  If the probe hangs beyond `CATALOG_TIMEOUT_SEC` or fails, returns `False` so
  the model is configured explicitly with `UNKNOWN_MODEL` limits.

  Args:
    name: Provider name (`anthropic`, `google`, or `model`).
    model: Model identifier string.
    env: Subprocess environment variables for the Pi CLI probe.

  Returns:
    `True` if `(name, model)` appears in `pi --list-models`, else `False`.
  """
  try:
    out = subprocess.run(
        [PI, "--offline", "--list-models", model],
        env=env,
        capture_output=True,
        text=True,
        timeout=CATALOG_TIMEOUT_SEC,
        check=False,
    ).stdout
  except (subprocess.TimeoutExpired, OSError):
    return False
  return any(line.split()[:2] == [name, model] for line in out.splitlines())


def configure(
    agent_dir: pathlib.Path,
    relay: taskbridge.Relay,
    session: taskbridge.Session,
    env: dict[str, str],
) -> tuple[str, str]:
  """Writes Pi's model, settings, and MCP configuration files for a task.

  Args:
    agent_dir: Directory where Pi reads its configuration files.
    relay: Local HTTP relay for the task container and its MCP servers.
    session: Active task session.
    env: Environment dictionary passed to Pi subprocesses.

  Returns:
    A tuple of `(provider_name, model_name)`.
  """
  model = os.environ["MODEL_NAME"]
  name, config = provider()
  models = agent_dir / "models.json"
  # `pi --list-models` reads the provider here
  models.write_text(json.dumps({"providers": {name: config}}))
  if not in_catalog(name, model, env):
    limits = profile(model).get("model", UNKNOWN_MODEL)
    config["models"] = [{"id": model, "name": model, **limits}]
    models.write_text(json.dumps({"providers": {name: config}}))
  (agent_dir / "settings.json").write_text(json.dumps(SETTINGS))
  servers = {
      s["name"]: {"url": relay.mcp_url(s["name"]), "timeout": 300}
      for s in session.mcp_servers
  }
  (agent_dir / "mcp.json").write_text(json.dumps({"mcpServers": servers}))
  return name, model


class Run:
  """Tracks JSON stream events from a single Pi subprocess run."""

  def __init__(self, session: taskbridge.Session, model: str):
    self.session, self.model, self.replies = session, model, 0

  async def on_event(self, event: dict[str, Any]) -> None:
    """Processes a parsed JSON event from Pi, updating final message and usage.

    Args:
      event: Decoded JSON event dictionary from Pi's stdout stream.
    """
    kind, message = event.get("type"), event.get("message") or {}
    if kind == "message_end" and message.get("role") == "assistant":
      self.replies += 1
      text = "\n".join(
          b.get("text", "")
          for b in message.get("content") or []
          if b.get("type") == "text"
      )
      if text.strip():
        self.session.final_message = text.strip()
      if message.get("stopReason") == "error":
        await self.session.log(
            f"pi: model error: {message.get('errorMessage')}"
        )
      # input_tokens counts cached prompt tokens too
      u = message.get("usage") or {}
      await self.session.usage(
          self.model,
          input_tokens=u.get("input", 0)
          + u.get("cacheRead", 0)
          + u.get("cacheWrite", 0),
          output_tokens=u.get("output", 0),
          cache_read_tokens=u.get("cacheRead", 0),
      )
    elif kind == "tool_execution_start":
      await self.session.log(
          f"pi: {event.get('toolName')} {json.dumps(event.get('args'))[:300]}"
      )
    elif kind in ("auto_retry_start", "compaction_start"):
      await self.session.log(f"pi: {kind} {json.dumps(event)[:300]}")

  async def on_line(self, line: bytes) -> None:
    """Parses a raw stdout line from Pi as JSON and forwards it to `on_event`.

    Args:
      line: Raw line bytes emitted by Pi.
    """
    try:
      event = json.loads(line)
    except ValueError:
      return
    if isinstance(event, dict):
      await self.on_event(event)


async def solve(session: taskbridge.Session) -> str:
  """Runs Pi on a single task and returns the final response.

  Creates an isolated temporary agent home, configures tools and MCP servers to
  communicate through `taskbridge.Relay`, and feeds the task instruction on
  standard input.

  Args:
    session: Active task session.

  Returns:
    The final message produced by Pi.

  Raises:
    RuntimeError: If Pi exits before the model produces any assistant reply.
  """
  # AHPELE: local time-boxed probe runs. When AHPELE_MAX_MINUTES is set (only in
  # local research configs, never in a submitted entry), pull the task deadline
  # in so the agent is told the shorter budget and wraps up early.
  cap_min = os.environ.get("AHPELE_MAX_MINUTES")
  if cap_min:
    cap_deadline = time.monotonic() + float(cap_min) * 60
    session.deadline = (
        cap_deadline
        if session.deadline is None
        else min(session.deadline, cap_deadline)
    )
    await session.log(f"ahpele: time-boxed probe, {cap_min} min budget")
  index_note = await build_index(session)
  with tempfile.TemporaryDirectory(
      prefix="pi-",
      dir=os.environ.get("HOME") or None,
      ignore_cleanup_errors=True,
  ) as scratch:
    agent_dir, work = (
        pathlib.Path(scratch) / "agent",
        pathlib.Path(scratch) / "work",
    )
    agent_dir.mkdir()
    work.mkdir()
    async with taskbridge.Relay(session) as relay:
      env = relay.env()
      env.update(
          PI_CODING_AGENT_DIR=str(agent_dir),
          PI_OFFLINE="1",
          PI_SKIP_VERSION_CHECK="1",
          PI_TELEMETRY="0",
          NODE_NO_WARNINGS="1",
          TASK_WORKDIR=session.workdir,
      )
      left = session.time_left()
      if left is not None:
        # wall-clock time at which run_process stops pi (settle-guard.ts)
        env["AHPELE_STOP_AT_EPOCH"] = str(
            int(time.time() + max(left - STOP_BEFORE_SEC, 0))
        )
      name, model = await asyncio.to_thread(
          configure, agent_dir, relay, session, env
      )
      argv = [
          PI,
          "--print",
          "--mode",
          "json",
          "--no-session",
          "-nc",
          "-ns",
          "-np",
          "-na",
          "-e",
          str(HERE / "task-tools.ts"),
          # AHPELE RC-0002: keep only recent images in each model request
          "-e",
          str(HERE / "context-guard.ts"),
          # AHPELE RC-0005: do not let pi settle on a truncated/empty turn,
          # and ask once for a deliverable check before finishing
          "-e",
          str(HERE / "settle-guard.ts"),
          "--provider",
          name,
          "--model",
          model,
          "--thinking",
          profile(model).get("thinking", THINKING),
          "--append-system-prompt",
          note(session) + index_note,
      ]
      run = Run(session, model)
      done = await taskbridge.run_process(
          argv,
          session,
          env=env,
          cwd=str(work),
          on_line=run.on_line,
          stdin=session.instruction.encode(),
          stop_before_sec=STOP_BEFORE_SEC,
          log_prefix="pi: ",
      )
  if not run.replies:
    raise RuntimeError(
        f"pi exited with {done.code} before the model answered:"
        f" {done.stderr[-2000:]}"
    )
  return session.final_message or "(pi stopped without a final message)"
