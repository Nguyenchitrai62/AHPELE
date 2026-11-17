---
name: structural-member-design
description: Structural member and connection design - steel (AISC 360: tension, compression, flexure, shear, interaction, bolts, welds, base plates), concrete (ACI 318: flexure, shear, development, slabs, punching, columns, deflection), timber (NDS), masonry (TMS 402), with demand/capacity tables.
---

# Structural member design

Project specifications, drawings and the adopted editions govern (AISC 360-16/-22, ACI 318-14/-19, NDS 2018, TMS
402-16, Eurocodes + NA); values below are code defaults or *typical*. Units: E steel 29,000 ksi (200 GPa); 1 ksi =
6.895 MPa; 1 kip-ft = 1.356 kN-m; US formulas use sqrt(f'c) in psi (SI differs: 2sqrt(f'c) psi = 0.17sqrt(f'c) MPa).

## 1. Working method
- Row per check: member, location, governing combo, demand + units, capacity formula with every factor (phi/Omega,
  adjustments, lengths), capacity, D/C, OK/NG. LRFD Ru <= phi*Rn, ASD Ra <= Rn/Omega - never mix. Check every limit
  state (beam: yield, LTB, local buckling, shear, deflection, web crippling, connections), record the governing one;
  properties from the manual for the exact shape; units (kip/lb, in/ft, psi/ksi, kN-m/N-mm). Project may cap D/C < 1.

## 2. Steel - AISC 360 (phi LRFD / Omega ASD)
- Tension: yield Fy*Ag (0.90/1.67); rupture Fu*Ae, Ae = U*An (0.75/2.00); net-area hole width d + 1/8 in; stagger adds
  s^2/(4g). Block shear 0.6Fu*Anv + Ubs*Fu*Ant <= 0.6Fy*Agv + Ubs*Fu*Ant (0.75/2.00), Ubs 1.0 uniform. L/r <= 300.
- Compression (E3; 0.90/1.67): Fe = pi^2*E/(Lc/r)^2; Lc/r <= 4.71sqrt(E/Fy) (113 at 50 ksi): Fcr = 0.658^(Fy/Fe)*Fy,
  else 0.877Fe; Pn = Fcr*Ag. K recommended: pin-pin 1.0, fix-fix 0.65, fix-pin 0.80, fix-free 2.1; sway frames via
  alignment chart or direct analysis (K = 1). Use larger of KLx/rx, KLy/ry; slender elements per E7; Lc/r <= 200.
- Flexure, compact doubly symmetric I, major axis (F2; 0.90/1.67): Mp = Fy*Zx; Lp = 1.76ry*sqrt(E/Fy);
  Lr = 1.95rts(E/0.7Fy)*sqrt(Jc/(Sx*ho) + sqrt((Jc/(Sx*ho))^2 + 6.76(0.7Fy/E)^2)), c = 1. Lb <= Lp: Mn = Mp;
  Lp < Lb <= Lr: Mn = Cb[Mp - (Mp - 0.7Fy*Sx)(Lb - Lp)/(Lr - Lp)] <= Mp; Lb > Lr: Mn = Fcr*Sx <= Mp with
  Fcr = Cb*pi^2*E/(Lb/rts)^2*sqrt(1 + 0.078*(Jc/(Sx*ho))*(Lb/rts)^2). Cb = 12.5Mmax/(2.5Mmax + 3MA + 4MB + 3MC)
  (1.14 uniform load unbraced; 1.0 conservative). Compact at 50 ksi: bf/2tf <= 0.38sqrt(E/Fy) = 9.2, h/tw <= 3.76sqrt
  (E/Fy) = 90.6; noncompact flange F3. Minor axis Fy*Zy <= 1.6Fy*Sy. Lb = spacing of compression-flange bracing; deck
  on the top flange does not brace the bottom flange under uplift or negative moment.
- Shear (G2): Vn = 0.6Fy*Aw*Cv1, Aw = d*tw; rolled I, h/tw <= 2.24sqrt(E/Fy): Cv1 = 1.0, 1.00/1.50 (else 0.90/1.67).
  J10: web yielding Fy*tw*(5k + lb) interior, (2.5k + lb) at end (1.00/1.50); web crippling (0.75/2.00); stiffen if NG.
- Combined (H1-1): Pr/Pc >= 0.2: Pr/Pc + (8/9)(Mrx/Mcx + Mry/Mcy) <= 1.0; else Pr/(2Pc) + Mrx/Mcx + Mry/Mcy <= 1.0,
  with second-order moments (direct analysis or B1/B2).
- Bolts (J3; 0.75/2.00): Rn = Fn*Ab; Group A (A325): Fnt 90 ksi, Fnv 54 threads included (N) / 68 excluded (X);
  Group B (A490): 113, 68/84; A307: 45, 27. Bearing 2.4d*t*Fu, tearout 1.2lc*t*Fu per bolt. Tension+shear: F'nt =
  1.3Fnt - Fnt*frv/(phi*Fnv) <= Fnt. Slip-critical mu*Du*hf*Tb*ns, mu 0.30/0.50 (Class A/B), Du 1.13, phi 1.00/Om 1.50
  std holes; Tb Group A 3/4" 28 k, 7/8" 39 k, 1" 51 k. Spacing >= 2-2/3d, edge per J3.4, prying, eccentric groups (IC).
- Welds (J2; 0.75/2.00): fillet Rn = 0.60FEXX*0.707w*L*(1.0 + 0.5sin^1.5 theta); E70 = 1.392 kip/in per 1/16 in leg
  (LRFD), 0.928 (ASD). Base metal shear: yield 0.6Fy*t (phi 1.00), rupture 0.6Fu*t (0.75). Min fillet by thinner part:
  <= 1/4 in: 1/8; to 1/2: 3/16; to 3/4: 1/4; over: 5/16. Max along edge t (t < 1/4) or t - 1/16. CJP matching = base.
- Base plates (DG1, J8): bearing 0.65/2.31, Pp = 0.85f'c*A1*sqrt(A2/A1) <= 1.7f'c*A1; t = l*sqrt(2Pu/(0.9Fy*B*N)),
  l = max(m, n, lambda*n'), m = (N - 0.95d)/2, n = (B - 0.8bf)/2, n' = sqrt(d*bf)/4.
- Anchors (ACI 318 ch. 17): steel phi 0.75 tension / 0.65 shear; breakout Nb = kc*lambda*sqrt(f'c)*hef^1.5 (kc 24 cast-
  in, 17 post-installed), phi 0.70 (0.75 with supplementary bars); pullout 8Abrg*f'c; blowout, pryout; x0.75 SDC C-F.

## 3. Concrete - ACI 318 (strength design)
- phi: tension-controlled 0.90; compression-controlled tied 0.65, spiral 0.75, linear between (318-19 epsilon_t from
  epsilon_ty to epsilon_ty + 0.003; 318-14 0.002 to 0.005); shear/torsion 0.75; bearing 0.65; plain 0.60.
- Flexure: a = As*fy/(0.85f'c*b), Mn = As*fy(d - a/2); beta1 = 0.85 to 4000 psi, -0.05 per 1000 psi, >= 0.65; c = a/
  beta1, epsilon_t = 0.003(dt - c)/c. Design: Rn = Mu/(phi*b*d^2), rho = (0.85f'c/fy)(1 - sqrt(1 - 2Rn/(0.85f'c))).
  Beams As,min = max(3sqrt(f'c), 200)*bw*d/fy and epsilon_t >= 0.004; slabs/footings 0.0018Ag (Gr 60), s <= 3h, 18 in.
- Shear: Vc = 2*lambda*sqrt(f'c)*bw*d (with Av,min; 318-19 without it 8*lambda*lambda_s*rho_w^(1/3)*sqrt(f'c)*bw*d,
  lambda_s = sqrt(2/(1 + d/10)) <= 1); Vs = Av*fyt*d/s <= 8sqrt(f'c)*bw*d. Av,min = max(0.75sqrt(f'c), 50)*bw*s/fyt
  where Vu > 0.5phi*Vc; s <= d/2 <= 24 in, d/4 <= 12 in if Vs > 4sqrt(f'c)*bw*d. Critical section d from support face.
- Development (simplified, clear spacing and cover >= db with stirrups, or >= 2db): ld = fy*psi_t*psi_e*psi_g/
  (25*lambda*sqrt(f'c))*db for #6 and smaller, /20 for #7+ (other cases /16.7, /13.3); >= 12 in; psi_t 1.3 top bars,
  psi_e 1.5/1.2 epoxy (psi_t*psi_e <= 1.7), psi_g 1.0 Gr 60 / 1.15 Gr 80 (318-19); sqrt(f'c) <= 100 psi. Gr 60, 4000 psi
  #8: 47db. Tension laps Class B = 1.3ld (Class A 1.0ld only if As,prov >= 2As,req, <= 50 % spliced). Hooks (318-19)
  ldh = fy*psi_e*psi_r*psi_o*psi_c/(55*lambda*sqrt(f'c))*db^1.5 >= 8db, 6 in; compression ldc = max(0.02fy/(lambda*
  sqrt(f'c)), 0.0003fy)*db >= 8 in.
- Slabs: one-way if long/short > 2. Min h without deflection calc (Gr 60): one-way slab l/20 simple, l/24 one end
  continuous, l/28 both, l/10 cantilever; beams l/16, l/18.5, l/21, l/8; flat plates ln/30 exterior without edge beam,
  else ln/33, >= 5 in. Two-way static moment Mo = qu*l2*ln^2/8 (DDM interior span 0.65 negative / 0.35 positive).
- Punching (22.6; phi 0.75): bo at d/2 from column faces; vc = least of 4, (2 + 4/beta), (2 + alpha_s*d/bo) times
  lambda*lambda_s*sqrt(f'c) psi (alpha_s 40/30/20 interior/edge/corner, beta = long/short column side). Unbalanced
  moment: vu = Vu/(bo*d) + gamma_v*Mu*c/Jc, gamma_v = 1 - 1/(1 + (2/3)sqrt(b1/b2)). Edge/corner columns and openings
  near columns govern; fixes: thicker slab, drop panel, larger column, stud rails.
- Columns: phi*Pn,max = 0.80phi*Po tied (0.85 spiral), Po = 0.85f'c(Ag - Ast) + fy*Ast; rho_g 1-8 % (<= 4 % practical).
  Interaction points: pure axial, balanced (epsilon_s = epsilon_ty), tension-controlled, pure bending. Slenderness
  neglected if klu/r <= 22 (sway) or <= 34 + 12(M1/M2) <= 40 (nonsway; 318-14+ M1/M2 negative in single curvature).
  delta = Cm/(1 - Pu/(0.75Pc)) >= 1, Cm = 0.6 - 0.4M1/M2, Pc = pi^2(EI)eff/(klu)^2, (EI)eff = 0.4Ec*Ig/(1 + beta_dns);
  Ec = 57000sqrt(f'c) psi (4700sqrt(f'c) MPa); fr = 7.5lambda*sqrt(f'c).
- Cracking: s <= 15(40000/fs) - 2.5cc <= 12(40000/fs), fs = 2/3fy (Gr 60, 2 in cover: 10 in). Cover: earth 3 in;
  exposed #6+ 2 in, #5- 1.5 in; interior slabs/walls 3/4 in, beams/columns 1.5 in to ties (fire/exposure may add).
- Deflection: Ie = Icr/(1 - ((2/3)Mcr/Ma)^2(1 - Icr/Ig)) for Ma > (2/3)Mcr (318-19); long-term xi/(1 + 50rho'), xi 2.0
  at 5+ years. Limits (24.2.2): floors L/360 immediate live; after attachment L/480 damage-prone, L/240 otherwise.

## 4. Timber - NDS (reference values x adjustment factors, ASD)
- Fb' = Fb*CD*CM*Ct*CL*CF*Cfu*Ci*Cr; Ft' = Ft*CD*CM*Ct*CF*Ci; Fv' = Fv*CD*CM*Ct*Ci; Fc' = Fc*CD*CM*Ct*CF*Ci*CP;
  Fc_perp' = Fc_perp*CM*Ct*Ci*Cb; E' = E*CM*Ct*Ci; Emin' = Emin*CM*Ct*Ci*CT. Glulam: lesser of CL and CV.
- CD: permanent 0.9, occupancy live 1.0, snow 1.15, construction 1.25, wind/seismic 1.6, impact 2.0; check every
  combination with the CD of its shortest load (D alone at 0.9 can govern). Cr 1.15 for 3+ members <= 24 in o.c.;
  CM for MC > 19 %; Ct above 100 F; CF from the size table for dimension lumber.
- CP = (1 + a)/(2c) - sqrt(((1 + a)/(2c))^2 - a/c), a = FcE/Fc*, FcE = 0.822Emin'/(le/d)^2, c 0.8 sawn / 0.9 glulam,
  le/d <= 50. CL same form with FbE = 1.20Emin'/RB^2, RB = sqrt(le*d/b^2) <= 50, c = 0.95.
- fv = 1.5V/(b*d) (loads within d of support may be excluded); notches cut shear sharply. Fasteners Z, W x CD, CM, Ct,
  Cg, C_delta, Ceg. SDPWS walls/diaphragms nominal/2.0 ASD, x0.80 LRFD. NDS LRFD: KF, phi, lambda 0.6 (1.4D)-1.0 (W/E).

## 5. Masonry - TMS 402
- Em = 900f'm CMU, 700f'm clay (f'm typ. 1500-2500 psi); phi flexure/axial 0.90, shear 0.80, bearing 0.60; block
  0.80f'm over a = 0.80c; epsilon_mu 0.0025 CMU, 0.0035 clay.
- Vnm = [4.0 - 1.75(Mu/(Vu*dv))]*Anv*sqrt(f'm) + 0.25Pu (Mu/(Vu*dv) <= 1.0); Vns = 0.5(Av/s)*fy*dv; Vn <= 6Anv*sqrt(f'm)
  (M/(Vd) <= 0.25) to 4Anv*sqrt(f'm) (>= 1.0). Out-of-plane walls: second-order P-delta, Pu/Ag <= 0.20f'm (0.05f'm if
  h/t > 30), maximum-reinforcement strain limits. Lintels L/600 <= 0.3 in.

## 6. Load transfer and other codes
- Follow the force: member -> weld/bolt -> plate -> weld/bolt -> supporting member -> its web/flange local checks, with
  eccentricities. Composite studs Qn = 0.5Asa*sqrt(f'c*Ec) <= Rg*Rp*Asa*Fu. Eurocode (recommended, NA governs): gammaM0
  = gammaM1 = 1.0, gammaM2 = 1.25; fcd = alpha_cc*fck/1.5 (alpha_cc 1.0, UK 0.85), fyd = fyk/1.15; timber gammaM 1.3.
