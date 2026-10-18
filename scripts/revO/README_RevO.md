# Rev O：120 × 45 mm，27 个竖直 M.2

按用户要求继续排满连接器面。本版采用一排 **27 个竖直、同面、平行的 M-Key 2280 插槽**，中心距 4.35 mm。连接器行的包络为 X=1.275–118.725 mm、Y=11.025–35.575 mm。使用当前封装、保留边距和方向时，第 28 个插槽不能再放进这一排；上下剩余条带用于电源器件，无法再放一个同方向的 24.2 mm 长连接器。

**23 个槽保留 PCIe x4 网络分配，新增 P01–P04 四个槽仅接供电和地，所有数据信号、时钟、复位和边带脚均悬空。仅供电槽不能作为可识别的 NVMe 端口。** 全部 96 条主数据 lane 的分配仍为 CPU 上行 x4、23 个下行 x4。独立管理 lane 没有作为额外槽位使用，switch 端口固件仍未配置。[Broadcom PEX88096](https://www.broadcom.com/products/pcie-switches-retimers/expressfabric/gen4/pex88096)

本版是布局和部分布线草案。**CPU 完整电源/启动平台、绝大部分协议布线、固件、阻抗和散热未完成，不能直接生产。**

## 保留与调整

- 主板 120 × 45 mm，32 铜层、名义 1.6 mm；无 E1.S、子板、板间线缆和四角固定孔。
- CPU、PEX88096、USB-C、JHL9580 占位及原平台电源等共 **274 个器件保持坐标、朝向和安装面**。插槽重新均分为 4.35 mm，新增供电与无源器件重新排布。
- 23 个数据槽：M1–M4、N01–N19。4 个仅供电槽：P01–P04，位于原 F 面坐标 X=103.50、107.85、112.20、116.55 mm，Y=23.30 mm。`M2_PORTS.json` 和 `PORT_PLAN.csv` 标明两类用途。
- 连接器金属固定脚全部为 SMT；USB-C 各两个塑胶定位孔保留。M.2 是参考 MDT350 的 **无塑胶定位柱自定义草案**，原带柱型号不能不经修改直接装配；实际无柱器件和触点方向仍待厂家确认。[Amphenol 参考器件](https://www.amphenol-cs.com/product/mdt350m01001vt.html)
- 为保留 27 个插槽，新增数据槽的 AC 电容及配套小电阻改用 0201。AC 电容仍为 220 nF / 16 V，参考 GRM033R61C224KE14D；12 V 输入旁路电容保留 0402 / 50 V，未把低压电容用于 12 V。[Murata 原厂器件参数表](https://www.murata.com/-/media/webrenewal/tool/library/common-pdf/dynamic-model/component-list-d-mlcc-2504.ashx?cvid=20250523010405000000&la=en)
- USB-C 四个金属固定脚的 SMT 封装也是自定义草案，原 USB4160 穿板脚型号不兼容。TB5 器件/通道资格未确认；JHL9580 按要求继续暂缓。
- switch 面器件高度 ≤8 mm，连接器面 ≤9 mm；TPSM53604 按最大 4.1 mm 包络显示。SSD 模型仅为简化的裸板和元件包络，不包含散热器、保持架和外部插头。

## 供电与实际铜线

每槽按用户确认的 **3.3 V / 4 A** 预留，27 槽共 **108 A、356.4 W** SSD 输出预算。4 个原端部数据槽保留 TPS565201，其余 23 个槽各配 TPSM53604RDAR 集成电感模块。输入仍按 **12 V / 50 A、两个 25 A 支路**预留；按 85% 效率和 85 W 平台余量，计算输入预算约 42 A。**输入焊盘、铜厚、线材、保险丝实物和热设计没有完成额定能力验证。**

TPSM53604 使用真实 15 针封装，反馈 10 kΩ / 4.32 kΩ，两个 10 µF 输入电容、100 nF 旁路及三个 47 µF 输出电容。输出需至少 52 µF 有效容量，141 µF 仅为标称合计，偏压/温度容量仍待核对。DNC 4/5 独立悬空，V5V 不给外部供电。[TI SNVSBC9C 数据手册](https://www.ti.com/lit/ds/symlink/tpsm53604.pdf)

新增四个仅供电槽已画出电源铜层、焊盘连接过孔、地连接及反馈分压连线：四路 3.3 V 分别使用 In1/In3/In5/In7，VBANK_B 使用 In9，VIN_B 使用 In11；地接已有 In12 平面。J12 输入焊盘、F2 两侧及四路模块与各槽电源脚均包含在连接核验清单。**这是铜线几何和连接设计，不代表 4 A 持续电流、25 A 输入支路、过孔工艺或 32 层 HDI 叠层已通过制造和热验证。** `POWER_ONLY_ROUTING.json` 保存逐脚过孔与反馈路径证据。

新增 P01–P04 没有 PCIe/时钟/边带线路。23 个数据槽沿用原网络分配，大部分协议线仍未布线。自定义 USB 外形供电口仍非 USB/PD，并未接通主大电流母线；新增四路从 J12/F2 支路引入，任何 M.2 电源脚都没有接 12 V。

## 仍需完成

CPU 为官方 Intel 268V 的 2833 个非均匀球位，PEX88096 为真实 1550 球；保留几何经过逐球核对。CPU 的 0.25 mm 焊盘仍缺 Intel 装联图 751493 确认，多路 PMIC、时序、EC/BIOS/电源完整性未完成。

三颗 9ZXL0851 的网络计划保留。CPU ICC/BIOS、SSC/common-clock 模式、复位驱动和 switch 端口固件均未完成。新增数据槽 PERST 由下拉保持复位，不能宣称可枚举。

原 CPU–PEX 的 8 对数据差分线与 1 对 REFCLK 保留，共 34 个电容分段铜线网络；尚未等长、补偿封装延迟或进行整板 SI。KiCad 检查报告区分短路/间距、未连线和原理图错误，不能把“间距检查通过”理解为电气设计已完成。

## 文件

- `Main_27M2/Main_27M2.kicad_pro`：本机 KiCad 可编辑项目。
- `Main_27M2/Main_27M2.step`：板和器件；`Assembly_View/Assembly_View.step`：另带 27 块竖直 2280 简化包络。
- `M2_PORTS.json`、`PORT_PLAN.csv`、`BOM.csv`、`Main_27M2/PIN_MAP.csv`：用途、真实 lane 分配、器件和逐脚网络。
- `CORE_PLACEMENT_BASELINE.json`、`VALIDATION.json`、`POWER_ONLY_ROUTING.json`、`POWER_CONNECTIVITY_CHECK.json`：位置、原理图/PCB、供电铜线连接核验。
- `STEP_VALIDATION.json`：本机 KiCad 导入并再次导出 STEP 的结果；`SHA256SUMS.txt`：归档哈希。

历史版本保留：Rev M 为 110 × 45 mm、10 E1.S + 4 M.2；Rev N 为 120 × 45 mm、23 个 M.2。本版不附生产 Gerber 或钻孔包。
