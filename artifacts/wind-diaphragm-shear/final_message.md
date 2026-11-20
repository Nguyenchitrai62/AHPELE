All deliverables are in place at the exact path, in the required formats, and validated end-to-end from the submitted zip.

## Deliverable

**`/filesystem/final_batch4__structural_task5_wind_diaphragm_shear__blind/output/submission.zip`** — 125,800 bytes, exactly five files, `unzip -t` clean, MD5 `2e5ef67e0ffcf71e32f2f0f8797c5e82`.

| file | validation |
|---|---|
| `lateral_schedule.xlsx` | Exactly 9 sheets with the template headings: DeckZones 12, ChordSchedule 12, Piers 73, ShearWalls 72, Diaphragm 216, Chords 144, Drift 24, Convergence 3, Cost 26. No blank/placeholder cells; deck/chord/embed/tie-down quantities and costs reconcile; installed cost **$394,296.16**. |
| `diaphragm_plan.dxf` | 153 entities on the seven required layers; one plan on the building grid at the SW origin (X east, Y north, feet); grid A–G / 1–6; deck zones; all-12-scenario unit-shear and reaction envelope; chords/collectors; TRANSVERSE + LONGITUDINAL labels; ASD statement on its face. |
| `constraint_register.xlsx` | Sheet `Register`, 141 rows, six required columns, including EOR 5.1, 5.7, 8.1, 10.3, VE-1 published values and S-201 notes; every clause appears in the document it cites; `reqscan --register` → 0 notfound / 0 unmatched / 0 multi; no superseded documents. |
| `calculations.pdf` | 27 pages, 8½×11 portrait, ASD on its face; sections 1–12 plus Appendix A (full line-load table) and Appendix B (315-patch pressure take-off); full 63-panel connection design table; documented deck cost search. |
| `design_basis.md` | Both required tables with the exact item names and line/governing-scenario rows; 15 conflicts resolved in prose; numbers agree with the workbook and PDF. |

## Engineering results
- Deflection **0.5204 in ≤ 0.55** (utilisation 0.946); pier drift 0.377 ≤ 0.84 in.
- Deck D/C 0.539 (Z21); base connection 1.053 ≤ 1.40 kip/ft; chord D/C 0.386; 4 deck types; convergence L2→L3 0.108 %.
- 146 E1 embeds (unique panel total = Cost quantity); 48 T1 tie-downs (47 required by 0.6D+0.6W, S07 provided as reserve).
- Every reported shear, reaction, chord force and deflection re-derived from the workbook inputs and rebuilt DIAPH-MT model to <0.005 plf / 0.0005 kip / 0.00005 in.

## Review findings
All findings fixed except two rejected with reasons recorded at the end of `/tmp/ahpele/independent_review.md`: VE-1 chord (0.28 kip is inside the criteria's 2 kip absolute acceptance tolerance; all other VE-1 quantities reproduce) and the Piers embeds column (the task defines it as the panel quantity, repeated per pier row; unique-by-panel total 146 = Cost).

**Open item:** OBD §4.7's $310,000 cap is below the structurally achievable minimum. The selected design is $394,296; the cheapest design found at the 0.55 in limit is $377,079, and the reviewer's cheaper deck option fails at 0.633 in. This is reported with the search evidence in `calculations.pdf` §9/§11 and `design_basis.md` §8.14; no structural limit was relaxed.

Validation run on the extracted zip: `ahpele_check.py` → no problems; `ahpele_reqscan.py --check` → 21/21 reviewed; `ahpele_reqscan.py --register` → clean; full hard-limit/consistency self-check → **OVERALL PASS**.