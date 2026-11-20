All deliverables are present, complete and valid at the exact path and format required.

## Final verification

**Path:** `/filesystem/final_batch4__electrical_task17_ec_0205_d100__blind/output/submission.zip` (11,119 bytes, 5 members at the zip root, no extras).

| Member | Rows / size | Header | Blanks | Status |
|---|---|---|---|---|
| `takeoff.csv` | 17 data rows | exact `type_mark,description,quantity` | 0 | ✅ |
| `locations.csv` | 101 data rows (structural bays A1–D4) | exact `sheet,type_mark,grid_bay,condition,count` | 0 | ✅ |
| `bom.csv` | 90 data rows = 63 attribution + 27 purchase | exact 8-column schema | 0 | ✅ |
| `register.csv` | 23 data rows (E-01…E-22 incl. E-04b) | exact `family,document,clause,value,how_satisfied` | 0 | ✅ |
| `basis.md` | 1,870 words | conventions, sheets per type, governing issue, unresolved symbols, condition split, assemblies with clauses, spare/carton method, basket total | — | ✅ |

**Checks re-run just now**
- Format: `ahpele_check.py submission.zip` → **no problems found**; all five members parse with exact headers, no blank cells, basket `$15,943.22` present in the basis.
- Requirements: `ahpele_reqscan.py --check` → **33/33 reviewed, 0 unreviewed**; `--register` → **23/23 rows matched, 0 not found**.
- Engineering consistency (own checker, re-read from the zip): takeoff = locations per type; every attribution row = pair count × multiplicity; every unit price = the item's own required-quantity band; every purchase ≥ 1.05 × required and a whole carton; every extension exact; basket in `basis.md` = sum of attribution rows; all 27 catalogue items have a purchase row — **ALL CHECKS PASSED**.

**Final numbers:** 207 devices (D1 27, F1 12, F2 3, F3 3, F4 6, F5 24, J1 36, P1 7, R1 36, R2 7, R3 5, R4 6, R5 25, R6 4, R7 6; R8/F6 zero). Basket (work) **$15,943.22**; all rows including purchase **$34,137.75**.

**Review disposition:** findings 1, 2, 4, 5, 6, 8, 9 fixed; findings 3 (R5 double-count) and 7 (R5 keyed condition) rejected with reasons recorded at the end of `/tmp/ahpele/independent_review.md` — the four west-corridor R5 cannot serve the four perimeter CRAHs at tiles B01/P01/AC01/AQ01, and the task convention explicitly assigns DRY-STUD where a keynote names no wall.