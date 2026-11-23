---
name: technical-verification-review
description: Independent verification of a design, submittal, calculation or test report - basis, inputs, recomputation, disposition. Use for any technical review or verification work.
---

# Technical verification review

The reviewer's job is to decide, from the record, whether the item can be relied on for the work it releases. Do not
adopt the requester's framing: verify independently, then decide.

## 1. Fix the basis before checking anything
- **As-of date**: the date the request states. Documents dated after it are out of scope;
  say you set them aside. Events before it (RFIs, field reports, logs, NCRs) are in scope even if the designer ignored them.
- **Governing requirement**: the specification section (number, title, edition/date in force), the referenced standards
  and their editions, any project criteria, addenda and RFI responses that modify them. Quote the clause you apply.
- **Item under review**: title, designer/author, revision, date, transmittal. Build a revision table: rev, date,
  sealed/signed (by whom, licence), what changed, how it was transmitted. Rules:
  - Identify the revision in force and its seal status; changes to inputs require the dependent checks to be redone by
    the responsible engineer.
  - A revision issued for construction or verification must carry the seal and signature the contract requires; otherwise
    treat it as information.
  - Check the seal belongs to the right discipline and jurisdiction, and the revision is the one actually transmitted.
- **Responsibility**: read the contract/spec for who designs what (delegated design by the contractor's specialty
  engineer, temporary-works engineer, designer/engineer of record (EOR), geotechnical engineer of record, testing agency,
  inspector). Responsibility follows the contract and the seal: the party that sealed a design revises it.

## 2. Check the inputs against the record
List every design input with its value, unit and the document it came from, then the value the project record supports:
- Site investigation: boring/CPT logs (layer elevations and thicknesses, soil type, N-values, strengths, lab tests),
  the nearest boring to the work, groundwater levels (logged, stabilised, seasonal high, perched, artesian).
- Later field evidence: excavation/field reports, field observations, as-built elevations and foundation records,
  RFIs and their answers, NCRs, monitoring readings, test reports.
- Loads and surcharges: adjacent foundations, equipment, traffic, stockpiles, staged loads, live-load portion.
- Geometry and sequence: dimensions, depths, elevations (check the datum), stages, removal of supports.
A design built on an input the record contradicts (e.g. a soil parameter, load, level or dimension that differs from
the record) is not verified, however good its arithmetic.

## 3. Recompute the governing checks yourself
- Write a script (`/tmp/ahpele/verify.py`) with every input, its source and unit; recompute each governing check
  (capacity/demand, factor of safety, settlement, stability, % compaction...) with the record's inputs and, separately,
  the designer's inputs. Report both: "designer: X; with the record's inputs: Y; required: Z".
- State the method and standard used (formula, chart, code clause), the acceptance criterion and its source.
- Flag differences > ~5-10% and explain the cause (input, method, arithmetic).
- Classify every check in a table: check | designer's result | reviewer's result | criterion | **status**
  | reason (the input that changed, and the record that shows it). A check depends on its inputs: redo it when one changes.

## 4. Effects beyond the item
- Effects on adjacent and existing works (undermining,
  surcharge, dewatering drawdown and settlement, vibration, loss of support, heave, changed drainage). Name the elements
  (grid lines, footings, slabs, utilities) and give the magnitude or the check needed, plus protection and monitoring
  (instrument type, baseline, alert/action thresholds, frequency).
- Interfaces: other register items, inspections or hold points that depend on this one.

## 5. Disposition (use the register's own vocabulary if it has one)
- **Verified / accepted / closed**: all governing checks pass on the in-force revision with record inputs.
- **Accepted with conditions / accepted as noted**: passes, provided stated conditions are met (each condition
  specific, owned, timed). Use only when the conditions are minor and do not change the design basis.
- **Revise and resubmit / returned**: a check fails or rests on a wrong input; designer must revise and reseal.
- **Not verified - item remains open**: basis missing. Close an item only on evidence on file.
- Distinguish "rejected" (non-compliant) from "incomplete" (cannot judge). Dependent work waits for release under the project's procedure.

## 6. Required actions
One row per deliverable: what (e.g. revised calculation sealed and signed, updated drawings, monitoring plan,
additional borings or lab tests, retest at failed locations, survey, engineer's letter) | who (named party/role per the
contract) | reviewed by whom | needed before which activity | review time (from the spec, e.g. N working days).

## 7. Schedule
Work out the effect on dependent dates with a script.

## 8. Memo and register
- Follow the template provided and fill every section.
- Every number carries a unit and names the record it comes from (document, revision, table/page, boring, date).
- Register entry: item ID, disposition, decisive reason, actions and owner, date and status, consistent with the memo.
- If the task exposes a tracker/register application, update it and read it back (see workplace-apps).

## Write determinations the reader can verify
- For every check and every question in the request: the specific fact found in the record (value, unit, source and
  location) and a definite conclusion, and why.
- State the cause of each non-conformance (which input, assumption, revision or site condition) and the specific item
  that must be produced, by whom, before which activity.

## Review like a senior engineer, not a paperwork checker
- Read the subject's own records line by line (as-built notes, inspection and test records, photos, schedules,
  submittals): for each line note the material, method, label or condition, check it against the code edition and
  standards that govern, and record the result in a line-review table (line, requirement, conforms yes/no, evidence).
  Procedural approvals by others (inspector, AHJ, another reviewer) are evidence, not proof.
- Walk every operating state or construction stage: what is energised, loaded, flowing, open or exposed in each; what
  must keep working (protection, monitoring, drainage, access); where water, load or current
  goes when it leaves the element (downstream receiver, adjacent or existing work).
- Keep to the stated scope and address everything that bears on the question.
- Decide late: write the case for each possible disposition with its evidence before choosing; then commit to one.
- Write for the reader: answer first, then the basis; keep the memo as short as the question allows; report values to
  a sensible precision with units; an external letter carries no internal references.
