Final verification complete — every required deliverable exists at the specified path, in the specified format, and all checks pass.

**Deliverable:** `/filesystem/final_batch4__structural_task6_seismic_diaphragm_shear__blind/output/submission.zip` (73,774 bytes; exactly 5 files at the zip root, no enclosing folder)

| File | Validation |
|---|---|
| `design_record.json` | Parses; all template keys present; cost $386,864; `parapet_transfer_plf` = 316.1 |
| `diaphragm_plan.dxf` | All required layers present; E‑W and N‑S plans; w_px, zone shears/patterns, wall forces, CH/DR/OP runs and forces, revision block, LRFD statement |
| `seismic_calculations.xlsx` | Required sheets `WEIGHTS, BASE_SHEAR, DIAPHRAGM_FORCES, WALL_FORCES, PARAPET_ANCHORAGE, CHORD_FORCES` with exact headers, plus Stage A/B, deck, checks and cost sheets |
| `constraint_register.xlsx` | 162 rows, exact six columns, 0 notfound / 0 unmatched / 0 multi |
| `design_basis.md` | 13 sections, 17 rejected alternatives, 13 conflicts resolved, cost vs cap |

**Final design:** intermediate precast shear walls, R = 4, Ω₀ = 2.0 collectors, C_d = 4; W = 2,270.5 kip, V = 312.2 kip; all deck zones P5; C3 W8x31 on S/N, C2 L6x4x1/2 on W/E, C1 opening chords; JC1 joints; BA2 tie-downs; WA2 S/N and WA1 W/E at 8 ft. Installed cost **$386,864 < $395,000** cap.

**Checks:** `ahpele_check.py` — no problems; `ahpele_reqscan.py --check` — 25/25 candidates reviewed; `--register` — 162 rows, clean; independent recomputation — 0 failures. Worst utilisations: deck Z10 **0.976**, S base tie-down **0.979**, cost **0.979**; CH‑S 0.907, wall anchor W/E 0.857. Stage A reproduces DAP‑2 VP‑1 exactly; Stage B equilibrium 0.9986–1.0000.