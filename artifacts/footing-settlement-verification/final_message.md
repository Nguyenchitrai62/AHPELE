Final validation is complete — every required file exists at its exact path, parses correctly, and passes all checks.

## Deliverable

**`/filesystem/Thelbridge_Verification_Memo_Item051_BlockC.docx`**
- Microsoft Word DOCX, 9 pages, 5 tables, 5,914 words.
- Template sections 1–5 retained in order; header, cc and signature block complete.
- To: Adrian Vance, Project Engineer; From: Rahul Nimkar, Geotechnical Reviewer; cc: Rachel Marlbeck; Date: 07/20/2026.

## Determination

**NOT VERIFIED (design review) — revise and resubmit; Item 051 remains Open.**

Key findings in the memo:

- **CB-GEO-007 Sheet 4 says “Not computed”** — long-term consolidation is omitted. Total settlement is **6.32 in** on the designer’s stated basis and **5.38–6.75 in** across the defensible σ′₀/OCR treatments, against the **1.0 in** limit (utilisation 5.4–6.8). The totals exclude the Block B fill surcharge and secondary compression, so 6.32 in is a lower bound.
- **Load basis:** q_net is (D + 0.8L)/A, not service D + L. Full D + L at F-C6 is **3,918 psf, 98%** of the 4,000 psf allowable. The Es values used for the 0.90 in immediate settlement are not traceable to the GIR or Vantree report.
- **σ′₀:** 1,850 psf is the post-fill Block B stress, not Block C (1,685 psf); the B-06/B-08 sample elevations in the Vantree report, boring logs and CB-GEO-007 disagree.
- **Monitoring:** 0.61 in at MP-7 on 06/26/2026 — 61% of the limit since the 12/12/2025 baseline, with the rate increasing. The points are on a local A/1–D/3 grid not reconciled to S-101’s B–L / 6–8 grid, and the applied load stage is not recorded; at full load the predicted value at that date is 2.82 in (U ≈ 35.5%). The correlation is not closed.
- **Coverage:** 12 calculated footings against 30 on S-101 Rev.4; the 12 are not demonstrated to govern (documentation gap under GIR §8.1/§9.1).
- **Other:** as-built geometry conflicts with S-201 Rev.4 Detail 3; long-term differential and angular distortion are not computed; bearing is provisional at 98%; the calculation is an unsealed workbook in the review set.

## Required actions before closure

- **Gregory Nash / Calloway Braddock (EOR):** revised, sealed CB-GEO-007 Rev.1 by 07/31/2026 covering consolidation, secondary compression, per-footing Δσ, the service load combination, as-built geometry, Es derivation, fill surcharge, 30-footing coverage and monitoring correlation.
- **Alden Roscombe / Kelbrook with Vantree:** confirm σ′₀/σ′p/OCR, sample locations and elevations, cv/Cα and Es by 07/27/2026.
- **Steven Kendrow / Marcus Whitfield / Rowan Bay:** reconcile the 12 points to S-101, report applied load and measured-vs-predicted settlement at each load stage, and apply no additional load to Block C.
- **Thelbridge:** keep Item 051 open and re-verify; earliest realistic closure 08/07/2026.

## Validation performed

- `ahpele_check.py` on the DOCX and all CSV/Python working files — **no problems**.
- `ahpele_reqscan.py --check` — **375/375 strong candidates reviewed, 0 unreviewed**.
- `ahpele_reqscan.py --register requirements.csv` — **21 rows, 0 not-found/unmatched/multi-clause**.
- `verify.py` — all internal assertions pass; governing 6.32 in, upper bound 6.75 in, most favourable 5.38 in.
- `check_memo.py` — all content checks pass.
- `final_check.py` — all line-by-line checks pass.
- LibreOffice render — 9 pages, signature block on the final page, no blank or broken pages.

Supporting files: `/tmp/ahpele/requirements.csv`, `/tmp/ahpele/rejected.csv`, `/tmp/ahpele/verify.py`, `/tmp/ahpele/check_memo.py`, `/tmp/ahpele/final_check.py`, `/tmp/ahpele/checklist.md`, `/tmp/ahpele/asks.md`, and the revised review record at `/tmp/ahpele/independent_review.md` (including the reasons for the findings rejected in whole or in part).