# Rev V：12 V 输入 / 12 槽 E1.S 供电布线草案

本版在 Rev U 的 96 × 45 mm 板上补画可核实的 SSD 配电及辅助电源。**CPU 动态电源、虚构 switch 核心电源尚未实现，整机仍不可直接上电或生产。**

12 个竖直 E1.S、8 mm 中心距、Y=26.54 mm、插入后下侧边距名义 7.25 mm 均保持；无 M.2、子板或固定/定位孔。Ultra 9 288V / 32 GB、虚构 PEX90064、雷电 3 主机口及两个 USB-C 的位置保持。旧 Rev U 原样保留。

## 本次电路

- 输入为同一稳压 12 V 电源的两组独立正线及回流线，接 J101 / J102 焊线端子。每组预算 20 A，合计 40 A / 480 W 是电源容量预留，不是已验证的 PCB 额定功率。端子没有接触件额定电流认证，线径、焊接、散热及输入过压条件需按实际实现核准。
- F1、F2 改为 Littelfuse 0456025.ER、25 A SMT 保险丝；与原 456 系列 20 A 版本共用外形。保险丝需按环境温度和时间电流曲线降额。后级各有 SMBJ13CA 瞬态抑制器。TVS 处理瞬态，不能当持续过压稳压器使用。
- A 组供 S01–S05、S11；B 组供 S06–S10、S12，每组 SSD 150 W / 12.5 A。每槽保留 TPS259470A eFuse：UV 分压 76.1 kΩ / 10 kΩ，名义开启阈值 10.332 V；OV 分压 102 kΩ / 10 kΩ，名义关断阈值 13.44 V；ILM 为 1.10 kΩ，名义限流 3334/1100=3.031 A。阈值未加入 IC 和电阻误差，25 W 不是精确功率限值。
- 每槽 10 nF dVdt 电容、局部输入去耦和 10 µF / 25 V 输出去耦；MLCC 需确保 12 V 偏压下有效电容满足要求。AUXOFF、FLT、ITIMER 按器件允许方式保持 NC，未加入集中故障遥测或软件时序管理。
- 辅助支路 U30 的限流电阻由 3.32 kΩ 改为 750 Ω，名义限流约 4.45 A，支持后接两路降压。保留相同的 UV/OV 保护。
- U31 TPS62132：12 V → 3.3 V，芯片能力上限 3 A；U506 TPS62133：12 V → 5 V，芯片能力上限 3 A。两组 2.2 µH 电感及输入、输出、软启动电容改为局部布局，补齐 SW、VOS、PG、SS、输入输出与地铜箔。两只电感选为 Coilcraft XAL4020-222MEC，DCR 最大 38.7 mΩ，25°C 下电感降幅 30% 的饱和电流 5.6 A，低外形约 2.1 mm；仍需按实际温升、偏差和故障峰值验证。
- 5 V 送往 TPS65982 的 PP5V0；再经其受控开关送 J402 VBUS。3 A 外供需 PD 固件、电流限制、连接器、ESD 和热设计共同验证，目前没有加载可工作的 NVM。
- 3.3 V 供槽位辅助脚、时钟缓冲、雷电控制器输入和现有低压辅助电路。电源层及过孔已补画，并以实际填充铜区验证所选网络连通。具体覆盖范围见 POWER_CONNECTIVITY.json。
- J401 保留用户指定的非标准 USB-C 触点分配，但自定义 12 V 网络继续与主母线隔离。不能将其视为普通 USB-C/PD 口或已验证的 300 W 输入接口。

## 功率与边界

12 槽各 25 W，SSD 合计 300 W / 25 A。若两路辅助电源均按芯片最大输出 3 A 估算，输出共 24.9 W，按暂定 85% 效率需要约 29.3 W / 2.44 A 输入。因此当前已画支路预算约 329 W / 27.44 A；CPU 与 switch 另外计算。3.3 V、5 V 的芯片额定电流并不证明本板能同时满载，实际热设计与负载预算尚未验证。

32 层中，In5 和 In6 分别改为 A、B 组 12 V 专用电源层，移走原有信号，形成连续主母线铜面；迁移记录见 POWER_LAYER_RESERVATION*.json。其他电源层仍可能与信号共用，局部地和辅助电源跨接见 POWER_ISLAND_BRIDGES.json。还需重做可制造积层、功率铜厚/宽度、回流与过孔电流仿真；连通检查不能认证母线电流。0.1 mm 钻孔及跨多层盲孔均属未核准的 HDI 假设。

288V 的 IMVP/SVID 动态核心、内存及启动时序电源缺少 Intel 平台设计和 VR 方案；CPU_POWER_DOMAINS.csv 继续明确标为待实现。不会把未知 CPU 核心接到任意固定电压。虚构 PEX90064 没有真实供电定义，0.9 V / 1.8 V 标签不能代替芯片规格，本版未伪称完成其核心供电。雷电控制器的其余内部低压分配、去耦位置与平台时序仍需核对，不能据本次辅助输入布线认为整块雷电电路已完成。

原 523 段信号连通布线保留。仍有正负线分层、未成对耦合/等长、未验证阻抗、插损与封装延迟的问题，不具备 PCIe 额定速率保证。原始连接器带下伸固定脚/定位柱，而 PCB 已按用户要求取消对应孔，需确认或定制能安装的连接器版本。

VALIDATION.json、POWER_CONNECTIVITY.json、原生 DRC/ ERC 和 STEP_VALIDATION.json 分别记录检查结果。保留未供电网络和整板未连接项，不以删除网络或忽略规则制造“整机完成”的结论。

打开 Main_12E1S/Main_12E1S.kicad_pro。PCB、原理图、STEP、两面预览和电源结构图随工程提供。

资料：

- TI TPS25947：https://www.ti.com/lit/ds/symlink/tps25947.pdf
- TI TPS6213x：https://www.ti.com/lit/ds/symlink/tps62130.pdf
- Littelfuse 456：https://www.littelfuse.com/assetdocs/fuse-456-datasheet?assetguid=d86b18f9-14fa-4764-87ff-8aec12e9a89d
- Coilcraft XAL4020-222MEC：https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xal/xal40xx/xal4020-222/
- Intel 288V：https://www.intel.com/content/www/us/en/products/sku/240961/intel-core-ultra-9-processor-288v-12m-cache-up-to-5-10-ghz/specifications.html
- SSD 几何沿用 SFF-TA-1006 Rev 2.0：https://members.snia.org/document/dl/26956
