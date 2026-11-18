---
name: cost-estimate-review
description: How a reviewer checks an engineer's estimate (bid/bond estimate) against plans and a published unit-price schedule - quantities by reach/station and structure count, unit consistency, exact price matching, rounding rules, extensions, subtotal, contingency and bond amount, plus a line-by-line reconciliation and scripted self-check. Use for any cost estimate, bond estimate, quantity or unit-price review.
---

# Engineer's estimate review

## 1. Set the rules before touching numbers
- Write down, from the instructions/estimate notes, every rule: which section(s) are in scope, the price source
  (schedule title, edition/date), what to do with items the schedule lacks, "Actual"/lump-sum handling, rounding
  (what, to what, up/nearest), the measurement convention, contingency %, bond % and bond rounding. These rules
  beat general practice. Quote them in the memo.
- Records: estimate (as carried: item no., description, unit, qty, unit price, extension), plan sheets (plan +
  profile + details + notes), schedules/worksheets (pipe schedule, structure table, HGL sheet), the price schedule.
  Use drawing-takeoff for counting and measuring from the sheets.

## 2. Quantities
- Linear items (pipe, curb, ditch) by reach: length = |station down - station up| for each reach between
  structures; sum per item (same size AND material/class). Cross-check plan stationing, profile, and any pipe
  schedule; when they disagree, report it and say which governs (profile/schedule usually carries the design
  length; plan callout may be rounded).
- Measurement convention matters: centre-to-centre of structures vs inside face to inside face (subtract half of
  each structure's inside dimension). Use the convention stated in the estimate, specification or schedule; if
  none, state the one used. Slope length = sqrt(dx^2 + dz^2) differs only for steep reaches.
- Don't forget laterals/connector pipes (inlet to main), stub-outs, outfall pipe beyond the last structure,
  and reaches drawn on another sheet across a match line.
- Count structures by type and size (inlet type, manhole diameter, junction box, headwall/endwall, flared end,
  cleanout, outlet structure, riprap pad). Each schedule/plan tag counts once; reconcile counts across sheets.
- Area/volume items: SY = SF/9, CY = CF/27; TON = CY x unit weight (use the stated density; riprap typically
  ~1.4-1.7 ton/CY in place - cite the source). Riprap pad volume = length x width x thickness.
- Items with no measurable basis on the plans: apply the instruction's rule for them, otherwise flag them; state
  which you did.
- Apply rounding only where instructed and only to the stated quantity (e.g. "round up" = ceiling, per item
  or per reach as the rule says - state which). Never round intermediate values otherwise.

## 3. Unit prices
- Match the schedule entry on description, size, material/class and unit exactly (24" RCP is not 24" HDPE; a
  48" manhole is not a 60" one; EA vs LF vs LS). Unit of the estimate must equal the schedule unit; convert the
  quantity, not the price, if they differ.
- Allowance / actual-cost / lump-sum items: follow the instruction's rule for them and state it.
- No matching schedule entry: flag it (what the plans show, the closest entries and why they do not fit); never
  invent or interpolate a price; treat the subtotal as the instruction directs.
- Watch for prices taken from the wrong size row, outdated schedule edition, or units swapped.

## 4. Arithmetic
- Extension = qty x unit price (to the cent). Subtotal = sum of extensions in the section. Then the estimate's own
  sequence: e.g. subtotal -> contingency (% of subtotal) -> total -> bond = stated % of the stated base (often
  100% performance; some agencies 110-125%, plus a labour-and-material bond of 50-100%). Follow the estimate's
  formula exactly and only change the inputs you corrected.
- Bond rounding: apply the stated rule (e.g. up to the next $1,000 or $100) once, at the end. Show the unrounded
  value, then the rounded one.
- Report other sections' totals unchanged if out of scope, but recompute the grand total and bond with the
  corrected section.

## 5. Reconciliation table (the deliverable core)
Columns: item no. | description | unit | qty carried | qty corrected | unit price carried | unit price corrected |
extension carried | extension corrected | delta | source (sheet + station/tag, schedule page/row) | note.
- One row for every change (quantity and/or price), plus rows for items shown on the plans but missing from the
  estimate (carried = 0) and items in the estimate with no plan basis (flag; keep or remove per the rules).
- Footer: carried subtotal, corrected subtotal, net delta (= sum of row deltas - check it), contingency, total,
  unrounded and rounded bond.

## 6. Self-check (do it with a script)
- Put every line in a CSV/JSON and recompute in Python with Decimal: per-reach lengths from stations, rounding per
  rule, extensions, subtotal, delta sum, contingency, bond and its rounding. Assert corrected subtotal - carried
  subtotal == sum(deltas).
- Re-read the estimate once more for lines you did not touch: confirm their arithmetic too (carried extension may
  itself be wrong - an arithmetic correction is a change and gets a row).
- Every number in the memo must match the script output and carry a unit ($, LF, EA, SY, CY, TON, LS) and a
  source. Give one corrected subtotal and one bond figure, not options.
