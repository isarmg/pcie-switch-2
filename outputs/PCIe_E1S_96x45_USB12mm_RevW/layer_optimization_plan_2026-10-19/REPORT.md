# E1.S 96 × 45 mm: actual layer architecture audit and reconstruction proposal

Date: 2026-10-19. Read-only assessment. No source PCB, netlist, Git state, board outline, connector position, or M.2 design was changed.

Source: main 6c2364c22a1648e9eac45f1b1c66f55d32ce5f06, PCB SHA256 e33bc9bf7cb41045c3171abd07677bc36ebe7c3960d61349e4ad5ba2437ecb3c.
PCB: outputs/PCIe_E1S_96x45_USB12mm_RevW/Main_12E1S/Main_12E1S.kicad_pcb.

## Recommendation

**Start a separately identifiable 24-layer reconstruction experiment, not a production release.** Keep 20 layers as a subsequent cost-down trial; do not start by forcing 16 layers. Escalate to 28 or 32 only if measured escape, routing or PDN requirements require it. This is a reasoned starting point, not a claim that 24 is globally optimal or already routable.

Keep the 96 × 45 mm outline and current connector placeholders fixed during the comparison. Final optimization cannot be signed off until the real connectors, genuine switch ballmap, CPU VR/PDG data and manufacturer stackup/via process are available. Existing incomplete connectivity means the workload measured here is only the existing copper, not the entire finished circuit.

## 1. Reproducible current-state findings

- KiCad 10.0.7 native extraction: 9,065 track segments, 3,837 vias, 1,714 net entries and 32 layer-specific zone records. The 32 per-layer segment counts and lengths independently match the prior text/native usage audit.
- Actual routing uses 23 layers: F, In1, In8–18, In20–21, In23–29 and B. The other nine contain filled power copper. No copper layer is empty.
- Total trace length is 22,549.700 mm. Layer copper counts do not establish the required number of layers.
- The only GND-filled layers are In1, In10, In13, In16, In25 and In28; all six also carry signal traces. There is no track-free dedicated GND layer. All nine track-free plane layers are power.
- Each independently switched SSD 12 V net P12_SLOT01–P12_SLOT12 occupies its own filled layer. Shared physical power layers with isolated islands and corridors are a major optimization candidate; electrically shorting the outputs together is forbidden.

### Routed net classes

| Class | Trace length (mm) | Distinct routed net sections |
|---|---:|---:|
| PCIe | 13876.047 | 352 |
| USB_TBT | 1023.255 | 22 |
| DP | 815.415 | 20 |
| clock | 2244.312 | 36 |
| low_speed_control | 3726.138 | 157 |
| power | 801.678 | 31 |
| ground | 62.855 | 1 |

Classification is based on actual net names and recorded topology. The control bucket also includes bias, sense and local regulator-control/bootstrap auxiliaries; it is not blanket permission to treat every member as slow or noise-insensitive. Power trace length excludes filled plane area. AC coupling divides one physical channel into multiple net sections.

### Channel budget without AC-coupling double counting

- SSD: 12 slots × x4 PCIe = 48 bidirectional lanes = 96 unidirectional differential data channels.
- CPU–switch x4: 4 bidirectional lanes = 8 data channels.
- CPU–TBT x4: 4 bidirectional lanes = 8 data channels.
- Total PCIe: **56 bidirectional lanes / 112 differential data channels**, represented by 176 P/N net-section pairs in this routed source.
- Additional high-speed links: four TBT CIO differential channels and four DP main-link differential channels. There are 17 routed refclock/clock-input P/N sections. USB2 RP/TOP/BOTTOM and two AUX pairs are accounted separately; the three USB2 net sections are not assumed to be three independent external USB ports.

### Layer use, direction and occupied regions

| Layer | Length mm | Horizontal / vertical / diagonal % | Active 2 mm tiles | Trace pitch-area proxy % | Adjacent GND projection % |
|---|---:|---|---:|---:|---:|
| F.Cu | 321.1 | 51.0 / 12.4 / 36.6 | 197 | 1.8 | 81.2 |
| In1.Cu | 909.5 | 27.3 / 43.2 / 29.5 | 412 | 4.0 | 0.0 |
| In8.Cu | 949.4 | 44.0 / 26.9 / 29.0 | 414 | 4.4 | 0.0 |
| In9.Cu | 921.1 | 36.0 / 24.7 / 39.2 | 379 | 4.1 | 41.9 |
| In10.Cu | 973.3 | 32.6 / 28.8 / 38.6 | 419 | 4.2 | 0.0 |
| In11.Cu | 800.8 | 38.4 / 35.1 / 26.5 | 355 | 3.5 | 34.9 |
| In12.Cu | 961.0 | 33.7 / 36.7 / 29.6 | 388 | 4.2 | 64.8 |
| In13.Cu | 1221.5 | 31.1 / 23.4 / 45.5 | 403 | 5.3 | 0.0 |
| In14.Cu | 1019.7 | 24.3 / 19.8 / 55.9 | 380 | 4.4 | 66.9 |
| In15.Cu | 1102.0 | 22.0 / 12.2 / 65.7 | 404 | 4.7 | 34.6 |
| In16.Cu | 1109.8 | 26.4 / 16.7 / 56.9 | 421 | 4.9 | 0.0 |
| In17.Cu | 999.5 | 21.9 / 37.3 / 40.8 | 427 | 4.4 | 48.7 |
| In18.Cu | 1210.7 | 33.6 / 43.5 / 22.9 | 436 | 6.0 | 0.0 |
| In20.Cu | 1194.9 | 31.2 / 34.6 / 34.2 | 422 | 5.4 | 0.0 |
| In21.Cu | 1000.1 | 30.6 / 19.6 / 49.7 | 436 | 4.5 | 0.0 |
| In23.Cu | 1080.2 | 29.8 / 14.1 / 56.1 | 405 | 5.0 | 0.0 |
| In24.Cu | 1293.2 | 19.6 / 15.9 / 64.5 | 492 | 5.7 | 58.7 |
| In25.Cu | 967.6 | 28.1 / 22.7 / 49.2 | 403 | 4.3 | 0.0 |
| In26.Cu | 1187.3 | 24.0 / 38.8 / 37.1 | 496 | 5.1 | 63.3 |
| In27.Cu | 1225.1 | 20.7 / 19.3 / 59.9 | 449 | 5.5 | 82.2 |
| In28.Cu | 925.5 | 28.2 / 63.7 / 8.1 | 352 | 4.1 | 0.0 |
| In29.Cu | 866.0 | 29.9 / 57.1 / 13.1 | 389 | 3.7 | 57.4 |
| B.Cu | 310.4 | 36.7 / 16.6 / 46.7 | 191 | 1.8 | 0.0 |

The pitch-area proxy is Σ(length × (width + 0.10 mm)) / board area, not legal routing occupancy. It ignores pads, via holes/antipads, pair spacing and obstacles, and must not be used to declare free capacity. The active-tile metric samples trace centerlines at no more than 0.25 mm steps; it likewise is not a congestion solver.

Internal routing layers carry approximately 0.80–1.29 m each and generally span much of the board. All directions are mixed. Summed route length by x-region is 8.83 m in x=0–37 (switch side in PCB coordinates), 8.13 m in x=37–69 (CPU), and 5.59 m in x=69–96 (USB/PD). No existing whole internal routing layer is a clean spatially separate bundle that can simply be merged with another.

### Direct layer-overlay screening

All 253 pairs among the 23 occupied routing layers have at least one different-net trace copper overlap when superimposed at their current XY coordinates. At 0.10 mm gap screening, even the least conflicting pair of internal layers has 97 conflicting segment pairs. The screen excludes every pad, via and plane, so it is only a necessary-condition rejection of simple overlay, not a full DRC or routing proof. Native project minimum clearance is 0.075 mm; the overlap finding does not depend on selecting the larger 0.10 mm screening gap.

**Therefore neither direct layer-index remapping nor deleting presumed empty layers is a valid implementation method.** A smaller layer count requires changed route geometry, paired routing, plane allocation and a manufacturable via strategy.

### Reference copper screening

Saved filled polygons were projected against actual track centerlines, without refilling or editing the board. Among 17.959 m of PCIe/USB/TBT/DP/clock traces, 25.13% projects onto GND copper on at least one immediately adjacent physical copper layer; 76.30% projects onto any filled zone on an adjacent layer. This does not prove that the remaining length has no possible reference: coplanar copper, more distant planes, dielectric separation and electrical stitching are not modeled. It does show that immediate ground-reference continuity is not established by layer names.

The six GND fills occupy 60.7–87.0% of board area and contain 3–10 planar filled components each. These are geometric components, not proof of separate electrical ground nets: vias may join them. Any candidate must check the actual return path and projected antipad/slot corridors, not only DC continuity or total copper area.

### P/N layer pairing examples

Of 214 routed P/N net-section pairs, 140 have P and N each on a different single internal layer: 111 PCIe, 13 clock, 9 USB/TBT and 7 DP. The count includes AC-coupling sections and is not a physical lane count. Examples:

| Pair section | P layer | N layer | Intervening geometry |
|---|---|---|---|
| S06_SW_TX0 | In24 | In17 | In18–23 include filled PEX_0V9 on In19 and PEX_0V9A on In22, plus other filled copper |
| S08_SW_RX0 | In28 | In13 | Fifteen-layer-index separation, with several GND/power-filled layers between |
| TBT_CIO_RX1_SRC | In12 | In11 | Adjacent layers; could superficially resemble broadside routing, but no controlled broadside model is defined |

Cross-layer differential routing is not intrinsically forbidden; intentional broadside routing requires a controlled stackup, overlap/coupling model and validation. Those are absent here. The adjacent-layer example must not be called invalid solely because it is cross-layer, and the nonadjacent examples must not be silently accepted as intentional broadside pairs. The reconstruction default should be same-layer coupled P/N, matched transition topology and a defined reference plane.

## 2. Candidate comparison

| Total | Illustrative S/G/P budget | Disposition |
|---:|---|---|
| 16 | 8S / 6G / 2P (or 6S / 6G / 4P) | High-risk first attempt: power domains and/or routing reserve too constrained given unresolved CPU and switch data |
| 20 | 10S / 6G / 4P | Secondary cost-down trial; retains four power layers but only eight internal signal layers |
| 24 | 12S / 8G / 4P | Recommended reconstruction starting point: ten internal signal layers and eight dedicated ground layers |
| 28 | 14S / 10G / 4P example | Fallback for demonstrated escape/routing needs; adjust budget if the actual failure is PDN capacity |
| 32 | 16S / 10G / 6P example | Contingency only for a measured need; not justification of the current 23-mixed-signal-layer arrangement |

S includes both outer layers. The examples are resource budgets, not board-factory-approved dielectric stackups. Neither global trace-area percentage nor a lane-per-layer average proves routability.

## 3. Proposed 24-layer allocation

Symmetric kind sequence: S G S P G S S G P S G S | S G S P G S S G P S G S.

| Physical layer | Type | Proposed use |
|---:|---|---|
| 1 | S | F.Cu: connector escape, short local signal/control/power only |
| 2 | G | Dedicated GND |
| 3 | S | SSD data A: target 16 differential channels (2 x4 slots equivalent) |
| 4 | P | Power: bank A input/protected bus and six separately switched SSD output islands/corridors |
| 5 | G | Dedicated GND |
| 6 | S | SSD data B: target 16 differential channels |
| 7 | S | SSD data C: target 16 differential channels |
| 8 | G | Dedicated GND |
| 9 | P | Power: CPU/local VR and auxiliary rail regions; exact allocation unresolved |
| 10 | S | CPU-to-switch x4 and CPU-to-TBT x4: target 16 differential data channels |
| 11 | G | Dedicated GND |
| 12 | S | Clock/control A: reserve 17 refclock pairs across L12/L13 plus local control |
| 13 | S | Clock/control B: USB2/AUX and control; spacing from L12 clock channels must be modeled |
| 14 | G | Dedicated GND |
| 15 | S | TBT CIO 4 differential channels + DP main-link 4 differential channels; reserve routing margin |
| 16 | P | Power: PEX and TBT/auxiliary local rail regions; exact allocation unresolved |
| 17 | G | Dedicated GND |
| 18 | S | SSD data D: target 16 differential channels |
| 19 | S | SSD data E: target 16 differential channels |
| 20 | G | Dedicated GND |
| 21 | P | Power: bank B input/protected bus and six separately switched SSD output islands/corridors |
| 22 | S | SSD data F: target 16 differential channels |
| 23 | G | Dedicated GND |
| 24 | S | B.Cu: CPU/switch/TBT escape and short local control/power only |

The six SSD routing layers reserve 16 differential data channels per layer, equivalent to two x4 slots. Slot grouping must be selected from actual escape topology and corridor crossing, not mechanically by slot number. L10 reserves 16 CPU/PCIe interface channels; L15 reserves 8 CIO/DP channels. L12/L13 share the 17 clock pairs, AUX/USB2 and control workload, with local control also on outer layers. These are planning quotas to test, not an assertion that the tracks already fit.

Every signal layer has an adjacent dedicated GND layer in this abstract sequence. The neighboring signal pairs L6/L7, L12/L13 and L18/L19 need deliberate dielectric spacing, field-solver/crosstalk analysis and routing separation. Orthogonal routing alone is not a pass. Layer-to-layer transition return stitching must be designed with the actual via and plane geometry.

### Power partition rules

- P4 and P21 are candidate physical distribution layers for bank A and bank B plus their isolated switched-slot outputs. Existing bank A slots are 1,2,3,4,5,11; bank B slots are 6,7,8,9,10,12. They are not simply consecutive slot groups.
- Preserve VIN_A, VIN_B, VBANK_A, VBANK_B, AUX_12V_PROTECTED and all twelve P12_SLOTxx as different nets. Reusing a physical layer means non-overlapping islands/corridors with proper clearances, not shared copper across protection devices.
- Each per-slot output should become a local protected route from its eFuse to its connector, not retain a board-wide plane just because the historical source did so. Switch/connector footprints and bank path constraints determine the final partition shape.
- Keep noisy switching nodes local; do not spread bootstrap/switch-node copper onto a shared distribution plane. Low-voltage high-current CPU/PEX supplies need their own locally sized regions, via arrays and return paths.
- The recorded 12 × 25 W = 300 W / 25 A SSD total, 20 A input-feed budgets and PEX current assumptions are budgets only. The source explicitly says current and thermal capacity are unqualified. Four power layers are not proven enough for the missing CPU dynamic VR and final switch. If DC drop, thermal, impedance or decoupling targets fail, revise the budget before routing around it.

### Manufacturing boundary

Use a fabricator-reviewed 2+20+2 concept as a starting discussion, with near-surface microvia access L1–L2, L2–L3 and L22–L23, L23–L24, and only factory-approved core/through-via spans. Staggered buildup transitions are preferred where space permits; copper filling, stacking, buried spans and backdrill must be explicitly agreed. Do not inherit the old arbitrary deep-blind topology. A conventional 0.10 mm drilled blind via spanning thirty layer intervals is not made feasible by renumbering its endpoints.

The source has only general thickness=1.6 mm and no explicit stackup block. Do not preserve 1.6 mm as if approved. Copper foil, finished plating, dielectric thickness, material and total board thickness must be specified together with mechanical constraints. A thicker board is an option for evaluation, not authorized mechanical acceptance or a solved via-stub problem.

## 4. Controlled implementation and stopping conditions

1. Freeze and identify the source. Build the 24-layer experiment in a separate design copy with a manifest; retain netlist/outline/connector-position checks. Do not change M.2 in this pass.
2. Establish the legal via/stackup primitive set and a net-class constraint table before detailed rerouting. Keep the genuine-ballmap/connector/CPU-data limitations conspicuous.
3. Validate representative constrained channels first: longest SSD corridor, switch and CPU escape, CPU–switch, CPU–TBT, a CIO/DP route, clock source/fanout, and one slot power branch. Reassign and route P/N as a pair; do not translate layers independently.
4. Reserve four physical power layers with isolated electrical domains and eight continuous GND reference layers. Check real polygon continuity, via antipads and return stitching along every tested channel.
5. Measure actual local channel/cut capacity, legal via escape and low-speed capacity. Only then route all 112 PCIe data channels, 4 CIO, 4 DP main, clock/AUX/USB2 and controls. Existing 97 disconnected non-NC nets / 94 populated-net issues remain part of the work, not waived by a new layer count.
6. Require native DRC plus independent netlist/pad-cluster connectivity; verify no shorts/domain merges, no new unconnected mandatory pins, exact source/destination preservation, permitted via spans and layer masks. Then perform impedance, loss/crosstalk, timing and PDN/thermal validation with the actual stackup and models. DRC=0 alone is not signoff.
7. **Fallback to 28/32:** after geometry/placement-preserving route optimization, the 24-layer legal-via escape or local corridor capacity cannot fit the required channels with valid references; or verified power delivery needs more copper resources. Record the precise failed region/constraint. A small local routing failure is not proof that the entire 24-layer design is impossible.
8. **Try 20 only after measured success:** all required channels and legal vias fit at 24; actual pair spacing, local occupancy, reference continuity and PDN margins support removing one symmetric S/G resource pair on each half. Reroute and revalidate independently. Do not simply delete those layers. Do not escalate to an unsupported "minimum feasible" claim.

## 5. Data needed for an implementation-quality decision

- Selected real SMT connectors, authoritative land patterns/keepouts, mating datum and current ratings. Current USB placeholders cannot certify final escape or mechanical fit.
- Real switch selection, authentic package/ballmap, signal pin assignment, power domains/current and channel model. U1 is explicitly fictional and reordered for routing.
- Intel Ultra 9 288V authorized PDG, VR architecture, rail current/transient targets, decoupling, routing/escape constraints and complete mandatory signals. Existing draft land coordinates do not replace these.
- Fabricator quote/DFM review for 20/24/28 alternatives: material, foil/plating, total thickness tolerance, impedance stack, registration, buildup steps, drill aspect ratio, legal microvia/stacking and backdrill capabilities.
- Full endpoint topology/generation and loss/timing budgets, reference-clock mode/topology, connector/AC-cap/via models and intended operating environment.
- DC drop/current/thermal targets for 12 independently switched SSD branches and both banks, CPU/switch power and cooling. Distinguish electrical design budgets from rated hardware.

## Evidence files

- NATIVE_GEOMETRY.json: reproducible scratch output from dump.py, deliberately not committed; extraction does not save/refill the source board.
- LAYER_ARCHITECTURE_AUDIT.json: per-layer classes/directions/region metrics, saved-zone areas, 253 overlay checks and 214 paired-section records.
- LAYER_SUMMARY.csv: flat per-layer metrics.
- layer_plan.json: authoritative candidate budgets, exact symmetric 24/20 sequences and 24-layer role plan.
- dump.py / analyze.py: portable geometry reproduction scripts (KiCad 10 / Shapely 2). validate_layer_plan.py and test_validate_layer_plan.py check the proposal and negative controls. All counts/lengths were cross-checked against the independent prior usage audit.

**No SI, impedance, timing, thermal, current-rating or manufacturing signoff is claimed.**

## General official references

- TI SNLA426: https://www.ti.com/lit/an/snla426/snla426.pdf (reference-plane continuity, paired transitions and stub principles; not the product-specific CPU/PEX PDG).
- NCAB: https://www.ncabgroup.com/microvias/ (short-microvia and conservative stacked-via process guidance).
- TTM HDI: https://www.ttm.com/sites/default/files/documents/3K.%20HDI_Advanced%20Solutions_High%20Res_2026.pdf (2+N+2 process families, not approval of this board).

The machine-readable frozen plan is layer_plan.json; validate_layer_plan.py is the portable read-only consistency gate. See README.zh-CN.md for replay commands and explicit center S-S / 20-layer power-reference risks.
