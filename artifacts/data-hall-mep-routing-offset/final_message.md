Final path/format check complete — all required deliverables exist at the exact locations and validate.

## Delivered files

| Path | Format / validation |
|---|---|
| `output/solution.py` | Python, parses/compiles; self-contained IFC4 builder; writes to `sys.argv[1]`, default `output/model.ifc`; ~10 s, deterministic, no PNG/network reads |
| `output/model.ifc` | IFC4, millimetre units; `ahpele_ifc.py`: **0 errors, 0 warnings**; `ahpele_clash.py`: **0 validation issues, 0 clashes, 0 broken network groups** |
| `output/reconciliation.json` | Valid JSON, 29 drawing-note entries plus diagnostics |
| `output/DESIGN_NOTES.md` | Complete design/reconciliation record and direct answers to the brief |
| `/tmp/ahpele/requirements.csv` | 89 requirements; `reqscan --check`: **0 unreviewed candidates** |
| `/tmp/ahpele/independent_review.md` | Review findings with item-by-item dispositions appended |

## Final engineering results

- **94 racks, 16 CRAHs, 4 PDUs, 8 columns, 104 sprinkler heads, 98 supports**
- Tray, busway and CHW each form **one connected service network**
- **0 hard clashes** at >2 mm
- **100% row coverage** for all four rows/all three services; worst across-row **2350 mm**
- CHW to every CRAH: worst **0 mm**
- Tray–busway clear separation: **344.5 mm** (≥300)
- Ceiling-head clearance: **3099.6 mm**; in-aisle-head clearance: **1875 mm**
- No CHW in the PDU dedicated space
- Tray supports **1000 mm** max; busway supports **1400 mm** max
- CHW total **172.35 m**; all services in the access-floor plenum per A-301/A-602
- Row last cabinets corrected to **AJ05 / AJ10 / AH14 / AK19**; in-aisle heads on one line at y=7135; containment roof 1530 mm wide with end doors
- Final independent check: **42 PASS, 0 FAIL**
- Repeated same-path runs are **byte-identical**