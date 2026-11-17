---
name: electrical-safety-and-studies
description: Electrical studies and safety - arc flash (IEEE 1584, NFPA 70E), protective coordination and settings, harmonics (IEEE 519) and voltage limits (ANSI C84.1), motor-starting dip, MV cables, raceway fill, working space, hazardous areas, emergency power, acceptance testing (NETA). Use for studies, reviews and commissioning.
---

# Electrical safety, studies and acceptance (engineer's practice)
Project documents govern (spec, owner safety program, adopted NEC/NFPA 70E editions, utility data). Values below are
typical or from recent editions; re-read the actual table before quoting. Sizing and fault calcs: electrical-power-design.
## 1. Study basis and scenarios
- Model from field-verified data: utility max AND min fault MVA with X/R, transformers, cables, motors, generators,
  devices and settings as installed. Maximum case (all motors, ties closed) for equipment duty; minimum case (utility
  min, generator only, ties open): lower current can mean longer clearing and HIGHER incident energy; cover every mode
  (maintenance switch, tie, generator). Re-assess arc flash ≥ every 5 years and after changes (70E 130.5(G)).
## 2. Arc flash (IEEE 1584-2018, NFPA 70E)
- Range: 3φ 208 V-15 kV; I_bf 0.5-106 kA (≤ 600 V), 0.2-65 kA (601 V-15 kV); gap 6.35-76.2 mm LV, 19.05-254 mm MV;
  working distance ≥ 305 mm. Outside it (1φ, DC, > 15 kV) use another method (e.g. 70E Annex D for DC) and say so.
- Inputs per bus: V_oc, I_bf, electrode configuration (VCB, VCBB, HCB, VOA, HOA), gap, enclosure size, working distance,
  duration = clearing time of the device that actually clears a fault there (line side of a main -> upstream/primary
  device) at the ARCING current. Compute at I_arc and at reduced I_arc,min (variation factor); keep the worse energy.
- Typ. gap/working dist. (mm): 15 kV swgr 152/914; 5 kV swgr 104/914; LV swgr 32/610; LV MCC/panel 25/457; cable box 13/457.
- Outputs: I_arc, incident energy E (cal/cm²; 1 cal/cm² = 4.184 J/cm²), arc-flash boundary where E = 1.2 cal/cm²
  (5.0 J/cm²). E ≈ proportional to time; a 2 s cap only where egress is clearly possible (state it). 3φ ≤ 240 V with
  I_bf < 2 kA: sustained arc unlikely per 1584-2018 (label per owner policy).
- 70E PPE: incident energy method (arc rating ≥ E) or PPE category tables 130.7(C)(15)(a)/(b), valid only within their
  listed fault current and clearing time; categories 1 = 4, 2 = 8, 3 = 25, 4 = 40 cal/cm². Above 40: no category, plan
  de-energized work (electrically safe work condition 120.5: LOTO, test before touch); energized work permit 130.2(B).
- Shock approach (AC, Table 130.4(E)(a)): limited 3.0 m (10 ft) for movable conductors; fixed parts 1.0 m (3 ft 6 in)
  at 50-750 V, 1.5 m (5 ft) at 751 V-15 kV; restricted: avoid contact (50-150 V), 0.3 m (151-750 V), ≈ 0.7 m (0.75-15 kV).
- Label (70E 130.5(H), NEC 110.16): nominal voltage, arc-flash boundary, EITHER incident energy with working distance OR
  PPE category (not both), minimum arc rating/site PPE, and the date where the adopted code requires it.
- Mitigation: NEC 240.87 breakers ≥ 1200 A (ZSI, differential, maintenance switch, active mitigation, instantaneous below
  arcing current); 240.67 fuses ≥ 1200 A (≤ 0.07 s); current-limiting fuses, arc-flash relays, remote racking, HRG.
## 3. Protection coordination (IEEE 242, relay practice)
- TCC: log-log, currents on one voltage base (scale by turns ratio). Fuses: minimum melt to total clear band. Electronic
  trip: long-time pickup 0.4-1.0 × In + delay band, short-time 1.5-10 × Ir at 0.1-0.5 s (I²t in/out), instantaneous
  2-15 × In, ground fault (≤ 1200 A, ≤ 1 s at 3000 A where 230.95 applies).
- Margins: relay-relay CTI ≈ 0.3 s electromechanical, 0.2 s numeric; LV breakers/fuses: no band overlap, and in the
  instantaneous region only manufacturer selectivity tables prove selectivity; fuse-fuse by ratio tables.
- Phase 51 above maximum load incl. permitted overload (typ. 125-150 %) yet ≥ 1.5-2 × pickup at minimum fault; 51N/51G as
  low as unbalance allows; 50 above the maximum through-fault at the next bus and above transformer inrush.
- Transformer: primary device right of inrush (8-12 × FLC at 0.1 s), left of IEEE C57.109 through-fault curve; Δ-Y: a
  secondary L-G fault shows as 58 % on the primary (shift the curve). Cable damage (ICEA P-32-382): (I/A)²·t =
  0.0297·log10[(T2 + 234)/(T1 + 234)] Cu (A cmil, t s; Al 0.0125 and 228), XLPE 90 -> 250 °C. Motor: relay above
  starting curve, below hot stall time; 50 ≥ 1.6-2 × LRC. Deliver a settings table (CT ratio, pickups, curves) + TCCs.
## 4. Voltage, harmonics, motor starting
- ANSI C84.1 (120 V base): Range A service 114-126 V (±5 %), utilization 108-125 V (110 for lighting); Range B service
  110-127, utilization 104-127. Over 600 V: Range A service 97.5-105 %, B 95-105.8 %. 480 V: A service 456-504 V,
  utilization ≥ 432 V (460 V motors ±10 %, NEMA MG 1). Range B: occasional only, corrected in reasonable time.
- IEEE 519 at the PCC (weekly 95th percentile of 10-min values ≤ limit; daily 99th percentile of 3-s values ≤ 1.5 ×
  voltage / 2 × current limits). Voltage h / THD: ≤ 1 kV 5.0 / 8.0 %; 1-69 kV 3.0 / 5.0; 69-161 kV 1.5 / 2.5; > 161 kV
  1.0 / 1.5. Current (120 V-69 kV), % of I_L, odd h < 11 / 11-17 / 17-23 / 23-35 / 35-50 / TDD, by I_sc/I_L:
  < 20: 4.0 2.0 1.5 0.6 0.3 / 5.0; 20-50: 7.0 3.5 2.5 1.0 0.5 / 8.0; 50-100: 10.0 4.5 4.0 1.5 0.7 / 12.0;
  100-1000: 12.0 5.5 5.0 2.0 1.0 / 15.0; > 1000: 15.0 7.0 6.0 2.5 1.4 / 20.0. Even h: fraction of odd (2014 ed. 25 %).
  THD_V = √ΣV_h²/V_1; TDD = √ΣI_h²/I_L, I_L = max demand current (12-mo mean of monthly peaks); 6-pulse VFD + reactor ≈ 35 %.
- Starting dip ≈ S_start/(S_start + S_sc) (locked-rotor kVA at PF 0.2-0.3; S_sc at that bus incl. source + transformer).
  Typical criteria (spec governs): ≥ 80-85 % at motor terminals (torque ∝ V²), other buses ≤ 10-15 % dip, contactors and
  drives drop out below ≈ 70-80 %; flicker per IEEE 1453 with start frequency; genset transient dip ≤ 15-20 %.
## 5. Cables, raceways, clearances
- MV insulation level: 100 % (fault cleared ≤ 1 min), 133 % (≤ 1 h, e.g. impedance-grounded), 173 % (indefinite); 15 kV
  wall 4.45 mm/175 mil (100 %), 5.59 mm/220 mil (133 %). Shielded above 2 kV (NEC 311). Shields bonded both ends ->
  circulating current derates large single-cores; single-point/cross-bonding limits standing voltage. Check conductor
  and shield short-circuit rating, bend radius, pulling tension; terminations IEEE 48, splices IEEE 404.
- Conduit fill (NEC Ch. 9 Table 1): 1 conductor 53 %, 2 = 31 %, > 2 = 40 % of Table 4 area (Table 5 areas; EGC counts);
  nipples ≤ 24 in 60 %; jam ratio D/d 2.8-3.2 with 3 cables. Pull boxes 314.28: straight 8 ×, angle 6 × trade size.
- Cable tray (NEC 392, ≤ 2000 V multiconductor, ladder/ventilated): all ≥ 4/0 -> Σ diameters ≤ width, single layer;
  all < 4/0 -> Σ areas ≤ Table 392.22(A) col. 1 (7.0 in² per 6 in width: 12 in 14, 24 in 28, 36 in 42). Single
  conductors only ≥ 1/0. Ampacity 392.80 (solid cover > 6 ft: 95 %; single 1/0-500 kcmil uncovered 65 %, ≥ 600 kcmil
  75 % of free-air). Spec fill (often 40-50 %) and voltage-class separation govern if stricter.
- Working space 110.26 (≤ 1000 V), depth for Conditions 1/2/3: 0-150 V to ground 0.9/0.9/0.9 m; 151-1000 V 0.9/1.0/1.2 m
  (3/3.5/4 ft); 1 = nothing live/grounded opposite, 2 = grounded opposite (concrete, brick, tile), 3 = live both sides.
  Width ≥ 762 mm or equipment width; height 2.0 m; doors open ≥ 90°. ≥ 1200 A and > 1.8 m wide: entrance each end
  ≥ 610 mm × 2.0 m (unless unobstructed exit/double depth); ≥ 800 A: doors within 7.6 m open outward, panic hardware.
  Dedicated space to 1.8 m above footprint. 110.34 (> 1000 V): 1001-2500 V 0.9/1.2/1.5 m; 2501-9000 V 1.2/1.5/1.8 m.
## 6. Hazardous (classified) locations
- NEC 500-506; classify by NFPA 497/499, API RP 500/505, IEC 60079-10. Class I gas, II dust, III fibres; Division 1
  (normal) / 2 (abnormal only); Zones 0/1/2 gas, 20/21/22 dust. Groups A acetylene, B hydrogen, C ethylene, D propane
  (IIC ≈ A+B, IIB ≈ C, IIA ≈ D); E metal, F carbonaceous, G other dusts. T-code below autoignition: T1 450, T2 300,
  T3 200, T4 135, T5 100, T6 85 °C. Methods: Ex d/explosionproof, purged (NFPA 496), intrinsic safety (V_oc ≤ V_max,
  I_sc ≤ I_max, C_a ≥ C_i + C_cable, L_a ≥ L_i + L_cable), nonincendive, Ex e, Ex m; seals ≤ 450 mm (501.15).
## 7. Emergency and standby systems
- NEC 700 emergency: 10 s; wiring entirely independent of other wiring (700.10(B)); 2-h feeder protection in assembly
  > 1000 persons or buildings > 23 m; listed transfer switch; selective coordination (700.32). 701 legally required
  standby: 60 s, may share raceways, coordinated. 702 optional: load management if undersized. 708 COPS; 517 healthcare
  essential system (life safety, critical, equipment branches; 10 s; NFPA 99).
- NFPA 110 Type 10, Class = fuel hours, Level 1/2. Monthly ≥ 30 min at ≥ 30 % nameplate kW (or exhaust temperature), else
  annual load bank (50 % 30 min + 75 % 60 min); Level 1 4-h test every 36 months. Acceptance: cold start and transfer in
  type time, full-load test (typ. 2 h, load bank allowed). Check ATS withstand vs fault and clearing time; 3- vs 4-pole
  neutral switching vs grounding/GFP (separately derived only if the neutral is switched).
## 8. Commissioning and acceptance testing (NETA ATS, IEEE)
- Order: visual/mechanical, torque, as-built -> insulation resistance -> ratio/polarity -> contact resistance ->
  protective/functional tests -> energize (phasing, rotation) -> load tests -> thermography under load.
- IR (typical NETA ATS Table 100.1, 1 min, corrected to 20 °C, ≈ halves per 10 °C): 600 V class 1000 V DC / 100 MΩ; 5 kV
  2500 V / 1000 MΩ; 15 kV 2500 V / 5000 MΩ. Machines (IEEE 43): PI = R10/R1 ≥ 2.0, IR ≥ 100 MΩ form-wound, ≥ 5 MΩ
  random-wound. MV cable: VLF withstand (IEEE 400.2, e.g. 15 kV class ≈ 21 kV rms, commonly 30 min) + tan δ / PD.
- Transformers: TTR within 0.5 % of nameplate per tap, winding resistance, insulation PF, oil/DGA. Breakers: contact
  resistance (investigate > 50 % deviation between poles), primary injection of LT/ST/I/GF. Relays: secondary injection
  of every enabled element, CT ratio/polarity, trip to breaker. GFP test (230.95(C)). Ground: fall-of-potential, ≤ 5 Ω typ.
- Thermography (≥ 40 % load), ΔT similar components: 1-3 °C possible, 4-15 °C deficiency, > 15 °C major.
- Record: as-found/as-left, criterion and pass/fail per test, instrument calibration, tester/witness; settings vs study
  revision; labels installed; punch list with owners; as-builts, O&M, training. Accept only with deficiencies closed.
