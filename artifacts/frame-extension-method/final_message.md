Everything is in place and validated.

## Deliverable location

**`/filesystem/field_eng__constructability_4d__blind/output/submission.zip`** — a valid zip containing exactly the six required files at its root (no `output/` prefix). The same six files are loose in `output/`, and the zip is byte-identical to them.

| File | Size / rows |
|---|---|
| `construction_sequence.csv` | 294 activities × 11 required columns |
| `stability_check.csv` | 42 zone-lifts × 7 columns, all `temporary_bracing`, all `pass` |
| `occupancy_report.csv` | 42 zone-lifts × 9 columns |
| `temporary_works.json` | 42 zone-lifts × {shoring, reshore, scaffold, bracing, crane} |
| `constraint_register.csv` | 224 requirements × 6 columns |
| `method_note.md` | 2,793 words |

## Final content

- **Programme:** all 294 issued activities under their issued IDs, issued durations and crane hours; every finish = start + duration; makespan **211 days** against the 250-day deadline; 42 zone-lifts with TWP-09 7.2 level sequencing and stair-core separation.
- **Shoring:** SP-16 at 3.5 ft perimeter grids, 4,134 posts; worst post load **4,870.6/6,000 lb = 0.812**.
- **Reshoring:** RS-16 at 8 ft perimeter grids, 1,170 posts; installed at the start of STRK, removed pour + 28 days.
- **Scaffolds:** SF-3 (24 lifts) and SF-5 (18 lifts); rest platforms and two platform levels on the 28 L3/L4 lifts; 3 tie columns on the 35 ft B-zone scaffolds (17.5 ft intervals); 1-in back gap, 6.5/11.5-in front gaps, 42-in guardrails.
- **Crane:** one fixed CP-C position, Option 3, Table A 10 ft, demarcation 140 ft; worst capacity utilisation **0.931**.
- **Shared resources:** yard **3,594.1/3,600 sf** (conservative overlap model; 3,584 non-overlap), erected face **98/120 ft**, crane **9.49/10 h**, gangs **6/8**, laydown **16/16**, stair cores **1/1**.
- **Price:** temporary works 31,426 + programme 16,504 = **47,930 units**.
- **Register:** TWP-09 rev C, the five adopted CFRs, catalogues and model schedules only; no superseded or out-of-scope documents.
- **Method note:** document precedence, striking/reshoring method, per-zone governing constraints, margins, options evaluated, conditions, and the LivingBIM DOI / CC BY 4.0 attribution with licence conditions.

## Verification results

- `python3 /tmp/ahpele/bin/ahpele_check.py output/` — **no problems found** (loose files and zip members all parse; required headers present).
- `check.py` against the unzipped archive — **0 failures**.
- `audit_final.py` — **0 limits over 1.0**.
- `ahpele_reqscan.py --check` — **41/41** strong project-document candidates reviewed, 0 unreviewed.
- `ahpele_reqscan.py --register` — **notfound=0, unmatched=0, multi=0** for 224 rows.
- `zip -T` — archive integrity OK.
- Issued-activity comparison — **294/294 IDs match**, durations and crane hours exact, 0 mismatches.

The independent-review findings were addressed in place; partial dispositions (deck pricing, yard margin, discrete laydown/core caps, and the corrected IFC entity count) are recorded at the end of `/tmp/ahpele/independent_review.md`.