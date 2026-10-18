# Rebuilt S12 TX2 geometric candidate, current E1.S source

Source PCB cfd3a2a3de7bbeedeb94c3c2c9f6a1422be7a8a71141d28c105f218bc0c4ac80, project9086611e035a0210cfc1bdfb30769d78d36880dd96954c8f5b869291103f8f30.
Candidate `S12Fixed.kicad_pcb`: 2b6d056266d9a8befefa6c3fa314d900611e8c6a32b50935dfce282093d17739.
Formal same-stem project was copied before write/load/refill. Current source was parsed afresh; no missing historical PCB was substituted.

## Exact modification
Nine existing S12_SW_TX2 P/N segments replaced by eight0.08mm segments on In14.Cu. Existing four0.2/0.1mm blind signal vias, all footprints and populated220nF C4093/C4094 remain unchanged. No new vias or other-net routing.
`apply_delta.py SOURCE DEST s12_delta.json` enforces each exact old block and its SHA before replacement; adds deterministic UUIDs. Use only `S12Fixed`; the earlier `S12` draft is rejected (old block format did not match and old tracks had not been removed).

## Whole real drawn chain
P: U1.A13(16.5,7) → S12_SW_TX2_P → C4093.1(16.32,20.735) → populatedC4093 → S12_SSD_RX2_P → J12.B24(14.3,20.735).
N: U1.B13(16.5,8) → S12_SW_TX2_N → C4094.1(16.32,21.335) → populatedC4094 → S12_SSD_RX2_N → J12.B23(14.3,21.335).

Upper copper lengths25.855/60.845mm →14.2172969875/14.2182339781mm.
Existing downstream F.Cu lengths1.38mm each unchanged.
Complete chain27.235/62.225mm →15.5972969875/15.5982339781mm; absolute copper skew34.99mm →0.0009369906mm.
Only this chain changed copper length among143 actual capacitor-linked P/N candidates emitted by this adapted native audit. This count covers routed names ending_P/_N; it is not an assertion that all possible board channels are implemented. Direction/real switch pinout and timing are not certified.
The straight paired trunk has nominal0.20mm center spacing; endpoint fans are not a uniform coupled transmission line. No length-matching serpentine is introduced.

## Existing barrel/tap changes
Source vias span In1–B; capacitor vias span F–In30. P oldtapIn1 has unused layer intervals source0/cap29. N oldtapIn25 has source24/cap5. Both newtapIn14 have source13/cap16. Longest unused interval decreases P29→16, N24→16. No physical hole or barrel span changed, but tap/stub distribution did change. Layer interval counts are not physical lengths, electrical delay or resonances; actual stackup/fabrication remains unverified.

## Reference coverage: explicit incomplete whole-chain status
Upper new In14 traces use actual adjacent In13 GND. All missing area is geometrically within0.35mm of same-net existing signal vias: P0.03710644377mm2 and N0.03710319672mm2. Outside that vicinity, missing area is zero. These are retained raw endpoint antipads, not electrically approved exceptions. Old P In1/N In25 had no configured immediately adjacent GND zone, so the original reference assessment is explicitly unmapped, not a zero-area passing baseline.

The unmodified downstream F.Cu pair has a real pre-existing In1 reference slot under x14.8495–15.1505, P y20.685–20.785, N y21.285–21.385. Each gap is0.0301mm2. Obstacle is S07_SW_RX3_P In1 segment UUID a272dc40-ef16-44af-a9f5-bc73a24e0113, (15,28)→(15,0.65). This slot is unchanged. A same-F-layer route would need to go around a far end of this long reference slot, roughly fifteen millimetres of extra vertical travel around its nearer lower end, versus the existing1.38mm short segments. Such a detour is not proposed. Moving a single S07 polarity is also not proposed. Whole-chain reference closure requires coordinated layer/route planning.

Ten reviewed nets comprise this entire S12 chain (four named sections) and six existing TB USB2 sections. All previously mapped reference missing polygons of the other reviewed traces are unchanged. Some original USB2 sections still have meaningful existing slots/unmapped adjacent layers, listed verbatim in the audit. This candidate does not repair them.
Polygon analysis uses actual trace half-width buffers,128 segments per quadrant, native GND fill outlines and holes, make_valid with recorded area changes, and1/5/10µm sensitivity. It is a two-dimensional coverage test, not SI/impedance validation.

## Gates
- Native geometry DRC:0errors;199existing library warnings and1existing copper-sliver warning; unconnected list remains capped499.
- Native schematic parity:0items against copied current Main_12E1S hierarchy.
- Original positive-net pads/tracks/vias, including named NC nets: no original surviving group split, no unexpected deletion, no reassignment. The9 intentional old trace removals are explicitly allowlisted.
- Saved copper UUID-to-net assignments independently compared after slash-alias normalization: no reassignment.
- Existing source/cap pads and new traces remain in one native copper component per section.
- Both before/after full reference reports and source hashes retained. Existing isolated zone-only islands are not enumerated by the item-cluster test.

Accept only as a useful upstream geometric improvement. The full downstream reference gap, sparse near-end return vias, fictional PEX pinout, actual impedance stackup, fabrication and channel budget remain unresolved. No production or SI qualification follows from this report.
