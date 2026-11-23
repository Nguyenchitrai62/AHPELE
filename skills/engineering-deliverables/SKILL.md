---
name: engineering-deliverables
description: Method for engineering design and calculation packages - document precedence, superseded documents, requirement/constraint registers, hard-constraint checks, unit discipline, optimisation within constraints, and schema-exact deliverable files (CSV, JSON, XLSX, ZIP, IFC). Use for any work that asks for calculations, a design, a plan, a schedule, a register or a structured submission.
---

# Engineering deliverables

## 1. Know exactly what is asked
- Copy every deliverable requirement from the instruction into `/tmp/ahpele/checklist.md`: path, file name, format,
  required columns, keys and allowed values (exact spelling), units and row granularity.
- The instruction is a data contract. Use its column names, allowed values and IDs verbatim. Extra columns are
  usually harmless; missing or renamed ones are not.
- If evaluation criteria are stated, read them when setting priorities; never trade a hard constraint for objective value.

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
- Hard requirements include: safety and code limits, permit limits, capacities, resource limits, milestones.
- If a register is a deliverable, build it from this table. Cite the originating document and clause.
  Cite only documents that are in force.

## 4. Calculations
- Work in one unit system internally; convert at the boundary. Keep inputs, intermediate results and units in a script
  (`/tmp/ahpele/calc.py`) so numbers can be recomputed after every change.
- Take every input from a document you can cite; write assumptions down where the documents leave a choice.
- Cross-check: totals equal sums of parts, the same quantity has the same value in every file, schedules respect
  durations and predecessors, quantities respect the caps.

## 5. Build early, then improve
- Produce a complete first version of every deliverable early with conservative choices that satisfy all hard
  requirements, even if it is not optimal. Keep a complete valid version on disk.
- Leave no placeholders; mark not-applicable values as the instruction defines.

## 6. Verify with code
- Write `/tmp/ahpele/check.py` that loads your deliverable files exactly as written and tests every requirement row and
  every checklist item (columns, allowed values, units, ranges, cross-file consistency). Run it after every change.
- Run the format checker: `python3 /tmp/ahpele/bin/ahpele_check.py <deliverable paths>`.
- For CAD/BIM outputs, re-open the file with the standard library you wrote it with and check the entities, property
  sets and attributes the instruction names.
- IFC written by hand (no BIM library): generate it with a small script, not by typing STEP lines. Follow the schema:
  every attribute in order (`$` for an unset one), every REAL with a decimal point (`20.` or `20.0`, never `20`),
  double apostrophes inside strings. Run `python3 /tmp/ahpele/bin/ahpele_ifc.py <file>` until it reports 0 errors. One
  unreadable entity can make the whole file unreadable.
- Placed or routed 3D models (coordination models, MEP routing, layouts): verify the FILE, not your script's variables.
  `python3 /tmp/ahpele/bin/ahpele_clash.py <file.ifc>` re-reads it with ifcopenshell's geometry engine in world
  coordinates; resolve what it reports. Coordinates in `IfcCartesianPoint` are in the project length unit; library helpers
  such as `ifcopenshell.api` placement calls take SI metres and convert for you, so do not convert by hand as well.

## 7. Optimise last
- Only after all hard checks pass: improve the objective (cost, performance) with a systematic search (enumerate
  options, or scipy.optimize when available), re-running the checks for every candidate. Keep the best feasible plan
  on disk at all times.
