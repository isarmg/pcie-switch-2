# E1S BP bypass repair, independently rebuilt

## Accepted candidate
BP.kicad_pcb SHA2564218c8c6b73c41261c931e5ed33e3c4775f19da83482ae810e9cecbe8a6eaec1, based on current frozen cfd3a2a3de7bbeedeb94c3c2c9f6a1422be7a8a71141d28c105f218bc0c4ac80. No historic lost candidate or earlier report is used as acceptance evidence. Formal same-name project is present before load/refill; project SHA2569086611e035a0210cfc1bdfb30769d78d36880dd96954c8f5b869291103f8f30.

C9004 changes from2.2uF/0402 to4.7uF10V±10% X7R Murata GRM188Z71A475KE15D, max height0.95mm. Position F(1.25,6.35),90deg. Library alias Local:C_0603_1608Metric_BP_Official is the complete installed standard KiCad footprint with only top-level name changed. Original C9004 footprint UUID and numbered-pad UUIDs/nets retained. No pad or courtyard reduction; FOOTPRINT_ORIGIN.json proves exact alias origin, native DRC has no library mismatch.

R9007 moves(1.8,5.0)→(1.8,4.65); R9011 moves(1.8,4.2)→(1.8,4.15). C9005 remains unchanged. Existing PG blind via5053bd63-424e-41b2-aaa4-f67dc41f8a58 moves(1.48,5.0)→(1.48,4.9), with its existing In11 trace endpoint moved identically. The old via type, drill and net remain unchanged; this is not qualification of its existing deep-blind fabrication structure. No new holes.

36 old BP F.Cu fine-route segments are replaced by9 new tracks. The bypass supply and DRGND return are each direct0.30mm F.Cu tracks. Low-current BP configuration/BOOT branch connectivity is retained via a0.10mm side branch. Moved resistor pads have explicit short copper to existing vias rather than depending on edge-touching pad overlap. Existing zone settings/boundaries are unchanged; zone fill is regenerated using the formal project.

## Evidence and integration
- Base-drc.json / BP-v4-drc.json: both only the original In23 copper_sliver warning;0 errors,0 new warnings,0 library mismatch.499 capped unconnected findings are not interpreted as full-board completeness.
- Base-audit.json / BP-v4-audit.json / BP-v4-regression.json: all6624 original numbered physical pads, including NC, retain identity/net; no original physical cluster splits; surviving original copper UUIDs retain their net assignments. Full non-NC disconnect count unchanged at107, populated104.
- LOCAL_LOOP_EVIDENCE.json uses a diagnostic copy with all vias/zones/non-F tracks removed to prove each C9004 terminal still connects on F to U901.31 BP or U901.29 DRGND. This diagnostic PCB is not an integration candidate.
- BP_FINAL_delta.json contains full added/removed/replacement blocks. merge_guarded.py checks exact old blocks and project hash, refuses duplicate added UUIDs and existing output, copies project before output is loaded, and includes the real alias footprint. Guarded replay object blocks match the accepted candidate (GUARD_REPLAY_TEST.json). Zone fills must be regenerated on the combined board.
- Writer must synchronize C9004 value, footprint, height and MPN/datasheet in metadata, schematic/library instance and BOM, then rerun formal parity/ERC/native full gates. These source files are deliberately not overwritten by this copper candidate.

Only BP-v4 is accepted. Earlier DRC/regression reports record rejected geometry/continuity experiments; they must not be used as passing results.

## Official requirements and limits
SOURCE_EVIDENCE.json links current official sources. TI TPS548D22 RevD8.2.3.6 calls for4.7uF BP bypass to DRGND with localized low-impedance return; BP typical is5.07V. Murata's current official MLCC list and SimSurfing selection confirm the chosen0603 X7R10V4.7uF±10% part and0.95mm maximum height.

No numeric DC-bias curve was retrieved for this exact part. Effective capacitance versus bias, temperature and aging remains unverified. TI does not specify an effective minimum of4.7uF here; that stricter requirement is not invented. Nominal4.7uF plus physical connection is not proof of regulator stability, startup margin, gate-drive ripple,40A power delivery, thermal performance, EMC or full assembly clearance. This candidate does not alter CFF or other compensation/settings.
