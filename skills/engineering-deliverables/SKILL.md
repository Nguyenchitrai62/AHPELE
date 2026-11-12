---
name: engineering-deliverables
description: Method for engineering design and calculation packages graded against requirements - document precedence, superseded documents, requirement/constraint registers, hard-constraint checks, unit discipline, optimisation within constraints, and schema-exact deliverable files (CSV, JSON, XLSX, ZIP, IFC). Use for any task that asks for calculations, a design, a plan, a schedule, a register or a structured submission.
---

# Engineering deliverables

## 1. Know exactly what is graded
- Copy every deliverable requirement from the instruction into `/tmp/ahpele/checklist.md`: path, file name, format,
  required columns/keys/tokens (exact spelling), units, row granularity ("one row per X and Y"), and any scoring rule.
- The instruction is a data contract. Use its column names, token vocabularies and IDs verbatim. Extra columns are
  usually harmless; missing or renamed ones are not.
- If the instruction states how the work is scored (e.g. hard constraints gate the score, cost objective, recall of a
  register), let that decide where effort goes: never trade a hard constraint for objective value.

## 2. Document precedence and status
- Read the governing specification first: it usually lists which standards, revisions and documents apply.
- Typical precedence (unless the project documents say otherwise): addenda / RFI responses / site instructions issued
  later > specification > drawings > schedules > vendor data > reference standards. Later dated responses override
  earlier ones on the same point.
- A document marked superseded, cancelled, withdrawn, void or draft, or an older revision of a document that exists in
  a newer revision, is not an authority. Do not cite it, do not take values from it. Record in your narrative that you
  saw it and why you set it aside.
- Words like "cancelled" inside a document's text often describe another document. Check before discarding.

## 3. Requirements table and register
- Before designing, list every hard requirement with: id, document, clause/table, requirement, limit value, unit, what
  it binds (which items). Save as `/tmp/ahpele/requirements.csv`.
- Hard requirements include: safety and code limits, permit/authorisation limits (discharge, noise, setbacks),
  capacities (power, flow, head, load), resource caps (equipment, crews, water, budget), milestones and deadlines.
- If a register is a deliverable, build it from this table. Cite real project documents and clauses, not the brief.
  Cite only documents that are in force.

## 4. Calculations
- Work in one unit system internally; convert at the boundary. Keep inputs, intermediate results and units in a script
  (`/tmp/ahpele/calc.py`) so numbers can be recomputed after every change.
- Take every input from a document you can cite; write assumptions down where the documents leave a choice.
- Cross-check: totals equal sums of parts, the same quantity has the same value in every file, schedules respect
  durations and predecessors, quantities respect the caps.

## 5. Build early, then improve
- Produce a complete first version of every deliverable early with conservative choices that satisfy all hard
  requirements, even if it is not optimal. An incomplete or missing file scores nothing.
- Never write placeholders (TBD, NaN, "to be determined") in a numeric field. If a value is genuinely not applicable,
  use the not-applicable convention the instruction allows (often blank, N/A or NONE).

## 6. Verify with code
- Write `/tmp/ahpele/check.py` that loads your deliverable files exactly as written and tests every requirement row and
  every checklist item (columns, tokens, units, ranges, cross-file consistency). Run it after every change.
- Run the format checker: `python3 /tmp/ahpele/bin/ahpele_check.py <deliverable paths>`.
- For CAD/BIM outputs, re-open the file with the standard library you wrote it with and check the entities, property
  sets and attributes the instruction names.

## 7. Optimise last
- Only after all hard checks pass: improve the objective (cost, performance) with a systematic search (enumerate
  options, or scipy.optimize when available), re-running the checks for every candidate. Keep the best feasible plan
  on disk at all times.
