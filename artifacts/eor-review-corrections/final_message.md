Final validation is complete. All seven required files exist at the top level of the submission zip, parse correctly, satisfy their schemas, and every hard check passes.

## Deliverable

`/filesystem/dc_structural__eor_revision__blind/output/submission.zip` — 29,339 bytes, 7 files:

| File | Validation |
|---|---|
| `disposition_register.csv` | 34 rows (BP‑2 16 / BP‑3 18), exact 14 columns: 24 CONCUR, 2 documented NON_CONCUR, 8 VOID with grounds |
| `sheet_index.csv` | 56 rows, exact 7 columns, discipline order G/GI/C/S/M/E and G/GI/S/A/M/E/T |
| `revision_log.csv` | 33 rows, exact 7 columns: BP‑2 mark 3 / overflow Option 2; BP‑3 no-entry rows |
| `issue_plan.csv` | 33 rows, exact 7 columns, all bundles ≤50 MB, discipline sets whole |
| `continuation_sheet.md` | Amendment 0003 format, 2 added + 14 replaced, Document 00 01 15 LIST OF DRAWINGS, BP‑3 statement |
| `constraint_register.xlsx` | 73 requirement rows, exact template columns, 0 value-lookup failures |
| `design_basis.md` | Exactly one JSON block, all required keys, narrative (a)/(b)/(c) |

## Final plan

Reference sweep is **block-to-block** per `drawings/README.txt`: a callout belongs to its drawing block and points to the block it calls out, so only blocks whose callouts point at the changed block are reissued.

| | BP‑2 | BP‑3 |
|---|---|---|
| Issue state | **AMENDMENT 0003** | **PRE_ADVERTISEMENT_REISSUE** |
| Sheets | 16 (14 reissued + 2 added) | 17 (15 reissued + 2 added) |
| Bundles | 3 | 2 |
| Production / delay | 14 days → 14 Sep 2026, D = 1 | 12 days → 12 Sep 2026, D = 0 |
| Ledger | **$57,886.92** | **$46,558.66** |
| **Combined** | **$104,445.58** | |

- **Layers:** `Z-ANNO-REVC` (clouds) / `Z-ANNO-REVS` (symbols/notes/block), per FC 1‑300‑09N para. 12‑3.3.4 precedence.
- **Overflow:** 8 rows; six full BP‑2 sheets; Option 2 set-wide on M‑501/S‑502, $1,760 vs Option 1 $3,120.
- **Title blocks:** BP‑2 E‑501 (seal discipline) and S‑301 (CHK=DRW); BP‑3 A‑501 (CHK=DES) and M‑101 (seal discipline).
- **Non-concurrences:** EOR‑2‑011 and EOR‑3‑030, each cost-justified against adoption.
- **Voids:** 8 markups with stated grounds (superseded prints, non-roster authors, missing timestamp, closed/elevated).

## Checks run

- `ahpele_check.py`: no problems.
- `ahpele_reqscan.py --check`: 184/184 strong candidates reviewed, 0 unreviewed.
- `ahpele_reqscan.py --register`: 73 rows, 0 not-found / 0 unmatched.
- 16-gram licensing scan: 0 hits in both narratives.
- Citation scan: 0 unknown clauses.
- Independent PDF-derived block-level recomputation (`verify_final.py`): 0 failures; ledger, bundles, issue sets, title blocks and revision rows all match.
- `check.py`: 0 errors.

The independent review response and rejected findings are appended to `/tmp/ahpele/independent_review.md`.