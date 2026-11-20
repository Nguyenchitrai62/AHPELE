Everything is in place and validated.

## Deliverable
`/filesystem/final_batch4__structural_task7_roof_deck_design__blind/output/submission.zip`  
37,373 bytes — four files at zip root, integrity OK.

| File | Contents |
|---|---|
| `deck_design.xlsx` | Six sheets in required order: Zones (4 zones / 14 rectangles), DesignBasis (all 17 keys), Drifts (4 required rows), CalcSummary (4 zones), Diaphragm (S05–S08, S10), BOM |
| `roof_deck_plan.dxf` | 14 closed `S-DECK-ZONE` polylines matching the Zones sheet, 4 zone labels on `S-DECK-TEXT`, 48 framing lines on `S-FRAMING`, 3 openings on `S-OPENING`; feet, grid 1-A origin |
| `constraint_register.xlsx` | `Register`, 112 rows, one governing document and ≤3 clauses per row, ≤8 numbers per row; reqscan clean |
| `design_basis.md` | 4,875-word narrative covering document precedence, snow/seismic bases, diaphragm analysis/classification, zoning/cost decisions, checks and EOR items |

## Final design
- Z1 22g 36/4 BP×2, 5,184 sf; Z2 22g 36/9 SCREW-10×5, 11,376 sf; Z3 18g 36/7 SCREW-10×3, 21,216 sf; Z4 18g 36/9 SCREW-10×5, 4,536 sf.
- Two gages, three patterns, four zones, 14 rectangles, all boundaries on the 6 ft module.
- Installed cost **USD 218,140** at CP-RD-2026 rates.
- BOM: 18 gage 25,752 sf; 22 gage 16,560 sf; support fasteners 17,359 ea; sidelap connectors 8,532 ea.
- Drifts: MEP-PH-1 W 104.3 psf / 41.2–60.0 ft; SCR-N S 89.5 / 147.5–163.7; PARAPET N 34.0 / 167.1–179.3; RTU-1 E 98.2 / 36.0–53.7.

## Verification
- Independent re-read of the submitted zip: **0 failures** — gravity 0.926, uplift 0.922, shear 0.902, snow deflection 0.272 in of 0.30, end reaction 0.549, chord 27.82/38.0 kip, amplified collector 41.30/58.0 kip, diaphragm deformation 0.98 in of 1.60, regularisation springs 0.31%.
- `ahpele_check.py`: all four root files present and format-valid.
- `ahpele_reqscan.py --check`: 72/72 strong candidates reviewed, 0 unreviewed.
- `ahpele_reqscan.py --register`: 112 rows, 0 not-found, 0 unmatched, 0 multi-document.

## Review disposition
The independent review findings were checked against the documents. Confirmed and fixed include the bearing requirement (staggered/lapped panel ends on the 2.5 in chord), MEP-PH-1 W / RTU-1 E drift rows, span/240 = 0.30 in, cost reduction, register clause/number fixes, BOM/grid explanation, model-validation wording, permanent fall protection, and opening/zone documentation.

Rejected findings, with reasons, are at the end of `/tmp/ahpele/independent_review.md`: the 28.6 ft SCR-N band (5.4.3 requires 0.75 hd, giving 16.13 ft), the 111.7 psf RTU-1 E value (0.75 hd gives 98.2 psf), and treating total nodal displacement as the 9.2 diaphragm-deflection quantity (the frames alone translate 1.75 in; the relative diaphragm deformation is 0.98 in < 1.60 in, and the diaphragm is semi-rigid under either reading).