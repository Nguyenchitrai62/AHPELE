Final check complete. Everything required is in place and valid.

**Deliverable**
- `/app/files/output/CFDME-2025-041_E119_Validation_Memo_revA.docx`
- Word memo, 11 pages, 13 tables, 5,932 words; opens and parses cleanly; no empty cells, placeholders or broken zip members.
- `ahpele_check.py`: no problems.
- All 12 memo sections and every requested item are present, including the sendable-today Bianca paragraph and the §7 drop-in text.

**Validation checks**
- `verify.py`: 76/76 content/contract checks passed.
- Hard-limit check reproduces the finding: |E| = 12.94 min vs 11.8 min limit (utilisation 1.096), and vs u_val = 8.77 min (utilisation 1.474). The run fails, as the memo states.
- `ahpele_reqscan.py --check`: 245/245 strong project-document candidates reviewed, 0 unreviewed.
- `ahpele_reqscan.py --register requirements.csv`: 74 rows, 0 notfound / 0 unmatched / 0 multi.

**Memo conclusions**
- **No validation:** S = 131 min, D = 118 min, E = +13 min; criterion 11.8 min; u_val = ±9 min. |E| exceeds both by 1.2 min and 4 min. Largest clearing S = 129.8 min (129 min whole-minute; 127 min within u_val).
- **Assembly:** yes to the certified construction, no to a specimen replica. All Ironwood §1.2 parameters match revC and the Rev A drawing; run panel is 5.02 m², 54% of the 9.30 m² test specimen. RevD’s parapet postdates the run.
- **Section 7 stub:** S = 131 min stands as the run value; the stub draws no conclusion. “Validated” is Bianca’s wording and is unsupported.
- **Bianca’s 129 min:** rejected as D under Validation Procedure §6; if reissued and recertified, it could support a 2-hour rating, but only Red Butte and Ironwood can act.
- **Comparisons:** 45 min vs 45 min separation; 85 °C vs 91 °C hot-spot margin; common-mode +13 min delay; rework belongs in the E119 model and any shared wall-model correction must propagate to the wildfire LES; no E119 rework started.
- **Checklist:** item 6 closed; items 2, 3, 4, 5, 7, 9 and 10 remain open.
- **Wildfire claim:** not established by E119 work; the memo states the gap-closing evidence and required future S/D/E/u_val reporting form.
- **Stamp language** is included verbatim.

**Independent-review response**
- Findings 2, 3, 4 and 6–15 fixed.
- Finding 5 fixed by adding the project-specific u_val tabulation as Attachment B, issued for filing with the memo.
- Finding 1 partially accepted: the plan-size difference is now stated explicitly, but the “yes to the assembly” conclusion is retained because Ironwood §1.2’s deviation clause is tied to the tabulated geometry, which does not include plan size. The reason is recorded at the end of `/tmp/ahpele/independent_review.md`.

No project files were changed; `output/` contains only the memo.