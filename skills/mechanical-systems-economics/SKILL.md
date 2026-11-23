---
name: mechanical-systems-economics
description: Pumps, piping and life-cycle cost - pump/fan curves, affinity laws, NPSH, parallel/series operation, pipe sizing (Darcy-Weisbach, Hazen-Williams), energy and life-cycle cost (present worth, escalation, FEMP/NIST 135), option comparison, expansion, insulation, vibration, TAB and acceptance tests.
---

# Mechanical systems and life-cycle economics

Project documents (specification, owner's LCC rules, tariff, manufacturer curves) govern; values marked "typical" are
for cross-checks only. Constants: g = 9.81 m/s²; water ρ ≈ 998 kg/m³ at 20 °C; 1 psi = 6.895 kPa = 2.31 ft water (SG 1);
1 m water = 9.79 kPa; 1 bar = 10.2 m; 1 hp = 0.7457 kW; 1 gpm = 0.06309 L/s = 0.2271 m³/h; 1 ft = 0.3048 m.

## 1. Pumps (and fans by analogy)
- Hydraulic power P[kW] = ρ·g·Q·H/1000 = Q[L/s]·H[m]·SG/102; IP whp = gpm·H[ft]·SG/3960. Shaft = hydraulic/η_pump;
  electrical input = shaft/(η_motor·η_VFD). Fans: P[W] = Q[m³/s]·Δp[Pa]/η; bhp = cfm·Δp[in.wg]/(6356·η).
- Affinity (same impeller): Q ∝ N, H ∝ N², P ∝ N³; small impeller trims (≲ 10-15 %) Q ∝ D, H ∝ D², P ∝ D³ roughly.
  They follow H ∝ Q² through the origin, which is NOT the system curve when static head or a DP setpoint exists.
- System curve H = H_static (+ control setpoint) + k·Q²; duty point = pump curve ∩ system curve; for a VFD find the speed
  whose scaled curve meets the required point, then its efficiency. Never extrapolate beyond the last published point.
- Preferred operating region typical 70-120 % of BEP flow (HI 9.6.3); check motor non-overload over the whole curve.
- NPSHa = (p_surface,abs − p_vapour)/(ρg) + z_s − h_f,suction (z_s > 0 when the liquid is above the impeller); IP
  NPSHa = 2.31·(p_abs − p_v)[psia]/SG + z_s − h_f. Require NPSHa ≥ NPSH3 × margin (HI 9.6.1, typical ratio 1.1-1.5).
  Water p_v: 20 °C 2.34 kPa, 40 °C 7.38, 60 °C 19.9, 80 °C 47.4, 100 °C 101.3; p_atm falls ~11 kPa per 1000 m altitude.
- Parallel: add flows at equal head, check one-pump runout and matched shutoff heads. Series: add heads at equal flow.
- VFD energy: compute each point from the system curve, not (Q/Q0)³, when static head or a DP setpoint exists; efficiency
  falls at low speed; VFD loss typical 2-5 %. Annual E = Σ P_input,i·hours_i over the load profile (bins or 8760 h).

## 2. Pipe sizing
- Darcy-Weisbach: h_f = f·(L/D)·V²/(2g); Δp = f·(L/D)·ρV²/2. Re = V·D/ν (water ν: 10 °C 1.31e-6, 20 °C 1.00e-6, 60 °C
  0.47e-6 m²/s). Laminar f = 64/Re (Re < 2300). Turbulent: Colebrook 1/√f = −2·log10(ε/(3.7D) + 2.51/(Re·√f)); explicit
  Swamee-Jain f = 0.25/[log10(ε/(3.7D) + 5.74/Re^0.9)]². Roughness ε: commercial steel 0.045 mm (0.00015 ft), drawn
  copper/PVC/PE 0.0015 mm, cast iron 0.26 mm; aged pipe rougher. Glycol: higher ν raises f; use the mix's properties.
- Hazen-Williams (water ~5-25 °C, turbulent only): SI h_f = 10.67·L·Q^1.852/(C^1.852·D^4.87) (m, m³/s, m); IP
  p = 4.52·Q^1.85/(C^1.85·d^4.87) psi/ft (gpm, inside diameter in inches; NFPA 13 form). C typical: new steel 120 (dry
  sprinkler 100), copper/plastic 150, unlined cast iron 100 (old 80). Use actual inside diameter for the schedule.
- Hydronic design typical (project spec governs): friction 100-400 Pa/m (1-4 ft/100 ft), velocity ≤ 1.2 m/s (4 fps)
  up to 50 mm, 1.2-3 m/s (4-10 fps) larger; pump suction slower (≤ 1.5-2 m/s); copper erosion limits ~2.4 m/s cold,
  ~1.5 m/s hot (> 60 °C). Low velocity (< 0.6 m/s) lets air and dirt settle.
- Minor losses h = K·V²/(2g) or equivalent length. Typical K: 90° elbow standard 0.3-0.9 (long radius 0.2-0.3),
  tee through 0.2-0.4, tee branch ~1.0, gate/ball valve open 0.05-0.2, butterfly 0.3-1, globe 6-10, swing check ~2,
  strainer 1-3 (clean; dirty much higher), entrance 0.5, exit 1.0. Coils, chillers, HX: manufacturer's Δp at actual flow,
  scaled by (Q/Q_rated)² (≈ 1.8-2 exponent).
- Control valves: Q[gpm] = Cv·√(Δp[psi]/SG); Q[m³/h] = Kv·√(Δp[bar]/SG); Kv = 0.865·Cv. Authority = Δp_valve /
  (Δp_valve + Δp_rest of circuit) typical ≥ 0.25-0.5. Index circuit (largest total Δp path) sets pump head.

## 3. Annual energy and life-cycle cost
- Energy: bin method Σ(load_i/efficiency_i)·hours_i; equivalent full-load hours only as a check. Electricity bill =
  Σ kWh·energy rate (time-of-use) + monthly peak kW·demand rate (+ ratchets, power-factor, fixed charges). Demand
  savings count only if they occur at the billing (or coincident) peak; a measure that saves kWh off-peak saves no kW.
- Water and chemicals: makeup volume × water rate + discharge volume × sewer rate (evaporation credit only if metered
  and allowed); chemical cost per unit makeup or per unit blowdown as the treatment vendor quotes.
- Discounting (end-of-year convention unless the rules say otherwise): P/F = 1/(1 + d)^n;
  P/A = [(1 + d)^n − 1]/[d·(1 + d)^n]; escalating annual cost A0 (today's price, escalating at e from year 1):
  PV = A0·(1 + e)/(d − e)·[1 − ((1 + e)/(1 + d))^n] (= A0·n when d = e). Check: d 3 %, n 20 → P/A = 14.877.
- Real vs nominal: (1 + d_nom) = (1 + d_real)·(1 + i); real d with constant prices, nominal d with inflated; never mix.
- US federal (FEMP, 10 CFR 436, NIST HB 135): real discount rate and energy escalation indices from the current HB 135
  Annual Supplement (region, sector, fuel); study period limit of the edition in force; constant dollars. Otherwise the owner's rules.
- LCC = initial + PV(energy) + PV(water/sewer, chemicals) + PV(O&M) + PV(repair/replacement) − PV(residual).
  Replace each component at the end of its service life within the study period (typical lives: ASHRAE Applications
  ch. 38 or owner data). Residual = replacement cost × remaining life/service life, discounted from the end year. Same
  study period and base date for every option; exclude sunk costs; include disposal if stated.
- Metrics: net savings NS = LCC_base − LCC_alt; SIR = PV(operational savings)/PV(added investment) (> 1 accepts);
  AIRR = (1 + d)·SIR^(1/n) − 1; simple payback = added cost/first-year savings; discounted payback = first year with
  cumulative discounted savings ≥ added cost. Lowest LCC among mutually exclusive options wins, not highest SIR.
- Sensitivity: vary discount rate, energy price/escalation, hours, efficiency, maintenance and life over stated ranges;
  report break-even values (tornado chart) and whether the option ranking changes.

## 4. Option comparison matrices
- Screen hard constraints (code, capacity, space, weight, noise, redundancy, schedule) as pass/fail first; a failing
  option is not scored. Tabulate raw values with units (first cost, LCC, kW, water, footprint, lead time, risk); state
  weights (sum 1) before scoring, normalise linearly, show raw and scored values, test the winner against weight changes.

## 5. Thermal expansion, anchors and guides
- ΔL = α·L·ΔT; α typical: carbon steel 11.7e-6/K (6.5e-6/°F; ≈ 1.2 mm per m per 100 K), copper 16.8e-6/K (9.3e-6/°F),
  stainless 304 17.3e-6/K (9.6e-6/°F), PVC ~54e-6/K (3e-5/°F), HDPE ~150-200e-6/K. ΔT from installation to the
  extreme operating (and cleaning/flushing) temperature both ways.
- Absorb with loops/offsets (guided-cantilever leg L = √(3·E·D·Δ/S_A), consistent units, S_A per ASME B31.9/B31.1)
  or expansion joints. Anchor at each end of a run; guides near joints (typical first ≤ 4D, second ≤ 14D from a bellows).
  Anchor load = friction of supports + spring force of joint/loop + pressure thrust p·A_effective for unrestrained
  bellows (often the largest term). Check branch connections for displacement.

## 6. Insulation and condensation
- Cylindrical heat flow per length q' = 2π·(T_i − T_a)/[ln(r2/r1)/k + 1/(h·r2)]; surface T_s = T_a ± q'/(2π·r2·h);
  surface coefficient h typical 5-10 W/m²·K (≈ 1-1.7 Btu/h·ft²·°F) in still indoor air. Method: ASTM C680 / 3E Plus.
- Cold surfaces: T_s must exceed the design ambient dew point (margin typical ≥ 1-2 K) at the worst humidity; continuous
  vapour retarder (ASTM C1136 jacket, low-perm, sealed seams and fittings). Hot surfaces: personnel protection
  T_s ≤ 60 °C/140 °F typical (ASTM C1055). Minimum thickness by ASHRAE 90.1/IECC table for fluid temperature and size.

## 7. Vibration isolation (ASHRAE Applications "Noise and Vibration Control")
- f_n = (1/2π)·√(k/m) = 15.76/√δ[mm] Hz = 3.13/√δ[in] Hz (δ = static deflection). Transmissibility (undamped)
  T = 1/|(f/f_n)² − 1|; isolation starts at f/f_n > √2; 90 % isolation needs f/f_n ≈ 3.3. Use the lowest forcing
  frequency (shaft speed). Typical spring deflection 25-50 mm (1-2 in) on upper floors / long spans, inertia bases
  for pumps and fans, flexible connectors at pipes and ducts, no short-circuits (rigid conduit, pipe supports).

## 8. Acceptance: TAB and functional testing
- TAB (AABC, NEBB, ASHRAE 111) to the spec tolerances; typical air terminals and totals −5/+10 %, hydronic flows ±10 %;
  report design vs measured, instrument calibration dates, final pump/fan speed, valve and damper positions.
- Functional performance tests (ASHRAE Guideline 0, Standard 202; data centres integrated systems tests): written
  procedure per sequence and every mode (normal, part load, failure/changeover, utility loss, alarms, seasonal), measurable
  acceptance criteria, trend logs, issues log with closure, deferred seasonal tests. A test without recorded evidence is
  not passed. Pressure tests per code (e.g. ASME B31.9 hydrostatic 1.5 × design pressure, no leaks) before insulation.
