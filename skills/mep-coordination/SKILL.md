---
name: mep-coordination
description: How an MEP coordinator routes and coordinates services (cable tray, busway, pipes, ducts, sprinklers) in a 3D model - elevation bands per service, routing along aisles and the grid, crossing priority, clearance zones from fire and electrical codes, iterative clash detection on the exported file, system continuity and coverage checks, and confirming the model against the drawings. Use for any routing, coordination, clash-free modelling or BIM layout task.
---

# MEP coordination and routing

## 1. Background model first, confirmed against the drawings
- Build the coordination background (structure, equipment, racks, terminals, ceilings/floors) before routing anything.
- After every export, confirm the model against the drawings: print the world positions of a few known items (grid
  intersections, room corners, one item per equipment type) and compare them with the drawing dimensions. Equipment of
  one type all at the same spot, or a model a thousand times too small or large, means placements or units are wrong.
- Units: drawings in metric sets are in millimetres. Raw IFC coordinates (IfcCartesianPoint, extrusion depths, profile
  dimensions) are in the project length unit. Library helpers that take a placement matrix in SI units (for example
  ifcopenshell.api placement calls with is_si=True) convert for you; never convert twice.

## 2. Plan the space before drawing routes
- Give each service its own elevation band, ordered by gradient, size, access and clearance, with gaps between bands at
  least as large as the clearance rules; a change of band is a vertical segment.
- Route mains along aisles and parallel to the grid, with branches at right angles to the equipment they serve. Keep
  routes out of column lines and away from the tops of racks and equipment that need service access.
- In shallow zones separate services in plan and prove the vertical fit with sections.
- Avoid routing liquid-carrying piping above electrical equipment and distribution; where unavoidable, provide drip
  protection.
- Crossing priority when services compete for space: gravity drainage > large ducts and pipes > pressure pipes > cable
  tray and busway > small conduit. The more flexible service yields, and changing elevation is preferred to rerouting
  horizontally.

## 3. Clearances that count as clashes or code violations
- Insulation, lagging, flanges and support envelopes are part of the solid that must not clash.
- Leave a coordination allowance between services for installation tolerance, hangers and insulation, on top of required
  clearances. Establish whether the sizes given are bare or overall (insulated, jacketed); if that stays unclear, keep
  space for the larger, or state the assumption.
  When a requirement says an envelope counts but not whether it is already in the drawn size, keep the envelope as a
  gap around the run as well where space allows; `--clearance CLASS=MM` lists what is closer (the end connection to the
  equipment served is expected there).
- Where a run passes a floor, wall or roof, provide a real opening larger than the run with its envelope (sleeve and
  fire-stopping where required, agreed with the structural engineer), and prefer places that are open anyway. If the
  acceptance check is not known to subtract openings, build the host in pieces around the penetration where allowed.
- Sprinkler heads: keep the zone directly below each deflector clear (NFPA 13: 18 in (457 mm) below deflectors, or the
  value the project states, with extra rules for obstructions near heads). Wide obstructions need heads beneath them.
- Electrical equipment: dedicated space above switchboards, switchgear, panelboards and motor control centers is kept
  free of foreign systems (NEC 110.26(E): the width and depth of the equipment, up to 6 ft / 1.8 m above it or to the
  structural ceiling); working space in front stays clear.
- Separate power from data by the distance the project, TIA-569 or the manufacturer requires, and keep the minimum
  headroom below the lowest service.

## 4. Model each element as the product it is
- Choose the IFC class and PredefinedType from the target schema's definition of the physical product (look it up in the
  schema, do not guess from an error message), and group each service in its own distribution system.
- Terminate each system at its documented source and loads; if an elevation is not given, state the assumption or raise an
  RFI.

## 5. Required envelopes
- Model insulation, envelopes and clear zones the project requires, or check them as clearances with
  `ahpele_clash.py --clearance CLASS=MM`.

## 6. Verify on the exported file, iterate to zero
- Validate and clash-check the file you will submit, not the lists in your script (a schema or EXPRESS-rule error
  can make the file unreadable, e.g. every IfcShapeRepresentation needs its RepresentationIdentifier such as 'Body'):
  `python3 /tmp/ahpele/bin/ahpele_clash.py model.ifc --point=<source x,y>` (plan point: each network's distance and
  elevation range there). Resolve hard clashes by moving whole runs to
  their band, then re-run until there are none.
- Review the close gaps it lists: every gap smaller than the project's allowance is either moved or accepted for a stated reason.
- Continuity: each system is one connected network from its source, and every load it serves has a connection. Runs join
  at an end, a fitting or a tap; running side by side is not a connection, however small the gap.
- After ANY geometry change (a run added, moved or resized, often in response to a review), re-run the whole
  coordination check on the exported file (validation, hard clashes, clearances between systems, continuity): fixing one
  service often breaks another.
- Re-check code clearances and efficiency (total length) after the last change, then re-export and check again.
