Final validation complete — every deliverable exists at the exact path and format, and all checkers pass.

## Deliverable

**`Municipal_Witness_Test_Package.docx`** — Rev 1, 07/14/2025, 19 pages, 66,129 bytes, MD5 `1925c1d80ed2d593c35608f82f5abf20`
- **Document store (as instructed):** `/DER_Program/Commissioning/Municipal/Municipal_Witness_Test_Package.docx` — confirmed listed, correct MIME, downloaded over WebDAV and hash-matched
- **Local mirror:** `/filesystem/Commissioning/Municipal/Municipal_Witness_Test_Package.docx` — same hash

Working records: `/tmp/ahpele/requirements.csv` (59 rows), `rejected.csv`, `checklist.md`, `asks.md`, `check_municipal_package.py`, `final_validate.py`, and the finding dispositions appended to `independent_review.md`.

## Contents of the package

- **Scope:** five arrays in scope on 07/14/2025; Tresbay Community Center out (withdrawn 07/09/2025, case WP45).
- **Carriage, one-way calls:** Cravenwood High **YES** (SM-215K-3P, CEL-2025-Q2 row 6); Marden Falls **YES** (SM-245K-3P, row 7); Darnwick **NO** (Arvexa PV-750 absent from both CEL editions); Holcott **NO** (SV-720 only on superseded CEL-2024-Q4 row 29); Lockmere **NO** (actual installed SV-720, not the checklist's TE-180K).
- **Witness scope (Darnwick, Holcott, Lockmere):** full DPS-07 §6.2 set including items 1–2 (insulation resistance/dielectric, CT/VT ratio-polarity-burden) and ANSI 79/reclose-block where a POI recloser is installed; DPS-07 §4.5 anti-islanding basis; corrected IEEE 1547 Category II ride-through criterion (no trip *inside* the envelope, trip *outside* within the specified time).
- **Roles and prerequisites:** customer/EPC performs, Standards Engineering witness engineer witnesses (no self-witnessing), Distribution Protection Engineering issues the §6.3 written acceptance; record list before test and before PTO, including the ER-11/POI-recloser determination and the unconditional Lockmere AHJ reconciliation.
- **Schedule:** Holcott 07/22, Darnwick 07/24, Lockmere 07/29/2025, reserves 07/25, 07/31, 08/05; latest test 08/08; waiver-decision deadline 07/18 with a §3.6 fallback.
- **SOC release list as of 07/14/2025: none.** Marden Falls is the only candidate — carried and telemetry recorded, but the waiver is unsigned (ENG-PRC-014 §4.3), no Form ER-11 determination on DPS-07 §4.2 is on file (F-12), and the RTU model/transport are not recorded (TCS-02 §3.2/§4.1, F-13).
- **Case:** WP45 Closed/100% with the batch determination and a Rev 1 revision comment; exactly three scheduling items (WP47/48/49, due 07/22, 07/24, 07/29) matching the three witness-test arrays, with three "includes" relations from WP45. Waiver disposition explicitly reserved to Standards Engineering.

## Verification results

- `final_validate.py`: **FILE VALIDATION PASSED** (all files present, DOCX structure and 13 required sections present, all three copies identical)
- `ahpele_check.py`: **no problems found** on the built file, local mirror and store copy
- `ahpele_reqscan.py --check`: **54/54** strong candidates reviewed, **0 unreviewed**
- `ahpele_reqscan.py --register requirements.csv`: **rows=59, notfound=0, unmatched=0, multi=0**
- `check_municipal_package.py`: **ALL CHECKS PASSED** (scope 5 / carried 2 / witness 3 / releasable 0; CEL rows re-read; schedule and business-day arithmetic; findings; case/package agreement; store-copy hash)