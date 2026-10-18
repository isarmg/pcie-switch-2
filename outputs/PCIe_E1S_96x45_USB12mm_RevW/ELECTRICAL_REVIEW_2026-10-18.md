# Rev W 电气与布线复核（2026-10-18）

本版本仍是不能生产或上电的工程草案。最终检查以本目录最新原生检查报告的源文件 SHA-256 为准；旧 `VALIDATION.json`、`POWER_CONNECTIVITY.json`、STEP 和图片不能替代对修改后文件的复核。

## 已实施的电路纠错

### U605 复位输入电平

原 U605 TPS3808G09 的 VDD 为 3.3 V，而 MR 直接接 CPU 的 1.8 V PERST。TPS3808 的 MR 高阈值为 0.7×VDD，因此 1.8 V 不能保证被识别为高。

最终方案保留 U605 的 3.3 V 辅助电源；MR 改接独立 U511 SN74AXC1T45 的 3.3 V B 输出，并加 R9040（10 kΩ，1%）到地。该输出虽沿用 `TBT_PCIE_PERST_3V3_N` 网名，源头是 CPU PERST 的独立电平转换，未经过 Thunderbolt 控制器或其复位状态机。C9040（100 nF）就近去耦。原理图/PCB 网络归属和局部下拉已同步，但 U605 MR 到 U511 的长支线仍未布通：普通贯孔候选违反 0.4 mm 板边规则，移位则与既有铜冲突，已从主板撤回。必须重新布局/布线后才具备预期复位功能，不能把逻辑修正当作可运行电路。

10 kΩ 下拉用于在 U511 隔离时对抗 U605 内部上拉。仍不能宣称完整复位时序合格：AXC 的完全掉电隔离条件、棕断电过渡、U501 L4 的内部上下拉/漏电/箝位、CPU PERST 的实际 VOH/VOL、辅助电源与 PEX 电源时序都需要真实芯片资料和实测。AXC 的 VCCA<0.1 V 才保证隔离，0.1–0.65 V 过渡未保证；在 3.6 V、U605 内部上拉最小 70 kΩ、AXC Ioff 最大 7.5 µA 条件下，10 kΩ 下拉估算 MR≤0.516 V，但尚未计入未知 U501 L4 漏电。CPU 动态电源尚未实现。

- [TI TPS3808，§5、§6.3/6.5、§7.4.3](https://www.ti.com/lit/ds/symlink/tps3808.pdf)
- [TI SN74AXC1T45，引脚、输出驱动和隔离条件](https://www.ti.com/lit/ds/symlink/sn74axc1t45.pdf)

### 电气符号不再全部被视作被动引脚

根据官方引脚功能表补充 U901/TPS548D22、U902/TPSM63610、U605/TPS3808 以及已固定方向的 U511/U512 的名称和电气类型。并联输出的一个端子标为电源输出，其余同一器件并联端子保留被动类型，避免虚构多个驱动器冲突；bootstrap 等模拟端子没有伪装成直流电源源头。其他未建模器件仍存在被动占位引脚，ERC 不能代替完整电路审查。

- [TI TPS548D22，§5 引脚功能](https://www.ti.com/lit/ds/symlink/tps548d22.pdf)
- [TI TPSM63610，§5 引脚功能](https://www.ti.com/lit/ds/symlink/tpsm63610.pdf)

## 原生一致性修正

KiCad 的显示网名 `/GND` 与内部网名 `{slash}GND` 不同。旧 XML 网表检查只对显示名称，掩盖了原生 schematic parity 的差异。现在用刚由 KiCad 导出的 `kicadsexpr` 网表，按全部 `(ref,pin)` 双向匹配；仅在映射不分裂、不合并旧网络的前提下改内部名称，不改铜线所属 netcode。自动生成的未连接网也由原生网表决定，未通过删除 NC 或关闭检查来消除问题。

已有厂家链接同步保留在 PCB/原理图/元数据。网类必须在保存并重新加载后逐网检查，不能相信改名对象的旧缓存。`w_verify_eco.py` 检查实际匹配的 PCIe/REFCLK 网类。

## 布线改善与未解决问题

- USB2 TOP 已由原 22 段跨层长绕行改为 10 段同 In27 层短路径：P=11.567977 mm，N=11.636791 mm，几何差从约 137.808 mm 降至 0.068814 mm。修改前后原生全 track DRC 均为 0 几何错误、1 处既有铜毛刺警告。即使几何长度差很小，参考平面割裂、阻抗、过孔残桩和电气时延仍未签核。
- 原始记录中 S10_RX0 的 P/N 长度差约 152.60 mm，其他 PCIe/TB 差分网络也存在跨层、失配。仍有 141 个 P/N 分层段，不能用局部 USB2 修正代表全板 SI 完成。
- 全 pad 原生审计揭示旧供电报告只抽样 `pad_stitches`，2915 行中只有 2616 个唯一 `ref.pin`，并漏掉许多 GND 脚。新审计逐个原生 pad、利用真实填铜连通簇，不把重复记录计成独立覆盖。本轮 6624 个实际 pad 形状对应 6558 个唯一 ref.pin；最终断裂网络数见 NATIVE_ALL_PAD_AUDIT.json。
- 接地改进采用 6 个 F–In1 相邻层孔及 U701.4/Y501.2 的 2 个 0.45/0.25 mm 普通贯孔；98 个跨三层 0.20/0.10 mm 盲孔保留在 `DEFERRED_GROUND_CANDIDATES.json`，未为了清零未连数而并入主板。8 个新增目标 pad 已逐个验证实际接入输入地所在主簇；包括局部 U605 修复后，GND 簇从原 156 降至 147。
- 32 层仅有总厚度 1.6 mm，没有可制造的材料/铜厚/介质厚度叠层；已有盲孔、局部新增相邻孔及局部电路接地孔仍须板厂确认。DRC 几何通过不意味着孔结构可生产。

## 阻塞真实硬件完成的资料

1. 真实 switch 型号、授权球位/封装、供电时序、strap、管理接口及参考设计。当前 PEX90064 球位是虚构，不可用于真实贴片，也不能凭类似芯片推导真实 ball map。
2. CPU 288V 完整电源设计资料、实际 PMIC/VR 配置与 OTP、时序、BIOS/启动链。
3. 完整 Alpine Ridge/TPS65982 电源、NVM/固件、引脚电气和掉电行为资料。
4. 可采购连接器及机械图、额定电流、SSD 安装/散热方案；USB-C 自定义供电仍与主输入隔离。
5. 板厂确认的 32 层叠层、过孔类型/深度、阻抗目标、PCIe/TB 通道预算及热/电源完整性分析。

## 可复现检查

在具有 KiCad 10 的 Python 环境中运行 `scripts/revW/w_native_audit.py` 和 `w_verify_eco.py`。运行 `w_native_review.py --kicad-cli <CLI命令> --output-dir <全新报告目录> --pad-audit <本目录/NATIVE_ALL_PAD_AUDIT.json>` 可生成新 ERC、含 schematic parity 的 DRC、源哈希和诚实的阻塞状态。

`w_schematic.py` 已去除其自身的 Windows 路径/历史 work 缓存依赖，可在指定副本上重新生成原理图；它会更新 UUID，因此必须再导出原生网表和检查 parity。其他历史全板构建/自动布线脚本仍依赖旧工作资料，不能当作跨平台的一键完整构建。

## 最终原生结果

KiCad 10.0.7 独立验收：几何 DRC 0 error、1 个既有 In23 铜毛刺 warning；schematic parity 0。原生未连报告 499（可能截断）；全 pad 审计 107 个断裂网络。ERC 43 error、212 warning，保留真实缺失驱动和孤立标签，不通过 PWR_FLAG 或排除项隐藏。审查期间所有原生源哈希保持不变。报告：`review_2026-10-18/final_native/REVIEW.json`。

复位链额外断点：最终全 pad 审计中，`PEX_SYS_RESET_N` 有 3 个物理簇、`PEX_RESET_CT` 有 2 个物理簇、`TBT_PCIE_PERST_3V3_N` 有 2 个物理簇。除了新增 MR 长支线待布，原有 RESET 输出和 CT 定时路径也未闭合，需整条复位链重新布线验证。

ERC 从历史 42 error 到 43 error 的净新增项是 U901.21 PVIN（VBANK_B）缺少 power_out 驱动：此前被动占位类型漏检，本轮按 TPS548D22 真实电源输入类型揭示。P3V3_AUX 的既有未驱动错误仅代表节点由 U702.1 改为 U511.6；24 个普通 input 未驱动数未变。没有添加 PWR_FLAG 来掩盖外部电源模型与实际供电验证的缺口。
