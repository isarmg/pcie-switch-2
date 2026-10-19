# SLOT11 bounded power bridge recovery, 2026-10-19

Independently reviewed change starting from the published f31316e79ea4290db7e75fc3f79ba0a1861925ea6e8a98a7d457b0c1a1160a60 board. Integrated as a separate commit after the local loopback repair. Final candidate hash is bound in DELTA.json/MANIFEST.json.

## Scope
Only P12_SLOT11 is changed. No component, capacitor, connector, board outline, net, rule or zone boundary changes. U21.6 is the eFuse output, C133.1 the existing output capacitor, and J11.B1–B6 the SSD power pads. Input/control/ground/capacitor placements are preserved. This does not complete the eFuse input/ground/system sequencing architecture.

The candidate removes58 old In13 segments:53 at0.1mm wide (cumulative131.4212mm),5 at0.3mm (cumulative19.1078mm). These totals describe all deleted copper, including branches; they are NOT a single series current-path length or a computed source-to-load resistance.

New copper: one8.15mm long,0.6mm wide B.Cu bridge from(12.45,6) to(20.6,6), plus two ordinary F–B through vias,0.6mm copper diameter and0.3mm drill. The original source/load pad escape vias remain. The new bridge spans the existing SLOT11 plane islands; it does not directly replace every source/package/connector bottleneck.

## Actual dependence tests
Fresh native pad-cluster reports cover source U21.6, local output cap C133.1 and all six J11 power pads. Removing only the original0.1mm In13 segments splits source+cap from all six load pads, demonstrating real narrow-route dependence. Removing all58 intended old segments has the same split. The candidate connects them without those segments. Removing only the newly introduced bridge copper from the candidate splits them again. Thus the bridge carries the restored source-to-load connection; no fake pad or isolated copper is used to preserve connectivity.

## Via-size choice and rejected trial
A0.45/0.25mm via trial passed geometric checks but was not selected as a justified current-capacity optimization. At the same original left point(12.6,6),0.6/0.3mm vias caused three real clearance violations and reference loss beneath S12_TX0_N/S12_RX0_N/S02_TX3_P. That rejected attempt is documented in the LARGE_REJECTED reports; rejected board files are not published. The final bounded adjustment moves only the left new via and bridge endpoint0.15mm left. No old signal is moved.

## Electrical limits
Trace-only resistance is rho*L/(w*t). For this8.15mm by0.6mm bridge, using room-temperature copper rho=1.724e-8 ohm*m gives6.69mOhm IF copper thickness is35um, or3.35mOhm IF70um. At a hypothetical25W/12V=2.083A, the35um trace alone would drop about13.9mV and dissipate29.0mW. These are illustrative assumptions, not evidence of actual copper thickness, load, allowable temperature or25W capability. They exclude all plane spreading, eFuse, connector contacts, pad escapes and vias.

Via barrel resistance depends on actual board thickness and plating: approximately rho*h/[pi*(d+t_plating)*t_plating], with drill d=0.3mm. Those fabrication inputs and thermal conditions are not defined here. Passing current design rules does not establish via current rating or safe load. The actual remaining pad/via/plane bottlenecks and thermal/current budget need engineering validation.

## Gate interpretation
DELTA.json binds exact old removals/new blocks and all expected surviving/new copper net names. Every original footprint and retained copper block is unchanged; prefill/postfill copper identities, geometry and nets match. Native all-pad including NC/old-cluster comparison must pass. Full all-zone power-and-ground reference changes and functional-pad projections are recorded, including new bridge's own via-launch voids. New bridge self-launch loss is not an old-signal regression or proof of a controlled-return power interconnect.

Native geometry/parity checks and replay proof are delivered separately. Existing schematic ERC/board incompleteness remains; this is a local power-path geometry improvement, not fabrication or power-on approval.

## Final results
Final PCB SHA256 105148eff6d2d17b32d6b61c081103438f84cfed36f086c4c6a7f540ce61854e. Exact guarded replay was executed and reproduced this hash. Native parity0, geometry errors0, original sliver warning1; ERC remains43 errors/212 warnings. All original pad/NC/connected-cluster checks pass. New copper is explicitly constrained to P12_SLOT11 and matches prefill intent. C133.2 and U21.8 remain in precisely the original1875-pad GND cluster including both12V input returns. No capacitor or its grounding has moved.

All-plane existing differential added loss is zero. One old non-differential P12_SLOT04 track shows5.66e-9mm2 numerical boundary change; C5205.2 far from the ECO shows4.48e-9mm2. Both disappear at1um erosion, and raw geometries remain in the reports. The new B bridge itself has0.715mm2 endpoint via-launch reference voids, explicitly retained. The supported reproduction entry point is scripts/revW/slot11_power_bridge/replay.py with the exact preceding formal project and a new output directory.

## Independent publisher checks

The publisher rechecked all supplied manifest hashes, executed the guarded reconstruction and KiCad refill from the published formal project to the exact final PCB hash, and independently confirmed 58 removals/3 additions with every retained non-zone object unchanged. Fresh official KiCad all-track DRC, full native pad/copper/cluster inventory, all power-and-GND reference projections and functional-pad projections reproduced the delivered results. Source-and-load dependence remains a bounded local test, not current or thermal qualification.
