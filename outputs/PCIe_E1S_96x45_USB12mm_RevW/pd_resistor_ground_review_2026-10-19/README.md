# TPS65982 ROSC and address resistor ground completion

Source formal commit55eb949ab9d1a89e3777bfc1533c1e45cfb63b3d; PCB dbd2588c3fddfe6ec132bdcae97372fcd677cde3e7feedb17f144cc0c3a2c872. Candidate e33bc9bf7cb41045c3171abd07677bc36ebe7c3960d61349e4ad5ba2437ecb3c. Project9086611e035a0210cfc1bdfb30769d78d36880dd96954c8f5b869291103f8f30 unchanged.

## Official requirement and existing configuration
TI TPS65982 SLVSD02E RevE, https://www.ti.com/lit/ds/symlink/tps65982.pdf, official primary document independently reopened by publisher; vendor PDF not included:
- Pin table G2 R_OSC explicitly connects through resistance to GND. Page28 section7.24 gives15k oscillator set resistance. Page82 section10.2.1.2.3 explicitly recommends15k0.1% for PD BMC communication and USB2 endpoint timing;1% is not recommended. Existing R5151 is15k0.1%, unchanged.
- Page80 Table9-10 identifies I2C_ADDR resistance0Ω to ground as SPI Owner/UART Master0 Primary. Page82 section10.2.1.2.2 describes this grounding configuration. Existing schematic R5152 is0Ω, unchanged. This closes the already selected configuration, not an authorization to choose new address/mode. Firmware, debug straps and system address assignment remain unverified.
- Page69 oscillator section and pages92–97 layout were reviewed: no dedicated ROSC quiet-ground route or maximum ground-return length was found in these sections. Absence of a numeric restriction does not qualify noise or timing performance.

## Exact physical change
Four new B.Cu GND segments, all .15mm wide, zero vias, zero moved footprints, zero changed/deleted old copper. All old pad geometry, footprint properties, capacitor paths and board rules unchanged. No metadata position change required.
- R5151.2 (69.83,34.30) → C5115.2 (71.32,34.35):1.490839mm.
- R5152.2 (69.78,35.30) → (69.50,35.00) → (69.50,34.30) → R5151.2:1.440366mm.
- Both use existing C5115→C5113.2→U503.L1 main-ground return3.977539mm. Total surface return R5151≈5.468378mm, R5152≈6.908744mm. These are shared returns, not independent quiet-ground paths. No existing decoupling track is lengthened or removed.
- Native positive-side groups remain R5151.1+U503.G2 and R5152.1+U503.F1; each ground pad changes from singleton to main1897-pad GND group. This completes the actual resistor DC circuits, but not regulator/oscillator/system qualification.

## Shared impedance screening only
At assumed20°C copper resistivity1.724e-8Ωm, .15mm width, uniform18–35µm finished copper, the existing shared3.977539mm segment is about25.4–13.1mΩ. Per1mA flowing along that shared segment, DC voltage is25.4–13.1µV. Assuming copper temperature coefficient.00393/K,85°C gives31.9–16.4mΩ. Actual copper thickness, vias, pads, temperature and current are not established; these values exclude all via/pad/plane resistance. Existing1V8A/VOUT currents and their dynamics dominate potential shared-noise concerns. No specified ROSC operating-current maximum was found; I2C address diagram p80 shows5µA current source, not a tolerance-qualified maximum. Do not use this screening as worst-case timing evidence. L·di/dt coupling and frequency accuracy remain unverified.

## Verification and application
DRC.json:0errors,1pre-existing copper_sliver warning, parity0. AUDIT/INDEPENDENT_REGRESSION compare all6626 numbered physical pads including NC and all old native clusters/nets. VERIFICATION3 confirms combined old pad+copper clusters and G2/F1 intended connections. ALL_PLANE has0 affected old signal-track projections; PAD_INPUT/PAD each0 functional-pad losses over all evaluated GND and power planes. All source items preserved exactly; DELTA3 guards no replacements/deletions, only4 additions. Prefill expected copper and footprint blocks match postfill.

Use officialKiCad10 Python replay3.py EXACT_SOURCE_PROJECT_DIR NEW_PROJECT_DIR. Full project is copied before anyLoadBoard/refill. Exact source/prohash guards and postfill expected block hashes apply. Publisher independently repeated all native checks and exact full project replay before publishing.

## 发布者独立验收
原生复验DRC0错误/1旧sliver/parity0、ERC旧43错误/212警告、6626旧pad含NC/全部旧铜pad簇和net守卫、全plane和功能pad投影通过。所有旧FP/铜/zone含填充完整块不变；仅新增4条地铜。两电阻正端原2pad簇保留，地端均入1897物理pad主地。完整发布重放PCB字节一致。

重新核查TI官方15k0.1%及0Ω既有Primary模式依据。原电容路径与参数未改，未发现本次新增地铜造成明确数值要求违背；这不构成稳压稳定性/ROSC噪声/频率精度认证。共享原地支段独立条件估算18–35µm/20℃为25.397–13.061mΩ，排除孔、pad、plane及AC阻抗，不能当最差值。系统地址与firmware匹配仍待确认。

状态更新：97断网/94实装、minimumjoins1754、GND129。没有位置或BOM修改；CURRENT和ROUTING_STATUS同步。历史STEP/预览未重生成。完整重放入口scripts/revW/pd_resistor_ground/replay_full.py EXACT_SOURCE_REVW_DIR NEW_REVW_DIR。
