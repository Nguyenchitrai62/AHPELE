All deliverables are present, complete, and validated.

**Location:** `/filesystem/dc_structural__foundation_strategy__blind/output/submission.zip`  
52,200 bytes, exactly six files at archive root, `unzip -t` clean.

| File | Content |
|---|---|
| `foundation_geometry.json` | 6 pads × 6 foundations = 36; BIM Rev. 2 shape; 3-in grid; no nulls; spread footings zeroed pier fields; W1 stability fields |
| `ground_improvement_plan.json` | n_s = 10, 30-in piers, 2 rigs × 2 pads, $80,000 mobilisation, 1 test per improved pad, k_g, treatment depths, 761/769/440/753 pier LF |
| `foundation_schedule.xlsx` | Owner template, all 36 rows, field-for-field agreement with the parameter file |
| `foundation_feasibility_matrix.md` | Pad-by-pad and foundation-by-foundation demand, bearing, settlement, true AD, W1 stability incl. D+L+W toe, governing constraint, both alternative costs |
| `constraint_register.xlsx` | Owner template, 111 rows; 85 live HARD requirements in the first 96; real documents/clauses; cancelled/superseded/inapplicable documents marked set aside |
| `design_basis.md` | Opens with required fenced JSON block; covers governing criteria and set-asides, bearing/settlement methods and FS basis, tolerable movement, ground improvement, conflicts, campus programme, action items |

**Final outcome:** P1/P2/P4/P6 improved spread, P3/P5 shallow spread. Bearing depths 42–48 in, all in Stratum I; FS 3.5 / 3.5 / 3.5 / 3.0 / 3.0 / 3.5. Max settlement 0.880 in; max true angular distortion 0.001417 (0.71 of 1/500); max bearing utilisation 0.957; max shear utilisation 0.949; R_a 0.3377–0.4086; max gross top-of-pier stress 14,934 psf; sliding FS 2.30; uplift FS 2.72. Campus total **$460,100** with 2 rigs and $80,000 mobilisation.

**Validation:** `check_submission.py` 0 errors; `verify.py` 0 errors/0 warnings; `ahpele_check.py` no problems; `ahpele_reqscan.py --register` notfound=0/unmatched=0/multi=0; `ahpele_reqscan.py --check` 35/35 project candidates reviewed. Content validation confirmed 6 pads, 36 foundations, 36 schedule rows, 111 register rows, and a parseable design-basis JSON block with a matching campus total. Review dispositions, including the one rejected finding (W1 ratio L×t retained with reason), are recorded at the end of `/tmp/ahpele/independent_review.md`.