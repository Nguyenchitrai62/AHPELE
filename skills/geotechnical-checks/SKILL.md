---
name: geotechnical-checks
description: Geotechnical design and review - lateral earth and water pressure on shoring, embedment, base heave and piping, dewatering effects, footing settlement on clay (consolidation, time rate, allowable settlement), fill compaction acceptance (Proctor, field density testing). Use for any foundation, excavation or earthwork task.
---

# Geotechnical checks (reviewer's practice)

Units: γw = 9.81 kN/m³ = 62.4 pcf; 1 kPa = 20.9 psf; 1 pcf = 0.157 kN/m³; 1 ft = 0.3048 m. Take parameters from the
boring/lab record nearest the work and say which. Effective stress σ'v = σv - u, u = γw·(z - zw) below the water table.

## 1. Shoring: earth and water pressure
- Coefficients: Ka = tan²(45° - φ'/2), Kp = tan²(45° + φ'/2), K0 = 1 - sin φ' (NC), K0,OC ≈ K0·OCR^(sin φ').
  Active with cohesion: σa = Ka·σ'v - 2c'√Ka (ignore negative tension zone; minimum ≈ 0.25·σ'v in clays is common).
  Use at-rest K0 where the wall is stiff/braced and adjacent structures limit movement.
- Below the water table: earth pressure on γ' = γsat - γw, **plus** full water pressure γw·(z - zw) (K = 1). Net water
  pressure across the wall depends on the water level each side and seepage. A higher water table than designed adds
  roughly (1 - Ka)·γw per metre of rise at every depth below it, a large share of the total: recompute.
- Apparent pressure envelopes for multi-braced/anchored walls (Terzaghi-Peck, FHWA GEC-4), for strut/anchor loads:
  sand 0.65·Ka·γ·H uniform; stiff clay (γH/cu ≤ 4) trapezoid 0.2-0.4·γH; soft-medium clay (γH/cu > 4)
  Ka = 1 - m·4cu/(γH) (m = 1, 0.4 if soft clay continues below), pressure Ka·γH. Add water and surcharge separately.
- Surcharges: uniform q → Δσh = K·q full depth. Traffic/construction ≈ 12 kPa (250 psf) within ~H of the edge.
  Strip load q (elastic, rigid wall, doubled Boussinesq): Δσh = (2q/π)(β - sin β·cos 2α), angles in radians.
  Line load Q (kN/m) at x = mH, depth z = nH: m > 0.4 → Δσh = (4Q/πH)·m²n/(m²+n²)²; m ≤ 0.4 → (Q/H)·0.203n/(0.16+n²)².
  Adjacent footings inside the active wedge (from wall base at 45° + φ'/2 to horizontal) or a 1H:1V line must be included.
- Embedment: cantilever - free earth support, FS 1.5-2.0 on passive (or factored Kp), then add 20-40% to depth of
  rotation; braced - moment of passive about lowest brace, FS ≥ 1.5. Check the passive side's water and soft layers.
- Base heave in clay: stability number N = γH/cu; N > ~6 signals basal failure. Bjerrum-Eide FS = cu·Nc/(γH + q),
  Nc 5.1-9 (Skempton, by H/B, B/L); Terzaghi FS = (5.7cu)/(H(γ - cu/0.7B)). Require FS ≥ 1.5 (2.0 near structures).
- Sand: piping/boiling, exit gradient i = Δh/L; critical ic = γ'/γw ≈ 0.9-1.1; FS = ic/i ≥ 1.5-2.0 (more where
  boiling would undermine). Uplift of a clay base over a confined (artesian) layer: FS = Σ(γ·t) / (γw·h_piezo) ≥ 1.2-1.5.
- Dewatering: drawdown Δh raises σ'v by γw·Δh in compressible layers → consolidation settlement of nearby structures
  (compute as §2). Radius of influence (Sichardt) R ≈ 3000·s·√k (R, s in m; k in m/s). Mitigate with cutoff walls,
  recharge, monitoring. Check fines loss from pumping.
- Ground movement behind excavations: well-braced walls in sand/stiff clay δv,max ≈ 0.15-0.3% H (Clough-O'Rourke),
  soft clay up to 1-2% H; trough extends ~2H (sand/stiff) to 3H (soft clay). Compare with structures in that zone;
  require pre-construction survey, settlement points/inclinometers, alert/action levels (e.g. 50%/75% of tolerable).
- Reviewer list: groundwater level used vs highest logged/seasonal; layer boundaries vs nearest boring; c' or cu not
  over-used; surcharges (footings, cranes, traffic, spoil) included; each stage incl. brace removal; passive not taken
  in disturbed/soft zone; drained vs undrained case; FS meets spec; effects on adjacent and permanent works.

## 2. Footing settlement on clay
- Net pressure q_net = (sustained load)/(B·L) - γ·Df. Use sustained (dead + long-term live) for consolidation.
- Stress increase: 2:1 → Δσ = q_net·B·L/((B+z)(L+z)) (strip: q_net·B/(B+z)). Boussinesq/Newmark for centre, corner,
  neighbouring footings (square, centre, z = B: Boussinesq ≈ 0.34q vs 2:1 = 0.25q). Superpose adjacent footings.
- Subdivide compressible layers (sublayers ≤ ~1-1.5 m or ≤ B/2), evaluate at mid-depth, stop where Δσ < 10% σ'v0
  (≈ 2B square, 4B strip) or at incompressible stratum.
- Immediate (undrained): Si = q·B·(1 - ν²)·Is/Eu, ν = 0.5; Eu ≈ 200-500·cu (lower for plastic/soft clay).
- Primary consolidation per sublayer (H thickness, σ'f = σ'v0 + Δσ, σ'p preconsolidation, OCR = σ'p/σ'v0):
  NC (σ'p ≈ σ'v0): Sc = Cc·H/(1+e0)·log10(σ'f/σ'v0); OC with σ'f ≤ σ'p: Sc = Cr·H/(1+e0)·log10(σ'f/σ'v0);
  OC with σ'f > σ'p: Sc = Cr·H/(1+e0)·log10(σ'p/σ'v0) + Cc·H/(1+e0)·log10(σ'f/σ'p). Alternative Sc = mv·Δσ·H.
  Typical: Cc ≈ 0.009(LL - 10); Cr ≈ Cc/5 to Cc/10; CR = Cc/(1+e0). Get σ'p by Casagrande from the oedometer;
  an "OC" assumption the test does not show (OCR ≈ 1) can understate settlement several-fold.
- Secondary: Ss = Cα·H/(1+ep)·log10(t2/t1), t1 = end of primary; Cα/Cc ≈ 0.04 ± 0.01 inorganic, 0.05-0.07 organic.
- Time rate: t = Tv·Hdr²/cv; T50 = 0.197, T90 = 0.848; Hdr = half thickness if drained top and bottom, full thickness
  if one drainage face (check logs for sand seams/impervious base). cv typical 0.3-10 m²/yr NC clay (higher in OC range).
- Criteria (project criteria govern): isolated footings on clay total ≈ 25-65 mm (1-2.5 in), differential ≈ 13-20 mm
  (½-¾ in) common for buildings; angular distortion β = δ/L: 1/500 safe for framed buildings, 1/300 first cracking
  in panels, 1/150 structural damage, 1/750-1/1000 settlement-sensitive machinery.
- Reviewer list: borings/lab used are the ones under the footings; water table (lower σ'v0 → more settlement; future
  drawdown adds load); loads current; neighbouring footings superposed; differential between adjacent footings on
  different clay thickness; time vs construction stages (how much occurs before connections/finishes).

## 3. Fill and compaction acceptance
- Proctor basis: ASTM D698 standard (24.4 N/5.5 lbf rammer, 305 mm/12 in drop, 3 layers, ≈ 600 kN·m/m³ /
  12,400 ft·lbf/ft³) vs D1557 modified (44.5 N/10 lbf, 457 mm/18 in, 5 layers, ≈ 2,700 kN·m/m³ / 56,000 ft·lbf/ft³).
  Modified gives higher γd,max and lower w_opt; a percent of one is not a percent of the other. Use the method the
  spec section names; a report using the other method does not demonstrate compliance.
- Relative compaction RC = γd,field/γd,max·100%; γd = γwet/(1 + w). Moisture window relative to w_opt (often -2 to +3
  points or ±2). Typical specs: under slabs 95% D698 or 90-95% D1557; under footings 98% D698/95% D1557; landscaped 85-90%.
- The Proctor must represent the material tested: same source/soil description, gradation, plasticity. New borrow or
  visibly different soil needs a new Proctor or a one-point Proctor check (AASHTO T 272) on the tested material.
  Oversize (> 5% on 19 mm) needs correction (ASTM D4718). Red flags: RC > ~102%, a field point plotting beyond the
  zero-air-voids line γzav = Gs·γw/(1 + w·Gs), identical numbers repeated, moisture far from the curve.
- Frequency and lifts (per spec; typical): 1 test per 2,500 ft² (≈ 230 m²) per lift under buildings, min 2-3 per lift;
  trenches 1 per 50-100 ft per lift; loose lifts ≤ 200-300 mm (8-12 in) for rollers, 100-150 mm (4-6 in) hand
  compactors. Cross-check placement log (lift elevations, areas, dates) against test elevations: every lift and area tested.
- Nuclear gauge ASTM D6938: direct transmission with probe depth ≥ tested lift (≤ 300 mm); daily standard counts within
  limits of prior average; calibration ≤ 12 months; moisture correction against oven-dry ASTM D2216 for each soil type
  (always for organic, micaceous, gypsum or high-chloride soils); report gauge ID, standard counts, probe depth,
  Proctor ID, location (grid, elevation, lift). Alternatives: sand cone D1556, drive cylinder D2937.
- Failed test (density or moisture): rework (scarify, moisture-condition, recompact) and retest at the same location
  and lift, linked to the original test number; failures cannot be averaged out; lifts placed over a failed lift come off.
- Before building on fill: subgrade stripped and proof-rolled/observed; fill material approved; every lift and area
  tested with passing results on the correct Proctor; retests closed; final grade verified; report signed by the
  testing agency's responsible engineer and reviewed by the geotechnical engineer; fill re-tested if softened by rain
  or frost. Missing testing is "not accepted - incomplete", distinct from failing results.
