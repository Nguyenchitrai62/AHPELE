All deliverables are present, complete, and validated. Final verification results:

## Files at the exact path
`/filesystem/final_batch4__mechanical_task3_ct_heat_lcc__blind/output/submission.zip` (134,099 bytes, 8 files, `unzip -t` OK):

```
CT_SCHEDULE_CUP.dxf     CT_CALC_CUP.xlsx
CT_SCHEDULE_ANNEX.dxf   CT_CALC_ANNEX.xlsx
CT_SCHEDULE_LAB.dxf     CT_CALC_LAB.xlsx
constraint_register.csv design_basis.md
```

## Validation
- `ahpele_check.py` on the zip → **no problems found** (all formats parse).
- Schema enumeration script → **NONE**: every DXF cell key (11) and plant key (14), one closed polyline per installed cell, `G-TBLK` revision, five exact workbook sheets, every required `DesignPoint`/`WaterBalance`/`Energy`/`LifeCycleCost` key numeric, `OffDesign` 17 columns × 180 rows all numeric with Hours = 8,760, evaporation method agrees, register 95 × 6 CSV rows, design basis with 3 governing lines and 3 conflict lines.
- `ahpele_reqscan.py --check` → **82/82 strong candidates reviewed, 0 unreviewed**.
- My engineering audit (rebuilds each plant from its DXF, recomputes energy/water/LCC, checks all hard limits, geometry, clearances, structural loads, COC/PSI, allocations, MCC, redundancy, validity envelope, L/G, totals) → **0 failures**.

## Final design
| Plant | Cells / model | Flow (gpm) | Floor/offset (°F) | COC | CWS sched / achieved (°F) | Peak / MCC (kW) | Makeup / allocation (kgal) | NS (USD) | Governing constraint |
|---|---|---|---|---|---|---|---|---|---|
| CUP | 4 × CTX-0600-S | 1,800 | 65 / 11 | 4.13 | 91.0 / 85.36 | 513.0 / 528 | 9,743 / 10,300 | 240,555 | structural capacity 0.0250 |
| ANNEX | 4 × CTX-0600-S | 1,800 | 80 / 11.5 | 3.99 | 91.5 / 85.69 | 570.7 / 590 | 12,555 / 12,600 | 246,666 | water allocation 0.0035 |
| LAB | 3 × CTX-0900-H | 2,025 | 58 / 8.5 | 3.86 | 88.5 / 85.99 | 633.1 / 641.14 | 17,057 / 17,400 | 290,978 | electrical capacity 0.0125 |

Design wet bulb 80.0 °F (1.0 % 75.0 + 5), redundancy wet bulb 81.0 °F (0.4 % 76.0 + 5), 99.6 % dry bulb 41.0 °F (no basin heater), SATURATED-EXIT water balance, SS-304 casings/basins, DE-2 eliminators, premium-efficiency 6-pole TEFC motors, 4 ft basin clearance. All redundancy capacities exceed the block loads; all condenser/cell flow, WFR and L/G limits are met; all three plants are inside the reclaimed-water allocation, peak-day and blowdown limits and the MCC spare capacities.

The independent findings and their dispositions (including the one part of finding 5 rejected — the peak-day test is the PW-LTR-014 design day, not the highest-rate bin) are appended to `/tmp/ahpele/independent_review.md`.