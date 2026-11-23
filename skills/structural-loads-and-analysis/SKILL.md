---
name: structural-loads-and-analysis
description: Structural loads and analysis - ASCE 7 load combinations, live load reduction, wind (MWFRS, C&C), seismic ELF (base shear, distribution, drift, redundancy, overstrength, irregularities), distribution to frames with torsion, serviceability, existing buildings and alterations (IEBC, ASCE 41).
---

# Structural loads and analysis

Project criteria, adopted code edition (ASCE 7-16 vs 7-22, Eurocode + NA) and drawings govern; values below are code
defaults or *typical* - cite edition/clause. Snow drift, uplift zones, deck, collectors: see `structural-design-checks`.

## 1. Order of work and load path
Basis (code edition, risk category, occupancy, LRFD or ASD - never mix) -> loads per area with sources (D, SDL, L, Lr,
S, R, W, E, H, F, T, ice, crane) -> load path to the foundation for gravity, lateral AND uplift/overturning -> tributary
take-down per level -> combinations, governing case per element -> model check (6) -> serviceability (7).
- Gravity: deck -> joists -> girders -> columns/walls -> footings. Lateral: cladding -> girts -> diaphragm -> collectors
  -> frames/walls -> foundation. Every transfer needs a designed connection; discontinuities hide the errors.
- Typical L (Table 4.3-1, *check*): office 50 psf (2.4 kPa) + 15 partitions; corridors above 1st floor 80; lobbies,
  stairs 100; residential 40; assembly 60 fixed/100 movable; storage/manufacturing 125 light, 250 heavy; garage 40.

## 2. ASCE 7 combinations (2.3 LRFD / 2.4 ASD)
LRFD: (1) 1.4D  (2) 1.2D + 1.6L + 0.5(Lr or S or R)  (3) 1.2D + 1.6(Lr or S or R) + (L or 0.5W)
(4) 1.2D + 1.0W + L + 0.5(Lr or S or R)  (5) 0.9D + 1.0W  (6) 1.2D + Ev + Eh + L + 0.2S  (7) 0.9D - Ev + Eh
ASD: (1) D  (2) D + L  (3) D + (Lr or S or R)  (4) D + 0.75L + 0.75(Lr or S or R)  (5) D + 0.6W
(6) D + 0.75L + 0.75(0.6W) + 0.75(Lr or S or R)  (7) 0.6D + 0.6W  (8) D + 0.7Ev + 0.7Eh
(9) D + 0.525Ev + 0.525Eh + 0.75L + 0.75S  (10) 0.6D - 0.7Ev + 0.7Eh
- Eh = rho*QE, Ev = 0.2*SDS*D. Overstrength combos use Emh = Omega0*QE (collectors, columns under discontinuous walls,
  anchorage). L factor in LRFD (3),(4),(6) may be 0.5 where Lo <= 100 psf, except garages/assembly. W is strength level.
- EN 1990 6.10: 1.35Gk + 1.5Qk,1 + 1.5psi0Qk,i (psi0 imposed 0.7, snow 0.5, wind 0.6; NA governs); seismic G+psi2Q+AEd.

## 3. Live-load reduction (ASCE 7 4.7-4.8)
- L = Lo(0.25 + 15/sqrt(KLL*AT)) [ft2], SI 0.25 + 4.57/sqrt(KLL*AT) [m2], only where KLL*AT >= 400 ft2 (37.16 m2);
  L >= 0.50Lo for members supporting one floor, >= 0.40Lo for two or more.
- KLL: interior columns 4, exterior columns without cantilever slabs 4, edge columns with cantilever slabs 3, corner
  columns with cantilever slabs 2, interior beams and edge beams without cantilever slabs 2, all others 1.
- Not reduced: Lo > 100 psf and passenger garages (20 % allowed for members supporting >= 2 floors), assembly. One-way
  slabs AT <= 1.5*span^2. Roof Lr = 20*R1*R2, 12-20 psf: R1 = 1 (At <= 200 ft2), 1.2 - 0.001At, 0.6 (>= 600);
  R2 = 1 (F <= 4), 1.2 - 0.05F, 0.6 (F >= 12), F = rise in inches per foot.

## 4. Wind (ASCE 7 ch. 26-30)
- qz = 0.00256*Kz*Kzt*Kd*Ke*V^2 psf (V mph) in 7-16; SI 0.613*Kz*Kzt*Kd*Ke*V^2 Pa (V m/s). 7-22 moves Kd from qz into
  the pressure equations (same product). Kd = 0.85 buildings; Kzt = 1.0 flat terrain; Ke = 1.0 at sea level.
- Kz = 2.01(z/zg)^(2/alpha), z >= 15 ft; 7-16: B alpha 7, zg 1200 ft; C 9.5, 900; D 11.5, 700 (7-22 revised the table).
  Kz at 15 ft: B 0.57, C 0.85, D 1.03; at 30 ft: B 0.70, C 0.98. Exposure per direction: B = urban/suburban/wooded
  upwind > 2600 ft or 20h; D = flat unobstructed/water > 5000 ft or 20h; otherwise C (the default when unsure).
- MWFRS directional: p = q*G*Cp - qi*(GCpi), G = 0.85 rigid; windward qz varies with height, leeward/side/roof use qh.
  Low-rise envelope (h <= 60 ft): p = qh[(GCpf) - (GCpi)]. C&C: p = qh[(GCp) - (GCpi)]; GCp rises as effective wind
  area falls (area >= span x span/3); corner > edge > interior. GCpi enclosed +/-0.18, partially enclosed +/-0.55,
  open 0, both signs. Minimums: MWFRS 16 psf walls + 8 psf roof; C&C 16 psf. MWFRS to frames, C&C to cladding/purlins.

## 5. Seismic - equivalent lateral force (ASCE 7 ch. 11-12)
- SMS = Fa*Ss, SM1 = Fv*S1, SDS = 2/3 SMS, SD1 = 2/3 SM1 (7-22: multi-period, from USGS). SDC (RC I-III): SDS < 0.167 A,
  < 0.33 B, < 0.50 C, else D; SD1 < 0.067 A, < 0.133 B, < 0.20 C, else D; worse governs; RC IV one step up; S1 >= 0.75
  -> E (F for RC IV). Ie: RC I/II 1.0, III 1.25, IV 1.5. Ta = Ct*hn^x (hn ft): steel MRF 0.028, 0.8; concrete MRF
  0.016, 0.9; EBF/BRBF 0.03, 0.75; others 0.02, 0.75; computed T <= Cu*Ta (Cu 1.4 at SD1 >= 0.3 to 1.7 at SD1 <= 0.1).
- Cs = SDS/(R/Ie) <= SD1/(T*R/Ie) (T <= TL) or SD1*TL/(T^2*R/Ie) (T > TL); Cs >= 0.044*SDS*Ie >= 0.01; S1 >= 0.6 also
  Cs >= 0.5*S1/(R/Ie). V = Cs*W; W = D + 25 % storage live + partitions (>= 10 psf) + equipment + flat-roof snow share
  (share and threshold by code edition). Fx = V*wx*hx^k/sum(wi*hi^k), k = 1 (T <= 0.5 s), 2 (T >= 2.5 s), linear between.
- Typical R / Omega0 / Cd (Table 12.2-1; verify system, height limit, SDC): steel SMF 8/3/5.5; OMF 3.5/3/3; SCBF 6/2/5;
  OCBF 3.25/2/3.25; BRBF 8/2.5/5; EBF 8/2/4; special RC shear wall (building frame) 6/2.5/5; wood-panel light-frame
  walls 6.5/3/4; steel not detailed for seismic (SDC A-C) 3/3/3.
- Drift delta_x = Cd*delta_xe/Ie (T without Cu cap, Cs without minimum allowed). Allowable (Table 12.12-1, "all other"):
  RC I/II 0.020hsx, III 0.015hsx, IV 0.010hsx; masonry shear-wall 0.007-0.010hsx; SDC D-F moment frames limit/rho.
  P-delta theta = Px*Delta*Ie/(Vx*hsx*Cd) <= 0.10 ignore; theta_max = 0.5/(beta*Cd) <= 0.25.
- rho = 1.0 in SDC B-C and for drift, Fpx, nonstructural; SDC D-F 1.3 unless each story > 35 % V passes the removal
  test or is regular with >= 2 perimeter bays per side. Irregularities: torsional delta_max > 1.2 delta_avg (extreme
  > 1.4), reentrant > 15 %, diaphragm opening/stiffness change > 50 %, out-of-plane offset, nonparallel; soft story
  < 70 % of above (< 80 % of 3-story avg), weight > 150 %, geometric > 130 %, in-plane offset, weak < 80 % (extreme
  < 65 %). Effects: Ax = (delta_max/1.2delta_avg)^2 in 1-3; +25 % collector connections (SDC D-F); no ELF in SDC D-F
  for T >= 3.5Ts or H1/V1-V3 (Table 12.6-1); some prohibited in SDC E-F.
- Fpx = (sum Fi/sum wi)*wpx, 0.2*SDS*Ie*wpx <= Fpx <= 0.4*SDS*Ie*wpx, + transfer forces; collectors x Omega0 in SDC C-F.

## 6. Distribution to vertical elements and model checks
- Flexible diaphragm (untopped wood/steel deck typical, or deflection > 2x average drift of supports): tributary width,
  no torsion. Rigid (slab, topped deck): by stiffness plus torsion about the centre of rigidity:
  Vi = V*ki/sum(k) + V*e*ki*di/J, J = sum(kx*dy^2) + sum(ky*dx^2), e = actual + accidental 0.05 x plan dimension
  perpendicular to the force, both signs; torsion may not reduce direct shear. Orthogonal 100 % + 30 % where required.
- Before using results: sum reactions = applied load per case (0.1 %); hand estimate within ~10-15 % (wL^2/8, portal or
  cantilever method); deflected shape sensible; units checked on one member; base fixity as actually built.
- Stiffness: ACI 318 6.6.3.1.1 beams 0.35Ig, columns 0.70Ig, walls 0.35Ig cracked / 0.70Ig uncracked, flat plates
  0.25Ig (x1.4 for service drift). Steel: AISC direct analysis (0.8EI/EA, tau_b, notional 0.002Yi) or B1/B2.

## 7. Serviceability (IBC Table 1604.3; project limits govern)
- Floors L/360 live, L/240 total; roofs: plaster ceiling L/360 / L/240, non-plaster L/240 / L/180, none L/180 / L/120;
  walls brittle finish L/240, flexible L/120; supporting masonry L/600 <= 0.3 in; cantilevers use 2x length; ponding.
- Wind drift typical H/400-H/500 (H/600 brittle cladding) under ~10-year wind. Walking vibration (AISC DG 11):
  fn = 0.18*sqrt(g/Delta); ap/g = 65 lb*exp(-0.35fn)/(beta*W) <= 0.5 % office, 1.5 % malls; beta 0.02-0.05; fn >= 3 Hz.

## 8. Existing buildings, alterations, extensions
- IEBC: repair, alteration Level 1/2/3 (Level 3 = work area > 50 % of building), addition, change of occupancy.
  Gravity: an element whose D, L or S (incl. new drift) rises > 5 % must comply or be strengthened. Lateral: an element
  whose demand/capacity ratio rises > 10 % over the existing case triggers compliance; additions independent or within
  that 10 %; tabulate DCR with/without the work per element. Higher risk category, substantial alteration or damage
  triggers seismic evaluation (often ASCE 41, reduced forces).
- ASCE 41: Tier 1/2/3; BPOE (RC II) Life Safety at BSE-1E, Collapse Prevention at BSE-2E; knowledge factor 0.75-1.0;
  m-factors x expected strength (deformation-controlled), lower-bound strength (force-controlled). Existing capacity
  from as-builts, era code/grades, survey and testing - never assume current-code detailing.
- Alteration work typically covers: investigation; old-vs-new load comparison to the foundation (drift against a taller addition, new
  equipment); temporary works (propping, back-propping, needling, bracing while lateral elements are cut); sequence with
  stability at every stage; new-to-existing connections (post-installed anchors per ACI 355/ICC-ES, movement joint vs
  tied); differential settlement; monitoring, hold points, fire protection, approvals.
