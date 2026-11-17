---
name: cfd-fire-modelling
description: Fire and buoyant-plume CFD review knowledge - characteristic fire diameter D*, plume resolution index, puffing frequency, why steady solves of fire plumes fail, LES quality checks, transient time-control (OpenFOAM controlDict / FDS), write interval and end time, wall-clock projection, mesh verification scope, writing a technical disposition. Use for any fire/smoke/plume CFD setup, review or disposition task.
---

# Fire and buoyant-plume CFD: physics, checks, time control, cost

## 1. Work like a CFD peer reviewer
- The firm's modelling standard / reference dictionary governs; textbook values below are fallbacks. Quote the clause for
  every limit applied; where the standard leaves a value case-specific, say what you took it from.
- Recompute every number from its inputs (HRR, ambient state, cell size, logs); never copy a report figure unchecked. Show
  formula, inputs with units, result, and the band/limit it is judged against. Track attempt, mesh and solver mode.

## 2. Characteristic fire diameter and plume resolution index
- D* = ( Q̇ / (ρ∞ · c_p · T∞ · √g) )^(2/5)   [m]. Q̇ = total HRR [kW], ρ∞ [kg/m³], c_p [kJ/(kg·K)], T∞ [K], g [m/s²].
  Units: kW / (kg/m³ · kJ/(kg·K) · K · m^0.5/s) = (kJ/s)/(kJ/m³ · m^0.5/s) = m^2.5 → ^(2/5) = m.
  Check: Q̇ = 1000 kW, ρ∞ = 1.204, c_p = 1.005, T∞ = 293.15 K → denominator 1111 → D* ≈ 0.96 m (sanity: 1 MW ≈ 1 m).
- Plume resolution index R = D*/δx (cells across the characteristic diameter). FDS User Guide (citing the US NRC
  validation, NUREG-1824, where D*/δx spanned about 4 to 16): ~4 coarse, ~10 moderate, ~16 fine. Use the firm's band if
  it states one. δx = the cell size in the fire/plume region actually used for the result the report rests on (finest
  refinement level there; for non-cubic cells state which dimension - conservative is the largest).
- Ideal gas: ρ∞·T∞ = p∞/R_air (R_air = 287.05 J/(kg·K)), so D* ∝ Q̇^(2/5) · p∞^(-2/5): ambient temperature cancels
  when ρ∞ is computed consistently from p and T. Altitude matters: ISA p(z) = 101325·(1 − 2.25577e-5·z)^5.25588 Pa; at
  1000 m p ≈ 89.9 kPa → D* ×1.049 (+4.9 %), R rises the same. A file using ρ = 1.2 kg/m³ with a hot T∞ (or sea-level ρ at
  an elevated site) is internally inconsistent: flag it and give the corrected D* and R. Hot ambient also lowers
  buoyancy for a given plume temperature (reduced gravity g·(T − T∞)/T). Ambient inputs must represent the site/design
  condition (elevation, design temperature), not a solver default; say what site conditions do to D*, R and buoyancy.

## 3. Puffing: a buoyant fire plume has no steady solution
- Pool fires puff (periodic large-vortex shedding near the base): Cetegen & Ahmed (1993) f ≈ 1.5/√D [Hz, D in m],
  D = physical source diameter (not D*, unless the standard says otherwise; record which length you used). Dimensionless
  form f·√(D/g) ≈ 0.48 (1.5/√9.81). Period T_p = 1/f. Check: D = 2 m → f = 1.06 Hz, T_p = 0.94 s. Data scatter around
  the correlation is of order ±10–20 %, so agreement within that is a match. Strouhal–Froude/Richardson forms
  (St = fD/U vs Fr = U²/(gD)) cover sources with momentum (Hamins et al. 1992). Non-circular source: D = √(4A/π).
- A steady (SIMPLE / steadyState ddt) solver on a puffing plume cannot converge: residuals stall on a plateau and
  oscillate, monitors cycle. That is the physics, not a mesh, relaxation or scheme fault; more iterations, relaxation or
  refinement will not fix it. Verdict: no steady solution exists; run transient (LES as fire practice expects).
- Prove it: convert the residual/monitor oscillation to a frequency (cycles / simulated time; if only iterations are
  logged, state the pseudo-time step used to convert, or say conversion is not possible) and compare with the
  correlation: difference % = |f_obs − f_exp| / f_exp × 100. Report f and T to the requested precision.

## 4. LES quality measures
- Pope (2004) criterion: resolved fraction of TKE k_res/(k_res + k_sgs) ≥ ~0.8 (≤ 20 % modelled). FDS equivalent:
  'TURBULENCE RESOLUTION' (measure of turbulence resolution) ≤ ~0.2. Celik et al. (2005) LES_IQ ≥ 0.8 "good".
- Evaluate it in the region the resolution index describes (plume/flame zone), time-averaged over the statistics window
  after start-up. Domain-averaged or far-field values are dominated by quiescent ambient cells and say nothing about
  the plume - a figure taken outside the region of interest does not support the resolution claim. Other indicators:
  Δ/η (Kolmogorov scale), cell Reynolds number, inertial-range spectra. Grid convergence is ill-defined in implicit-filter
  LES (filter = cell size): acceptance rests on R + resolved fraction + sensitivity of the quantities of interest.

## 5. Transient time control
- Courant number Co = |u|·Δt/δx (OpenFOAM: 0.5·Σ|φ_f|·Δt/V per cell, max reported). LES practice maxCo ≈ 0.5–1 (≤ 1
  for explicit stability; ~0.5 for accuracy with PIMPLE); FDS defaults CFL_MAX = 1.0, CFL_MIN = 0.8. fireFoam also has
  maxDi (diffusion number). Velocity scale: McCaffrey intermittent-region centreline u ≈ 1.9·Q̇^(1/5) m/s (Q̇ in kW;
  1 MW → 7.7 m/s), or √(g·D*). Δt ≈ maxCo·δx/u_max: 0.05 m cells, 7.7 m/s, Co 0.5 → Δt ≈ 3.2 ms.
- OpenFOAM system/controlDict: application (buoyantPimpleFoam / fireFoam), startFrom (startTime | latestTime),
  startTime, stopAt endTime, endTime [s], deltaT [s, initial], adjustTimeStep yes, maxCo, maxDeltaT [s], writeControl
  adjustableRunTime (Δt is trimmed to land exactly on write times; runTime does not; timeStep counts steps), writeInterval
  [s for run-time controls, steps for timeStep], purgeWrite (0 = keep all; N = keep last N - destroys time history),
  writeFormat, writePrecision, timeFormat, timePrecision (must resolve the write interval, e.g. 0.0125 s needs ≥ 4
  digits or directories collide), runTimeModifiable. Steady→transient also changes fvSchemes ddtSchemes (steadyState →
  backward/Euler) and fvSolution (SIMPLE → PIMPLE: nOuterCorrectors, nCorrectors); averaging starts after the flush.
- FDS: &TIME T_BEGIN/T_END/DT; &MISC CFL_MAX/CFL_MIN/VN_MAX; &DUMP DT_DEVC/DT_HRR/DT_SLCF/DT_RESTART (else duration/NFRAMES).
- Write interval: 2 samples per period is the Nyquist minimum (aliasing-prone); standards ask for N per puffing period
  (often 10–20+): Δt_write ≤ T_p/N. "Largest allowed" = T_p/N_min, rounded DOWN to the stated precision.
- End time = start-up flush (initial transient, often a stated number of periods or flow-through times, discarded) +
  statistics window (N periods, often ≥ 10–20): t_end = t_start + (N_flush + N_stats)·T_p, rounded UP. "Shortest
  allowed" uses the standard's minimum N values. maxDeltaT should not exceed the write interval or a fraction of T_p.
- Authorized vs delivered block: list every differing key with both values; an absent key = solver default (name it).

## 6. Wall-clock projection
- t_wall = N_cells · N_steps · c / N_cores, N_steps = (t_end − t_start)/Δt, c = core-seconds per cell-step from a
  benchmark on the same solver/models/hardware. Units: cells · steps · core·s/(cell·step) / cores = s. Check: 2e6 cells,
  30 s at Δt = 1 ms (3e4 steps), c = 2e-6 core·s, 64 cores → 1875 s = 0 h 31 min. Matrix = per-case × cases (÷ concurrent
  jobs only if the basis allows it). Report hours and minutes; state every assumption. Failed-run cost = iterations ×
  cost per iteration (or the logged ClockTime); compare with one authorized case.
- The basis is invalid (figure becomes an optimistic lower bound, indicative only) when: actual Δt < benchmark Δt
  (finer cells, higher velocity, Courant limit binding); the benchmark already ran at maxCo, leaving no Courant margin
  for higher plume velocities; adaptive Δt shrinks during growth/puffing peaks; cell count, core count (parallel
  efficiency), models (radiation, combustion) or write frequency (I/O) differ; maxDeltaT caps Δt below the Courant
  value. Courant margin = maxCo / Co_bench: Δt can grow at most by that factor (and not past maxDeltaT). Test each
  condition the basis sets, one by one, and say met / not met with numbers.

## 7. Mesh verification scope
- Roache GCI (Celik et al. 2008 ASME JFE procedure): refinement ratio r = h_coarse/h_fine (≥ 1.3); observed order
  p = ln((f3 − f2)/(f2 − f1))/ln r (constant r, 3 grids, f1 finest); GCI_fine = F_s·|(f2 − f1)/f1|/(r^p − 1), F_s = 1.25
  (3 grids) or 3.0 (2 grids). Asymptotic check GCI_23 ≈ r^p·GCI_12. Oscillatory convergence (sign change) → p undefined.
- Scope: it verifies THAT quantity, at THOSE locations, for THAT HRR/ambient/solver mode and time step. It does not
  cover other quantities (e.g. heat flux vs temperature, visibility), other locations, other fire sizes (D* and R change),
  transient statistics if done on a steady run, or LES resolution (needs R + resolved fraction). Say both explicitly.

## 8. Technical disposition / review note
- Structure: run reviewed (case, attempt, mesh, date) → findings with numbers (expected vs observed, % difference) →
  verdict → conformance table vs the firm's standard (item, clause, required, delivered, conforming/non-conforming,
  corrective value) → authorized run (full block, governing clause) → delta vs delivered → cost → carry-forward → open
  items and who must decide → reviewer, date, stamp/limitations block (what was and was not reviewed).
- A failed steady attempt can carry forward: mesh (if verified), boundary conditions (state the inlet's defining
  settings: HRR or fuel mass flux, area, temperature, turbulence), thermophysical/radiation/combustion setup, and fields
  mapped as an initial condition (mapFields; still needs a start-up flush). NOT usable: its "converged" values or stats.
- Item cannot close → name the evidence that would close it (computation, location, acceptance value), new run or not.
