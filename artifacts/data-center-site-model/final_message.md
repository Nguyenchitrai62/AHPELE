Final validation passed.

Deliverable:
- `/app/files/frontier__DCBim__p6_002/submission/model.ifc` — 10,576 bytes, valid IFC4 STEP file.

Verification:
- `ahpele_check.py`: no problems.
- `ahpele_ifc.py`: 168 entities, 0 errors, 0 warnings; 1 project, 1 site, 7 buildings, 9 storeys, metre units.
- IFC re-extracted from disk and checked: all engineering constraints pass.
- Final design: road 402.0 m, MV 343.21 m, objective 463.81 ≤ 473; Phase 1 weighted 205.81 ≤ 314; noise R1 38.01 dB(A), R2 41.04 dB(A) ≤ 42.35; H-1 separation 29 m ≥ 28 m; retention 1,900 m².
- `ahpele_reqscan.py --check`: 23/23 strong requirement candidates reviewed, 0 unreviewed.