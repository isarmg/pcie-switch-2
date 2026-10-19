# Two small GND repairs, recovery source 2026-10-19

Accepted local candidate: `Candidate3/Main_12E1S.kicad_pcb`.
Source PCB SHA256: `d00db6176ae27151f5d08b64233ef289fe29c3ec41095fc2a38e91462fe26e44`.
Candidate PCB SHA256: `6aea6e07ec86c0348b5d17a504394f3979a35f4719db8e6ce12315f795c1227f`.
Formal project SHA256: `9086611e035a0210cfc1bdfb30769d78d36880dd96954c8f5b869291103f8f30`.

Only six new B.Cu tracks, no added vias, no component/value/net moves, no old copper edits or deletions. Both targets are non-DNP. R716.2 and C5159.2 previously were individual GND pad islands; both now join the original main GND cluster. Native GND components decrease 143 to 141.

- R716.2 (67.365,4.545) to existing U501.A22 GND via (70.5,6.84): five segments, 4.753455 mm total, 0.15 mm width except a 1.1 mm long 0.10 mm neck between AC-coupling pads. Existing anchor UUID 638ac707-7728-462d-b382-3802a1690a47.
- C5159.2 (80.1,32.52) directly to existing C5158.2 GND via (79.88,31): one 0.15 mm segment, 1.535839 mm. Existing anchor UUID 80534738-726a-4d0b-99af-cdecd91b1358.
- Both anchors are pre-existing In28–B blind vias, diameter/drill 0.2/0.1 mm. Their manufacturing feasibility remains unverified. This package does not add or qualify those structures.
- CPU_CLKREQ2_N remains two components and CPU_VCCPRIM_1P8 remains 27 components. These two ground closures do not complete either functional domain, establish PDN performance, or qualify the design for production.

## Verified gates

`DRC3.json`: KiCad 10.0.7 native DRC, zero geometry errors, one existing In23 sliver warning, zero schematic parity issues, 499 remaining unconnected DRC items.
`BASE_AUDIT.json`, `AUDIT3.json`, `REGRESSION3.json`: all 6626 old numbered physical pad shapes, including NC, retained unchanged; no old cluster split and no surviving copper net change.
`VERIFICATION3.json`: all old connected copper/pad groups preserved, all old items and UUID nets preserved, native main-GND membership evidence for both targets and anchors.
`ALL_PLANE3.json`: exact filled-region delta for all power/GND layer/net groups; zero affected adjacent non-GND track projections, no skipped arcs, source hashes stable. This is an incremental reference check, not SI certification.
`PAD_INPUT3.json`, `PAD3.json`: 3789 functional pad-layer shapes checked on each board; zero lost-reference hits.
`DELTA3.json`: zero replacements/deletions, six additions; all prefill intended copper/footprint tokens equal postfill, old footprint/copper blocks unchanged, zone settings/boundaries unchanged. Expected copper UUID/net and native-block hashes included.

## Reproduce / integrate

Use `DELTA3.json` and self-contained `replay3.py`. Run KiCad10 Python with isolated writable HOME/XDG/TMPDIR and arguments EXACT_SOURCE_PROJECT_DIR NEW_PROJECT_DIR. It checks exact source PCB/project hashes, copies the full project before loading, adds six guarded blocks, refills, and compares all 13457 native footprint/copper/zone block hashes. `REPLAY3.log` proves replay produced the exact candidate file hash above. Main and Git were not modified by this worker. Writer must revalidate any combination with a different source.

Earlier `Candidate`, `DRC.json`, and `REJECTED_DIAGONAL_DRC.json` belong to rejected trials; they must not be merged. Candidate3 and reports with suffix 3 are the final package. First R716 trial collided with C5204/C5205 pads; second with R5105 bias pad. Both were rejected and rebuilt from clean Base before this accepted local candidate.

## Publisher independent verification
Exact source commit: 78d8d1f97a1f9d3527fa161f44fcb927683e63c2. Independent guarded replay produced the same full PCB SHA. Native DRC, all numbered pad/NC/cluster/copper-net regression, actual main-ground membership, exact old native objects, all-plane and input/output functional-pad checks were independently repeated. Published reports without suffix 3 are the publisher runs; VERIFICATION3 is also independently rerun. Geometry errors 0, one existing warning, parity 0. Fresh ERC remains 43 errors / 212 warnings. All source schematic/library/project/netlist bytes unchanged.

ROUTING_STATUS now binds this board SHA: 101 non-NC disconnected nets, 98 populated disconnected nets, minimum joins 1772 (previous1774). GND physical components143 to141. R716.1 and C5159.1 remain singleton physical pads. These ground connections do not complete either signal or power function. Historical STEP/previews remain unregenerated and unqualified.
