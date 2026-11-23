---
name: cfd-fire-modelling
description: Fire and plume CFD - scales, resolution, unsteadiness, LES quality, time control, cost projection, verification. Use for any fire, smoke or plume CFD setup, review or disposition work.
---

# Fire and buoyant-plume CFD: physics, checks, time control, cost

## 1. Work like a CFD peer reviewer
- The firm's CFD procedure and the defaults it references govern; textbook values below are fallbacks. Give the source
  (document and clause) of every limit applied.
- Recompute every number from its inputs (HRR, ambient state, cell size, logs); never copy a report figure unchecked. Show
  formula, inputs with units, result, and the band/limit it is judged against. Identify run, mesh and settings.

## 2. Characteristic fire diameter and plume resolution index
- D* = ( Q̇ / (ρ∞ · c_p · T∞ · √g) )^(2/5)   [m]. Q̇ = total HRR [kW], ρ∞ [kg/m³], c_p [kJ/(kg·K)], T∞ [K], g [m/s²].
  Units: kW / (kg/m³ · kJ/(kg·K) · K · m^0.5/s) = (kJ/s)/(kJ/m³ · m^0.5/s) = m^2.5 → ^(2/5) = m.
  Check: Q̇ = 1000 kW, ρ∞ = 1.204, c_p = 1.005, T∞ = 293.15 K → denominator 1111 → D* ≈ 0.96 m (sanity: 1 MW ≈ 1 m).
- Plume resolution index R = D*/δx (cells across the characteristic diameter). FDS User Guide (citing the US NRC
  validation, NUREG-1824, where D*/δx spanned about 4 to 16): ~4 coarse, ~10 moderate, ~16 fine. Use the firm's band if
  it states one. δx = the cell size in the fire/plume region of the run whose results are reported (finest refinement
  level there; for non-cubic cells state which dimension - conservative is the largest).
- Ideal gas: ρ∞·T∞ = p∞/R_air (R_air = 287.05 J/(kg·K)), so D* ∝ Q̇^(2/5) · p∞^(-2/5): ambient temperature cancels
  when ρ∞ is computed consistently from p and T. Altitude matters: ISA p(z) = 101325·(1 − 2.25577e-5·z)^5.25588 Pa. Buoyancy scales with reduced gravity g·(T − T∞)/T.
  Use ambient properties consistent with the site.

## 3. Puffing and unsteadiness
- Pool fires puff (periodic large-vortex shedding near the base): Cetegen & Ahmed (1993) f ≈ 1.5/√D [Hz, D in m],
  D = physical source diameter (not D*, unless the standard says otherwise; record which length you used). Dimensionless
  form f·√(D/g) ≈ 0.48 (1.5/√9.81). Period T_p = 1/f. Check: D = 2 m → f = 1.06 Hz, T_p = 0.94 s. Data scatter around
  the correlation is of order ±10–20 %, so account for that scatter when comparing. Strouhal–Froude/Richardson forms
  (St = fD/U vs Fr = U²/(gD)) cover sources with momentum (Hamins et al. 1992). Non-circular source: D = √(4A/π).
- Regular residual oscillation can indicate physical unsteadiness; test it against the puffing frequency and exclude
  mesh, scheme and relaxation causes before concluding.
- Compare the monitored frequency with the correlation, stating the conversion.

## 4. LES quality measures
- Pope (2004) criterion: resolved fraction of TKE k_res/(k_res + k_sgs) ≥ ~0.8 (≤ 20 % modelled). FDS equivalent:
  'TURBULENCE RESOLUTION' (measure of turbulence resolution) ≤ ~0.2. Celik et al. (2005) LES_IQ ≥ 0.8 "good".
- State the region and averaging window of each LES-quality figure (report it for the region the conclusion concerns). Other indicators:
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
  writeFormat, writePrecision, timeFormat, timePrecision (must resolve the write interval),
  runTimeModifiable. Discretisation and solver settings must match the time mode; averaging starts after the flush.
- FDS: &TIME T_BEGIN/T_END/DT; &MISC CFL_MAX/CFL_MIN/VN_MAX; &DUMP DT_DEVC/DT_HRR/DT_SLCF/DT_RESTART (else duration/NFRAMES).
- Write interval: 2 samples per period is the Nyquist minimum (aliasing-prone); standards ask for N per puffing period
  (often 10–20+): Δt_write ≤ T_p/N, N from the governing procedure.
- End time = start-up flush (initial transient, often a number of periods or flow-through times, discarded) +
  statistics window (N periods, often ≥ 10–20): t_end ≥ t_start + (N_flush + N_stats)·T_p. maxDeltaT should not exceed
  the write interval or a fraction of T_p.

## 6. Wall-clock projection
- t_wall = N_cells · N_steps · c / N_cores, N_steps = (t_end − t_start)/Δt, c = core-seconds per cell-step from a
  benchmark on the same solver/models/hardware. Units: cells · steps · core·s/(cell·step) / cores = s. Check: 2e6 cells,
  30 s at Δt = 1 ms (3e4 steps), c = 2e-6 core·s, 64 cores → 1875 s. State every assumption.
- A benchmark is comparable only when time step, cell count, core count, models and output frequency are similar; say
  how any difference affects the projection.

## 7. Mesh verification scope
- Roache GCI (Celik et al. 2008 ASME JFE procedure): refinement ratio r = h_coarse/h_fine (≥ 1.3); observed order
  p = ln((f3 − f2)/(f2 − f1))/ln r (constant r, 3 grids, f1 finest); GCI_fine = F_s·|(f2 − f1)/f1|/(r^p − 1), F_s = 1.25
  (3 grids) or 3.0 (2 grids). Asymptotic check GCI_23 ≈ r^p·GCI_12. Oscillatory convergence (sign change) → p undefined.
- Scope: a grid study verifies only the quantities, conditions and solver mode it covered.

## 8. Technical note
- State the scope (case, run, settings, date), findings with numbers, conformance against the governing procedure,
  recommendation, open items and limitations.
