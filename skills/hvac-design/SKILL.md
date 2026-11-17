---
name: hvac-design
description: HVAC and cooling design - heating/cooling loads, psychrometrics and coil conditions, ventilation (ASHRAE 62.1), data-centre cooling (TC 9.9, redundancy, PUE), chillers and cooling towers (range, approach, evaporation, blowdown), ducts and fans, selection at derated conditions. Use for any HVAC or heat-rejection task.
---

# HVAC design (designer's and reviewer's practice)

Project documents (design criteria, specification, adopted code edition, manufacturer data) govern. Values marked
"typical" are for cross-checks and first passes only; state in the deliverable which basis you used.
1 ton = 12,000 Btu/h = 3.517 kW; 1 W = 3.412 Btu/h; 1 cfm = 0.4719 L/s; 1 gpm = 0.06309 L/s; 1 in.wg = 249.1 Pa;
1 psi = 6.895 kPa = 2.31 ft water; ΔT 1 K = 1.8 °F (never add 32 to a difference).

## 1. Work order
1. Criteria: indoor setpoints/RH, outdoor design (ASHRAE climatic data: heating 99.6/99 % DB; cooling 0.4/1 % DB with
   mean coincident WB; dehumidification 0.4/1 % dew point; towers 0.4 % evaporation WB), altitude, occupancy, schedules,
   redundancy, code editions. 2. Zone, then block (coincident) loads. 3. Airflows, ventilation. 4. Coil states. 5. Plant
   at design and part load. 6. Ducts, pipes, fans, pumps. 7. Cross-check totals, units and every mode (incl. failure).

## 2. Heat transfer equations
- Q = ṁ·c_p·ΔT (air 1.006 kJ/kg·K = 0.240 Btu/lb·°F; water 4.19 kJ/kg·K = 1.0 Btu/lb·°F).
- Standard air (1.2 kg/m³ = 0.075 lb/ft³): sensible Qs[Btu/h] = 1.08·cfm·ΔT[°F], Qs[W] = 1.21·(L/s)·ΔT[K] (ASHRAE
  prints 1.23); latent Ql[Btu/h] = 0.68·cfm·ΔW[gr/lb] (7000 gr = 1 lb), Ql[W] = 3010·(L/s)·ΔW[kg/kg]; total
  Qt[Btu/h] = 4.5·cfm·Δh[Btu/lb], Qt[W] = 1.2·(L/s)·Δh[kJ/kg]. At altitude scale every factor by ρ/ρ_std.
- Water: Q[Btu/h] = 500·gpm·ΔT[°F]; Q[kW] = 4.19·(L/s)·ΔT[K]; chilled water 24/ΔT[°F] gpm per ton. Glycol: use the
  mix's ρ·c_p (30-40 % PG c_p ≈ 3.6-3.8 kJ/kg·K), so the same load needs roughly 10-15 % more flow.
- Conduction Q = U·A·ΔT, U = 1/ΣR incl. films. Infiltration cfm = ACH·V[ft³]/60 (L/s = ACH·V[m³]/3.6). Degree days:
  E = UA·HDD·24/η (UA in W/K with K·day, or Btu/h·°F with °F·day).
- Cooling load: envelope and solar (RTS method, ASHRAE Fundamentals ch. 18), people (typical office ~75 W/250 Btu/h
  sensible + ~55 W/200 Btu/h latent), lighting/equipment W × 3.412 Btu/h, ventilation and infiltration (sensible +
  latent), fan heat (a motor in the airstream adds its whole input), reheat. Block load = coincident peak, not the sum of
  zone peaks. One stated safety factor (typical ≤ 10 %). Supply cfm = Qs_room/(1.08·Δt), typical Δt 10-11 K (18-20 °F).

## 3. Psychrometrics (p[kPa] = 101.325·(1 − 2.25577e-5·Z[m])^5.2559)
- W = 0.621945·p_w/(p − p_w); RH = p_w/p_ws(t); dew point = t where p_ws = p_w; p_ws ≈ 0.6112·exp(17.62·t/(243.12 + t))
  kPa (Magnus, t °C; prefer psychrolib or CoolProp HAPropsSI when installed). h = 1.006·t + W·(2501 + 1.86·t) kJ/kg dry
  air; IP h = 0.240·t + W·(1061 + 0.444·t) Btu/lb. From wet bulb t*: W = [(2501 − 2.326t*)·W_s* − 1.006(t − t*)]/
  (2501 + 1.86t − 4.186t*). Check value: 25 °C, 50 % RH → W ≈ 0.0099 kg/kg, h ≈ 50 kJ/kg, dew point ≈ 13.9 °C.
- Mixing: mass-weighted W and h. SHR = Qs/Qt. The coil process runs from the entering state toward the apparatus dew
  point (ADP); bypass factor BF = (t_leave − ADP)/(t_enter − ADP) (typical 0.05-0.15 for 6-8 rows). The leaving dew point
  must sit below the room dew point by enough to absorb the room latent load; typical leaving 12.8/12.2 °C (55/54 °F)
  DB/WB. Coil load = ṁ_air·(h_in − h_out). Humidifier water = ṁ_air·ΔW (IP lb/h = 4.5·cfm·ΔW[lb/lb]).

## 4. Ventilation: ASHRAE 62.1 Ventilation Rate Procedure (use the adopted edition's tables)
- Vbz = Rp·Pz + Ra·Az; Voz = Vbz/Ez (typical Ez 1.0 cool ceiling supply; 0.8 warm ceiling supply ≥ 8 K/15 °F above
  space with ceiling return; 1.0-1.2 underfloor). Typical rates: office 5 cfm (2.5 L/s)/person + 0.06 cfm/ft² (0.3 L/s·m²),
  5 people/1000 ft²; classroom 10 cfm (5 L/s) + 0.12 cfm/ft² (0.6 L/s·m²); conference 5 + 0.06; retail 7.5 + 0.12.
- System: single zone Vot = Voz; 100 % outdoor air Vot = ΣVoz; multi-zone recirculating Vot = Vou/Ev with
  Vou = D·ΣRp·Pz + ΣRa·Az, D = Ps/ΣPz, simplified Ev = 0.88D + 0.22 (D < 0.6) else 0.75, or the Appendix A method from the
  critical Zpz = Voz/Vpz (VAV zones at minimum airflow govern). Exhaust from the exhaust table (typical public toilet
  50 cfm per fixture continuous / 70 intermittent); balance makeup and pressurisation; energy recovery per 90.1.

## 5. Data-centre cooling
- ASHRAE TC 9.9 Thermal Guidelines (5th ed. 2021; older editions differ): recommended IT inlet 18-27 °C (64.4-80.6 °F),
  dew point −9 to 15 °C, RH ≤ 70 % (≤ 50 % with high pollutants). Allowable A1 15-32, A2 10-35, A3 5-40, A4 5-45 °C (RH
  8-80/80/85/90 %, max dew point 17/21/24/24 °C); H1 allowable 5-25, recommended 18-22 °C. Derate the allowable maximum
  1 °C per 300 m above 900 m (A1/A2). Inlet is measured at the rack face, not at the return or unit discharge.
- IT airflow cfm = 3.16·W/ΔT[°F]; m³/s = kW/(1.21·ΔT[K]); server ΔT typical 11-14 K → ~120-160 cfm/kW (55-75 L/s
  per kW). Cooling units typically supply 10-20 % more than IT airflow (bypass/leakage; containment reduces it). Air
  cooling typical to ~15-25 kW/rack, then rear-door/in-row/liquid. SHR ≈ 1.0: rate coils on sensible capacity.
- Redundancy N, N+1 (spare of the largest unit), 2N (two independent systems), 2(N+1): check with the largest unit or
  one path failed, at design ambient and on utility loss (restart, ride-through, UPS fans/pumps, storage). PUE = annual
  facility energy / annual IT energy (ISO/IEC 30134-2), never a peak ratio; WUE = site water L / IT kWh.

## 6. Chillers and heat rejection
- COP = cooling/input; kW/ton = 3.517/COP = 12/EER; EER = 3.412·COP. Heat rejected = cooling + compressor input
  ≈ 1.15-1.3 × cooling (typical). Condenser water 1 K colder typically cuts kW/ton 1.5-3 %.
- IPLV/NPLV (AHRI 550/590): IPLV = 0.01A + 0.42B + 0.45C + 0.12D (A-D = COP or EER at 100/75/50/25 % load); in kW/ton
  IPLV = 1/(0.01/A + 0.42/B + 0.45/C + 0.12/D). NPLV uses project conditions. Compare with 90.1 Path A/B of the edition.
- Evaporator approach = leaving CHW − saturated suction (typical 1-3 K). Tower: range = hot − cold water (typical
  5.6 K/10 °F at 3 gpm/ton); approach = cold water − entering WB (typical 3-4 K/5-7 °F; under 2.8 K/5 °F is costly);
  effectiveness = range/(range + approach). Design WB + recirculation allowance (typical 0.5-1 K) for enclosed towers.
- Water balance: evaporation E ≈ Q_rejected/h_fg (h_fg ≈ 2430 kJ/kg = 1045 Btu/lb) ≈ 0.15 % of flow per K of range,
  i.e. ≈ 0.85-1 % per 10 °F (some heat leaves as sensible). Drift D 0.001-0.005 % of circulating flow (modern
  eliminators; 0.02 % older). Cycles C = tower/makeup concentration (e.g. chloride) = M/(B + D). Blowdown
  B = E/(C − 1) − D; makeup M = E + B + D = E·C/(C − 1). Typical C 3-6, capped by silica, hardness, chloride and the
  treatment programme. Annual water = Σ(hourly load-based E), never design E × 8760.
- Dry cooler / air-cooled condenser: approach to ambient DB typical 5-8 K (10-15 °F); size at design DB + recirculation
  (typical +2-3 K) with glycol properties; capacity falls and power rises with ambient: use the maker's derated curve.
- Waterside economiser: full free cooling when WB ≤ CHW supply − tower approach − HX approach (plate HX typical 1-2 K);
  partial while tower water < CHW return. Airside by DB or enthalpy limits. Count hours from 8760 h weather (TMY) or bins.

## 7. Ducts and fans
- Pv = 0.6·V² Pa (V m/s); VP[in.wg] = (V[fpm]/4005)². Δp = friction + ΣK·Pv (ASHRAE fitting database) + components
  (filters at stated loading, wet coils, terminals, diffusers) + system effect.
- Equal friction typical 0.08-0.10 in.wg/100 ft (0.65-0.8 Pa/m); static regain for long high-velocity mains. Velocity
  typical (noise governs): low-pressure mains 5-7.5 m/s (1000-1500 fpm), branches 3-4.5 m/s (600-900 fpm), outdoor-air
  louvres ≤ 2.5 m/s (500 fpm) free area. Rectangular equivalent De = 1.30·(ab)^0.625/(a + b)^0.25; aspect ≤ 4:1.
  SMACNA leakage F = CL·p^0.65 cfm/100 ft² of duct surface (p in.wg).
- Fan laws: Q ∝ N·D³, Δp ∝ ρ·N²·D², P ∝ ρ·N³·D⁵. System curve Δp = Δp_fixed + k·Q² (a static-pressure setpoint is a fixed
  part). Operating point = fan curve ∩ system curve, right of the surge/stall region, near peak efficiency.
- Shaft power P[W] = Q[m³/s]·Δp[Pa]/η_fan; bhp = cfm·TSP[in.wg]/(6356·η_fan); input adds motor, belt and VFD losses.
  90.1 fan power limit (e.g. Option 1: hp ≤ 0.0011·cfm CV, 0.0015·cfm VAV; check edition). Fan heat ΔT[K] ≈
  Δp[Pa]/(1210·η_fan), motor out of the airstream.

## 8. Equipment selection and pitfalls
- Select at project design conditions (entering air/water, flow, fluid, altitude, ambient + recirculation), not the
  catalogue rating point; check sensible and total capacity, flow, pressure drop, noise, power, footprint, access.
- Altitude: ρ/ρ_std = (p/101.325)·(293.15/T); fans move the same volume but less mass and pressure; the 1.08/1.21
  factors scale with ρ. Pitfalls: kW/ton vs COP inverted; °F ΔT used as K; ventilation latent counted twice; gross vs
  net capacity (fan heat); summed zone peaks; design WB used for annual water; coil checked only at the design point.
