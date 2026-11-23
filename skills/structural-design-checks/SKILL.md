---
name: structural-design-checks
description: Practical structural engineering knowledge for designing and checking roofs, decks, diaphragms, frames and foundations against project criteria - load paths, snow drift geometry, wind uplift zones, steel deck tables, diaphragm stiffness and collectors, validating your own analysis model, zoning for cost. Use for any structural design, check or optimisation task.
---

# Structural design and checking

## 1. Project criteria first, code defaults second
- A project design-criteria document usually modifies the code (drift rules, live-load reductions, deflection limits,
  resistance factors). Apply the project's method exactly as written; use code defaults only where it is silent.
- When the criteria say a value "is taken from" or "is governed by" a standard clause, that clause is the governing
  source. In a requirement register, give that standard clause a row of its own (standard, edition, clause number as
  printed, value), in addition to the criteria row that invokes it, even when the standard is not in the project files.
- Never mix design bases: allowable (ASD) tables are checked with service-level combinations, factored resistances (phi)
  with factored (LRFD) combinations. Resisting dead load in uplift/overturning is factored down (typically 0.9D) and
  excludes loads that are not permanently attached (hung services, equipment allowances).

## 2. Snow loads
- Balanced snow acts everywhere, including under drifts and across low obstructions. Drift clear height is measured from
  the top of the balanced snow (hc = h - hb).
- A drift is a triangle against ONE face: peak at the face, zero at distance w, and it extends only along the length of
  that face (no infinite strips). Evaluate every face for every wind direction the criteria require; take the envelope
  per point unless the criteria say to superimpose.
- Windward vs leeward drifts use different fetch lengths and factors; truncated drifts (hd > hc) have peak hc*gamma and a
  different width rule. Parapets are windward-type obstructions measured from their inside face.
- Seismic weight usually includes a share of the flat-roof snow load above a threshold (ASCE 7: 20 % of pf where pf > 30
  psf); drifts are normally excluded from seismic weight.

## 3. Wind uplift on roof cladding and deck
- Components-and-cladding zones: corners carry the highest suction, then the perimeter band, then interior. An
  attachment zone must satisfy the worst pressure zone it overlaps.
- Fastener uplift capacity per unit area = design tension of one fastener / its tributary area (cover width / number of
  fasteners across it x span). Pull-over usually governs thin sheet; it scales with sheet thickness.

## 4. Steel roof deck
- A higher gage number is a THINNER sheet. Price, strength and stiffness all rise with thickness.
- Typical economical deck design: one base gage and attachment over most of the roof (governed by balanced snow,
  interior uplift and low shear), with heavier gage or attachment only where drifts, corner/perimeter uplift or high
  diaphragm shear (near braced frames and boundaries) require it.
- Gravity tables give allowable TOTAL load including self weight for a stated span condition (often 3-span). Deflection
  is checked under live or snow load only. A deck run shorter than the tabulated span condition needs its own capacity.
- Diaphragm tables vary with gage, support pattern, sidelap type and sidelap count; read the column labels explicitly and,
  when the manual prints the formula behind the table, recompute every value you use from it. Some sidelap types are not
  permitted on heavier gages.
- Deck is not placed over framed openings; zones stop at opening frames, and edges at boundaries and openings usually get
  a minimum attachment regardless of demand.

## 5. Diaphragms, chords and collectors
- Force distributes to vertical elements by relative stiffness (rigid/semi-rigid) or by tributary width (flexible). In
  a semi-rigid diaphragm the distribution depends on deck stiffness: re-run the analysis with the deck specified.
- Collectors and their connections to the vertical system are designed for overstrength-amplified seismic force (Omega_0)
  in the higher seismic design categories; chords and the diaphragm itself use the unamplified force. Compare the
  AMPLIFIED collector force with the collector/splice capacity; the weakest link (often a bolted splice) governs.
- Hand checks for any diaphragm model: unit shear ~ reaction / diaphragm depth at the support lines; chord force ~ M / d;
  sum of frame reactions = applied force; with accidental torsion, frames on both sides change in opposite senses.

## 6. Validate your own analysis before designing with it
- Before using a numerical model for any decision: check equilibrium (sum of reactions = applied load, to 0.1 %), run a
  one-element or patch test with a closed-form answer, compare the full model with a hand estimate, and check units on
  one member by hand. Wildly changing results between code edits mean the model is still wrong.
- When you fix a bug in a model or an input, redo the design selection and the optimisation from scratch: decisions
  made with the wrong model are not valid. Write every reported number from the model output by script.

## 7. Zoning and cost
- Build a map of the minimum specification each location needs (gravity, deflection, uplift, shear, boundary rules)
  and zone to that demand map, within any zoning limits the project sets. Compare several layouts.
- Price each layout completely with the project's cost rules (including any per-zone or set-up costs) and keep the
  cheapest feasible layout.
- Recheck all hard limits for every candidate; keep the best feasible layout on disk.

## 8. Units and models (BIM / CAD)
- Read IfcUnitAssignment: raw IfcCartesianPoint coordinates are in the file's length unit (often millimetres) and are
  relative to a chain of local placements. ifcopenshell.geom.create_shape returns vertices in SI metres by default,
  whatever the file unit. Convert once, at the boundary, and print a few known dimensions (grid spacing, footprint) to
  confirm.
- DXF: check $INSUNITS and the title block; drawings may disagree with the coordinated model, and the transmittal or model
  note says which governs.
