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
- Give each service its own elevation band (top of steel/slab down to the lowest allowed point), with gaps between bands
  at least as large as the clearance rules; a change of band is a vertical segment. Typical order from the top: zone kept
  clear below sprinkler deflectors, cable tray / busway (separated from each other), then larger pipes; an access-floor
  plenum is another band when it is allowed.
- Route mains along aisles and parallel to the grid, with branches at right angles to the equipment they serve. Keep
  routes out of column lines and away from the tops of racks and equipment that need service access.
- Crossing priority when services compete for space: gravity drainage > large ducts and pipes > pressure pipes > cable
  tray and busway > small conduit. The more flexible service yields, and changing elevation is preferred to rerouting
  horizontally.

## 3. Clearances that count as clashes or code violations
- Insulation, lagging, flanges and support envelopes are part of the solid that must not clash.
- Sprinkler heads: keep the zone directly below each deflector clear (NFPA 13 obstruction rules: about 18 in / 460 mm
  below deflectors, with extra rules for obstructions near heads). Wide obstructions need heads beneath them.
- Electrical equipment: dedicated space above switchboards, panelboards and PDUs is kept free of foreign systems,
  notably piping (NEC 110.26: the width and depth of the equipment, up to 6 ft / 1.8 m above it or to the structural
  ceiling); working space in front stays clear.
- Keep power and data separated (a stated minimum distance on at least one axis) and keep the minimum headroom below the
  lowest service.

## 4. Model the contract's conventions into the geometry
- Read how the instruction defines clashes and clearances, and build the solids that way: any covering, envelope,
  clear zone or extent the contract says to include must be in the modelled solids, or checked with
  `ahpele_clash.py --clearance CLASS=MM`.

## 5. Verify on the exported file, iterate to zero
- Validate and clash-check the file you will submit, not the lists in your script (a schema or EXPRESS-rule error
  usually fails the whole file, e.g. every IfcShapeRepresentation needs its RepresentationIdentifier such as 'Body'):
  `python3 /tmp/ahpele/bin/ahpele_clash.py model.ifc --point <entry x,y,z>`. Resolve hard clashes by moving whole runs to
  their band, then re-run until there are none.
- Continuity: each service must be one connected network that starts at its entry point; check that every row or piece
  of equipment it must serve is within the required distance and over the required share of its length.
- Re-check code clearances and efficiency (total length) after the last change, then re-export and check again.
