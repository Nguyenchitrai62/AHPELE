All deliverables are present, valid and checked.

## Deliverable
`/filesystem/CFDME-2025-041_resolution_note_revA.docx` — 7 pages, 3 tables, 4,406 words. It re-opens cleanly (`ahpele_check.py`), converts to PDF without error, and contains the complete memo, conformance table, closure/decision section and signature block.

## What the note says
- **Index:** D*/dx = **29.9** at **dx = 0.125 m** and **D* = 3.74 m** (30.1 using the report’s 3.76 m). At the 0.25 m plume-box cell it is **15.0**. The firm band **5–10 is not met** on either fire-region cell; only the 0.5 m background cell gives 7.5, and that is not the fire region.
- **Cell-size audit:** the mesh log sets level 4 inside `refinementBox_plume` (0.25 m) and level 5 within 3.00 m of `plumeSource` (0.125 m); the 0.75·D* probe at 2.81 m is inside that zone. Report §6.2 and the three-grid study header independently put the fire-source cell two levels below the 0.5 m background. The log’s L3 “plume core” / L5 “wall boundary layer” annotation is flagged as an internal documentation defect.
- **Acceptance basis:** QA Verification Standard rev 3 §5 accepts either the band (§5.1) or the Pope criterion (§5.2), either alone. The project requires ≥20 puffing cycles / ≈23 s (Modeling rev 4 §4; SOW §3.1), not the QA ten-cycle floor. The §6.1 three-grid table is not valid LES verification. The 84% is a summary assertion in the three-grid LES study, not a documented time average; the study’s fine-grid max Courant is 0.90 at the 0.9 limit, and the live controlDict is not the required transient control.
- **Probe and ambient:** the probe is inside the 0.125 m region, but the 84% is not demonstrated to be a time average. The reported D* uses sea-level 20 °C air; the site gives **D* = 3.88 m** and **R = 31.0** (+3.7% vs 3.74 m; +3.2% vs the memo’s 3.76 m), still outside the band. The DWA archive gives 6.40–6.49 m and R = 51.2–51.9, but its ambient does not represent the site and conflicts with the log’s T = 308.15 K.
- **Decision:** checklist item 4 **cannot close on the present record**. It can close without a new run on the **§5.2 route alone** if a Verification addendum states the 84% with probe coordinates and a ≥20-cycle averaging window, and puts the required values, SGS closure and total cell count into a Verification section ahead of Results and Validation. Otherwise it needs a new LES run/mesh in the band or a written deviation from §5.1. No separate acceptance of D*/dx >10 is required on the §5.2 route.

## Independent review
All 13 findings were checked against the documents and addressed. Two proposed alternatives were rejected on the record:
- Finding 1’s alternative that 7.5 may be the plume-core index and the band met — rejected because the operative mesh settings, report §6.2 and the study header all put the fire-source cell at 0.125 m; even 0.25 m gives 15.0.
- Finding 11’s statement that the study “asserts a window length” — rejected in part because “20+ cycles sampled” is a sampling statement, not a documented averaging window.

## Supporting files
- `/tmp/ahpele/requirements.csv` — 50 hard requirements, all cited and checked.
- `/tmp/ahpele/rejected.csv` — 255 candidate dispositions.
- `/tmp/ahpele/asks.md` — every instruction question with a direct answer.
- `/tmp/ahpele/checklist.md` — deliverable checklist and final verification record.
- `/tmp/ahpele/verify_resolution.py` — independent recomputation and conformance check.
- `/tmp/ahpele/independent_review.md` — reviewer findings plus the disposition of each.
- `/tmp/ahpele/verify_output.txt`, `reqcheck.txt`, `reqreg.txt`, `notecheck.txt` — final check logs.

## Final validation
`verify_resolution.py` exits 0 with all checks passed; `ahpele_reqscan.py --check` reports **245/245** strong candidates reviewed, **0 open**; `--register` reports **50 rows, notfound=0, unmatched=0, multi=0**; `ahpele_check.py` reports all deliverable files clean. PDF re-render: 7 pages, US Letter.