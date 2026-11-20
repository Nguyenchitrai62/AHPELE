Final verification is complete. The deliverable exists at the exact required path:

`/filesystem/final_batch4__mechanical_task5_pcw_flush_mop__blind/output/submission.zip`

It contains exactly the seven required files:

| File | Contents |
|---|---|
| `flush_plan.csv` | 52 rows × 25 cols (24 required + `softened_water_gal`), 8 circuits, all seven stage tokens |
| `chemistry_plan.csv` | 40 rows × 15 cols |
| `acceptance_matrix.csv` | 152 rows × 10 cols — RINSE / PASSIVATION / DISCHARGE / TURNOVER |
| `schedule.csv` | 62 rows × 9 cols |
| `resources.json` | all six required objects; `cost.total_usd` = **$96,771.15** |
| `constraint_register.csv` | 186 rows × 6 cols, no superseded/cancelled document cited |
| `MOP.md` | 9,840 words, 8 `GOVERNING CONSTRAINT` lines |

**Validation results**
- `ahpele_check.py` on the zip: **no problems found** (7 files, all schemas readable, no placeholders).
- `ahpele_reqscan.py --check`: **59/59** strong project-document candidates reviewed, 0 unreviewed.
- My independent `check2.py` re-deriving volumes, flush/passivation heads, component dP, durations, rinse counts, water/effluent identities, routes, chemistry packages, crew/skid overlaps, milestones, daily water, sewer cap, power and cost from the delivered files: **0 failures**.
- Worst hard-limit utilisations: flush velocity 0.971 (C5), flush head 0.807 (C1), passivation head 0.919 (C6), component dP 0.903 (C7 CL-401), rinse endpoint 0.990 (C7) — all below 1.0.

**Key plan values**
- Flush flows C1–C8: 1216.9 / 642.4 / 742.0 / 371.0 / 490.4 / 371.0 / 304.2 / 155.7 gpm.
- Passivation/turnover at reduced `Q_pass` with all components back in the path: C1 1156.1, C2 610.3, C3 650.7, C4 313.2, C5 382.4, C6 307.6, C7 267.5, C8 147.9 gpm.
- C4–C8 effluent all hauled; C1–C3 sewered. Sewer **307,678 gal**, haul **231,047 gal**.
- C1/C8 final rinse softened at ≤5,225 gal/day; final hardness <20 mg/L for C1/C8, 195–214 mg/L for C2–C7, all below 250 mg/L.
- Rinse 6/8 displacements, cascade first, C_n 652–670 µS/cm against 676.5.
- TM-1 day 4.3, TM-2 day 15, TM-3 day 29.1, TM-4 day 30.1.
- Governing constraint: **rinse endpoint** on every circuit, margins 0.0096–0.0359.

The independent review dispositions are appended to `/tmp/ahpele/independent_review.md`; findings 1 and 6 are rejected with the document basis explained there.