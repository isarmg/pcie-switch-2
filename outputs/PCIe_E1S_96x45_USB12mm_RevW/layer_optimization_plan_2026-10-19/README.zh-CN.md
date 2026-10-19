# E1.S 合理层数规划：24 层受控重构，20 层作为后续候选

## 结论与范围

建议从独立的 **24 层重构试验**开始，先验证真实逃线、成对布线、地参考与电源分区。20 层作为量化有余量后的降本候选；16 层暂不作为首轮目标。若证实 24 层的合法过孔逃线、局部通道或 PDN 不够，再调整到 28/32 层。不能宣称 24 层已经可布通，更不能宣称它是已证“绝对最优”。

当前正式 PCB 保持 32 层，未改铜、过孔、板框或连接器位置；M.2 不在本次范围。源 SHA256：e33bc9bf7cb41045c3171abd07677bc36ebe7c3960d61349e4ad5ba2437ecb3c。仍有 97 个非 NC 断网、其中 94 个实装断网，原始设计未完成。连接器真实 SMT 型号、真实 switch ballmap、CPU VR/PDG 及板厂叠层均未定。

layer_plan.json 是可检查的“层资源/重构计划”，**不是制造 stackup**。不填写虚构介质、Dk/Df、铜厚或成品厚度。所有 SI、阻抗、时序、PDN、载流/热和制造签核均为 false。

## 已核实的实际资源

- 23 个走线层、9 个仅电源填充层，全部 32 层有实际铜。9,065 段线总长 22.55 m。
- 六个 GND 填充层 In1/10/13/16/25/28 全都混有走线，没有专用仅 GND 层。
- 12 路独立 SSD 开关输出各占一个填充层。这是可以重新分区利用物理层的机会，不能把 12 路电气输出短接。
- 21 个内部走线层大多每层 0.80–1.29 m，横/竖/斜方向混合并跨大半板。全板面积统计不能代表局部 BGA 逃线可用容量。
- 23 个走线层的 253 种两两原位叠合全部存在异网线铜重叠。不能按旧层号直接合层、删层或重映射过孔。
- 214 对差分“分段网”中 140 对 P/N 分别在不同内层。包含 AC 隔直两侧，不能当成物理 lane 数。跨层本身不必然错误，但受控 broadside 需要明确定义的叠层和耦合验证；当前没有这些证据。新方案默认 P/N 同层成对。
- 例：S06_SW_TX0 的 P=In24/N=In17，中间含电源填铜；S08_SW_RX0 的 P=In28/N=In13；相邻层例 TBT_CIO_RX1_SRC 的 P=In12/N=In11 也没有受控 broadside 模型。

完整每层长度、方向、2 mm 占区采样、填充面积及投影筛查在 LAYER_ARCHITECTURE_AUDIT.json / LAYER_SUMMARY.csv。投影只检查几何，不能证明真实回流或 SI 合格。全部原生统计与既有独立统计一致。

## 候选资源分配

| 候选 | S 信号 / G 专用地 / P 电源 | 用途 |
|---|---|---|
| 16 | 8S/6G/2P；另案 6S/6G/4P | 电源或布线资源压缩较激进，暂不首选 |
| 20 | 10S/6G/4P | 后续挑战方案，保四电源层；仅八内层 S |
| 24 | 12S/8G/4P | 建议首轮重构；十内层 S |
| 28 | 14S/10G/4P 示例 | 已证逃线/屏蔽资源不足时退让 |
| 32 | 16S/10G/6P 示例 | 已证需要后采用，与现混合 32 层不是同一方案 |

S 包含两个外层。示例是资源预算，不是可制造性结论。

24 层对称顺序：
S G S P G S S G P S G S | S G S P G S S G P S G S

- G：L2、5、8、11、14、17、20、23
- P：L4、9、16、21
- 内层 S：L3、6、7、10、12、13、15、18、19、22
- L1/L24：短逃线、本地控制和局部电源

每个 S 至少邻接一个专用 G，具体邻层及默认参考在 JSON 逐层列出。

### 通道预算，去除 AC 隔直重复

PCIe 合计 56 条双向 lane，即 112 条单向差分数据通道：12 个 x4 SSD = 96，CPU–switch x4 = 8，CPU–TBT x4 = 8。另有 4 条 TBT CIO、4 条 DP 主链路及 17 对已走线参考时钟/时钟输入分段；USB2/AUX 另计。

- L3/6/7/18/19/22：六层 SSD 数据，每层预留 16 差分通道，等效两个 x4 插槽。实际分组由球位及局部走廊决定，不能机械按槽号分配。
- L10：CPU–switch 与 CPU–TBT 的 16 条 PCIe 差分通道。
- L15：4 条 CIO + 4 条 DP 主通道。
- L12/L13：时钟、USB2/AUX 与控制；部分局部控制留外层。

这些是待验证的配额。没有据此声称已可布通；尚缺必需电路也不因“预留层数”自动得到解决。

### 相邻 S-S 的边界

L6/L7、L12/L13、L18/L19 没有夹在两者之间的 GND。尤其跨中面对称的 L12/L13 分别参考 L11/L14，镜像关系不是屏蔽。

须由真实介质距离和场求解验证串扰，限制长距离平行重叠，设计合适 S-G 与 S-S 间距；正交走线不能单独视作通过。P/N 仍同层，不把一对拆到这两个相邻 S 上。若不满足，调整为更少信号、更多地的 24 层资源方案（例如 10S/10G/4P 后重查容量），或增加到 28 层获得地隔离；不能硬压介质或无模型宣布通过。

20 层顺序：
S G S P G S P S G S | S G S P S G P S G S

20 层每个 S 仍有邻接 G，但少两个 S、两个 G；P7/P14 没有直接邻接 G，额外 PDN/噪声耦合风险已在 JSON 记录，不能因四 P 保留就宣布电源等价。

### 电源独立性

拟将 L4/L21 作为两个 bank 及各自六个 SSD 开关输出的物理分区资源；L9/L16 给 CPU/PEX/辅助局部多轨，是否足够仍待真实电流/VR 数据。

- bank A：槽 1、2、3、4、5、11；bank B：槽 6、7、8、9、10、12。
- 原生 U11–U22 焊盘核对：pad5 为 VBANK_A/B，pad6 为对应 P12_SLOT01–12。见 SLOT_DOMAIN_NATIVE_PROOF.json；这证明源网分组，不替代器件手册认证。
- VIN_A、VIN_B、VBANK_A、VBANK_B、AUX_12V_PROTECTED 和十二 P12_SLOTxx 必须继续为不同网络。共用物理层只是独立岛/走廊，绝不绕过 eFuse 或短接输出。
- 每路从 eFuse 到插槽应局部分区，按压降、温升、过孔阵列及载流核验。300 W/25 A SSD 总预算不等于已认证额定能力；真实 CPU VR 目前缺失。

## 制造与验证门

候选仅讨论板厂认可的 2+N+2：24 层可讨论 2+20+2，近表面相邻微孔 L1–2、2–3、22–23、23–24。核心埋孔、铜填叠孔、通孔和背钻由板厂给出合法工艺集合，不继承旧 arbitrary 深盲孔；所有尺寸待定。

通用依据：
- [TI SNLA426](https://www.ti.com/lit/an/snla426/snla426.pdf)：完整参考、成对过孔/转换及 stub 处理原则。它不是此 CPU/PEX 的正式 PDG，也不证明本板方案通过。
- [NCAB 微孔指南](https://www.ncabgroup.com/microvias/)：短微孔及有限叠孔的制造/可靠性建议；需落实到选定厂商。
- [TTM HDI 工艺资料](https://www.ttm.com/sites/default/files/documents/3K.%20HDI_Advanced%20Solutions_High%20Res_2026.pdf)：2+N+2 工艺类别，仅是供应商能力参考。

受控推进顺序：原始源冻结 → 实际合法过孔/器件约束表 → 最难的代表性逃线与成对通道试验 → 独立电源域和 GND 连续性 → 全部通道/控制 → 原生 DRC + 独立焊盘连通 → SI/PI/时序/热/制造。

24→28/32 的条件是具体合法逃线、局部通道、屏蔽或 PDN 证据失败；不能把一次局部失败当全局无解。24→20 的条件是完整目标已通过且有可量化局部余量，再独立重布复验；不能删掉预留层后沿用结论。

## 重放与文件

只检查计划一致性，不需要 KiCad/Shapely：

```sh
python validate_layer_plan.py --board /path/Main_12E1S.kicad_pcb --plan layer_plan.json --out /your/scratch/plan-validation.json
python test_validate_layer_plan.py --board /path/Main_12E1S.kicad_pcb --plan layer_plan.json --out /your/scratch/plan-negative-tests.json
```

validator 检查源 SHA、原板仍 32 层、候选计数/对称、每 S 的邻 G、S-S 未签标志、电源域与源网存在、通道去重及未签核状态。反例测试确保假签核、错误源、断参考、短接分区、虚构 Dk、重复通道和旧深盲孔放行等会失败。

重新提取几何需 KiCad 10 可用的 pcbnew Python；分析需普通 Python + Shapely 2。运行时使用自己的 HOME/XDG/TMP，输出指定 scratch，源只读，不调用 SaveBoard/Refill。

```sh
/path/KiCad/AppRun python3.11 dump.py --board /path/Main_12E1S.kicad_pcb --out /your/scratch/NATIVE_GEOMETRY.json
python analyze.py --geometry /your/scratch/NATIVE_GEOMETRY.json --outdir /your/scratch/analysis
```

大型 NATIVE_GEOMETRY.json 可按原源重建，无须入库。layer_plan.json、摘要 JSON/CSV、计划验证器及本说明构成审查交付；REPORT.md 是扩展英文技术说明。
