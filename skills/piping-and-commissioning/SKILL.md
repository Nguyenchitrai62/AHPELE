---
name: piping-and-commissioning
description: Engineering cross-checks for piped systems (hydronic, process, fire) - hydraulics and pump duty points, pressure testing, flushing, water quality, discharge, commissioning. Use for any piping, pump or commissioning task.
---

# Piping systems, flushing, testing and commissioning: engineering cross-checks
- Check every operating mode, stage or load case, not only the design case. Recompute the system head for each
  configuration and check every component in the flow path against its limits (pressure, flow, temperature,
  velocity, rating). Apply each criterion to the stages or
  modes its clause names.
- Pumps: duty point = intersection of the system curve (static + friction ~ Q^2 + component dP scaled by
  (Q/Q_rated)^2) and the pump curve; never beyond the last published point. Parallel pumps share flow and
  each must make the full head; series pumps share head.
- When several limits apply to one parameter, control within all of them and state the resulting band.
- Show every required hold, cure, soak or recirculation period as an explicit schedule activity.
- When a standard gives different values in different clauses, use the clause whose scope matches the
  application and cite it.
- Check each test record against the evidence the specification requires (method, values, instruments, dates, signatures).
- Effluent and permits: read how the permit measures each limit (instantaneous, daily, total).
- Check water quality and materials against the treatment supplier's and the specification's limits.
