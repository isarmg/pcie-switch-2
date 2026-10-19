# R743 value-only bias correction

Recommended: `4.7k 1% / Intel WAKE external bias`, covering a possible enabled 15 kΩ internal pull-down. This is a conservative engineering selection, not an Intel-specified resistor value or proof that 10 kΩ fails in every phase.

Freshly reread primary Intel 829568 Rev004 §§11.9.1, 11.9.3, 11.9.4 and embedded Electrical Specification/GPIO workbooks. Full source hashes, exact relevant rows and numeric budget: OFFICIAL_BUDGET.json. GPIO row181 TERM none differs from PDF PD table; retain uncertainty, do not presume firmware disables PD. S0ix WAKE is output; external driver conditions still need architecture review.

At VCC=1.71 V, RPU=4747 Ω, RPD=15 kΩ and 5 µA sink leakage, high=(VCC/RPU−I)/(1/RPU+1/RPD)=1.280902 V. VIH=0.65 VCC=1.1115 V; margin169.402 mV. 10 kΩ+1% under the same PD assumption gives0.991733 V. At1.89 V and4653 Ω, worst sink upper bound411.190 µA; atVOL0.45 V,314.478 µA. Future sink must support≥0.412 mA atVOL≤0.45 V with valid domain/off-state behavior.

Six files / eight exact Value string substitutions: COMPONENTS source metadata, PCB, schematic cached symbol and instance, Local symbol library, exported net component and library value, BOM. GUARD.json contains exact pre/post file hashes; scripts/revW/wake_bias_value/replay.py guards input and reproduces only the R743-context replacements in a new directory. PCB baseline85925cdd → candidate c784b3f7. Integrated as its own value-only commit. Historical earlier-revision generator scripts are untouched.

Native KiCad10.0.7 loaded both complete projects and checked candidate schematic parity:0; geometric errors0; existing copper_sliver warning1; capped unconnected entries499. NATIVE_VALUE_CHECK.json confirms R743 value and WAKE endpoints. The byte reversibility assertion proves every other PCB byte, including all pad/NC nets, UUIDs, all-layer copper and existing fills, unchanged. No copper added, so no new plane/pad-reference delta. The publisher independently refilled a verification copy with KiCad 10.0.7 and reproduced the exact same candidate PCB bytes (REFILL_CHECK.json).

WAKE signal remains physically disconnected; no supply source or sequencing implementation is claimed. No R744 or CPU power-layout candidate is included. Only the six GUARD-listed design files are changed; this review directory contains fresh checks, not copied historical acceptance reports.

## Publisher verification

All six input/output hashes and all eight replacements were independently checked. Reverse value replacement recovers every original file byte. The self-contained replay script was executed against the published project; independent refill produced the exact final PCB hash. Fresh native DRC reports zero geometry errors, one existing sliver warning and zero schematic parity findings. Fresh ERC remains 43 errors and 212 warnings. Primary PDF/workbook hashes, WAKE electrical limits, supply tolerance and the conflicting termination entries were independently reread; the high-state margin was independently recalculated. The 0.412 mA sink figure is a conservative future-driver requirement, not validation of an existing driver. Physical WAKE routing and qualified power sequencing remain unfinished.
