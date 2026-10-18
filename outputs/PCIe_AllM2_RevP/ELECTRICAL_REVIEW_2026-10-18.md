# Rev P 电气修复记录

## 检查点 1：同步与局部复位偏置

目的：补完上次暂停的四个端部槽位下拉，恢复 PCB/原理图原生一致性，修复错误网类和被动化 ERC 模型。工程仍是未完成的硬件草案，不可生产或上电。

实际变更：新增 4 个 100 kΩ 电阻、16 个相邻层微孔、20 段铜线；保留其余器件位置、连接器、CPU/switch 球位及全部 510 个原有铜对象。元数据、原理图、PCB、BOM、逐脚表、网表现已同步。网名变更按每个 ref.pin 的官方导出关系逐项检查一一对应，没有合并、拆分或猜接网络。

检查点结果：647 个器件；0 几何 DRC 项，0 native parity 项，47 ERC 错误、104 警告；全焊盘检查有 749 个断网。原生 DRC 499 条未连线已截断。继承的五项忽略规则见原始报告，未增加或放宽规则。4 个下拉只有连接器本地地闭环，尚未达到输入地，因此还不是可用的复位系统。

## 可重跑命令

需要 KiCad 10 的 Python（pcbnew）和 kicad-cli。读取和检查脚本均以仓库根目录自动定位，不依赖 Windows 历史工作路径。

- p_electrical_audit.py --output PATH：标准 Python，核对 PCB、元数据、导出网表、lane/AC/时钟/模块 DNC 分配；并非布线验证。
- p_native_audit.py --output PATH：KiCad Python，全编号焊盘的实际连通簇，不使用 DRC 截断列表。
- p_native_review.py --kicad-cli "PATH/AppRun kicad-cli" --output-dir NEW_DIR --pad-audit PATH：原生 ERC、DRC、parity 与前后源哈希；有报告发现时返回 2，工具/输入失败返回 3。
- p_verify_eco.py --baseline BASELINE_BOARD --output PATH：KiCad Python，4 组局部下拉、真实网类及旧铜 UUID/几何/归属回归。

p_add_reset_bias.py 是一次性、可重复调用不重复添加的四下拉 ECO。p_power_models.py、p_sync_metadata.py、p_sync_native_names.py 是受控增量修复，顺序及输入必须先审查，不能替代最终检查。原历史 p_build/p_pipeline 没有包含全部增量修复且依赖未提交原始资料，禁止把其重新生成结果当当前源。

## 公开依据

- [TI TPS6213x SLVSAG7F，表 6-1](https://www.ti.com/lit/ds/symlink/tps62132.pdf)：SW/PG/控制脚/电源和地的引脚功能。TPS62132 为固定 3.3 V 版本。
- [TI TPS565201 SLVSE71](https://www.ti.com/lit/ds/symlink/tps565201.pdf)：VBST 为浮动自举电源，不是独立输出电源。
- [TI TPS3808](https://www.ti.com/lit/ds/symlink/tps3808.pdf)：MR 输入高阈值相对 VDD，1.8 V 与 3.3 V 域问题仍未修复。
- [TI TPSM53604 SNVSBC9C](https://www.ti.com/lit/ds/symlink/tpsm53604.pdf)：DNC4/5 必须不接；7/8 为并联输出；输出电容与布局仍需逐模块完成。

## 明确阻断项

749 个断网，包括输入返回、3.3 V 槽位功率回路；CPU PMIC/顺序、PEX rails、复位域与释放、控制器固件、20 槽数据线和时钟线、SI/阻抗、热、载流、机械实料及 HDI 工艺均没有完成。U607 I2C mux 及第三组时钟等已识别支持电路遗漏，但没有凭空补接真实芯片脚位。下一组只接收有原生验证和完整回归的局部电源候选。

## 附件时效

本检查点只交付当前可编辑源、必要本地库/模型、脚本及对应报告。历史 STEP/图片仍保留于仓库但未刷新，不作为最新几何证明。SHA256SUMS 是文件完整性记录，不是电气可用性认证。
