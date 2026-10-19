# SLOT1 power bridge recovery, 2026-10-19

Independently reviewed change from published SLOT11 board105148eff6d2d17b32d6b61c081103438f84cfed36f086c4c6a7f540ce61854e. Final candidate85925cdde82c42707f076a2f72fd9e6779cc3108ed5079a6396b24edfbc7b9bb. Integrated as a separate commit; no capacitor, resistor, IC, connector, outline, net assignment, value or project rule change.

## Exact local improvement
Only P12_SLOT01 changes. Remove79 In26 segments:67 at0.1mm width, cumulative161.466147mm;12 at0.3mm, cumulative49.963746mm. These are sums of removed copper including branches, not one series source-to-load path. No old vias are deleted.

Add two ordinary F–B vias,0.6mm diameter/0.3mm drill at(84.3,25.3) and(91.4,17.4), and three0.6mm B.Cu segments:
(84.3,25.3) → (84.5,17.5) → (84.8,17.3) → (91.4,17.4).
Total new series bridge length14.763876mm. It links actual source/load plane islands; existing source and connector pad escapes remain additional paths and possible bottlenecks.

## Physical dependence and capacitor preservation
Baseline U11.6/C103.1 and J1.B1–B6 form one actual pad group. Removing only original0.1mm In26 tracks splits source+cap from all six connector power pads. Candidate reconnects the groups after all79 old tracks are removed. Removing only final new bridge objects splits them again. BRIDGE_DEPENDENCY.json records fresh hash-bound diagnostics.

C103 remains at its original location with its original pads, local copper and ground return. C103.2 and U11.8 remain in exactly the original GND group (1,875 distinct reference/pin labels, 1,881 physical pad shapes). No reference capacitor has been moved or substituted. The input/control/startup architecture is not inferred or completed by this same-net geometry change.

## Verification
Exact guarded removals/additions are in DELTA.json, including every expected copper UUID/net. All old footprints and retained copper are unchanged; zone rules/boundaries are unchanged; all prefill/postfill expected copper/footprint objects match. All original pad identities including NC, all old connected groups, and surviving copper UUID/net assignments pass native regression.

Native all-track geometry DRC:0 errors, original In23 sliver warning1. Schematic parity0. ERC remains the existing43 errors/212 warnings and unconnected-items report is capped at499; no flag or waiver was added.

Whole power+GND plane comparison retains every raw projection hit. Existing differential raw overlap totals5.2631e-7mm2; largest individual old hit about1.54e-7mm2. Every old track hit disappears at1um sensitivity. These are native refill numerical boundary slivers, not a suppressed design-rule failure. Functional-pad projection hits are empty. New power bridge endpoint launch voids against In30 AUX are approximately0.35751mm2 at each endpoint and explicitly recorded separately. None of these tests establishes impedance, loop inductance, SI or PDN qualification.

## Current and thermal boundary
Bridge trace-only R=rho*L/(w*t). With room-temperature copper rho=1.724e-8 ohm*m, the14.763876mm by0.6mm bridge would be approximately12.12mOhm IF copper thickness35um, or6.06mOhm IF70um. At hypothetical25W/12V=2.083A,35um trace-only drop would be25.3mV and heat52.6mW. Actual copper thickness, temperature, load, pad/plane spreading, eFuse, connector contacts and existing escapes are not specified by this calculation. It is not a25W rating.

Each via additionally depends on board thickness and plating; approximate barrel resistance rho*h/[pi*(d+t_plating)*t_plating], d=0.3mm. Neither drill DRC nor chosen via diameter proves current capacity or thermal compliance.

## Reproduce
With KiCad10 Python: scripts/revW/slot1_power_bridge/replay.py EXACT_SOURCE_PROJECT_DIR NEW_PROJECT_DIR. It checks source PCB/pro SHA, copies the complete formal project before native load, applies exact old-block removals/new UUID additions, builds connectivity, refills and asserts final candidate hash. The replay has been executed, producing the exact final hash. No metadata or schematic change is required because all original footprints and circuit definitions remain identical.

## Other evaluated slots excluded
SLOT4 two bounded F-bridge trials caused real SLOT09 plane loss under old S07_TX0_P and TBT_PA_AUX_P and are rejected. SLOT2 bounded surface/inner-corridor searches did not produce a permissible0.6mm route. These bounded excluded evaluations do not establish global impossibility. Neither is present in this candidate. SLOT6/10 were not reopened.

## Independent publisher checks

The publisher rechecked all supplied manifest hashes, executed guarded reconstruction and KiCad refill from the published formal project to the exact final PCB hash, and confirmed 79 removals/5 additions with every retained non-zone object unchanged. Fresh official KiCad all-track DRC, full native pad/copper/cluster inventory, all power-and-GND reference projections and functional-pad projections reproduced the delivered results. All old physical pad groups remain contained. The C103.2/U11.8 GND group retains the exact same physical pads and both input-connector returns. These checks do not qualify current, temperature or full system behavior.
