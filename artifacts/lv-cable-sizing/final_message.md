Final validation is complete: all five deliverables exist at the required top level of the zip, parse cleanly, and every hard check passes.

## Final summary

**Deliverable:** `/filesystem/electrical__lv_cable_sizing__blind/output/submission.zip` — 63 KB, 5 files at top level, SHA-256 `13e56fa8…24c3be6e`.

| File | Verified content |
|---|---|
| `wire_schedule.csv` | 32 circuits (every connected-load-schedule circuit), 27 columns in the exact required order; sizes/materials/EGCs/raceway/ducts/ampacities/VD/audit columns |
| `E-621_wire_schedule.dxf` | Title block naming **P-4210** and **E-621**; 32 schedule rows × 27 columns in CSV order; abbreviation list; every circuit designation and conductor size agrees with the CSV |
| `calc_book.xlsx` | Exactly `front_sheet` (54 parameters incl. all 17 required), `duct_assignment` (10 rows, one per duct-bank set), `cost_ledger` (last row `Total`) |
| `design_basis.md` | Fenced JSON block with `codes_of_record`, `environment`, `sources`, `voltage_drop`, `cost`, `duct_assignment`, `mutual_heating_rise_k`; 9 prose sections |
| `constraint_register.xlsx` | Exact 9-column header; 166 single-requirement rows (141 HARD / 25 SOFT), 20 documents, no blanks, superseded documents explicitly marked non-governing |

**Final engineering position**

- Codes of record: **NEC 2023 + IBC 2024**, adopted by **UFC 1-200-01**; most-restrictive precedence; **EDS-26 Rev 4** governs (Rev 2, E-601 Rev A and Meridian explicitly not governing).
- Environment: **42 °C** outdoor, **46 °C** roof, **27.45 °C** earth, **0.60 K·m/W** backfill (0.95 recorded as rejected), **1030 W/m²**.
- Ampacities calculated under engineering supervision (NFPA 70 **310.14**) using Cascadia heat balance and EDS-26 5.3 Neher-McGrath, capped at the 60/75 °C termination values.
- **SE-1 = 5 × 600 kcmil Cu** in DB-1 D1,D3,D4,D8,D9 = **2064 A** against the 2000 A bus; 6 × 500 kcmil (2229 A, $1,262 more) recorded as the fallback. **F-10 = 2 × 350 kcmil Cu** in D5,D10. **F-05 = 3 × 600 kcmil Al** in **E1,E2,E3**, one set per duct. DB-1 uses 7 loaded ducts, DB-2 3.
- VD starts at the **T-1 secondary lugs**, no reset at K-13; limits 3 % feeder / 3 % branch / 5 % total; worst own **2.347 %** (B-17), worst cumulative **4.999 %** (B-17), inside the 5.0 % limit and its 0.02-point allowance. Fire pump 1.41 % at FLC and 3.19 % at locked rotor.
- Five standardised sizes: **4/0, 300, 350, 500, 600 kcmil**.
- Installed cost **$151,236.32** = material **$98,230.49** + labour **$53,005.83**, including the 6 % quantity break on 39,752 ft of conductor; every ledger line’s material + labour equals its amount, and the total equals `total_usd` and the design-basis cost total. Raw re-extension agrees within $0.03 (per-line rounding).

**Review disposition:** 13 findings accepted and fixed (F-05 three-duct assignment and dT, R0012 scope, 5 × 600 service option, R0111 3/0 EGC, ledger rounding, tray ccc = 18, governing constraints, R0162/R0028/R0056/R0152/R0154, UFC clause); 3 rejected with reasons recorded at the end of `/tmp/ahpele/independent_review.md` (B-08 ambient already 40 °C, B-08 4 AWG EGC is the strict 250.122(B) result, fire-pump 3.19 % uses the stated 2179 A basis); design-current convention documented rather than changed; DXF row-count item needed no file change.

**Validation:** `ahpele_check.py` — no problems; `ahpele_reqscan --register` — 166 rows, 0 notfound/unmatched/multi; `--check` — 39/39 strong candidates reviewed, 0 outstanding; independent re-parse of Cascadia/E-619/NOAA/schedules — 0 ampacity, VD, EGC or length failures; ledger and hard-limit checks — 0 failures.