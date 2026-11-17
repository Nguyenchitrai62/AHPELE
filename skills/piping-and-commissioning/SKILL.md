---
name: piping-and-commissioning
description: Engineering cross-checks for piped systems (hydronic, cooling water, process, fire) and their flushing, cleaning, passivation, pressure testing, water treatment, discharge and commissioning plans - every operating mode, pump duty points, overlapping limit bands, required hold periods as scheduled activities, choosing the clause whose purpose matches, test evidence, effluent limits. Use for any piping, pump, flushing, commissioning or water-treatment task.
---

# Piping systems, flushing, testing and commissioning: engineering cross-checks
- Check every operating mode, stage or load case, not only the design case. For each mode list which
  components are in the flow/load path and check each against ALL of its limits (pressure drop, flow,
  temperature, particle size, pressure rating, pH, power) at that mode's own flow. When a mode changes the
  configuration (bypass removed, valve opened, equipment energised), recompute the system head for that mode
  and choose a flow that keeps every in-path component and the pump inside its limits; a minimum-velocity
  rule only applies to the stages that state it.
- Pumps: duty point = intersection of the system curve (static + friction ~ Q^2 + component dP scaled by
  (Q/Q_rated)^2) and the pump curve; never beyond the last published point. Parallel pumps share flow and
  each must make the full head; series pumps share head.
- Several bands on one quantity (inhibitor band, azole band, vendor limit, permit limit): control to the
  intersection and write that intersection in every row that states the band. A vendor limit "at all times"
  applies to every stage, including turnover/maintenance.
- A required period (contact, soak, hold, recirculation, curing, test hold) must exist as explicit scheduled
  activities whose summed hours meet it. An idle gap or an envelope that contains it is not the period.
  Every stage with a duration in a plan file must have matching activities in the schedule.
- When a standard gives several values for the same quantity in different clauses, take the one from the
  clause whose stated PURPOSE matches the purpose the project spec names (e.g. "for keeping X in
  suspension", "for passivation"), not the first number found.
- Test or inspection results count only with their cited evidence on file; a record citing missing evidence
  is not an accepted result.
- Effluent and permits: local limits are usually instantaneous at the discharge point and apply per stream;
  a stream that cannot meet one goes to the alternative route. Volume caps are programme totals.
- Fluids and water treatment: rinse/acceptance criteria are usually relative to the makeup water analysis;
  check makeup hardness/chloride/sulphate against each programme's admission limits; dose on the volume the
  spec names (system vs flush volume); copper anywhere in the circuit means an azole residual.
