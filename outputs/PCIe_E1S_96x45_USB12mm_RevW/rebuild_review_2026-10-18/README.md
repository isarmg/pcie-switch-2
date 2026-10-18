# 当前重新审查：第二组

最新PCB SHA `0083dece575e4515719c6dc3248dbae3c60fdb5734550eb05b64d91e5e4ad6b1`。

已补BP实际4.7µF旁路及短回路、translator局部去耦，纠正两Flash料号/U510模型，U607无功能预留DNP，并改善S12一对上游差分。详见[本组说明](second/README.md)和[独立验收](independent_second/DISPOSITION.json)。仍107断网、104涉及实装，最少1784次簇连接；DRC几何0错误/1旧铜毛刺、parity0，ERC43错误212警告。所有参考/时序/供电限制仍未完成，不能生产或上电。

## 历史：第一组重新审查

# E1.S rebuilt review, 2026-10-18

The previous fifteenth-checkpoint source and local commit were lost after an environment reset. Remote GitHub main was independently checked at 394c0d3; GitHub returned 422 for a001a6e. This review starts again from the retained de635e94 first-round source and does not claim recovery of the later source.

## First rebuilt electrical ECO
- U31/U506: direct 0.3 mm F.Cu connections from AGND6/PGND15/16 to EP17.
- U31: AVIN10 and PVIN12 locally joined to PVIN11; existing C311 input trace widened 0.2 to 0.5 mm.
- No new holes, footprint movement, net reassignment or rule changes.
- TI [TPS62130 family Rev F](https://www.ti.com/lit/ds/symlink/tps62130.pdf), Table 6-1 and section 11.1 require the direct ground connections and short/wide input paths.

Native audit includes every numbered pad, including NC, and surviving track/via UUID nets. All original pad clusters remain connected; all filled polygon geometry is exactly unchanged after refill. U31/U506 EP, C311 ground and both input-connector return pads belong to the same 1879-pad native ground cluster.

This improves local copper paths only. VOS routing, input/output loop inductance, thermal capability and real power budgets remain unqualified. Baseline and candidate both still have 107 disconnected non-NC nets, 104 involving populated components. No manufacturing or functional approval is implied.

Rebuild with KiCad 10 Python using scripts/revW/w_rebuild_local_power.py SOURCE NEW_OUTPUT. The script requires the exact de635e94 PCB and its same-name project before refill. Original source is retained in the recovery snapshot; accepted output is Main_12E1S. [Independent review](independent_first/REVIEW.json) passed: native geometry 0 errors / 1 copper-sliver warning; schematic parity 0; ERC 43 errors / 212 warnings. Global cluster joins remain 1788; this is local path improvement, not a new global net closure. Native unconnected report is capped at 499, so use the full-pad audit for totals.
