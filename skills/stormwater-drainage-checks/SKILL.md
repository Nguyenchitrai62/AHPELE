---
name: stormwater-drainage-checks
description: How a civil reviewer checks site drainage - detention basins and emergency spillways (weir sizing, freeboard, crest/berm/apron, erosion protection, overflow path), rational-method flows, storm-drain Manning/HGL checks, when revisions trigger a drainage-study amendment, and plan-vs-study QA/QC. Use for any stormwater, detention, spillway, storm drain or drainage-report review task.
---

# Stormwater and drainage review

## 1. Governing records and their order
- Build a register: accepted drainage study (and its acceptance letter with conditions), worksheets/calcs, plan
  sheets (plan, profile, detail), agency comments, county/district criteria manual. Cite record + page/table for
  every value. The accepted study is the baseline; plans must agree with it or the difference must be justified.
- Agency criteria override textbook defaults. Read the acceptance letter conditions verbatim: they usually list
  what changes void acceptance or require an amendment/resubmittal.
- Units: US (ft, cfs, in/hr, ac) vs SI (m, m3/s, mm/h, ha). Never mix within one equation; state units on every value.

## 2. Detention basin and emergency spillway
- Elevation stack (check it is monotonic and identical on plan, section, detail and study): basin bottom / outlet
  invert < primary outlet control elevations < routed 100-yr WSE < spillway crest < spillway design WSE
  (crest + H) < top of berm. Typical criteria: crest at or above the routed 100-yr WSE (often +0.5 ft), freeboard
  >= 1.0 ft (0.3 m) from spillway design WSE to top of berm (some agencies 1-2 ft or more; dam-safety
  jurisdiction applies above size/height thresholds). Use the agency number when one exists.
- Design flow: commonly the unrouted 100-yr peak INFLOW with the primary outlet assumed fully blocked (some
  agencies 1.25-1.5 x Q100, the 500-yr, or a PMF fraction for regulated dams). Using routed outflow, or crediting
  the outlet, under-sizes the spillway - flag it.
- Broad-crested weir: Q = C L H^1.5. US: C about 2.6-3.1 ft^0.5/s (2.6-2.8 for grassed/irregular earthen crest,
  ~3.0 typical, 3.087 theoretical). SI: C about 1.44-1.71 m^0.5/s (C_SI = C_US x 0.552). L = crest (bottom) length
  perpendicular to flow; H = head above crest measured upstream. Solve H = (Q / (C L))^(2/3), then
  freeboard = top of berm - (crest + H). Side slopes add flow; conservative practice ignores them, or uses the
  mid-depth width L + z H as an approximation (say which). Sharp-crested C (3.33 US / 1.84 SI) is wrong here.
- Recompute every number shown with the stated C, L, Q; do not round intermediate values. Report the margin
  (required vs provided) and which criterion governs.
- Location: cut the spillway into undisturbed native ground beside the embankment where possible, not in fill;
  keep it away from the outlet structure. Flow over fill needs armour down the full downstream face to the toe.
- Erosion protection: riprap, turf reinforcement mat, articulated block or concrete across crest, downstream face
  and apron. Riprap stone size (Isbash, a screening check): D50 = V^2 / (2 g C^2 (Gs - 1)), C = 0.86 high
  turbulence / 1.20 low, Gs ~ 2.65, g = 32.2 ft/s2 (9.81 m/s2) -> D50[ft] ~ V^2/78.6 for C = 0.86. Layer thickness
  >= 1.5 x D50 (or D100, whichever larger, many manuals 2 x D50) on geotextile or granular filter; toe-down/key at
  the apron end; concrete cutoff walls at crest edges and apron end to stop undermining and seepage (depth per
  detail, commonly 2-3 ft / 0.6-1 m below finished grade). Size outlet aprons from a stated method (e.g. FHWA HEC-14,
  local manual); length and width depend on Q, tailwater and pipe/opening size.
- Velocity: compute at the chute/toe (critical depth on the crest, supercritical down the face); energy
  dissipation (apron, stilling basin, riprap basin) where the slope flattens or flow re-enters a channel.

## 3. Where the overflow goes
- Trace the path from the crest to a safe receiver: public street, drainage channel, storm-drain system with
  capacity, or natural watercourse - within a drainage easement or right-of-way. It must not cross private lots,
  structures, slopes, septic fields or a neighbour's property without an easement, and must not divert water to a
  different watershed or concentrate sheet flow onto downstream property.
- Check grading contours/spot elevations along the path: does the ground actually fall that way? Note finished-floor
  elevations near the path (typical requirement: >= 1 ft above the overflow WSE). State the final receiving
  point by name/station.

## 4. Flows and storm drains
- Rational method: Q = C i A. US: Q cfs, i in/hr, A acres (factor 1.008 ignored). SI: Q = C i A / 360 with Q m3/s,
  i mm/h, A ha. i from the agency IDF at Tc (min Tc often 5-10 min). Frequency factor where used: 1.1 (25-yr),
  1.2 (50-yr), 1.25 (100-yr), with C x Cf <= 1.0. Weighted C = sum(Ci Ai)/sum(Ai). Typical limit ~ 200 ac (agency).
- Manning: V = (k/n) R^(2/3) S^(1/2), k = 1.486 US (1.49 rounded), 1.0 SI; Q = V A. Full circular pipe:
  Q = (0.464/n) D^(8/3) S^(1/2) US (D ft) / (0.312/n) D^(8/3) S^(1/2) SI (D m). n: concrete 0.012-0.013, smooth
  HDPE/PVC 0.010-0.012, corrugated metal 0.022-0.027. Partial flow: max Q ~ 1.08 Qfull at y/D ~ 0.94, max V at
  y/D ~ 0.81; Q = Qfull at y/D ~ 0.82. Velocity criteria typically >= 2-3 ft/s (0.6-0.9 m/s) self-cleansing, <=
  10-15 ft/s (3-4.5 m/s) unless lined/anchored.
- HGL: compute upstream from the outfall. Start at tailwater or (dc + D)/2 at the outlet, whichever is higher;
  add friction hf = Sf L with Sf = (Q n / (k A R^(2/3)))^2 and minor losses K V^2/2g (exit 1.0, entrance ~0.5,
  junction/bend/manhole per manual). EGL = HGL + V^2/2g. Typical criteria: HGL >= 0.5-1.0 ft (0.15-0.3 m) below
  inlet grates/gutter flowline and manhole rims for the design storm; check each structure, not just the last.
- Worksheet audit: carry the same Q, D, slope, n, length and inverts as the profile; slope = (inv up - inv down)/L;
  a pipe flagged "surcharged" needs the HGL check, not just capacity.

## 5. Does a revision need a study amendment?
- Usually yes when any of these change relative to the accepted study: drainage area boundaries or tributary
  areas, impervious area/runoff coefficient or land use, basin volume or stage-storage, outlet structure (sizes,
  elevations), spillway location/direction, routing or diversion, outfall location, or peak discharge leaving the
  site (any increase over accepted or allowable). Changes that only add detail consistent with the study (dimension
  callouts, notes, armour detail) are typically handled on the plans with a calc package or letter.
- Decide against the acceptance letter's own wording and agency comments; give one disposition with the reason.

## 6. Plan-sheet content and QA/QC
- Spillway detail should show: crest elevation and length, side slopes, design storm and Q (blocked-outlet basis),
  depth over crest and design WSE, top-of-berm elevation and freeboard dimension, lining type with D50/thickness/
  filter, apron length/width/thickness, cutoff walls, discharge direction, reference to the study/calc.
- Basin notes: 100-yr WSE and volume, outlet sizes/elevations, a note keeping the spillway and overflow
  path clear of obstructions, maintenance responsibility and easement, inspection/certification requirements.
- QA/QC habits: same elevation and label on plan, profile, section and detail; north arrow/flow arrows; units;
  notes cite the correct (current) study title/date; revision clouds match the comment response; every agency comment
  closed or answered with a sheet reference. Use drawing-takeoff for reading the sheets themselves.
