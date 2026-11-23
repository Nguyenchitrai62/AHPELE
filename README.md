# AHPELE: an engineer-style agent harness for PLE

Entry for the Kaggle competition
[Google - Agent Harness on Physical-Engineering's Last Exam](https://www.kaggle.com/competitions/physical-engineerings-last-exam).
The harness is built on the kit's `pi-opus` sample (the Pi coding agent, `@earendil-works/pi-coding-agent`)
and adds a review cycle, run-time guards, general engineering skills and a small engineering toolbox.

## Files

| Path | Role |
|---|---|
| `submission.yaml` | Entry spec: `model_api`, `install`, `serve` |
| `serve.py` | WebSocket server on `0.0.0.0:$PORT` (kit serve protocol) |
| `harness.py` | Task loop: prompt, Pi sessions, review cycle, deadlines, final message |
| `taskbridge.py`, `task-tools.ts` | Relay that runs Pi's `read`/`write`/`edit`/`bash` tools and MCP servers in the task container |
| `settle-guard.ts`, `phase-guard.ts`, `skill-guard.ts`, `context-guard.ts` | Pi extensions (run-time guards, see below) |
| `skills/` | 25 skills of general engineering practice (structural, civil, MEP, electrical, cost, plan review, memos) |
| `toolbox/` | Helper scripts copied into the task container at `/tmp/ahpele/bin/` |
| `tools/` | Local-run helpers only (model gate, progress, run status); not used by the harness |
| `artifacts/` | Dev-set outputs exported by `eval/run.py` |

## Architecture

```
task (instruction, files, MCP)  ──►  harness.py
                                      │ 1. index the task documents (ahpele_index.py)
                                      │ 2. AUTHOR session (Pi + skills + toolbox), deadline pulled in
                                      │    to reserve review time
                                      │ 3. CHECKER session: clean context, sees only the instruction,
                                      │    documents and files on disk; writes a list of defects
                                      │ 4. FIXER session: fixes the listed defects, re-runs the checks
                                      ▼
                                 deliverables + done.final_message
```

- **Author → independent checker → fixer.** The checker never sees the author's reasoning, so it reviews the
  deliverable the way a senior engineer reviews a junior's package: hard requirements first, then whether every
  question is answered directly, then a line-by-line review (operating states, scope, recomputed totals,
  plausibility). The fixer changes a design decision only on decisive evidence.
- **Resumed check.** A check cut off by its time limit before it recorded a result is not read as a clean check: it is
  resumed once, for a limited time, when enough task time is left.
- **Back-check (off by default).** `AHPELE_CHECK_ROUNDS=2` lets a second clean-context checker verify that the comments
  are closed and re-check the hard requirements on the corrected files; only blocking findings start a second fix, and
  an unfinished second fix is undone. On the dev probes it found further defects but did not raise the scores.
- **Engineering workflow in the prompt.** Read everything, build a requirement register (one requirement per
  row, value as written, cited clause), design for feasibility first, then optimise, then verify with
  calculations and tools, and answer every question with the fact, its source and a definite conclusion.
- **Guards (Pi extensions).**
  - `settle-guard`: Pi would end a run on a truncated or empty turn; the guard asks the model to continue,
    and once asks it to verify that every deliverable named in the instruction exists and is complete
    before it stops.
  - `phase-guard`: at fixed fractions of the time budget, reminds the agent which deliverable paths named
    in the instruction do not exist yet, and asks it to finalise near the end.
  - `skill-guard`: if the agent has opened no skill and recorded no choice, reminds it to choose; it never
    suggests a particular skill, and "none fits" is a valid choice.
  - `context-guard`: keeps only the latest images in the request, so long tasks with scanned drawings do not
    grow requests without bound (and the prompt-cache prefix stays stable).
- **Toolbox.**
  - `ahpele_index.py`: indexes documents (PDF, spreadsheets, images).
  - `ahpele_reqscan.py`: scans for requirements and checks a register against its cited sources.
  - `ahpele_check.py`: re-opens each deliverable the way the recipient's software would (missing or empty
    files, files that do not parse, placeholder values).
  - `ahpele_ifc.py`, `ahpele_clash.py`: IFC inspection, schema validation, clash and clearance checks.
  - `ahpele_drawing.py`: reads drawings by grid tiles, crops and symbol matching.
- **Skills.** General professional knowledge only (codes, units, design principles, review practice). Nothing
  in the harness names, detects or branches on a specific task.

### Models

`harness.py` picks the API from `MODEL_NAME`, following the kit samples:
- Claude: native Anthropic Messages with prompt caching (cache warming during long commands), and without the
  request features the Google Cloud route refuses.
- Gemini 4 Argon: native Gemini API, without a thinking budget (Argon rejects it with 400), as in the kit's
  `pi-opus` README.
- Other models: OpenAI-compatible Chat Completions or Responses, with per-model limits in `MODEL_PROFILES`.

Pi retries failed requests up to 8 times with exponential backoff (2 s to 60 s), with a 1-hour idle timeout so
long reasoning turns are not cut off.

## Install and run

`submission.yaml` holds the install and serve commands used by the evaluator:

```bash
npm ci --prefix {src} --no-fund --no-audit
uv venv --python 3.12 /opt/harness/venv
uv pip install --python /opt/harness/venv/bin/python -r {src}/requirements.txt
/opt/harness/venv/bin/python {src}/serve.py
```

With the [PLE kit](https://github.com/google-research/ple) checked out next to this repo:

```bash
cd ple
uv run python -m kit check ../AHPELE          # build, smoke test, readiness
uv run python eval/run.py ../AHPELE           # run the 29 dev tasks, export artifacts/
uv run python -m kit artifacts ../AHPELE      # check artifacts/
```

## Reproducing the dev artifacts

`artifacts/` were generated with `eval/run.py` on a local model, as the competition allows. The run used:
- **Model:** DeepSeek-V4.1-Flash, an OpenAI-compatible endpoint behind a local gate
  (`tools/opencode_gate.py`), which adds the provider's required headers and logs token use.
- **Judge:** DeepSeek-V4.1-Flash as the kit's LLM judge (`JUDGE_*` settings).

To reproduce:
1. Start the gate: `tools/start_gate.sh` (needs a provider key in `.env`, never committed).
2. Run the kit with an `openai-compatible/<model>` `model_api` and
   `--env-file local.env --model-base-url http://localhost:8090/v1`.

`submission.yaml` currently holds this local configuration; for evaluation its `model_api` is set to a
`google-cloud/<id>` model and `model_base_url` is removed.

## License

Apache-2.0 (see `LICENSE`). `harness.py`, `serve.py`, `taskbridge.py` and `task-tools.ts` derive from the
kit's Apache-2.0 sample harness.
