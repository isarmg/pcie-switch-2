# TPS65982 LDO_BMC local bypass topology

Exact source PCB SHA256: 518aa6761e0a69122ed0daf2ba59297fb774352e7c3383f438162cfd757eff56 (published f032e7e).
Candidate PCB SHA256: a501903278d07b19a431bb5bfb35a8012abc06ce05154d7c82ad7a32a5abfe19.
Formal project SHA256: 9086611e035a0210cfc1bdfb30769d78d36880dd96954c8f5b869291103f8f30.

C5114 retains its existing 0402 footprint and 2.2uF 6.3V label, moving from B(78.2,43), angle0, to B(72.15,35.8), angle270. Pin1 (72.15,35.32) connects directly to U503.E1 (73.5,35.7), 1.402462 mm. Pin2 (72.15,36.28) connects directly to U503.A1 main ground (73.5,37.7), 1.959311 mm. LDO_BMC components decrease 2 to 1, and GND 134 to 133. Only two new 0.15 mm B.Cu segments; no added vias or old copper edits/deletions. Both old capacitor pads were isolated, so no old ground leaf is left dangling. The same pre-existing A1 ground access also serves the previous 1V8D bypass; shared return impedance has not been characterized. No long new daisy-chain is introduced.

TP702 and TP705 flip B to F at original XY (71.725,35.225) and (71.725,36.225), angle180. Their one-pad nets and UUIDs remain unchanged and isolated; they are not working signal probe connections. Three complete guarded footprint replacements are in DELTA3.json; exact source placement-file hash, before/after position/layer/angle metadata are in PLACEMENT_METADATA_DELTA.json. All previous CT/SS/1V8A/1V8D geometry is unchanged.

TP_F_COURTYARD.json explicitly checks each new F TP pad+court bbox against every other actual F courtyard bbox. No overlap; minimum gap to J7 is only 0.025 mm, while pad-only gap is 0.200 mm. Native DRC also checks front/back courtyards and copper. Mechanical accessibility, assembly margin and complete 3D fit remain unqualified. No pad or courtyard geometry was shrunk.

## Electrical basis and limits

Official TI TPS65982 SLVSD02E, August2021, https://www.ti.com/lit/ds/symlink/tps65982.pdf : pin table p7 identifies E1 as LDO_BMC, requiring a bypass to ground. Table11-1 p91 gives effective minimum 1uF, typical placed 2.2uF, maximum 4uF and voltage rating 4V. Section10.2.1.2.9 p83 requires DC-voltage derating to be considered. Official URL and revision above were independently checked; vendor files remain research inputs and are not included.

The existing nominal 2.2uF6.3V label does not prove effective capacitance≥1uF. Exact MLCC MPN, DC-bias/temperature/tolerance curves and dynamic stability remain unverified. This package completes a local physical bypass topology, not regulator stability or the whole PD-controller system. The reused A1 via is inherited In28–B, 0.2/0.1 mm diameter/drill; fabrication feasibility remains unresolved. No new via process is introduced.

## Validation and replay

DRC3.json: native KiCad10 all-track-errors plus schematic parity; zero geometry errors, one old In23 sliver warning, zero parity issues. REGRESSION3.json covers all 6626 old numbered physical pad shapes including NC, with zero missing/changed identity/net, old cluster split or surviving copper net change. VERIFICATION3.json also verifies all native old copper/pad connected groups and target E1/A1 membership.
ALL_PLANE3.json evaluates all actual power/GND plane-region changes against adjacent track references; PAD_INPUT3.json and PAD3.json evaluate source and candidate functional pad reference projections. All affected lists are empty. This is incremental reference preservation, not SI qualification.
DELTA3.json permits exactly the three named footprint replacements and two additions; all unlisted old footprint/copper blocks and zone settings remain unchanged. Every intended prefill copper/footprint token matches postfill. Self-contained replay3.py verifies exact source PCB/pro hashes, copies the whole project before native LoadBoard/refill, applies guarded blocks and checks resulting native block hashes; REPLAY3.log records the independently reproduced candidate. Main and Git were not modified by this worker. Any combined-source integration requires independent full gates.

## Independent publisher verification
Exact baseline commitf032e7e097cab938c0477d0954d6ce48c7603faf. Full guarded replay reproduces exact PCB, COMPONENTS/BOM/PLACEMENT and measured status. Publisher independently repeated native DRC geometry0 errors/1 oldsliver, parity0, fresh ERC43 errors/212 warnings, all original pad/NC/cluster/copper-net checks, exact allowed native object delta, all-plane and before/after functional-pad reference projections. All passed. Reports without suffix3 and VERIFICATION3 are publisher native runs.

Native courtyard enum regression covers six front testpoints and three back LDO capacitors. Added testpoints have full unchanged courtyard geometry; all six front TP pad+court bounding boxes are separately checked against every defined front courtyard. TP702/705 gap to J7 remains only0.025mm, not a mechanical clearance or probe-access qualification. Both signal pads remain unconnected.

Current disconnected nets98, populated95, minimumjoins1761, GNDcomponents133. The BMC effective-capacitance minimum is1uF, not the0.5uF A/D limit; no actual MLCC bias/tolerance proof or stability measurement exists. Shared return impedance at the inherited A1 anchor is uncharacterized. Previous A/D/CT/SS geometry is retained. STEP/previews remain historical. Full replay: scripts/revW/ldo_bmc/replay_full.py EXACT_SOURCE_REVW_DIR NEW_REVW_DIR under official KiCad10 Python.
