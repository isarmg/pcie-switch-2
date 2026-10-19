# C5112/C5113/C5114 实际设计料号选定，待资格验证

基线693d19bdde0f9183e9e9af15c1ec057f321d71c1，源板a501903278d07b19a431bb5bfb35a8012abc06ce05154d7c82ad7a32a5abfe19。

三颗选定Murata GRM155Z71A225KE44D：0402、2.2µF±10%、10V、X7R(MURATA Z7)。D为包装后缀，不代表另一个电性能等级。本批为设计料号填充，没有采购或硬件验证。

值、MPN、厂家、额定电压、容差、材质、最大高度及datasheet同步到PCB隐藏属性、原理图实例/缓存、Local库、COMPONENTS、BOM和重新导出的逻辑网表。BOM新增字段，其余器件已有字段保持。位置、pad/net/UUID、所有旧铜、填铜和模型完全未改。

## 原厂依据及未关闭条件

[当前Murata规格](https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM155Z71A225KE44-01A.pdf)给出外形1.0±0.2×0.5±0.2×0.5±0.2mm，因此高度按最大0.7mm更新，不能继续沿用generic0.6mm。现有7.25mm机械记录是板面内距离，不能当Z余量；未找到此区域明确0.6mm硬限，但没有因此签核新最大外形的装配间隙。原通用0402模型未缩放、未更换，仍不是该料号最大外形模型。旧STEP/预览不作为新料号机械证据。

[官方典型特性](https://ds.murata.com/simserve/characteristics?ReqType=TechPDF&partnumber=GRM155Z71A225KE44&ModeType=&techpdfname=technical_pdf_Capacitor01&lang=en)只用于优先级筛查。图读DC1.9V约损失11–14%，1.2V约4–7%，测量激励1Vrms；实际低纹波可能不同。不得将DC、AC和温度独立曲线相乘当联合保证。

详细规格温变计算的分母是25°C无偏压容量，且所给温度条件施加5V；不能对偏压后剩余容量乘0.85，也不能自动外推为1.2V/1.9V的保证。初始±10%和老化注意事项不能替代实际温度、偏压、小信号、寿命联合上下界。没有计算或宣称最差有效C合格。

[TI TPS65982 RevE](https://www.ti.com/lit/ds/symlink/tps65982.pdf)要求A/D有效容量至少0.5µF、BMC至少1µF，最大分别12/12/4µF，额定至少4V。三路现选2.2µF10V仅满足公称选择方向；有效C、ESR、瞬态、共享回流和系统稳定性继续待验。不能称所有PD供电完成。

## 独立验证和重放

原生KiCad10 DRC几何0错误、1项既有sliver；parity0；ERC保持43错误/212警告。旧6626编号物理pad含NC、铜簇和net回归通过。6560逻辑ref.pin节点全部不变，fresh导出核实新MPN和值。原生板块逐字检查证明仅3FP属性变化；其余pad、图形、位置、zone、铜和模型不变。没有重填铜或生成新STEP。状态仍98断网/95实装断网、GND133、最少join1761。

scripts/revW/ldo_mlcc_selection/replay.py EXACT_SOURCE_REVW_DIR NEW_REVW_DIR按整文件SHA和精确字节替换范围重放，不序列化几何。每个输出SHA均守卫并独立实际重放。

同批归档VOUT有限尝试的拒绝报告及复现脚本，失败PCB未进入工程；独立复现7真实几何错误，后续接受门禁未声称通过。
