**Final verification passed — deliverable is complete and in place.**

**Deliverable**
- `/filesystem/ALN-108_PreApplication_Response.docx` — valid Microsoft Word 2007+ file, 42,518 bytes, 4 pages, 1,621 words, MD5 `8cc949c4f0da71c5aef742f571058891`.
- Filed copy: `/DER_Program/Correspondence/ALN-108_PreApplication_Response.docx` — byte-identical (same size and MD5).

**Determination**
- **3.0 MW is not confirmed.** Current available capacity on Feeder ALN-108 as of 07/14/2025 is **0.8 MW**:
  - 3.0 MW — HCM-2024-Q2 published value (05/15/2024)
  - less 1.2 MW — PXA-2024-0231, queued 09/18/2024
  - less 1.0 MW — PXA-2025-0044, queued 02/06/2025
- The 3 MW request exceeds current headroom by **2.2 MW**.
- Pre-publication entries PXA-2023-0894 (1.1 MW) and PXA-2024-0091 (690 kW) are not deducted; the letter quotes the HCM “adjusted for queue entries added since publication” method.
- No later map edition and no later full ALN-108 study are in the record as of 07/14/2025.

**Conditions stated**
- **3 MW:** full DIS-01 Table 5-1 Category 3 set — DER-side lockable visible-break disconnect, dedicated protection relay, DER breaker/protection relay scheme where specified, utility-owned POI recloser (also DPS-07 §4.2), anti-islanding with transfer trip where required, ANSI 32 directional element, bidirectional revenue meter, utility RTU/SCADA and live telemetry before PTO; approximately 8-month RTU/recloser lead time against the Q4 2026 target.
- **0.8 MW option:** remains export-capable and in scope; TCS-02 §5 RTU/live telemetry, Category 2 disconnect and metering, and the DIS-01 Table 5-1 Category 2 “POI recloser not required” / DPS-07 §4.2 conflict routed to a per-site **ERP-9 §3 Form ER-11** determination; plan for a POI recloser pending that determination.
- No project-specific upgrade scope or cost can be confirmed without a system impact study.

**Case tracking**
- WP44 — **Closed**, 100%, due 08/15/2025; description records the call, conditions, map maintenance, SIS-status note and follow-ups.
- WP47 — priority refresh/re-study and PXA-2024-0231 SIS-status reconciliation; due 08/18/2025.
- WP48 — formal application tracking and ERP-9 referral if filed at 0.8 MW; due 08/18/2025.
- WP49 — 07/29/2025 pre-application meeting; due 07/29/2025; calendar hold exists.

**Review disposition**
- All six independent-review findings were checked against the source documents and **accepted and fixed**; **none was rejected**. The 0.8 MW determination and arithmetic are unchanged.

**Validation**
- `ahpele_check.py`: **no problems found**.
- `check.py`: **PASS** — all 39 requirement rows and content/case checks; worst case 3.0 / 0.8 = 3.75 (375%), 2.2 MW over.
- `ahpele_reqscan.py --check`: **68/68** strong candidates reviewed, 0 unreviewed.
- `ahpele_reqscan.py --register`: **39 rows**, 0 notfound/unmatched/multi.