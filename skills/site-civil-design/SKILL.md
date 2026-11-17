---
name: site-civil-design
description: Site civil design - grading and accessible routes (ADA), earthwork volumes, road and parking geometry and pavement design (AASHTO 93), water and sewer utilities, erosion control, NRCS curve-number hydrology, detention routing, water quality volume, floodplains. Use for any site, roadway, utility or hydrology task.
---

# Site civil design (practising engineer's checks)

Project documents, the local design manual and the reviewing agency's criteria govern; "typical" values are defaults
for when the record is silent - say so. Spillways/rational/Manning/HGL: stormwater-drainage-checks; shoring, settlement,
compaction: geotechnical-checks. Order: criteria and datum (NAVD88 vs NGVD29; ft, US survey ft, m) -> existing
conditions -> layout -> grading -> hydrology/drainage -> utilities -> ESC -> quantities -> cross-check sheets vs calcs.

## 1. Grading and accessibility
- Slope % = rise/run x 100; H:V = run:rise. 2:1 = 50 %, 3:1 = 33.3 %, 4:1 = 25 %, 1:12 = 8.33 %, 1:20 = 5 %,
  1:48 = 2.08 %. Spot elevation between points: E = E1 + s d; horizontal distance between contours d = dz/s.
- Typical minimums: asphalt 1.0 % (1.5 % preferred), concrete 0.5 %, gutter flowline 0.5 %, lawn 2 %, grass swale
  1-2 % (lined 0.5 %). Away from buildings 5 % for 10 ft (6 in fall, IBC 1804.4), impervious 2 %. FFE >= 0.5-1 ft
  above adjacent grade and >= 1 ft above overflow/flood WSE.
- Typical maximums: mowed turf 3:1 (4:1 preferred), planted 2:1 (steeper needs geotech/stabilisation), parking 5 %,
  driveways 10-15 %; grade breaks over ~8-10 % need a vertical curve/transition.
- ADA 2010 / ICC A117.1: accessible route running slope <= 1:20 (5 %); steeper is a ramp: <= 1:12, rise <= 30 in
  (760 mm) per run, landings >= 60 in long, clear width >= 36 in, handrails if rise > 6 in. Cross slope <= 1:48
  (design ~1.5 % for tolerance). Curb ramp <= 1:12, flares <= 1:10, top landing 36 in. Accessible stalls and aisles
  <= 1:48 every direction; car 96 in + 60 in aisle, van 132 in + 60 in (or 96 + 96). Recompute slopes from spot
  elevations along the actual path; never trust a slope label.

## 2. Earthwork volumes (to SUBGRADE = finished grade minus pavement/topsoil section; stripping 4-12 in separate)
- Average end area V = L (A1 + A2)/2 per station interval; ft3/27 = yd3. Prismoidal V = L (A1 + 4Am + A2)/6
  (Am from mid-section dimensions, not the mean of A1 and A2); AEA overestimates pyramid-like shapes.
- Grid method, square cells area A, corner depths h: V = (A/4)(sum h1 + 2 sum h2 + 3 sum h3 + 4 sum h4), hn = corner
  shared by n cells; cut and fill separately, split cells on the 0-line; cross-check with a TIN surface volume.
- Shrink/swell: loose LCY = BCY (1 + swell); compacted CCY = BCY (1 - shrink). Typical swell earth 20-30 %, clay
  30-40 %, rock 50-65 %; shrink earth 10-20 %; rock compacts to ~1.2-1.4 x bank. Bank needed = CCY/(1 - shrink);
  truck loads use LCY. Net balance = cut(bank) - fill/(1 - shrink); label every quantity bank/loose/compacted.

## 3. Roadway and parking geometry (AASHTO Green Book)
- Horizontal curve: T = R tan(Delta/2), L = pi R Delta/180, LC = 2R sin(Delta/2), E = R(sec(Delta/2) - 1),
  M = R(1 - cos(Delta/2)); PC = PI - T, PT = PC + L (stationed along the arc). Arc degree D = 5729.58/R (ft).
  Min radius R = V^2/(15(e + f)) US (mph, ft), V^2/(127(e + f)) SI (km/h, m). Typical lanes 10-12 ft, crown 1.5-2 %.
- Vertical curve (g in %): y(x) = y_PVC + g1 x/100 + (g2 - g1) x^2/(200 L); A = |g2 - g1|, K = L/A, middle ordinate
  E = A L/800, high/low point x = g1 L/(g1 - g2) from PVC, PVC = PVI - L/2.
- SSD = 1.47 V t + 1.075 V^2/a (ft; t = 2.5 s, a = 11.2 ft/s2); SI 0.278 V t + 0.039 V^2/a (a = 3.4 m/s2). Design
  SSD / crest K / sag K: 30 mph 200 ft/19/37; 40 mph 305/44/64; 50 mph 425/84/96; 60 mph 570/151/136.
  Crest: S < L: L = A S^2/2158 (SI 658); S > L: L = 2S - 2158/A. Sag (headlight): S < L: L = A S^2/(400 + 3.5S)
  (SI 120 + 3.5S); S > L: L = 2S - (400 + 3.5S)/A. Min L ~ 3V ft. Stalls 9 x 18 ft, 24 ft aisle; fire lane >= 20 ft.
- AASHTO 93 flexible: log10 W18 = ZR S0 + 9.36 log10(SN + 1) - 0.20 + log10(dPSI/2.7)/(0.40 + 1094/(SN + 1)^5.19)
  + 2.32 log10 MR - 8.07 (MR psi). ZR: 85 % -1.037, 90 % -1.282, 95 % -1.645; S0 0.45 flexible (0.35 rigid);
  dPSI = 4.2 - pt (pt 2.0-2.5). SN = a1 D1 + a2 m2 D2 + a3 m3 D3 (in); typical a1 0.44 HMA, a2 0.14 crushed base,
  a3 0.11 subbase, m 1.0; MR ~ 1500 CBR psi (fine soils). Solve SN iteratively, size layers top-down so the SN above
  each layer protects it, then apply agency minimum thicknesses. ESAL factor ~ (axle/18 kip)^4. Rigid: k, Sc, Ec, J, Cd.

## 4. Water and fire flow
- 1 psi = 2.31 ft water. Service 40-80 psi (PRV > 80); >= 20 psi residual everywhere at max day + fire flow; fire
  flow/duration per fire code (IFC App. B: 1,000 gpm small 1-2 family, >= 1,500 gpm others, 2-4 h).
- Hydrant test (NFPA 291): Q_R = Q_F ((S - R_target)/(S - R_test))^0.54. Hazen-Williams: hf = 10.67 L Q^1.852/
  (C^1.852 D^4.87) SI (m, m3/s); p = 4.52 Q^1.85/(C^1.85 d^4.87) psi per ft US (gpm, in). C: PVC 150, lined DI 130-140.
  V <= 5 ft/s normal, <= 10 ft/s fire. Mains typically 8 in (6 in min to hydrants), looped, valves at tees.
- Hydrants (typical, IFC 507.5/App. C): within 400 ft of all exterior walls along fire access (600 ft sprinklered or
  R-3); street spacing 300-500 ft; FDC within 100 ft of a hydrant; 3-5 ft behind curb, clear of obstructions.

## 5. Sanitary sewer (Ten States Standards typical)
- Min slopes for 2 ft/s full (n = 0.013): 8 in 0.40 %, 10 in 0.28 %, 12 in 0.22 %, 15 in 0.15 %, 18 in 0.12 %,
  21 in 0.10 %, 24 in 0.08 %. Main >= 8 in; building sewer 4-6 in at 1/8-1/4 in/ft; max V ~10-15 ft/s. Flow = avg
  (e.g. 100 gpcd) x Harmon PF = 1 + 14/(4 + sqrt(P)) (P thousands) + I/I; peak depth <= 0.5-0.75 D.
- Manholes at every change of grade, size, direction, junction and line end; spacing <= 400 ft (<= 15 in), <= 500 ft
  (18-30 in). Drop across MH ~0.1 ft straight, ~0.2 ft at bends; match crowns on size increase; drop connection when
  inlet >= 24 in above outlet invert. Recompute slope = (inv up - inv down)/length for every reach.
- Separation: water-sewer >= 10 ft horizontal edge to edge; at crossings water >= 18 in above sewer, one full water
  pipe length centred on the crossing; otherwise pressure-rated sewer/encasement per state rules.

## 6. Erosion and sediment control / SWPPP
- EPA CGP (or state permit) at >= 1 ac disturbed or part of a common plan: NOI, SWPPP on site, inspection every
  7 days (or 14 days + within 24 h of >= 0.25 in rain), stabilisation begun when work stops >= 14 days and finished
  within 14 days (7 in sensitive waters); final = 70 % uniform perennial cover; then NOT.
- BMPs in sequence: stabilised entrance, perimeter silt fence/wattles (fence on contour, ~1/4 ac per 100 ft, J-hooks)
  and inlet protection BEFORE clearing; traps (< ~5 ac) and basins (>= 10 ac to one point: 3,600 ft3/ac drained or
  2-yr 24-h runoff); dewatering filtration, washout, stockpile cover, check dams, blankets on slopes >= 3:1; remove
  perimeter controls after stabilisation. Show phasing, details, maintenance and responsible party.

## 7. Hydrology beyond the rational method (NRCS TR-55/TR-20)
- S = 1000/CN - 10 in (SI 25400/CN - 254 mm); Ia = 0.2 S; Q = (P - 0.2S)^2/(P + 0.8S) if P > Ia else 0. Volume
  (ac-ft) = Q(in) A(ac)/12. Typical CN (HSG A/B/C/D): impervious 98; open space good 39/61/74/80; woods good
  30/55/70/77; 1/4-ac lots 61/75/83/87. Split pervious/impervious runoff when CNs differ widely. Rain: NOAA Atlas 14.
- Tc = sum of Tt: sheet flow (<= 100 ft) Tt = 0.007 (nL)^0.8/(P2^0.5 s^0.4) h (L ft, P2 = 2-yr 24-h in, s ft/ft;
  n smooth 0.011, short grass 0.15, dense grass 0.24, woods 0.4-0.8); shallow concentrated V = 16.13 s^0.5 unpaved,
  20.33 s^0.5 paved (ft/s); channel/pipe by Manning; Tt = L/(3600 V) h. Minimum Tc 0.1 h.
- SCS unit hydrograph: lag = 0.6 Tc, Tp = D/2 + lag (D ~ 0.133 Tc), qp = 484 A Q/Tp (cfs, mi2, in, h) [SI
  0.208 A Q/Tp: m3/s, km2, mm, h], base ~2.67 Tp; convolve incremental excess for the storm hydrograph.
- Detention (modified Puls): 2S2/dt + O2 = I1 + I2 + 2S1/dt - O1, dt <= Tp/5. Stage-storage by average-area/conic;
  orifice Q = Cd A sqrt(2 g h) (Cd ~0.6, h to centroid); rectangular weir 3.33 (L - 0.1nH) H^1.5, V-notch
  2.5 tan(theta/2) H^2.5 (US). Post <= pre (or agency rate) for every design storm; peak outflow must fall on the
  inflow recession limb; peak stage below the spillway crest. WQv = P Rv A/12 ac-ft, Rv = 0.05 + 0.009 I (I %
  impervious), P = 90th pct storm (often 1.0 in); drawdown 24-48 h (<= 72); channel protection 24-h ED of 1-yr storm.

## 8. Floodplain (FEMA NFIP) and final cross-checks
- Zones A (no BFE), AE (BFE), AO/AH shallow, VE coastal, X shaded 0.2 %/unshaded. P(>= 1 event in n yr) = 1 -
  (1 - 1/T)^n (100-yr in 30 yr = 26 %). Floodway: no rise (0.00 ft) by HEC-RAS + certification, else CLOMR/LOMR;
  fringe fill often needs 1:1 compensatory storage; lowest floor >= BFE + local freeboard (1-2 ft, ASCE 24); convert
  FIRM datum to plan datum before comparing.
- Before issue: same elevations, inverts, stations, sizes on plan/profile/details/calcs/quantities; cite each limit.
