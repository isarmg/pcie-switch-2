# CT and SS functional capacitor ground repair

Source PCB e80ee3c6ad1aaa93b5d93feca7fedda861da20c9d7c06eab80b9a04536464d56, published babbd684.
Candidate3 PCB e6740d92522d8ed735b19f9ff00cd6af5a69bb5190446667ebbe2cfcf9010c16.
Formal project 9086611e035a0210cfc1bdfb30769d78d36880dd96954c8f5b869291103f8f30.

## Electrical basis, freshly checked

Official TI TPS3808 PDF https://www.ti.com/lit/ds/symlink/tps3808.pdf downloaded 2026-10-19: SBVS050N, revised August 2026. PDF p4 SOT23 CT is pin4, GND pin2. Section 7.3.2/Figure 7-2/Equation 1, p11, specifies a ground-referenced timing capacitor, nominal minimum 100 pF. C5155 is existing 10 nF, implying typical delay10/175+0.0005=0.0576429s. Capacitor leakage, tolerance and stray capacitance affect timing. Native source proves C5155.1 already joins U510.4, U510.2 joins main GND and U510.5/.6 join the P3V3_AUX96-pad group. This repair closes its missing ground branch; it does not qualify reset timing across conditions.

Official TI TPS65982 PDF https://www.ti.com/lit/ds/symlink/tps65982.pdf: SLVSD02E, revised August 2021. Pin table p8 identifies H7 as SS and requires a capacitor to GND. Table 11-1 p91 recommends CSS 220 nF, 6.3 V. Existing C5116 is 220 nF and its pin1 already joins U503.H7. Exact capacitor MPN/rating/tolerance remain unresolved; no value substitution is made. The repair closes the physical capacitor branch but does not establish complete PD-controller power, configuration or timing compliance.

Vendor PDFs/text were research inputs, not copied into the repository; URLs and hashes are in OFFICIAL_CHECK.json. Browser index showed older TPS3808 RevM; this proof uses the actually downloaded RevN, with its actual section numbering.

## Physical delta

Four new 0.15 mm B.Cu tracks, zero added vias, zero component moves, zero existing copper changes/deletions.
- C5155.2 (71.08,32.6) directly to existing GND anchor (71.1,30.7375):1.862607mm.
- C5116.2 (80.1,36.52) via (80.75,36.1),(80.75,34.9) to existing GND anchor (80.1,34.52):2.726814mm.
Each target previously had an isolated ground pad. Native comparison records both joining the original main GND group. GND components 138→136. No new shared long ground chain. Existing anchor process limitations remain; see ANCHOR_DETAILS.json for dimensions/layers. No SI/PDN/fabrication approval is implied.

The initial straight SS trace crossed C5160.1/AUX via; rejected in REJECTED_STRAIGHT_DRC.json. Final candidate was rebuilt from clean Base with the short side detour. No rejected copper is retained.

## Gates and replay

DRC3.json: native KiCad10 with all-track-errors and schematic parity, zero geometry errors, one old In23 sliver, parity zero;499 remaining unconnected items. REGRESSION3.json checks all 6626 old numbered pad shapes including NC, no missing/changed pad identity, no old cluster split and no surviving copper net changes. VERIFICATION3.json additionally checks all native old copper/pad groups and UUID nets, with target/IC pin memberships.
ALL_PLANE3.json evaluates all actual power/GND plane-region deltas: zero affected adjacent track projections. PAD_INPUT3.json/PAD3.json have zero lost-reference hits on functional pad projections. DELTA3.json preserves all old footprint/copper blocks and zone settings, and verifies every intended prefill copper/footprint against postfill.
Self-contained replay3.py checks exact source PCB/pro hashes, copies a full formal project before native loading/refilling, adds the four guarded blocks, and verifies all native block hashes. REPLAY3.log records the replay output. Main/Git remain untouched by this worker; writer must independently check any combined source.

## Requested powered-decoupler scan

BASE_CAP_SCAN.json covers all 72 populated capacitors whose ground pads were outside the main GND group, on both board faces.68 have only their own single power-side pad in native connectivity. The other 4 are C5153/C5154 crystal loads, C5155 CT and C5116 SS. Thus there was no eligible already-source-connected decoupling capacitor to repair in this scope. Crystal loads and their uncertain selection were not modified. The 68 isolated power-side pads remain a substantive system power/layout gap, not working bypass circuits.

## Publisher independent verification
Exact source commit: babbd6841ddaa5b6c09007557ed64cf84d8d81e4. Independent guarded replay produced the same full PCB SHA. Native DRC, all numbered pad/NC/cluster/copper-net regression, actual main-ground membership, exact old native objects, all-plane and input/output functional-pad checks were independently repeated. Published reports without suffix 3 are the publisher runs; VERIFICATION3 is also independently rerun. Geometry errors 0, one existing warning, parity 0. Fresh ERC remains 43 errors / 212 warnings. All source schematic/library/project/netlist bytes unchanged.

ROUTING_STATUS now binds this board SHA: 101 non-NC disconnected nets, 98 populated disconnected nets, minimum joins 1767 (previous1769). GND physical components138 to136. C5155.1 remains connected to U510.4 CT and C5116.1 to U503.H7 SS. These ground connections do not qualify reset sequencing or complete the PD system. Historical STEP/previews remain unregenerated and unqualified.
