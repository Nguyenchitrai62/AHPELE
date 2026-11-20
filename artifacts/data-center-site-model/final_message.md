All requested deliverables exist at the exact paths and are complete and valid.

**Primary deliverable**
- `/app/files/frontier__DCBim__p6_002/submission/model.ifc` — 11,453 bytes, ISO-10303-21 / IFC4 STEP.
- Contains 1 `IfcProject`, 1 `IfcSite`, 7 `IfcBuilding`, 9 `IfcBuildingStorey`, SI METRE; 182 entities total.
- Buildings: `DH_P1` and `DH_P2` 4,502 m² / 9 m / 2 storeys / GFA 9,004 m² each; `SUB` 1,005.12 m² / 6 m; `GEN` 501 m² / 3 m; `CTP` 802 m² / 4 m; `BRM` 320 m² / 8 m; `RET` 1,850 m² / 0 m below grade.
- `DCD_Layout` identity psets on all buildings and `DCD_Networks` JSON on the site, with road, three MV networks, all building nodes, `GATE`, `POC`, utility/power feeds and both data-hall access edges.

**Final design metrics**
- Footprint excl. basins/berms: 11,312.12 m² vs 13,529.6 m² cap; including BRM/RET: 13,482.12 m².
- Minimum non-exempt setback: 19.500 m; wetland minimum structure clearance 9.4465 m; road edge 10.0 m from WET2.
- Access: all buildings ≤17.5 m of road; occupied/hazardous ≤16.0 m.
- H-1 minimum: 32.17 m vs 28 m.
- Noise: R1 38.708 dBA, R2 40.339 dBA; Phase 1 38.370 / 40.328 dBA; limit 42.35 dBA.
- Visual screening: 0 unblocked generator-yard samples at both receptors, including a full-footprint grid.
- Retention: 1,850 m² vs 1,511.83 m² (core), 1,767.89 m² (all buildings), 980.6 m² (Phase 1).
- MV total 372.977 m; road 250 m; objective **447.977 < 473**; Phase 1 **275.278 < 314**.

**Validation just re-run**
- `ahpele_check.py`: no problems.
- `ahpele_ifc.py`: **0 errors / 0 warnings**.
- `check_model.py`: **ALL CHECKS PASS**.
- `ahpele_reqscan.py --check`: **23/23** strong candidates reviewed, none unreviewed.
- `ahpele_reqscan.py --register`: **44 rows, 0 notfound, 0 unmatched, 0 multi**.
- Custom final parse/validation confirmed STEP header/terminator, IFC4 schema, entity counts, metre units, both psets, and valid `DCD_Networks` JSON.

Working files are in `/tmp/ahpele/`: `requirements.csv` (44 requirements), `checklist.md`, `asks.md`, `verification.md`, `check_model.py`, `build_model.py`, `final_check.log`, and `independent_review.md` with the author’s response. The independent review’s only rejected recommendation was its shorter MV alternative, because it would drop total MV below the conservative sum-of-straight-line-legs reading of §6.2; the dead-end spur itself was removed.