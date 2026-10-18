# Rebuilt reset combination check

Fixed source: writer group2, SHA256 0083dece575e4515719c6dc3248dbae3c60fdb5734550eb05b64d91e5e4ad6b1.
Candidate: c350871d495780568e12e64cd4d33fe8ec5ce248fe5f51ea87519bf3b767b92e.

replay.py applies the guarded reset Clean delta, exact 14 leaf removals, and the CPU_PERST delta including R725 DNP. All original block guards passed. Same-stem formal project existed before native loading and refill. DRC.json contains zero errors, 199 scratch library warnings and one existing copper sliver. REGRESSION.json passes every original numbered pad (including NC), original connectivity cluster, and surviving copper net assignment.

The authorizing logical evidence and exact deltas remain in ../e1s-reset-rebuild and ../e1s-cpu-perst-rebuild. Original leaf cleanup proofs are retained; no blanket waiver for missing copper was introduced. Writer must independently check actual local footprint libraries and reference-plane coverage before main integration.

R725 is DNP to remove the confirmed external pull-up/internal power-sequence pull-down conflict. Its physical pads and nets remain, including an intentionally unjoined DNP-only signal island. CPU F24, translator input and draft PEX input are physically connected. Unknown PEX input loading, CPU power sequencing, rail sources, and adjacent-microvia manufacturing remain unqualified. This is topology repair, not boot or timing sign-off.

## Reference-plane follow-up

The exact In1 GND lost polygon has area 15.7090385025 mm². Intersecting it with the full copper width of every original F/In2 track gives zero affected tracks (527 F tracks, no In2 tracks). Conservative F-pad bounding-box intersections above 1e-6 mm² are GND pads J8.A1/A2/A3 and J101.2, and electrically NC mechanical pads J4.MP1/J5.MP1. Tiny numeric boundary intersections are retained in the raw report. Existing GND connectivity remains intact; this does not measure return inductance.

Writer's rebuild_second/reference_audit.py ran on Base and Candidate with the same config and native fills. Ten selected signal nets presently have routed traces; every reported added missing-reference area is zero. BASE_REFERENCE.json and CAND_REFERENCE.json retain full polygons. This is not a guarantee for future routes or unrouted nets.
