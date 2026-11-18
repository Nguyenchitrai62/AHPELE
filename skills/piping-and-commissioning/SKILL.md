---
name: piping-and-commissioning
description: Engineering cross-checks for piped systems (hydronic, cooling water, process, fire) - hydraulics and pump duty points, flushing, cleaning and passivation, pressure testing, water treatment, discharge, commissioning cross-checks. Use for any piping, pump, flushing, commissioning or water-treatment task.
---

# Piping systems, flushing, testing and commissioning: engineering cross-checks
- Check every operating mode, stage or load case, not only the design case. For each mode list which
  components are in the flow/load path and check each against ALL of its limits (pressure drop, flow,
  temperature, particle size, pressure rating, pH, power) at that mode's own flow. When a mode changes the
  configuration (bypass removed, valve opened, equipment energised), recompute the system head for that mode
  and choose a flow that keeps every in-path component and the pump inside its limits. Apply each criterion
  to the stages or modes its clause names.
- Pumps: duty point = intersection of the system curve (static + friction ~ Q^2 + component dP scaled by
  (Q/Q_rated)^2) and the pump curve; never beyond the last published point. Parallel pumps share flow and
  each must make the full head; series pumps share head.
- When several limits apply to one parameter, control within all of them and state the resulting band.
- Show every required hold, cure, soak or recirculation period as an explicit schedule activity.
- When a standard gives different values in different clauses, use the clause whose scope matches the
  application and cite it.
- Test or inspection results count only with their cited evidence on file; a record citing missing evidence
  is not an accepted result.
- Effluent and permits: read the discharge authorisation for how each limit is measured (instantaneous, daily,
  total) and for any permitted alternative disposal.
- Fluids and water treatment: use the specification's definitions for acceptance criteria and dose basis
  volume; check makeup hardness/chloride/sulphate against each programme's admission limits; copper anywhere
  in the circuit needs an azole residual.
