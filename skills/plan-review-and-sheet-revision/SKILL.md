---
name: plan-review-and-sheet-revision
description: Plan sets and sheet revisions - sheet index, title and revision blocks, clouds and deltas, comment-response matrices, propagating a change across plan/profile/details/notes/schedules, landscape plant schedules and code tables, editing DXF with ezdxf without disturbing other content, QA/QC before reissue.
---

# Plan review and sheet revision (civil, site, landscape)

The project's own drawing standard, the agency's checklist and its comment letter govern; conventions below are
typical (US National CAD Standard, NCS) - follow what the existing set already does when it differs. Order of work:
read the comment letter and current set -> build the sheet index -> comment-response matrix -> make each change ->
propagate it -> update title/revision blocks and index -> QA/QC -> issue with the response matrix.

## 1. Set organisation and sheet index
- NCS sheet ID = discipline (G, V survey, C, L, A, S, M, P, E) + type digit (0 general/index/legend/notes, 1 plans,
  2 elevations, 3 sections, 4 enlarged, 5 details, 6 schedules, 9 3D) + sequence, e.g. C-101. Office series vary
  (C-0 notes, C-1 existing/demo, C-2 layout, C-3 grading, C-4 utilities, C-5 ESC, C-6 P&P, details; L planting,
  planting details, irrigation, irrigation details).
- Sheet index: number, title, current revision and date per sheet, matching the title blocks exactly; added and
  deleted sheets shown as the set's practice does.
- Title block: project, owner, consultant, sheet title/number, scale + scale bar, date, drawn/checked, seal, revisions.

## 2. Revision control
- Revision block row: number (or letter), date (ISO or set format), concise description naming the change or the
  comment it answers ("Revised per City comments dated ...; relocated hydrant"), by / checked. Never renumber or
  delete previous rows; add the new row on top/bottom per the block's existing order. Pre-issue review sets often
  use letters (A, B, C), issued-for-construction sets numbers (0, 1, 2); continue the series in use.
- Mark every change for THIS revision: cloud around the changed area (geometry, text, schedule row) plus a delta
  (triangle with the revision number) next to the cloud. Clouds from previous revisions are usually removed, deltas
  may remain (office practice). A change without a cloud, or a cloud with nothing changed, is a QA failure.
- Only revise sheets that actually change; each revised sheet gets the new row and date, unrevised ones keep theirs.
  Superseded files are not edited further; write the revision to a new file name if the task asks for one.

## 3. Comment-response matrix
- One row per comment, numbered as the reviewer numbered them: comment no., reviewer/agency and letter date,
  reference (sheet/detail/page), comment text verbatim, response, sheet(s) and detail(s) changed, revision/delta
  no., status (Addressed / Partially / Not adopted - justification / Clarification requested / Open), owner.
- Response style: state what was done and where ("Hydrant relocated to sta 12+40; see C-401 delta 2"), or give the
  technical reason and supporting reference when not adopted. Never "Noted" or "Will comply" alone. The response
  must match the drawing exactly (same values, same sheets); answer every comment, including ones needing no change.
  Flag comments that trigger other submittals (drainage study amendment, permit modification, calc update).

## 4. Propagating a change (the step most often missed)
- For every changed object list where else it appears and update all of them: plan view, profile, sections,
  details and detail callouts, enlarged plans, general/keyed notes and keynote legend, schedules (structures, pipes,
  plants, fixtures), quantity tables and estimates, legends (add a symbol only if used; remove unused), labels and
  leaders, stationing/coordinates, match lines, other disciplines' sheets (utility vs landscape vs grading conflicts).
- Examples: moving a pipe changes inverts, slopes, lengths, crossings, profile, structure schedule and quantity;
  removing a tree changes the symbol count, plant schedule quantity, label, tree-protection plan, mitigation total,
  and possibly irrigation; changing a grade changes spot elevations, slopes, ADA compliance, drainage arrows, volumes.
  New annotation uses the set's text style/height, does not overlap linework, and keeps units consistent.

## 5. Landscape plans
- Plant schedule columns: key/symbol, quantity, botanical name (Genus species 'Cultivar'), common name, size (trees:
  caliper per ANSI Z60.1, measured 6 in above grade up to 4 in cal, 12 in above for larger; evergreens by height;
  shrubs by container #1/#3/#5 or height), root (B&B, container), spacing, remarks. Botanical name governs.
- Reconcile counts: quantity per key = symbols on plan = sum of plan labels ("3 QV") across all sheets and match
  lines; groundcover/massing quantity from area and spacing: square A/s^2, triangular A/(0.866 s^2) = 1.155 A/s^2.
  Report any discrepancy with location; do the counting in code from the DXF/blocks when available.
- Code requirements (typical forms, the local ordinance governs): street trees per length of frontage, parking-lot
  interior landscape % and island every N spaces, perimeter buffers/screens by adjacent use (width, plants per
  100 ft, opaque height), minimum tree canopy or replacement inches, species diversity (e.g. <= 10 % one species,
  <= 20 % one genus, <= 30 % one family), native/drought-tolerant share. Tabulate required vs provided per item.
- Clearances (typical): sight triangles (plants <= 2.5-3 ft, canopy >= 7-8 ft), trees 5-10 ft from water/sewer/
  storm lines and 10 ft from hydrants, none in easements without consent, small trees under overhead lines.
- Tree protection: DBH at 4.5 ft (1.37 m); protection zone radius ~1-1.5 ft per inch DBH (or drip line, whichever the
  ordinance says); fencing before clearing, no grading, trenching, parking or storage inside; arborist for work
  within; removal mitigation per ordinance (often inch-for-inch).
- Irrigation: point of connection, meter, backflow preventer (RPZ/PVB per code), static pressure vs head
  requirements, zones by hydrozone (spray/rotor turf separate from drip for shrubs/trees), head-to-head coverage,
  matched precipitation, rain/ET sensor. Water budget where adopted (e.g. California MWELO): MAWA = ETo x 0.62 x
  [ETAF x LA + (1 - ETAF) x SLA] gal/yr (ETo in/yr, ft2; ETAF 0.55 residential, 0.45 non-residential); ETWU <= MAWA.

## 6. CAD and DXF practice
- Layers (NCS form discipline-major-minor-status, e.g. C-STRM-PIPE, L-PLNT-TREE, C-TOPO-MAJR-E): put new objects on
  the existing layer for their kind; status E existing, D demolish, N new. Colour/linetype BYLAYER.
- Units: header $INSUNITS (1 in, 2 ft, 4 mm, 5 cm, 6 m, 21 US survey ft); $MEASUREMENT 0 imperial / 1 metric.
  Annotation in model space = plotted height x scale (0.1 in at 1" = 20' -> 2.0 ft; 2.5 mm at 1:100 -> 250 mm).
- ezdxf: `doc = ezdxf.readfile(p)` (damaged file: `from ezdxf import recover; doc, aud = recover.readfile(p)`);
  `msp = doc.modelspace()`; `doc.layouts` (title blocks often in paper space). Query `msp.query('TEXT MTEXT')`,
  `msp.query('INSERT[name=="TREE-01"]')`, `msp.query('*[layer=="L-PLNT"]')`. TEXT: `e.dxf.text`, `e.dxf.insert`
  (aligned text also uses `e.dxf.align_point`); MTEXT: `e.text` raw with codes (\P newline, {\f..;}), `e.plain_text()`
  to read, `e.dxf.insert`, `e.dxf.char_height`. Blocks: `ins.dxf.name`, `ins.dxf.insert`, `ins.attribs`
  (`a.dxf.tag`, `a.dxf.text`), `ins.get_attrib_text('TAG')`; set `a.dxf.text = 'new'`. Definitions in
  `doc.blocks[name]`. Dimensions: `d.get_measurement()`, override text `d.dxf.text` ('<>' = measured).
  Add: `msp.add_text('X', height=h, dxfattribs={'layer': L}).set_placement((x, y))`, `msp.add_mtext(...)`,
  `msp.add_blockref(name, (x, y)).add_auto_attribs({...})`, `msp.add_lwpolyline(pts, close=True)`; delete with
  `msp.delete_entity(e)`. Save with `doc.saveas(out)` keeping the original DXF version.
- Preserve everything not intended to change: edit entities in place (same handle, layer, style), never rebuild the
  drawing. Verify: entity counts per type/layer before vs after differ only by the intended edits; re-read the saved
  file; render (`from ezdxf.addons.drawing import matplotlib as m; m.qsave(msp, 'check.png')`) and look at it.
  Revision clouds: closed LWPOLYLINE with arc bulges on the cloud layer; delta = block or triangle + text.
  PDF-only sets: overlay clouds/text on a copy (e.g. PyMuPDF); never guess the CAD content.

## 7. QA/QC before reissue
- Every comment row has a response and the drawing shows it; every cloud has a delta, a revision-block row and a
  matching matrix entry; sheet index = title blocks (number, title, revision, date).
- Counts, quantities and schedule totals recomputed from the drawing; labels, callouts and keynotes point to
  existing details/sheets; legends list only used symbols; north arrows, scales, match lines, stationing consistent.
- Values identical across plan, profile, detail, notes, schedules, calcs and estimate; code tables (required vs
  provided) recomputed; seal/date fields updated; deliverable file names and formats exactly as requested.
