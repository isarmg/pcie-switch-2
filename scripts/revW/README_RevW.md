# Rev W：按 CPU / switch 面调整 USB-C

> 2026-10-18 电气复核已更新源文件；下述旧检查数字为历史记录。请先看 [本轮电气复核](../../outputs/PCIe_E1S_96x45_USB12mm_RevW/ELECTRICAL_REVIEW_2026-10-18.md) 和最新原生报告，旧报告不能证明当前整板通过。

板框保持 **96 × 45 mm**。从 CPU / switch 面看，供电 USB-C 中心距左板边 **12 mm**，雷电 USB-C 中心距左板边 **24 mm**，两口中心距 **12 mm**，均位于板高 **22.5 mm**。两口保持竖直安装及贴片固定脚。主要顺序为左侧 USB-C、中部 CPU、右侧 switch。

KiCad 正面坐标与此视图的 X 方向相反：J401=(84,22.5)，J402=(72,22.5)，CPU=(54.5,22.5)，switch=(20,22.5)。CPU 中心距此视图左边 41.5 mm，switch 为 76 mm。

打开 `Main_12E1S/Main_12E1S.kicad_pro`。`USB_12mm_CPU_Switch_View.png` 给出中心尺寸，`Main_12E1S/bottom.png` 是本机 KiCad 的 CPU / switch 面三维预览，`Main_12E1S/Main_12E1S.step` 为原生导出模型。

保留 12 个竖直 E1.S、8 mm 中心距和插入后名义侧边距 7.25 mm；无 M.2、小板、安装孔或连接器定位孔，未装入 SSD 三维模型。原连接器模型带下伸结构，移除板孔的草案仍需要最终连接器机械方案。CPU 为 Ultra 9 288V / 32GB；switch 仍为经授权虚构的 PEX90064，33 × 33 mm、1024 个球位，不能用于真实芯片贴装。

## 本次供电进展

保留原 12 V 输入及 12 路 SSD eFuse，每槽 25 W、共 300 W；J101/J102 是来自同一稳压 12 V 电源的两组正负焊线输入，各按 20 A 作预算。自定义供电 USB-C 继续与主输入隔离，尚无可核实的大电流接插件额定值。不能把它当作已完成的 300 W USB 输入。

新增 switch 参考电源来自 PEX88096 资料的保守电流预算，未因虚构芯片删减 lane 而缩小容量：0.9 V 域参考电流 37.427 A，1.8 V 域参考电流 6.903 A。0.9004 V 使用 TPS548D22RVFR（40 A IC），1.8 V 使用 TPSM63610RDFR（8 A IC）；两组模拟域经独立低 DCR 电感滤波，保持原四组电源网络。

TPS548D22 按 650 kHz / FCCM / DCAP3 / 2 ms 软启动配置，FSEL、VSEL、MODE 均包含必需的 BP 端 100 kΩ 上拉，低端分别 22.1 kΩ、33.2 kΩ、47.5 kΩ；ILIM 137 kΩ。输入欠压分压 100 kΩ / 18.2 kΩ，名义启动约 10.39 V。0.16 µH 主电感 XAL7070-161MEC 高 7 mm，位于连接器面；它的温升额定值和实板散热仍需验证。低 DCR 模拟滤波电感采用 XEL4020-101MEC 参考。

1.8 V 模块使用 100 kΩ / 125 kΩ 反馈、100 pF 前馈，400 kHz、强制 PWM、关闭扩频，RBOOT/CBOOT 间为 100 Ω。输出配置 2 × 220 µF 聚合物及 47 µF 陶瓷，实际有效电容须满足 TI 的 350 µF 下限并完成环路、启动和负载瞬态验证。封装依据所附 TI RDF0022A 图绘制，保留端部焊盘的缺口和非等距位置。

In5/In6 保留为两组 12 V 母线专用层；In19/In22 为 switch 0.9 V / 模拟 0.9 V，In4/In7 为 1.8 V / 模拟 1.8 V 专用层。32 层、盲孔和铜厚仍是假定叠层。IC 标称电流及布线连通不等于 PCB、过孔、电源线或接插件已达到额定载流量。

内层示意信号线使用 0.08–0.10 mm 临时宽度；高速差分线尚未按真实叠层完成阻抗、耦合、长度、损耗与过孔优化。部分 P/N 位于不同内层，连通验证不表示达到 PCIe 或雷电电气要求。

In3 另外保留给两组 12 V 输入分区，In2/In30 保留给 3.3 V 辅助电源。槽位及辅助电源的跨层连接完成的是铜箔连通示意；密集区部分铜岛连接以 0.10 mm 细颈接入较宽主线，不能据此认定达到每槽 25 W。仍需依据实板铜厚、温升和压降重新调整这些走线、过孔及供电平面。

## 保留的限制

根据用户选择，CPU 保留真实 200V 系列球位与电源域，未虚构 PMIC 引脚。RAA225019 公开短资料不足以实现完整球位、OTP 和动态电源配置，CPU 动态供电、时序、BIOS 及启动设计仍待完成。

雷电 USB-C 电路沿用用户先前选择的 **雷电 3 主机口**（Alpine Ridge DP + TPS65982），本次没有升级到雷电 4。控制器其余内部电源分配、固件、NVM 和兼容性仍待核实。不得因位置要求中使用“雷电4”称呼便认定已有 TB4 功能。

`VALIDATION.json`、`USB_POSITION_VERIFICATION.json` 和 `POWER_CONNECTIVITY.json` 记录本次真实检查结果。已实现网络的连通和 STEP 导出检查通过。KiCad 几何 DRC 无错误，仍有一项 In23.Cu 铜箔毛刺警告；原始报告保留在 `Main_12E1S/DRC.json`。未接线清单仍包含 CPU 等未完成电路，报告可能达到工具的显示上限。以上检查不能替代完整电气设计、PCIe 信号完整性、热设计、电源完整性或制造审核。该工程是布局及布线草案，尚不能直接生产、上电或认定能启动。

供电器件资料：

- [TI TPS548D22](https://www.ti.com/lit/ds/symlink/tps548d22.pdf)
- [TI TPSM63610](https://www.ti.com/lit/ds/symlink/tpsm63610.pdf)
- [Coilcraft XAL7070](https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xal/xal7070/)
- [Coilcraft XEL4020](https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xel/xel4020/)
- [Renesas RAA225019 公开短资料](https://www.renesas.com/en/document/sds/raa225019-short-form-datasheet)

## 2026-10-18 可复现工具

- `w_power_models.py`：有依据的电源/复位电气引脚模型。
- `w_reset_repair.py`：U605 常供 3.3 V、U511 译码输出、R9040 下拉和 C9040 去耦。
- `w_apply_reset_route.py`：已拒绝的 MR 普通贯孔候选；入口阻止应用，保留失败证据。
- `w_apply_usb2_pair.py`：严格 UUID 校验后的 USB2 同层几何修正。
- `w_apply_adjacent_ground.py` / `apply_through_patch.py`：仅六个相邻孔和两个普通贯孔。
- `w_sync_native_names.py`：从最新官方 sexpr 网表安全同步内部名。
- `w_native_audit.py` / `w_verify_eco.py` / `w_native_review.py`：全 pad、ECO、原生 ERC/DRC/parity 验证。

新增脚本不替代缺失的 CPU 电源、真实 switch 球位和制造叠层。旧全板流水线仍含历史路径依赖。
