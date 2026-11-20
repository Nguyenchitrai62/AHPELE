All requested deliverables are in place and validated.

**Primary deliverable**

`/filesystem/Memo_to_Callaway_Spillway_2026-10-31.docx`

A 16-page, 9,180-word memo to Garrett Nokes, Callaway Land Partners, dated October 31, 2026, for Max Braddock’s signature.

**What the memo says**

- **G-4 cannot be answered from C-9 today.** The 20-ft weir requires 1.294793994 ft of head but only 0.70 ft is available to the existing top of berm; it overtops by 0.594793994 ft. The existing grouted-riprap apron has no velocity basis and is inadequate for the calculated toe velocity of about 20 ft/s.
- **Revised C-9 design:** 42-ft broad-crested weir at crest 2,858.50 ft; top of berm 2,860.80 ft; freeboard 1.510435137 ft at Q100, 1.265377340 ft at 1.5Q, 1.161812206 ft at 1.5Q with C = 2.6, and 1.090805995 ft at 145.2 cfs with C = 2.6. It includes a full stilling-basin design — 20 ft × 42 ft × 12 in, y1 = 0.105468291 ft, V1 = 19.956347843 ft/s, y2 = 1.563336794 ft, Lj = 10.059292669 ft, tailwater 2,854.563336794 ft, exit velocity 1.346326596 ft/s — plus 18-in D50 riprap 36 in thick. Top-of-berm storage is 10.222131129 acre-feet.
- **Amendment:** no formal MDS amendment is the committed disposition, subject to two mandatory conditions: the C-9 outlet must reproduce the MDS 27.9 cfs rating at 2,857.91 ft (the 12 in × 18 in orifice alone passes about 18.99 cfs; a 4-ft weir at 2,857.00 ft gives 29.402622206 cfs combined), and CCRFCD must confirm in writing under Condition 2 that the 2,860.80-ft top of berm is not a storage-indication input revision. If either fails, an amendment is required.
- **Overflow:** dedicated swale through Parcel E, then a dedicated channel in the Windmill Lane right-of-way to the shared outfall and CCRFCD regional facility — not the Windmill Lane gutter, which CCPW G-6 documents as already over-spread. The Parcel E drainage easement must be added to the final map before recordation.

**Validation**

- `check_memo.py`: **661 checks pass**.
- `ahpele_check.py`: memo DOCX and all supporting CSV/Markdown files clean.
- `requirements.csv`: 50 rows, 0 notfound/unmatched.
- `ahpele_reqscan.py --check`: **590/590** strong candidates reviewed, 0 open.
- Path, date, addressee, signature block, key conclusions, tables and no-placeholder checks all pass.

**Supporting files**

`/tmp/ahpele/requirements.csv`, `/tmp/ahpele/rejected.csv`, `/tmp/ahpele/check_memo.py`, `/tmp/ahpele/asks.md`, `/tmp/ahpele/checklist.md`, `/tmp/ahpele/independent_review.md` — the last contains the disposition of all 21 independent-review findings.