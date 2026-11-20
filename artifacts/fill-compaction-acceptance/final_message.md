All required deliverables exist at the exact paths, are complete, and pass the format, content, register and hard-limit checks.

## Deliverable

**`/filesystem/Thelbridge_Materials_Acceptance_Fill_Compaction_2026-0708.docx`** — 10-page Materials Acceptance Record built on `Thelbridge_Materials_Acceptance_Record_TEMPLATE.docx`, dated 07/16/2026, signed by Karen Tarbray. All five template sections are present in order, with four tables and no placeholders.

## Determination: REJECTED

**Register entry:** Item 054 — **Status Closed; disposition REJECTED; verification date 07/16/2026.** The fill remains unaccepted. A new register item is required for the Lift 6 rework/retest and stockpile qualification.

## Basis and limits

- **Basis:** Specification Section 31 20 00 Rev.3 (03/06/2026), Articles 1.2.A.1/A.2, 1.3.E, 1.4.C, 2.1.A–D, 3.4.B/D and 3.7.B/C — ASTM D1557 Method C on the material actually placed. ASTM D698 is expressly not the acceptance basis.
- **Density:** ≥95% of 128.4 pcf = **121.98 pcf** (report rounds to 122.0 pcf).
- **Moisture:** **8.2%–11.2%** (9.2% optimum −1%/+2%).
- **Material:** USCS SM/SW-SM; ≤12% passing No. 200; PI ≤6; no organic material, frozen soil, debris or particles >3 in.
- **Procedural limits:** D1557 per source; subgrade proof-roll and prior-lift hold points; witnessed test strip; 8 in loose/7.2 in compacted within 12 in; hand lifts ≤6 in and 3-ft setback; wall backfill under Article 3.5; protection under 3.8.A; settlement under 3.6; capillary break under 2.3.

The 128.4 pcf/9.2% D1557 is the only one on file and is for **Larchwood Pit**, not the stockpile north of Block C actually placed. The RFI 079 gradation retest and letter TPM-25-079 are missing, and the Larchwood Pit report “pertains only to the sample tested.” The density results are therefore provisional, not certified. The Article 2.1.A/B/C material requirements are likewise not established for the stockpile.

## Results

| Test | Dry density (pcf) | Moisture (%) | % comp. vs 128.4 | Outcome |
|---|---:|---:|---:|---|
| FD-14 | 124.8 | 6.1 | 97.2 | **Moisture fail** — 2.1 points below 8.2% |
| FD-15 | 123.5 | 9.8 | 96.2 | Numeric pass; not accepted on basis |
| FD-16 | 122.9 | 10.4 | 95.7 | Numeric pass; only 0.92 pcf margin; not accepted on basis |
| FD-17 | 126.1 | 5.8 | 98.2 | **Moisture fail** — 2.4 points below 8.2% |

The report’s D698-based values (105.2%, 104.1%, 103.6%, 106.3% against 118.6 pcf) are not valid for acceptance. The report also omits the moisture criterion, gives only a density-only PASS disposition, and records no issue time.

## Record gaps and required actions

The record identifies: the D698 reference, density-only disposition, no issue time (24-hour requirement not demonstrated), missing calibration certificate and operator training/competency records, 6-in probe in a 7.2-in lift, missing FDR-BA-01 through FDR-BA-05, missing Lift 5 rework retest, missing proof-roll memo TPM-26-063 and 20-ton tandem record, missing test-strip results, 0.42 in overnight rain after Lift 5, unresolved Article 3.5 wall-backfill status, missing stockpile Article 2.1 qualification, and the RFI 065 frequency conflict.

Ten actions are required before construction, including rework/retest at the Contractor’s expense, stockpile qualification with D1557/gradation/Atterberg/USCS/deleterious inspection and RFI 079 retest, reissued SF-26-0708 with issue time and curve-fit confirmation, Lifts 1–5/rain records, proof-roll/test-strip/edge records, wall-strength/lateral-support and balanced-lift records or a documented scope determination, gauge/operator records, protection, and a new acceptance record. The capillary break must also satisfy Article 2.3.

## Independent review

All 14 findings were reviewed. Eleven were adopted and the record revised. Three were qualified or rejected with reasons appended to `/tmp/ahpele/independent_review.md`: Finding 5 (premise that the fill log establishes wall-adjacent placement), Finding 6 (remedy to change the sealed D1557 values), and Finding 14 (demand for candidate IDs on scanner-missed direct-text rows).

## Final checks

- `ahpele_check.py`: **no problems** — DOCX 6,223 words, 4 tables; CSV and Python files valid.
- `check.py`: **PASS**, 0 failures; 76 requirement rows, 0 unaddressed (22 PASS, 3 PROV, 39 GAP, 2 FAIL-REPORTED, 8 N/A, 2 REF).
- `final_consistency.py`: **PASS**.
- `ahpele_reqscan.py --register`: **76 rows, 0 not-found, 0 unmatched, 0 multi**.
- `ahpele_reqscan.py --check`: **375/375 strong project candidates reviewed; 0 unreviewed**.

Supporting QA files: `/tmp/ahpele/requirements.csv`, `/tmp/ahpele/rejected.csv`, `/tmp/ahpele/verify.py`, `/tmp/ahpele/check.py`, `/tmp/ahpele/final_consistency.py`, `/tmp/ahpele/checklist.md`, `/tmp/ahpele/asks.md`, `/tmp/ahpele/independent_review.md`.