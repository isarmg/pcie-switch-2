# TPS65982 LDO_1V8D local bypass topology

Source PCB SHA256: 444ec27be380166832ead348ed5d326d45554e9030f70c22d216fae331fae792 (published 6894cc9).
Candidate3 PCB SHA256: 518aa6761e0a69122ed0daf2ba59297fb774352e7c3383f438162cfd757eff56.
Formal project SHA256: 9086611e035a0210cfc1bdfb30769d78d36880dd96954c8f5b869291103f8f30.

## Local change

C5112 retains its 0402 geometry and 2.2uF 6.3V label, moves B(73.8,43), angle0, to B(72.15,37.85), angle90. Pin1 (72.15,38.33) connects via (74,38.33) to U503.A2 (74,37.7), total 2.480000 mm. Pin2 (72.15,37.37) connects directly to U503.A1 GND (73.5,37.7), 1.389748 mm. All three new segments are 0.15 mm B.Cu; no new vias. LDO_1V8D components decrease 2 to 1 and GND 135 to 134. The old two capacitor pads were independent islands and no old leaf needs deletion.

TP709 and TP707 flip B to F at original XY (71.725,37.225) and (71.725,38.225), respectively, angle180. Each retains its assigned net/UUID and remains an isolated single-pad testpoint; no signal testability is claimed. No existing CT/SS/1V8A or other copper is changed. Full three-footprint before/after blocks are in DELTA3.json; exact position/layer metadata guards and updates are in PLACEMENT_METADATA_DELTA.json.

Additional explicit front-side check: TP_F_COURTYARD.json compares each moved TP's combined pad/courtyard bounding box with every other actual F courtyard bbox. No overlap; minimum bbox gap to J7 is only 0.025 mm (pad-only gap 0.200 mm). Native DRC also passes front/back courtyard, copper and edge rules. These small 2D margins do not establish probe accessibility, assembly tolerances or complete 3D fit. The earlier y38.0 capacitor trial overlapped TP708's courtyard and was rejected; final capacitor moves 0.15 mm upward without moving TP708.

## Official basis and unresolved component qualification

TI TPS65982 SLVSD02E, August2021, https://www.ti.com/lit/ds/symlink/tps65982.pdf : pin table p6 identifies A2 as digital-core 1.8V LDO output with bypass to GND. Table11-1 p91 lists effective minimum 500nF, typical placed 2.2uF, maximum 12uF, minimum voltage rating 4V. Section10.2.1.2.9 p83 requires DC-voltage derating consideration. Original PDF/text/hash retained under sources/.

The existing 2.2uF6.3V nominal label is not a verified MLCC MPN. DC bias, tolerance, temperature, effective minimum capacitance and transient stability are unresolved. This package closes a local bypass topology and does not qualify LDO stability or the complete PD subsystem. The existing A1 ground via is In28–B 0.2/0.1 mm diameter/drill; its fabrication feasibility remains unverified, with no new via structure added.

## Gates and reproduction

DRC3.json: KiCad10 native all-track-errors and schematic parity, zero geometry errors, one old In23 sliver, zero parity issues. REGRESSION3.json covers all 6626 original numbered physical pad shapes including NC: no missing pads, changed identity/net, split old cluster or surviving copper net changes. VERIFICATION3.json additionally preserves every old native copper/pad connected group and records C5112/A2/A1 memberships.
ALL_PLANE3.json covers all actual filled power/GND plane-region changes and adjacent track reference projections. PAD_INPUT3.json and PAD3.json cover functional pads in source and candidate. All affected track/pad lists are empty. No SI approval is implied.
DELTA3.json has exactly three guarded footprint replacements and three added tracks, with all unlisted old footprints/copper and zone settings unchanged. All intended prefill copper and footprint tokens match postfill, including new-copper net ownership. Self-contained replay3.py verifies exact source PCB/pro hashes, copies the complete formal project before LoadBoard/refill, applies exact blocks and verifies resulting native hashes; REPLAY3.log records the output. Main/Git were not modified by this worker. Any combined source needs full independent verification.

## Independent publisher verification
Exact baseline commit6894cc92850028415d5bee9d40c625db1e93a849. Full replay reproduces identical PCB and guarded COMPONENTS/BOM/PLACEMENT/status fields. Independent DRC geometry0 errors/1 oldsliver, parity0, fresh ERC43 errors/212 warnings. All old numberedpad/NC/cluster/copper-net, permitted native object, all-plane and old/new functional-pad checks passed. Published unsuffixed reports are independent runs; VERIFICATION3 was also rerun.

Native enum check confirms TP706/710/709/707 each have four front courtyard graphics. The prior A-loop report incorrectly counted zero by comparing the displayed F.Courtyard name to F.CrtYd. This batch corrects that previous report and manifest, without changing its PCB. Native DRC and extra geometry checks used numeric layer IDs, so their collision results remain valid. The committed test_courtyard_layers.py verifies enum membership and display-name roundtrip on four front testpoints and two back capacitors; COURTYARD_REGRESSION.json records the passing native run. The committed check_tp_court.py reproduces the additional collision check using BOARD and OUTPUT_JSON arguments.

Independent pad-plus-courtyard bbox checks cover all four front testpoints and every defined front courtyard. TP709/707 have only0.025mm bbox separation from J7 and0.2mm pad separation; this is not probe, assembly, fixture or installed SSD/enclosure mechanical qualification. Both newly flipped testpoints remain electrically isolated.

Current disconnected nets99, populated96, minimumjoins1763, GNDcomponents134. Existing A/CT/SS retained. LDO1V8D short bypass topology is connected; actual MLCC effective capacitance/ESR/transient and PD system stability remain unqualified. STEP/previews remain historical. Full replay uses scripts/revW/ldo_1v8d/replay_full.py EXACT_SOURCE_REVW_DIR NEW_REVW_DIR under official KiCad10 Python.
