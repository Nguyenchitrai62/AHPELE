---
name: cost-estimate-review
description: How a reviewer checks an engineer's estimate against plans and a published unit-price schedule - quantities, unit consistency, price matching, extensions, roll-up, reconciliation and scripted self-check. Use for any cost estimate, quantity or unit-price review.
---

# Engineer's estimate review

## 1. Set the rules before touching numbers
- Write down the rules given for scope, price source, measurement, rounding and roll-up; they govern.
- Records: the estimate as carried, plan sheets (plan, profile, details, notes), schedules and worksheets, the price schedule.
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
- Follow the stated measurement and rounding rules, and state how you applied them.

## 3. Unit prices
- Match the schedule entry on description, size, material/class and unit exactly (24" RCP is not 24" HDPE; a
  48" manhole is not a 60" one; EA vs LF vs LS). Unit of the estimate must equal the schedule unit; convert the
  quantity, not the price, if they differ.
- Handle allowances and unmatched items as the estimate's rules state; never invent or interpolate a price.
- Watch for prices taken from the wrong size row, outdated schedule edition, or units swapped.

## 4. Arithmetic
- Extension = qty x unit price (to the cent). Subtotal = sum of extensions in the section. Then the estimate's own
  sequence: e.g. subtotal -> contingency (% of subtotal) -> total -> bond = stated % of the stated base (often
  100% performance; some agencies 110-125%, plus a labour-and-material bond of 50-100%). Follow the estimate's
  formula exactly and only change the inputs you corrected.
- Show unrounded values before rounded ones. Recompute every total that depends on a corrected line; leave others
  unchanged.

## 5. Reconciliation table (the deliverable core)
Columns: item no. | description | unit | qty carried | qty corrected | unit price carried | unit price corrected |
extension carried | extension corrected | delta | source (sheet + station/tag, schedule page/row) | note.
- One row for every change (quantity or price). Reconcile both ways: plans to estimate, estimate to plans.
- Footer: carried and corrected subtotals, net delta (= sum of row deltas - check it) and every roll-up line.

## 6. Self-check (do it with a script)
- Put every line in a CSV/JSON and recompute in Python with Decimal: lengths, extensions, subtotals and roll-up. Assert
  corrected subtotal - carried subtotal == sum(deltas).
- Re-read the estimate once more for lines you did not touch: confirm their arithmetic too (carried extension may
  itself be wrong - an arithmetic correction is a change and gets a row).
- Every number in the memo must match the script output and carry a unit and a source.
