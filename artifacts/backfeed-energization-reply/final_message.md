All requested deliverables are present, complete and validated.

## Deliverables

- **Word letter:** `/filesystem/Halbray_Backfeed_Reply.docx` — valid Microsoft Word DOCX, **2 pages**, dated **07/14/2025**, addressed to Ms. Imogen Strathe.
- **OpenProject work package:** **#47** in project 3, `DER Program Backlog Review` — “Halbray Field Solar Site 3 (PXA-2024-0002) — pre-PTO backfeed conditions,” Task, High priority, assigned to **S. Rennick**, start **2025-07-14**, due **2025-07-29**.
- **Working files:** `/tmp/ahpele/requirements.csv` (54 requirements), `rejected.csv`, `checklist.md`, `asks.md`, `check_halbray.py`, and `independent_review.md` with the review disposition appended.

## Determination in the letter

**07/29/2025 is not confirmed on the 07/14/2025 record.** Kelloway Township final approval under permit EP-25-0418 is the gating item; final inspection is booked for 07/24/2025 and no final approval is in the record.

The letter states that 07/29 remains achievable if written final approval issues before the switching order is released — approval need not issue by 07/24 — and these items are closed:

1. Kelloway final approval — Halbray/Tamsworth, before the switching order.
2. Inverter isolation/lockout at AD-1 to AD-4 — Halbray/Tamsworth.
3. CSB-1 arc-flash label content — Tamsworth, before the 07/24 inspection.
4. Inverter ac Type USE-2 above-ground cable — Tamsworth.
5. 13.2 kV interconnection conductor record — Tamsworth, or written confirmation it is utility-owned.
6. 800 V feeder ampacity/termination basis, including the NEC 250.122(B) EGC check — Tamsworth.
7. Revenue meter RM-0002 test/seal — Alleniom Metering, before switching.

The letter records that the backfeed energizes the 13.2 kV interconnection, T-1, CSB-1 and the collection system only up to the open AD-1 to AD-4; the inverter skids remain isolated. RTU/POI recloser acceptance, settings/coordination, switching, queue position and the SIS are expressly outside the letter; CEL, witness test and SOC telemetry are PTO items.

## Review disposition

- **Confirmed and fixed:** findings 2–10 and 12 — removed the incorrect 07/24 final-approval deadline; added the 13.2 kV and 800 V ampacity record confirmations; corrected the energized scope; corrected the arc-flash citation to NEC 110.16(A) and NFPA 70E 130.5(H); included all items in the path; tracked the meter test/seal; attributed construction-complete to Halbray; used the shared program contact; and moved the CEL statement to PTO.
- **Rejected finding 1:** NEC 2023 Table 250.122 assigns **1 AWG Cu to 600 A**; **2/0 Cu is the 1000 A row**. The recorded 1 AWG feeder EGC is at the table minimum, not undersized. The letter instead requires the NEC 250.122(B) proportionality check in the feeder ampacity basis.
- **Rejected finding 11:** REQ-PER-01 to 04 already cite `R0108` and EQ-DC cites `R0154`; the remaining blanks are table/drawing requirements with no scanner candidate.

## Validation

- `ahpele_check.py`: **no problems**.
- `ahpele_reqscan.py --check`: **68/68** strong project-document candidates reviewed, **0 unreviewed**.
- `ahpele_reqscan.py --register requirements.csv`: **54 rows**, `notfound=0`, `unmatched=0`, `multi=0`.
- `check_halbray.py`: **PASS**; worst hard-limit utilisation **1.000** on the EGC at the NEC Table 250.122 minimum, with the 250.122(B) check required in the ampacity calculation.
- DOCX renders to **2 pages**; OpenProject WP #47 read back with the correct project, subject, assignee, dates and description.