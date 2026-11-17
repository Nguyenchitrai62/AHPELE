---
name: electrical-power-design
description: LV/MV power distribution design - load schedules and demand, conductor and device sizing (ampacity, terminal ratings, 125 % rules), voltage drop, short-circuit currents and equipment ratings, transformers, grounding, motor circuits, NEC and IEC 60364 bases. Use for any electrical design or check.
---

# Electrical power distribution design (designer's and checker's practice)
Project documents govern (adopted code edition, spec, utility rules, drawings). Values below are typical or from a recent
NEC edition; section numbers move between editions: cite the adopted one and re-read its table before quoting.

## 0. Order of work and sanity checks
Basis (voltages, grounding, utility fault kA and X/R, code, spec) -> load schedules -> demand -> feeders/transformers ->
conductors (ampacity, then VD) -> fault current per bus -> ratings -> selectivity -> grounding; one script, one size set.
- 3φ I = S/(√3·V_LL) = P/(√3·V_LL·PF); 1φ I = S/V. A per kVA: 480 V 1.203; 400 V 1.443; 208 V 2.776; 240 V 1φ 4.167;
  4.16 kV 0.139; 13.8 kV 0.0418. 1 hp = 0.746 kW (≈ 1 kVA/hp for motors). 1 kcmil = 0.5067 mm²; AWG 10 = 5.26 mm²,
  6 = 13.3, 2 = 33.6, 1/0 = 53.5, 4/0 = 107.2; 500 kcmil = 253 mm². 1 VA/ft² = 10.76 VA/m².

## 1. Load schedule and demand (NEC Art. 220)
- VA per circuit by phase; balance phases. Continuous = max current for ≥ 3 h (office/retail lighting, EVSE, heaters).
- Lighting: occupancy unit load (dwelling 3 VA/ft²; office 1.3 VA/ft² from NEC 2020, 3.5 before) or actual if larger.
  Receptacles 180 VA/yoke, non-dwelling demand first 10 kVA 100 %, rest 50 %. Dwelling: 2 × 1500 VA small appliance +
  1500 VA laundry; lighting 3 kVA at 100 %, to 120 kVA 35 %, rest 25 %; ≥ 4 fixed appliances 75 %; dryer ≥ 5 kVA;
  ranges Table 220.55. Sign outlet 1200 VA; EVSE max(7200 W, nameplate) (NEC 2020+).
- Motors 125 % largest FLC + others (430.24). Noncoincident loads (heat vs cool): larger only. Existing service: 125 % of
  12-month peak 15-min demand (220.87). Neutral: 100 % to 200 A + 70 % above, no reduction for nonlinear loads.
- Demand factor = max demand/connected (≤ 1); diversity factor = Σ individual maxima/coincident max (≥ 1); load factor
  = average/peak. Apply diversity once, where loads actually combine. Add spare capacity per spec (often 20-25 %).

## 2. Conductors and OCPD (NEC 210/215/240/310)
- OCPD ≥ 125 % continuous + 100 % noncontinuous (100 % only for assemblies listed for it). Conductor: (a) table ampacity
  in the terminal-temperature column ≥ 125 % cont + 100 % noncont; (b) ampacity after correction/adjustment ≥ load;
  (c) protected by the OCPD. Terminals (110.14(C)): ≤ 100 A or 14-1 AWG -> 60 °C unless listed 75 °C; > 100 A -> 75 °C;
  90 °C column only as the derating start.
- Table 310.16 Cu 75 °C (30 °C, ≤ 3 CCC): 12 = 25, 10 = 35, 8 = 50, 6 = 65, 4 = 85, 3 = 100, 2 = 115, 1 = 130, 1/0 = 150,
  2/0 = 175, 3/0 = 200, 4/0 = 230, 250 = 255, 350 = 310, 500 = 380 A. Cu 60 °C: 12 = 20, 10 = 30, 8 = 40, 6 = 55, 4 = 70.
  Al 75 °C: 2 = 90, 1/0 = 120, 4/0 = 180, 250 = 205, 500 = 310. Cu caps (240.4(D)): 14 AWG 15 A, 12 20 A, 10 30 A.
- Ambient: k = √((Tc - Ta)/(Tc - 30)) (75 °C at 40 °C 0.88; 90 °C at 40 °C 0.91); rooftop raceway < 7/8 in: +33 °C.
  Grouping (> 3 CCC): 4-6 80 %, 7-9 70 %, 10-20 50 %, 21-30 45 %, 31-40 40 %, > 40 35 %; EGCs never count; neutral
  counts when it carries harmonic/unbalanced current; not for nipples ≤ 24 in.
- Next size up (240.4(B)) only ≤ 800 A; above, ampacity ≥ OCPD. 240.6(A): 100, 110, 125, 150, 175, 200, 225, 250, 300,
  350, 400, 450, 500, 600, 700, 800, 1000, 1200, 1600, 2000 A. Parallel: ≥ 1/0, identical sets, full-size EGC in each.

## 3. Voltage drop
- 3φ ΔV_LL = √3·I·L·(R cosφ + X sinφ); 1φ ΔV = 2·I·L·(R cosφ + X sinφ); R, X per conductor per length (NEC Ch. 9
  Table 9, by raceway, 75 °C), divided by n parallel sets; % on the same base. Resistive shortcut CM = 2KIL/ΔV (1φ) or
  √3·KIL/ΔV (3φ), K ≈ 12.9 Cu / 21.2 Al Ω·cmil/ft (understates large conductors where X dominates).
- Typical targets (NEC informational notes; binding only if spec/energy code adopts): feeder 2-3 %, branch 3 %, total 5 %;
  IEC 60364-5-52 Annex G: public supply 3 % lighting / 5 % other, private 6 % / 8 %. VD upsizing -> EGC upsized pro rata.

## 4. Short-circuit current and equipment ratings
- Infinite bus: I_sc = I_FL × 100/%Z (1500 kVA, 480 V, 5.75 %: 1804 A -> 31.4 kA). Utility Z_u = V²/S_sc; Z_total =
  Z_u + Z_T + Z_cable. A -7.5 % %Z tolerance raises I_sc ~8 %. Rebase: Z_new = Z_old·(kV_old/kV_new)²·(MVA_new/MVA_old).
  Point-to-point: f = √3·L·I/(C·n·V_LL) (1φ 2·L·I/(C·n·V)), I_end = I_start/(1 + f); C = conductor constant table.
- Motors ≈ 4-6 × FLC for first cycles (4 × in point-to-point); generator ≈ 1/X''d (0.12-0.20 pu). Maximum source is
  conservative for equipment duty, NOT for arc flash or protection sensitivity (run a minimum case too).
- Peak i_p = κ·√2·I_k'', κ = 1.02 + 0.98·e^(-3R/X); ½-cycle asym RMS ≈ I·√(1 + 2e^(-2π/(X/R))). IEC 60909
  I_k'' = c·U_n/(√3·Z_k), c_max 1.05 LV (+6 % tol.) / 1.10 MV and LV +10 %; c_min 0.95 LV, 1.00 MV.
- Test X/R: UL 489 MCCB ≤ 10 kA PF 0.50 (X/R 1.73), 10-20 kA 0.30 (3.18), > 20 kA 0.20 (4.9); LVPCB 0.15 (6.6); MV
  breakers 17; higher system X/R -> derate. Interrupting rating ≥ available fault (110.9); SCCR (110.10, 409.22, 440.4);
  series ratings only as tested/labelled, not with > 1 % motor FLC between devices (240.86); mark available fault and
  date at service (110.24); bus bracing, ATS withstand, busway ratings vs upstream clearing time.

## 5. Protection, selectivity and transformers
- Choose type (fuse J/RK1/L, thermal-magnetic MCCB, electronic LSI/LSIG, LVPCB, relay + breaker), rating, AIC, settings.
  GFPE on solidly grounded wye > 150 V to ground, ≤ 1000 V, disconnect ≥ 1000 A: ≤ 1200 A, ≤ 1 s at 3000 A (230.95).
- Selectivity required: emergency 700.32, legally required standby 701.32, COPS 708.54, elevators 620.62, healthcare
  517. In the instantaneous region prove it with manufacturer selectivity tables (curve non-overlap is not enough);
  fuses typically ≥ 2:1 within one family; breakers via short-time delay without instantaneous, or ZSI.
- Transformer kVA = demand × growth at the cooling class; K-factor for nonlinear loads. Typical %Z: dry 75-500 kVA 3-6 %;
  liquid 750-2500 kVA 5.75 %; X/R ≈ 4-10. Inrush ≈ 8-12 × FLC for 0.1 s; through-fault damage curve IEEE C57.109.
- Taps ±2 × 2.5 % on primary: V_sec = V_pri,actual × V_sec,rated/V_tap; a lower tap voltage RAISES the secondary.
- NEC 450.3(B) (≤ 1000 V): primary only 125 % (< 9 A 167 %, < 2 A 300 %), or primary 250 % + secondary 125 %.
  450.3(A) (> 1000 V, Z ≤ 6 %): primary CB 600 % / fuse 300 %, secondary ≤ 1000 V 125 %; Z 6-10 %: 400 % / 300 %.

## 6. Grounding and bonding (NEC 250)
- EGC Cu by OCPD (250.122): 15 A 14, 20 A 12, 60 A 10, 100 A 8, 200 A 6, 300 A 4, 400 A 3, 500 A 2, 600 A 1, 800 A 1/0,
  1000 A 2/0, 1200 A 3/0, 1600 A 4/0, 2000 A 250, 2500 A 350, 3000 A 400, 4000 A 500 kcmil; full size in each raceway.
- GEC Cu by largest service conductor/equivalent area (250.66): ≤ 2 -> 8; 1-1/0 -> 6; 2/0-3/0 -> 4; to 350 -> 2;
  to 600 -> 1/0; to 1100 -> 2/0; > 1100 -> 3/0; rod-only ≤ 6 AWG, concrete-encased 4 AWG. Bonding jumpers 250.102(C)(1).
- N-G bond only at the service and each separately derived system (250.24, 250.30). Earth is not a fault path; a single
  rod > 25 Ω needs a supplemental electrode ≥ 6 ft away; bond all electrodes present into one system.

## 7. Motor circuits (NEC 430)
- Table FLC (430.247-250), not nameplate, for conductors/OCPD/disconnect; nameplate FLA for overloads. 3φ 460 V: 10 hp
  14, 20 hp 27, 30 hp 40, 50 hp 65, 75 hp 96, 100 hp 124, 150 hp 180, 200 hp 240 A; 230 V ≈ 2 ×; 208 V ≈ 1.1 × 230 V.
- Conductor ≥ 125 % FLC; overload 125 % nameplate (SF ≥ 1.15 or rise ≤ 40 °C) else 115 %. Table 430.52 max % FLC:
  non-time-delay fuse 300, dual-element fuse 175, inverse-time CB 250, instantaneous 800 (1100 Design B energy-
  efficient), next size up allowed. Feeder OCPD ≤ largest branch device + Σ other FLC (430.62). Disconnect ≥ 115 %.
- Starting: DOL 6-8 × FLC (code letter kVA/hp, 430.7(B)); star-delta 1/3 current and torque; autotransformer tap k ->
  k² × DOL; soft starter 2-4 ×; VFD 1-1.5 × (conductors 125 % of drive input rating); torque ∝ V².

## 8. IEC 60364, power factor, checker's list
- I_b ≤ I_n ≤ I_z, I_2 ≤ 1.45·I_z; I_z = I_z0 × C_ambient × C_grouping × C_soil per method (A1-G, Table B.52; ref.
  30 °C air, 20 °C ground, 2.5 K·m/W). Adiabatic S ≥ √(I²t)/k: k = 115 Cu/PVC, 143 Cu/XLPE, 76 Al/PVC, 94 Al/XLPE.
  PE (Table 54.2): S ≤ 16 -> S; 16-35 -> 16; > 35 -> S/2. TN: Z_s ≤ 0.95·U_0/I_a; 230 V final circuits ≤ 32 A 0.4 s,
  distribution 5 s. TT: 0.2 s or R_A·I_Δn ≤ 50 V.
- PF: Q_c = P·(tan φ1 - tan φ2); capacitor conductors ≥ 135 % rated current (460.8); motor-switched ≤ magnetizing kvar.
  Resonance h_r ≈ √(S_sc/Q_c); near 5th/7th with VFDs -> detuned bank (h = 1/√p, 7 % -> 3.78) or filter.
- Common errors: LL vs LN base (208 vs 240); kW vs kVA; 125 % applied twice or never; 90 °C ampacity at 75 °C terminals;
  missing derates; one-way vs round-trip length; nameplate FLA for motor conductors; fault > rating; EGC not full size
  per parallel raceway; downstream N-G bond. State edition, table and every factor used.
