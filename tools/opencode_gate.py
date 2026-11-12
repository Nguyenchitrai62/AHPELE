# /// script
# requires-python = ">=3.11"
# dependencies = ["aiohttp==3.11.18"]
# ///
"""Local gate between PLE harnesses / judge and OpenCode Go (LOCAL DEV ONLY).

Never used in a submitted entry: the evaluator injects google-cloud models itself.

What it does:
  * Listens on 0.0.0.0:$GATE_PORT (default 8090) so the kit's serve and verifier
    containers can reach it (--model-base-url http://localhost:8090/v1).
  * Requires `Authorization: Bearer $GATE_KEY` (a random local key, NOT the
    OpenCode key), so nobody else on the network can spend the subscription.
  * Allows ONLY the models in ALLOWED (user rule, AGENTS.md section 0) and only on
    the API each model supports; everything else gets HTTP 403/400.
  * Forwards to OpenCode Go with the real key, a custom User-Agent and an
    `x-opencode-session` header (required by Go). The session id is taken from
    the caller's `x-opencode-session` header, or derived from the conversation's
    first message so one agent conversation keeps one id (better prompt caching).
  * Streams responses through untouched and appends one JSON line per call
    (model, status, tokens, cost) to $GATE_LOG for cost / efficiency analysis.

Run:  uv run --script tools/opencode_gate.py   (see tools/start_gate.sh)
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import sys
import time
from pathlib import Path

from aiohttp import ClientSession, ClientTimeout, web

UPSTREAM = "https://opencode.ai/inference/go/openai/v1"
USER_AGENT = "ahpele-ple-harness/0.1"

# model id -> the only endpoint OpenCode Go serves it on
ALLOWED = {
    "deepseek-v4.1-flash": "chat/completions",
    "muse-spark-1.3-contributor": "responses",
}

GATE_KEY = os.environ.get("GATE_KEY", "")
OPENCODE_KEY = os.environ.get("OPENCODE_API_KEY", "")
PORT = int(os.environ.get("GATE_PORT", "8090"))
LOG_PATH = Path(os.environ.get("GATE_LOG", str(Path.home() / ".cache/ahpele/gate-usage.jsonl")))

HOP_HEADERS = {"content-length", "transfer-encoding", "connection", "content-encoding", "keep-alive"}


def _err(status: int, message: str) -> web.Response:
    return web.json_response({"error": {"type": "gate_error", "message": message}}, status=status)


def _session_id(request: web.Request, body: dict) -> str:
    sid = request.headers.get("x-opencode-session")
    if sid:
        return sid[:128]
    # Stable per conversation: hash of the first message / input item.
    first = None
    if isinstance(body.get("messages"), list) and body["messages"]:
        # system prompt + first user message (the system prompt alone is shared by tasks)
        first = body["messages"][:2]
    elif isinstance(body.get("input"), list) and body["input"]:
        first = body["input"][0]
    elif isinstance(body.get("input"), str):
        first = body["input"]
    if isinstance(body.get("instructions"), str):
        first = [body["instructions"], first]
    digest = hashlib.sha256(json.dumps(first, sort_keys=True, default=str).encode()).hexdigest()[:24]
    return f"ahpele-{digest}"


def _usage_from_text(text: str) -> dict | None:
    """Find the last `usage` object in a JSON body or an SSE stream."""
    candidates = [text] if not text.lstrip().startswith(("data:", "event:")) else [
        line[5:].strip() for line in text.splitlines() if line.startswith("data:")
    ]
    usage = None
    for chunk in candidates:
        if '"usage"' not in chunk:
            continue
        try:
            obj = json.loads(chunk)
        except ValueError:
            continue
        if isinstance(obj.get("response"), dict) and obj["response"].get("usage"):
            usage = obj["response"]["usage"]  # Responses API stream: response.completed
        elif obj.get("usage"):
            usage = obj["usage"]
    return usage


def _log(entry: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


async def models(request: web.Request) -> web.Response:
    if request.headers.get("Authorization") != f"Bearer {GATE_KEY}":
        return _err(401, "missing or wrong gate key")
    return web.json_response({"object": "list", "data": [{"id": m, "object": "model"} for m in ALLOWED]})


async def proxy(request: web.Request) -> web.StreamResponse:
    if request.headers.get("Authorization") != f"Bearer {GATE_KEY}":
        return _err(401, "missing or wrong gate key")
    endpoint = request.match_info["endpoint"]
    raw = await request.read()
    try:
        body = json.loads(raw)
    except ValueError:
        return _err(400, "body is not JSON")
    model = body.get("model")
    if model not in ALLOWED:
        return _err(403, f"model {model!r} is not allowed (allowed: {sorted(ALLOWED)})")
    if ALLOWED[model] != endpoint:
        return _err(400, f"model {model!r} is only served on /v1/{ALLOWED[model]}, not /v1/{endpoint}")

    sid = _session_id(request, body)
    headers = {
        "Authorization": f"Bearer {OPENCODE_KEY}",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
        "x-opencode-session": sid,
    }
    started = time.time()
    session: ClientSession = request.app["client"]
    captured: list[str] = []
    status = 0
    ttfb = None
    params = {
        "max_tokens": body.get("max_tokens") or body.get("max_output_tokens"),
        "reasoning_effort": body.get("reasoning_effort") or (body.get("reasoning") or {}).get("effort"),
        "thinking": (body.get("thinking") or {}).get("type") if isinstance(body.get("thinking"), dict) else None,
        "n_messages": len(body.get("messages") or body.get("input") or []),
        "n_tools": len(body.get("tools") or []),
        "req_bytes": len(raw),
    }
    _log({"ts": round(started, 3), "event": "start", "model": model, "session": sid, **params})
    try:
        async with session.post(f"{UPSTREAM}/{endpoint}", data=raw, headers=headers) as upstream:
            status = upstream.status
            resp = web.StreamResponse(status=upstream.status)
            for key, value in upstream.headers.items():
                if key.lower() not in HOP_HEADERS:
                    resp.headers[key] = value
            await resp.prepare(request)
            async for chunk in upstream.content.iter_any():
                if ttfb is None:
                    ttfb = round(time.time() - started, 2)
                await resp.write(chunk)
                captured.append(chunk.decode("utf-8", "replace"))
            await resp.write_eof()
            return resp
    except (asyncio.CancelledError, ConnectionResetError):
        status = status or 499
        raise
    finally:
        text = "".join(captured)
        usage = _usage_from_text(text) or {}
        oc = usage.get("opencode", {}) if isinstance(usage, dict) else {}
        details = usage.get("completion_tokens_details") or usage.get("output_tokens_details") or {}
        _log({
            "ts": round(started, 3),
            "event": "end",
            "secs": round(time.time() - started, 2),
            "ttfb": ttfb,
            "resp_bytes": len(text),
            "reasoning_tokens": details.get("reasoning_tokens"),
            "cached_tokens": (usage.get("prompt_tokens_details") or usage.get("input_tokens_details") or {}).get("cached_tokens"),
            **params,
            "model": model,
            "endpoint": endpoint,
            "session": sid,
            "status": status,
            "stream": bool(body.get("stream")),
            "input_tokens": usage.get("prompt_tokens", usage.get("input_tokens")),
            "output_tokens": usage.get("completion_tokens", usage.get("output_tokens")),
            "list_cost": oc.get("list_cost"),
            "billing": oc.get("billing_source"),
            "error": text[:300] if status >= 400 else None,
        })


async def _startup(app: web.Application) -> None:
    app["client"] = ClientSession(timeout=ClientTimeout(total=None, sock_connect=30, sock_read=1800))


async def _cleanup(app: web.Application) -> None:
    await app["client"].close()


def main() -> None:
    if len(GATE_KEY) < 32 or not OPENCODE_KEY:
        sys.exit("GATE_KEY (>=32 chars) and OPENCODE_API_KEY must be set")
    app = web.Application(client_max_size=64 * 1024 * 1024)
    app.on_startup.append(_startup)
    app.on_cleanup.append(_cleanup)
    app.router.add_get("/v1/models", models)
    app.router.add_post("/v1/{endpoint:chat/completions|responses}", proxy)
    print(f"opencode gate on 0.0.0.0:{PORT}, models={sorted(ALLOWED)}, log={LOG_PATH}", flush=True)
    web.run_app(app, host="0.0.0.0", port=PORT, print=None)


if __name__ == "__main__":
    main()
