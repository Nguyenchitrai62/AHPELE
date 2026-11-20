# Desert Sage Ranch Phase 3 — L-4 Street Tree Revision / 11-30-2026 Resubmittal

**Bottom line:** The L-4 street-tree count (208 required vs 58 in the L-1 schedule/L-2 summary; +150 trees) and the revised annual irrigation demand (3.28 -> 4.20 ac-ft/yr) can be transmitted on 11/30/2026 as a partial revision. The complete, approvable package cannot be committed for 11/30/2026, and 12/18/2026 recordation cannot be held on this revision.

**Three independent date blockers, any one sufficient:**
1. L-2/L-3 turf is nonfunctional under SNWA WRC-2024-07 (lot-based carve-out; HOA park parcels expressly included; no playground amenities; 12/31/2026 deadline). It requires a Callaway decision, a dimensioned turf configuration exhibit, and likely Condition 14 design review/TAB.
2. The County's 20-business-day second-round review from 11/30 ends 12/29/2026, after 12/18 and after the 12/23/2026 statutory successive-map deadline. The latest complete resubmittal for 12/18 is 11/19/2026 (preferably 11/13).
3. CCWRD capacity confirmation CCWRD-SCC-2025-1187 expired 09/30/2026; Condition 22 requires a current confirmation at recordation and CCWRD requires re-review and reissuance. CCWRD's written turnaround is not in the record; 11/18 is not assumed.

**Separately, the package is not complete:** six hard General Comments remain open/in progress — F-1 permanent second point of access, F-2 cul-de-sac inside radius/turning exhibit, F-3 hydrant spacing/flow, F-4 fire-lane signage, G-5 storm-drain cover at Sta. 4+80 (2.6 ft against 3.0 ft), G-8 stand-alone ESC sheet — and the Condition 14 significant-change determination has not been made. All 30 comments must close and be back-checked; closing only the 10 Open and 3 Pending-client items is not enough.

## Files

| File | Purpose |
|---|---|
| `DSR_Ph3_L4_Street_Tree_Revision_Memo_2026-10-31.docx` | **The memo to Callaway** — dated 10/31/2026, from Max Braddock, for signature. Answer-first: 11/30 and 12/18 determination, the three date blockers and six hard comment items, L-4 math, L-2 finding/configuration gap, schedule arithmetic, a 16-item action table with owners/dates, recommendation. |
| `DSR_Ph3_Landscape_L1-L4_Rev1_L4_Tree_Revision_2026-11-30.pdf` | **Rev 1 review exhibit — not the sealed sheet set.** L-1 and L-2 revised for the L-4 count and L-5 dimensions (208-symbol location schematic, frontage table, schedule, sections); L-3/L-4 Rev 0. Delta 1 markers plus a revision-block row on each revised page. It expressly states that the issued CAD sheets must carry the clouds/revision triangles and that a sealed scaled 208-tree plan is still required. |
| `DSR_Ph3_Landscape_Tabulation_Rev1.xlsx` | Required vs shown by frontage (128/59/21; 34/16/8; 94/43/13; 208/58/150), species (50/79/79; 224 total), shade coverage (exact species-diameter area 58,473 sf / 65.2%), L-2 options A/B/C, **Turf Hydrozone Configuration** (L-2 area/category/configuration gap), document cross-check, revision log. |
| `DSR_Ph3_Irrigation_Demand_Worksheet_Rev1.xlsx` | 224 trees x 2,000 gal = 448,000 gal = 1.37 ac-ft; total 4.20 ac-ft (exact 4.2077), +0.92 vs 3.28; L-2 scenario totals 2.31 (full conversion) / 2.74 (hybrid). |
| `DSR_Ph3_Water_Budget_Rev1.xlsx` | Companion water budget: HZ-1 2.32 + HZ-2 0.51 + HZ-3 1.37 = 4.20 ac-ft; Rev 0 3.28; L-2 scenarios A 4.20 / B 2.31 / C 2.74. |
| `DSR_Ph3_Comment_Response_Matrix_Landscape_Rev1.xlsx` | L-1 through L-6 responses. L-4 is **PARTIAL — count/schedule/irrigation complete; sealed scaled planting plan, LA seal and utility clearance outstanding; NOT CLOSED.** L-5 answered in Rev 1; L-1/L-2/L-3/L-6 open. |
| `DSR_Ph3_Resubmittal_Tracker_Review_2026-10-31.xlsx` | Tracker status (10 Open / 3 Pending client / 17 In progress / 0 closed), schedule arithmetic (20 business days; 12/29; six business days after 12/18), 14 tracker findings including F-14 for the hard fire-access/pipe-cover/ESC items, and a 16-row critical path. |
| `DSR_Ph3_L4_Tree_Revision_Calcs.xlsx` | All constants/calculations: frontage, trees, irrigation, cost (tree-only $5,432,000; $5,392,000 with nonfunctional turf removed before conversion/amenity), schedule. |
| `check_l4_revision.py` | Independent check: recomputes all numbers from first principles, reads the output files back, tests every `requirements.csv` row and schema rule, and prints the worst case/utilisation for each hard limit. |
| `requirements.csv` | 63-row hard-requirement register with source, clause, value, unit, applies-to, candidate IDs and calculation reference. Includes the six hard General Comments (F-1..F-4, G-5, G-8) and the all-30-comments requirement. |
| `rejected.csv` | Candidate-level review record for non-governing/other-discipline/duplicate statements (1184/1184 strong candidates reviewed with `ahpele_reqscan.py --check`). |

## Run the checks

From this output folder:

```bash
python3 check_l4_revision.py
python3 /tmp/ahpele/bin/ahpele_check.py .
python3 /tmp/ahpele/bin/ahpele_reqscan.py --check
python3 /tmp/ahpele/bin/ahpele_reqscan.py --register requirements.csv
```

Current results:
- `check_l4_revision.py`: **328 passes, 0 failures, 0 warnings**. It reports L-2 functional turf, L-1 seal, L-6 quantity match, F-1, F-2, F-3, F-4, G-5, G-8, the L-4 sealed plan, the L-2 configuration exhibit, the CCWRD confirmation, the 11/30-12/18 review window and the 12/23 statutory date as OPEN/FAIL, and the memo correctly does not commit to them.
- `ahpele_check.py .`: no format problems.
- `ahpele_reqscan.py --check`: 1184/1184 strong candidates reviewed.
- `ahpele_reqscan.py --register requirements.csv`: 63 rows, 0 not found.

## Independent-review findings — disposition

Fixed in place:
1. **Incomplete blocker/action list.** The memo now separates the three date blockers from six hard General Comments (F-1..F-4, G-5, G-8) and the Condition 14 determination; the action table has 16 rows with owners/dates; row 15 requires all 30 comments, including the 17 In progress.
2. **Bond action.** The memo and action table qualify $5,432,000 as tree-only, before the L-2 adjustment; the final estimate must remove item 7.16 ($39,560) if the turf is nonfunctional and add the selected conversion/amenity cost. With item 7.16 removed the tree-revision total is $5,392,000 (not $5,392,440; the reviewer did not apply the Sec. 12.02 ceiling).
3. **L-4 plan vs count.** The PDF is labelled a review exhibit (not the sealed sheets); the matrix says PARTIAL/NOT CLOSED; the memo says the count is deliverable but the sealed scaled plan is not, and adds it to Ocotillo's Rev 2 scope.
4. **L-2 configuration.** Added a Turf Hydrozone Configuration tab, amended RQ-06, and added the dimensioned configuration exhibit to the memo action table and the revision log.
5. **Revision control.** Added delta 1 markers and a revision-block row to each revised exhibit page, deleted the false "clouds mark every changed table" claim, and stated that the issued CAD sheets carry the clouds/triangles.
6. **"58 shown" basis.** Relabelled the baseline as the L-1 schedule/L-2 summary quantity and disclosed that L-6 says the graphic count does not agree.
7. **Status wording.** The memo now says "Two of the 13" for the non-landscape Open/Pending items (F-1 and G-8) and records G-5 separately as "in progress" — G-5 is In progress on the tracker and is not one of the 13 Open/Pending items, so the reviewer's "Three of those" would have repeated the count error in the other direction.
8. **L-1 Note 7.** Narrowed to arterial/collector frontage within the HOA streetscape common area, with the local-street owner-planted basis disclosed and the risk of a wider County measurement flagged.
9. **Business days.** "Six business days after 12/18" throughout.
10. **Shade area.** Exact 58,473 sf / 65.2% (50 x 176.715 + 158 x 314.159 = 58,472.9). The reviewer's 58,479 used rounded diameters.
11. **Extension wording.** "Declined to act ... jurisdictional disposition, not a rejection on the merits."
12. **Confirmation letter.** A letterhead confirmation of the deadline is not an extension; informal communications cannot modify the statutory clock.
13. **11/30 ambiguity.** A 11/30 resubmittal can be transmitted on 11/30 but cannot produce 12/18 recordation or a 12/23 presentation.
14. **Estimate blend.** Item 7.16's estimate description must be conformed to the schedule's tall fescue description or documented under Sec. 12.04.
15. **CCWRD turnaround.** Do not assume 11/18; obtain CCWRD's written turnaround.
16. **CC&R cost allocation.** Qualified: CC&R 4.2 has the Declarant install Parcel A; Section 5.4 puts maintenance/replacement on the Association; post-recordation conversion/amenity cost allocation is to be confirmed with counsel.

Rejected or modified findings are recorded at the end of `/tmp/ahpele/independent_review.md` with reasons.
