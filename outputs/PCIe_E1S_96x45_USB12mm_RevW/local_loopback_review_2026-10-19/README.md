# Intel local loopback repair, rebuilt 2026-10-19

This independently reviewed change starts from freshly accepted corrected PCB bb7cc241cf5f548508e9091352a07ab4407bc8ff08489037f1e11aeb80c8ccbb. Integrated PCB SHA256 f31316e79ea4290db7e75fc3f79ba0a1861925ea6e8a98a7d457b0c1a1160a60. Formal project hash 9086611e035a0210cfc1bdfb30769d78d36880dd96954c8f5b869291103f8f30. Integrated as its own commit after the reference-plane correction.

## Scope and official basis
Exactly two B.Cu straight tracks, each 0.57mm long and 0.10mm wide, no vias or moved components:
- U502.Y27 EPD_ON_IN to U502.AB27 EPD_ON_OUT, existing CPU_EPD_ON_LOOP_1V25 net.
- U502.AA26 VDD2PWRGOOD_IN to U502.AC26 VDD2PWRGOOD_OUT, existing CPU_VDD2_PWRGOOD_LOOP net.

Intel document 829568 Rev004, May2025, downloaded again from the official source, specifies platform connection of these signal pairs on pages118,121 and178. Its embedded 825698-001_Ballout.xlsx Pinlist independently matches all four actual board balls. OFFICIAL_EVIDENCE.json binds source hashes and paraphrases requirements. This is not a guessed supply connection or proof that the CPU power and reset architecture works.

## Fresh verification
- Native connectivity: both actual nets were two populated singleton pad groups and are now each one physical group; LOOP_CONNECTIVITY.json.
- All old pad identities including NC, old physical clusters and copper UUID/net assignments pass REGRESSION.json.
- DELTA.json proves every original footprint, copper object, zone setting, boundary and filled polygon remains identical (token comparison). Only the two declared tracks are added, with prefill/postfill expected object equality.
- Full power-and-GND plane delta: zero affected adjacent track projections. All functional-pad projections: zero hits.
- Native all-track geometry DRC: zero errors; only existing copper_sliver warning. Schematic parity: zero findings.
- ERC remains the baseline 43 errors and212 warnings. These pre-existing undriven/isolated schematic issues are not fixed by these loopbacks. The native unconnected-items list reaches499 and is not a complete board residual count. No power flags or waivers were added.

## Replay
Using KiCad10 Python, run scripts/revW/local_power_loopbacks/replay.py EXACT_SOURCE_PROJECT_DIR NEW_PROJECT_DIR. The script verifies board/pro hashes, copies the complete formal project before LoadBoard/refill, adds only declared UUID blocks, builds native connectivity, refills and asserts the exact final candidate hash. No metadata, symbol, value or position updates are needed.

Only this small local loopback batch is included. Manufacturing, real CPU supply sequencing and system functionality remain unqualified.

## Independent integration check

The publisher independently checked every supplied manifest hash, verified the entire board is token-identical to bb7 after removing exactly the two declared new segment blocks, and reran official KiCad 10 all-track geometry DRC: zero geometry errors, one existing copper-sliver warning, zero parity findings. PUBLISHER_DRC.json records that run. The preceding correction remains a separate parent commit.
