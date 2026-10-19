# One local TPS65982 LDO_1V8A bypass topology

Source PCB SHA256 e6740d92522d8ed735b19f9ff00cd6af5a69bb5190446667ebbe2cfcf9010c16 (published e3074b9).
Candidate3 PCB SHA256 444ec27be380166832ead348ed5d326d45554e9030f70c22d216fae331fae792.
Formal project SHA256 9086611e035a0210cfc1bdfb30769d78d36880dd96954c8f5b869291103f8f30.

## Minimal physical change

C5113 retains its original 0402 footprint, value 2.2uF 6.3V, numbered pads and nets. Move from B(76,43), angle0, to B(72.15,32.9), angle90. Its pin1 (72.15,33.38) connects directly to U503.K1 (73.5,33.2) by a 1.361947 mm, 0.15 mm B trace. Its pin2 (72.15,32.42) connects directly to U503.L1 main ground (73.5,32.7) by a 1.378731 mm, 0.15 mm B trace. Total added copper 2.740678 mm, two segments, zero new vias. Native LDO_1V8A components decrease 2 to 1 and GND 136 to 135. Old C5113 pads were individually isolated, so no old copper leaf requires deletion.

TP706 and TP710 flip from B to F at their unchanged XY: (72.125,33.225) and (72.075,32.225). Both stay isolated one-pad testpoints with the same UUIDs and assigned nets. Their signal connectivity has NOT been established; mechanical probe accessibility on the front is unqualified. No other footprint, old copper, component value, pad identity or network changes. Placement details are in PLACEMENT_DETAILS.json. Writer should synchronize these three footprint placements into metadata without overwriting unrelated fields.

## Official electrical basis and limits

TI TPS65982 datasheet SLVSD02E, August2021, https://www.ti.com/lit/ds/symlink/tps65982.pdf : pin table p9 identifies K1 as the analog-core 1.8V LDO output requiring bypass to GND. Table11-1 p91 gives LDO_1V8A effective minimum 500nF, typical placed 2.2uF, maximum 12uF and voltage rating4V. Section10.2.1.2.9 p83 requires DC-voltage derating to be considered. The publisher independently reopened the official TI PDF; vendor files are research inputs and not included in this commit.

Existing 2.2uF6.3V label matches nominal recommendations but is NOT a verified MLCC selection. There is no exact MPN, bias/temperature/tolerance evidence proving effective C≥0.5uF, ESR validation or transient test. This package establishes a physically short complete bypass topology only, not regulator stability or system PD power readiness. Existing U503.L1 ground via is inherited (details recorded), with manufacturing feasibility still unverified. Other LDOs and all unrelated circuits remain unchanged.

## Validation and replay

DRC3.json: KiCad10 full native DRC including schematic parity, zero geometry errors, one old In23 sliver, zero parity issues. All old 6626 numbered physical pad shapes including NC are retained. REGRESSION3.json and VERIFICATION3.json prove no old net/pad/copper cluster split, missing pad, changed identity or surviving copper UUID/net change.
ALL_PLANE3.json checks all actual power/GND plane-group filled-region changes against adjacent signal/power tracks. PAD_INPUT3.json and PAD3.json check all functional pad projections on source and candidate. No affected track or pad projections. These are incremental geometry checks, not SI certification.
DELTA3.json permits exactly three guarded footprint replacements and two additions, preserving all other footprint/copper blocks and all zone settings/boundaries. Every intended prefill copper/footprint token matches postfill; no new-copper reassignment is allowed. replay3.py checks exact source PCB and formal project hashes, copies the full project before native loading/filling, applies guarded replacements/additions and validates every resulting native block hash. REPLAY3.log records the independently recreated candidate. Main/Git are unchanged by this worker. Combination onto any other source needs the complete gates again.

## Independent publisher verification
Source commit e3074b9674107526b485f349dcc0b345ae925a25. Full guarded replay reproduces this exact board plus the three metadata files and measured ROUTING_STATUS. Independent native DRC0 geometry errors/1 existing sliver, parity0, fresh ERC43 errors/212 warnings. Full old numberedpad/NC/cluster/copper-net regression, exact permitted objects, old/new functional-pad and all-plane checks all passed. Published unsuffixed reports are independent publisher runs; VERIFICATION3 is also independently rerun.

Correction: TP706/TP710 each have four front courtyard graphics. The previous displayed-name counter incorrectly reported zero because KiCad10 returns F.Courtyard while the counter compared F.CrtYd. Native DRC and the geometric bbox check used layer enums and remain valid. The unchanged formal project ignores missing courtyards but treats overlapping defined courtyards, copper and board-edge violations as errors. Additional conservative checks find no intersection between either new front testpoint pad bounding box and any defined front component courtyard bounding box. This does not qualify probe approach, fixtures, installed SSD/enclosure overlays or 3D assembly access. Both testpoints remain isolated.

Current native disconnected nets100, populated disconnected nets97, minimum joins1765, GNDcomponents135. This closes only the local LDO1V8A bypass topology. Effective MLCC capacitance, ESR, transient response and full PD system remain unqualified. Historical STEP/previews were not regenerated. Full replay: scripts/revW/ldo_1v8a/replay_full.py EXACT_SOURCE_REVW_DIR NEW_REVW_DIR using official KiCad10 Python.
