# Reconstructed reset reference correction, 2026-10-19

This correction is rebuilt from the published `13233812` source and its exact reset patches. The unpublished commit `10d4741` was not recovered. The reconstruction does reproduce the previously recorded corrected PCB SHA-256 `bb7cc241cf5f548508e9091352a07ab4407bc8ff08489037f1e11aeb80c8ccbb` byte for byte after KiCad 10.0.7 refill. Later unpublished improvements are not part of this source and must not be claimed as installed.

## Why this supersedes the third checkpoint

The third checkpoint checked GND reference planes and selected nets. That scope missed new reference loss on power planes adjacent to existing signals. Full power-and-GND plane review found the CPU_PERST In30 route changed AUX plane islands, and a new C741 ground via affected another existing reference. Geometry DRC and connectivity alone did not catch these regressions.

## Exact corrective scope

- Remove exactly the 19 CPU_PERST copper objects recorded in the published `scripts/revW/rebuild_reset/cpu_perst/patch.sexpr`, after matching each complete original object block.
- Move C741's GND via `e12543dc-2310-4aa2-bac6-200bd0dbe678` from (31.36,39.15) to (31.46,39.15) mm; update only the endpoint of GND segment `ddbbaa65-2e03-4765-aed8-60f0a8cfc69b` to match.
- Retain all 583 footprints, all other copper, the U605 local MR/CT/RESET circuit, R725 DNP, nets, rules, project settings, and board outline.
- Reopen the CPU_PERST connection between U502.F24, U511.3 and U1.AM32. This is an intentional incomplete connection, not a claim of completed reset operation.

Self-contained guarded reconstruction: `scripts/revW/recover_reset_reference/replay.py SOURCE_MAIN_DIR NEW_MAIN_DIR`, using KiCad 10's Python. It copies the formal project before refill and asserts the exact final PCB SHA. `DELTA.json` contains the 19 complete removed objects and two guarded replacements.

## Verification and boundaries

The independent reports in this directory are freshly generated for the reconstructed source. The generic comparison against the published third checkpoint deliberately reports the CPU_PERST split; the precise ECO scope must be read with it. Comparison against the second checkpoint preserves all original pad clusters.

Full plane checks cover actual power and GND zone fills and adjacent full-width tracks, plus functional pad projections. Tiny numerical boundaries are retained with 1/5/10 micrometre sensitivity; this does not change any design rule. New local reset pads at their moved positions have their own nearby launch/plane voids, explicitly distinguished from regressions beneath pre-existing signal geometry.

DRC/ERC do not qualify high-speed return paths, impedance, real switch pinout, CPU power architecture, reset timing, thermal current capacity, or manufacturing. The board is still incomplete and must not be fabricated or powered as a validated design. Historical STEP files and rendered views were not regenerated.
