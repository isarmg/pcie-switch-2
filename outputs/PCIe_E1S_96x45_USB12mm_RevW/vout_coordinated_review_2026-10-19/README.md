# VOUT coordinated local bypass candidate, 2026-10-19

Frozen source: formal Main at commit 451f87dc39f514485fbbdf5bc75af9c0903d1de3, PCB f7a11f8395f89a8cf62539c9f4f2b3c7325e8fc8373e40ed50a71f843a32ea32, project 9086611e035a0210cfc1bdfb30769d78d36880dd96954c8f5b869291103f8f30.
Candidate3 PCB dbd2588c3fddfe6ec132bdcae97372fcd677cde3e7feedb17f144cc0c3a2c872. This is the final NO VIA CHANGE version. Earlier candidate reports under rejected-via-shift are rejected evidence only.

## Electrical scope and real benefit
TI TPS65982 datasheet SLVSD02E Rev E, https://www.ti.com/lit/ds/symlink/tps65982.pdf : pin table p8 identifies H2 VOUT, switched VIN_3V3 output; p91 Table 11-1 recommends VOUT bypass 1uF, effective range .1–2.5uF, rating6.3V. Existing C5115 remains 1uF6.3V0402, unchanged geometry/value and no invented MPN. Bias/tolerance/temperature-effective capacity and regulator functional qualification remain open.

C5115.1 formerly isolated is now connected to U503.H2 by 2.223553mm B copper of width .075mm. C5115.2 formerly isolated is connected by 2.598808mm new .15mm B copper to C5113.2, then existing 1.378731mm .15mm 1V8A return to U503.L1. Total return 3.977539mm is SHARED with 1V8A; this is not a short independent bypass return. C5115 ground joins the existing main GND cluster (1894→1895 physical pads). Return sharing/inductance/noise and .075 output width remain engineering limitations.

C5155 CT moves .300mm toward U510. Its original GND line UUID446f959c-32f1-42c4-8ae5-d7dfe8b842c3 is shortened from1.862607 to1.562628mm (.299979mm reduction). CT signal gains .300001mm .1mm B lead; original signal copper/endpoint is preserved. Value10nF, pin nets, U510.4 CT two-pad cluster and main-ground connection all unchanged. TI TPS3808 datasheet https://www.ti.com/lit/ds/symlink/tps3808.pdf p4 CT pin4; p11 Eq1 gives nominal delay CT(nF)/175+.0005 seconds (~57.64ms at10nF). Additional signal parasitics/leakage not qualified.

R5151/R5152 low-speed signal pads retain their original net clusters through new .1mm B leads (.493964/.567539mm respectively). Their originally isolated GND pads remain isolated; this package does not claim those strap/oscillator functions complete. All original vias are byte-identical, including R_OSC In1–B via connected to original In25 trace and I2C_ADDR In1–B via connected to original In8 trace. No new via/inner-layer trace is added.

## Five footprint metadata changes (mm, native angles)
- C5115 B (80.1,39),90 → B(71.8,34.35),180
- R5151 B (70.6,33.7),0 → B(69.83,33.79),270
- R5152 B (70.6,34.75),0 → B(70.1,35.3),180
- C5155 B (70.6,32.6),0 → B(70.6,32.3),0
- TP711 B(72.125,34.225),0 → F same position,180; original isolated pad/net remains isolated. No signal test-point functionality or physical accessibility claim.
Exact old/new full blocks, UUIDs and source hashes in DELTA3.json; PLACEMENT_DETAILS.json supplies native full metadata. No pad/courtyard size/value/rule changes. Only one existing CT GND track endpoint changes, plus nine new B tracks.

## Mechanical limits
Native DRC finds no geometry errors. Nearby passives have tight 2D courtyard margins: C5115 to 1V8A/BMC ~.030mm; R5151 to coupling column~.035mm; CT/R5151~.050mm. These are not assembly/3D approval. TP711 F native pad+court bbox has nearest TP margin.150mm, J8.175mm, J7.425mm (TP_F_COURTYARD.json). Existing connector/board outline geometry is unchanged.

## Gates and reproduction
DRC.json: 0 errors, one pre-existing copper_sliver warning, schematic parity0. AUDIT/INDEPENDENT_REGRESSION preserve all6626 old numbered native physical pad shapes including NC, all old clusters and surviving copper nets. VERIFICATION3 additionally checks combined old copper+pad connectivity. ALL_PLANE has zero affected old track projections; PAD_INPUT and PAD have zero functional-pad reference loss hits across all relevant power/GND planes, not only six GND layers. DELTA3 guards all old blocks and expected prefill/postfill non-zone blocks, including every intended new copper net; zone settings unchanged. Vias unchanged.
Run official KiCad10 Python replay3.py EXACT_SOURCE_PROJECT_DIR NEW_PROJECT_DIR. It checks exact sourcePCB/pro, copies the complete project before LoadBoard/refill, applies only guarded blocks, and verifies resulting native tokens and SHA. Publisher synchronized all five footprint positions/layers/angles in COMPONENTS, BOM and PLACEMENT_PLAN and independently repeated native gates.

## Rejected alternative retained
Earlier .05mm I2C via shift passed DRC but caused real plane-reference loss including J7.B1 ~.00862mm² and old AR_FLASH_WP_N track. Rejected trial remains outside this published package; no rejected PCB is included. Final candidate restores ALL vias exactly and has zero projection losses.

## 发布者独立验收
基线451f87dc39f514485fbbdf5bc75af9c0903d1de3。完整守卫重放PCB字节完全一致；正式KiCad10重复DRC0几何错误/1旧sliver/parity0、ERC旧43错误/212警告，6626旧pad含NC/全部旧铜pad簇与net归属、全plane及输入输出功能pad参考投影均通过。两信号孔用原生整数XY/孔径/钻孔/层对/原支路全部一致门禁复核，未沿用已拒孔移位报告。全部未列入变更的旧对象保持；仅CT地一条原线端点缩短。新9条铜归属与预期守卫一致。

CT电容仍与U510.4连通、地保持主簇，原值不变。VOUT正端2.223553mm，地新2.598808mm加原1V8A末段共3.977539mm，真实共享返回，不认证噪声/稳定性。VOUT是受控VIN_3V3输出开关而非独立稳压器；真实有效C、输入电源/控制及系统时序仍未验。R5151/5152地脚仍孤立。TP711仍孤立且探针/3D可达未验。TI两份官方资料已重新核查。

实测97断网/94实装断网、minimumjoins1756、GND131；ROUTING_STATUS和CURRENT同步当前板hash。之前VOUT局部拒绝记录仍为历史证据，本批通过5FP协调形成有限拓扑改善，不代表PD系统全部完成。历史STEP/预览未重生成。完整重放：scripts/revW/vout_coordinated/replay_full.py EXACT_SOURCE_REVW_DIR NEW_REVW_DIR。
