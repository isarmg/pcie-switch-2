# Three ground-only closures, 2026-10-19

Exact source PCB SHA256: 6aea6e07ec86c0348b5d17a504394f3979a35f4719db8e6ce12315f795c1227f (published e09a0de).
Candidate3 PCB SHA256: e80ee3c6ad1aaa93b5d93feca7fedda861da20c9d7c06eab80b9a04536464d56.
Formal project SHA256: 9086611e035a0210cfc1bdfb30769d78d36880dd96954c8f5b869291103f8f30.

Three new 0.15 mm B.Cu segments only; zero new vias, no moved footprints, no value/net changes, no old copper replaced or deleted.
- C5101.2 (2.015,20.035) to existing main-ground via (2.015,21.135): 1.100 mm. C5101 is populated 100 nF on TBT_VCC3P3_LC.
- C701.2 (38.315,32.985) to existing main-ground via (38.315,34.085): 1.100 mm. C701 is populated 100 nF on CPU_VCCPRIM_1P8.
- C702.2 (2.015,32.134999) to existing main-ground via (2.015,31.035): 1.099999 mm. C702 is populated 1 uF on CPU_VCCPRIM_1P8.
All three ground pads were singleton islands. They now join the original main ground pad group (1885 to 1888 pads), and GND components decrease 141 to 138. Each connection ends directly at its own existing plane-access via, with no newly added long shared ground chain.

Important limits: all three power-side pads remain singleton islands. This package restores GND connectivity only; it does not establish functioning decoupling, source power delivery or acceptable placement relative to the IC. CPU_VCCPRIM_1P8 remains 27 components and TBT_VCC3P3_LC remains 7. Existing anchors are In28–B blind vias with 0.2/0.1 mm diameter/drill; their fabrication feasibility remains unverified. No new via process is introduced.

## Evidence
- DRC3.json: native KiCad10 DRC with all-track-errors and schematic parity; zero geometry errors, one old In23 sliver warning, parity zero. Remaining unconnected DRC items: 499.
- BASE_AUDIT.json / AUDIT3.json / REGRESSION3.json: all 6626 original numbered physical pad shapes including NC retained, no old pad identity/net change, no old connected group split, no surviving copper UUID/net change.
- VERIFICATION3.json: all old native pad/copper groups preserved, main ground membership for each target before/after.
- ALL_PLANE3.json: filled-region delta of all actual power/GND plane groups; zero affected adjacent track projections; no skipped arcs; input hashes unchanged. PAD_INPUT3.json and PAD3.json: zero lost-reference hits on functional pad shapes before and after.
- DELTA3.json: exactly three additions, no replacements/deletions; all old footprint/copper blocks unchanged, unchanged zone settings/boundaries; all prefill intended copper/footprint tokens equal postfill.
- ANCHOR_DETAILS.json: exact pre-existing via UUIDs, layer pairs and dimensions.

Use self-contained replay3.py with KiCad10 Python, EXACT_SOURCE_PROJECT_DIR and NEW_PROJECT_DIR. It copies the full formal project before LoadBoard/refill, checks source PCB/pro hashes, appends only the guarded delta, and verifies all native block token hashes. REPLAY3.log records replay result. Full-project Base, Candidate3 and Replayed3 stay scratch-only. Main and Git were not modified. Any combination onto a different source must receive the full gates again. Incremental DRC/connectivity/reference checks do not qualify SI, PDN, component selection or manufacturing.

## Publisher independent verification
Exact source commit: e09a0decbf9e6236fdd02419a304f32e368bda98. Independent guarded replay produced the same full PCB SHA. Native DRC, all numbered pad/NC/cluster/copper-net regression, actual main-ground membership, exact old native objects, all-plane and input/output functional-pad checks were independently repeated. Published reports without suffix 3 are the publisher runs; VERIFICATION3 is also independently rerun. Geometry errors 0, one existing warning, parity 0. Fresh ERC remains 43 errors / 212 warnings. All source schematic/library/project/netlist bytes unchanged.

ROUTING_STATUS now binds this board SHA: 101 non-NC disconnected nets, 98 populated disconnected nets, minimum joins 1769 (previous1772). GND physical components141 to138. C5101.1, C701.1 and C702.1 remain singleton physical pads. These ground connections do not complete either signal or power function. Historical STEP/previews remain unregenerated and unqualified.
