All required deliverables are present and valid. Final check results:

- **Deliverable:** `/filesystem/CFDME-2025-041_transient_solve_disposition_revA.docx`
- **Format:** valid Microsoft Word 2007+ DOCX, 13 pages / 8,092 words, no format problems under `ahpele_check.py`.
- **Requirement coverage:** 245/245 candidates reviewed; register checker reports **75 rows, 0 not found, 0 unmatched, 0 multi-clause**.
- **Engineering checks:** `verify.py` passes **322/322**.
- No missing or incomplete deliverable files.

**What the note contains**
- Signed disposition dated **10/10/2025** rejecting attempt 3 and authorizing no fourth steady solve.
- Expected plume behaviour **0.87 Hz / 1.15 s**; residual plateau **148 iterations**; on the log’s stated **0.001 s** pseudo-time, **0.15 s / 6.76 Hz — 680% above** expected. Alternatives shown: **0.68 Hz (22.0% low)** on the delivered 0.01 s step and **0.0068 Hz (99.2% low)** on the 1 s counter. The claimed 1.15 s is shown not to be a measurement.
- Item-by-item standards review covering solver, turbulence, radiation, inlet, solids, CHT, tie refinement, time control, regime record, case completeness and CO-002. Confirmed non-conformances include the one-band radiation model (32 rays are S4-equivalent), reversed inlet direction, 2.0× tie refinement versus 4× required, missing case files, and the unresolved CO-002 mesh of record.
- Authorized transient block: **`endTime 31.10 s`**, **`writeInterval 0.0461 s`**, `deltaT 0.0010 s`, `adjustTimeStep yes`, `maxCo 0.9`, `maxDeltaT 0.0090 s` as a 10% reserve below the 0.0100 s ceiling.
- Delivered `controlDict` corrected to **`endTime 2000 s`**, not 20.00 s; attempt 3 ran `endTime 800` outer iterations.
- Mesh: rev C production mesh, **11,214,862 cells**; verification covers the **0.5 m background D*/dx = 7.48** and checkMesh quality, not the **0.125 m source-zone D*/dx = 29.9**, the Pope time-average, tie refinement, CO-002, or production statistics.
- Carry-forward: rev C geometry, inlet type/profile after correcting `flowDir` to **`(+0.866, +0.500, 0)`** for 240° and **`(+1, 0, 0)`** for 270°, EDC/JANAF chemistry, 32-ray S4 fvDOM with two 2.5 µm bands, and iteration-800 fields only as a warm-start.
- Cost: **4 h 28 min per case**, **26 h 49 min for six cases** on the firm basis, explicitly a lower bound because the basis conditions are not met. Attempt 3 consumed **6 h 41 min on 64 cores**; at equal cores one authorized case is **13 h 25 min**, so attempt 3 used **50.2% less wall clock** and **50.6% less CPU-time**.
- All 17 independent-review findings were checked and addressed; none rejected outright. The review disposition is recorded at the end of `/tmp/ahpele/independent_review.md`.