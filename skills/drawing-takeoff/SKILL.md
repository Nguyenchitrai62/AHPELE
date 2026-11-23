---
name: drawing-takeoff
description: How a professional estimator counts and measures items from a drawing set (raster or vector) - sheet index, legend first, per-item register with coordinates, match lines and enlarged plans, revisions and addenda, and the cross-checks before pricing. Use for any quantity takeoff, equipment count, schedule check or bill of materials built from drawings.
---

# Quantity takeoff from drawings

## 1. Build the sheet index first
- One row per sheet: number, title, discipline (A/S/M/E/P/FA/T…), type (plan, enlarged plan, schedule, legend,
  details, section), scale, revision number and date from the title block, notes that point to other sheets.
- US National CAD Standard sheet ID: discipline letter + type digit (0 general/legends/notes, 1 plans, 2 elevations,
  3 sections, 4 enlarged/large-scale views, 5 details, 6 schedules and diagrams, 9 3D) + sequence, e.g. E-101. Office
  series vary: confirm on the sheet index and the sheets themselves.
- Dimensions on metric sets are millimetres unless noted; "do not scale" notes mean counts and grid references
  come from the drawing, distances from dimensions or from the grid, not from a ruler. If you must measure,
  calibrate on the graphic scale bar or the grid spacing of THAT sheet (scales differ between sheets).
- List the addenda, RFIs and bulletins with their dates. Read each for the sheets and items it changes.

## 2. Legend and notes before counting
- Transcribe the symbol legend into a table: mark, shape (outline, fill, inner bar/letter, dashed vs solid), text.
  Pay attention to pairs that differ only by fill, dashing or an inner mark; those are the common misreads.
- Read the legend notes, general notes, sheet notes and keynotes of every sheet you count: they set the counting
  conventions and can add or exclude items.
- Resolve a doubtful match by looking at it enlarged; record the decision and the reason.
- Raise any symbol the legend does not identify as a query; carry no quantity you cannot trace.

## 2b. Tools for reading the sheets (`python3 /tmp/ahpele/bin/ahpele_drawing.py ...`)
- `grid SHEET --cols 4 --rows 3` writes an overview with a labelled grid and one tile per cell: read the sheet cell by
  cell (tiles are large enough to see symbols) and refer to places by cell (B3) and pixel coordinates.
- `crop SHEET --box x0,y0,x1,y1 --dpi 300` zooms on a legend, a title block, a keynote or a doubtful symbol.
- `find SHEET --template legend_symbol.png --rot 0,90,180,270` lists every place that looks like a symbol, with scores:
  cut the template from the legend or from one clear instance on the same sheet at the same dpi. Look at the overlay;
  review every mid-score candidate crop; run it once per similar legend symbol and give each place to the best match.
  Never drop candidates by threshold alone, and never invent counts or locations: every register row points to a place.
- `census SHEET --legend DIR` does this for all legend symbols in one pass (DIR holds one crop per mark, the symbol
  only, named by the mark): each place goes to the best-fitting mark with its runner-up, and shapes no mark fits are
  listed. Start the register from its csv, then review the flagged places and the overlay.
- `mark SHEET --points register.csv` draws your counted items on the sheet: compare with the sheet for misses and doubles.

## 3. Count into a per-item register, never into totals
- Every counted item is one row: sheet, x, y (sheet coordinates), mark, grid bay, how found, flags
  (reference-only, duplicate-of, deleted-by-revision, added-by-note). All totals, per-sheet and per-condition tables
  are computed from this register by code.
- Count symbol by symbol, sheet by sheet; mark what you counted on an overlay image and look at it. Recount any sheet
  where the overlay shows a symbol without a mark or a mark without a symbol. Review low-confidence detections
  individually; do not drop them by threshold alone.
- Locations: derive them from the structural grid lines on the sheet, following the set's stated convention.

## 4. Avoid double counting and missing items
- Match lines: items on the far side are shown for reference (often greyed); count each item on the sheet that
  schedules it. Convert sheet coordinates to a common building grid to check that no item is counted on two sheets.
- Count areas shown at larger scale once, from the sheet that governs; deduplicate overlapping details by position.
- Keyed and general notes can require items that are not drawn: count them as the note says, record the basis
  (what was counted, on which sheet) and add them to the register flagged added-by-note. Count from the
  document that governs under the order of precedence and compare with any other stated quantity. Where
  drawings and schedules disagree, apply the order of precedence the contract sets and report the discrepancy.
- Revision clouds/addenda: list every item inside each cloud with coordinates, then apply the deletion/addition
  exactly as described, as explicit operations on the register (delete these rows, add these rows). Check the revision date against the addendum date.

## 5. Conditions and components
- Where an item's accessories depend on location or mounting, take the condition from the plans and the required
  components from the specification and record both. When a rule is geometric, compute it from coordinates by code.

## 6. Cross-checks before pricing
- Sum per sheet = sum per type = sum per condition, for every type.
- Account for every legend item.
- Repetitive layouts (typical bays or rooms) usually give repetitive counts; investigate outliers.
- Narrative (basis of estimate) and tables agree: same sheets, same counts, same exclusions.
- Price by the contract's rules and state the basis of each quantity.
