# U606 Flash本地回地与CS静态偏置恢复，2026-10-19

本次集成：新增R9041 10k±1%及9段B.Cu线，共0新孔、0旧器件移动、0旧铜删除/改网。不含被拒的C9044或任何新增旁路电容。本报告随正式工程与可重放脚本一并提交。

基线commit4a5e0687a41fd2ed114786b1f9562942d5f4b43f，PCB19d8c4acb0864a77939dd64220e8a3c99aa1bc40799fd65ac28729134a9c4aae；正式pro9086611e035a0210cfc1bdfb30769d78d36880dd96954c8f5b869291103f8f30。
候选Candidate/Main_12E1S.kicad_pcb SHA d00db6176ae27151f5d08b64233ef289fe29c3ec41095fc2a38e91462fe26e44。

## 当前源事实与修复
SOURCE.json重新读取当前源，未引用丢失候选的通过声明。U606.1 CS和U606.4 GND原本各为单pad簇。U606.8 VCC则已经在PEX_1V8 DC源簇，包含U902.5/.9/.10及C9023/24/25/28等，不能称为未接电。原GND孤岛是输入状态，不是本次改动导致。

- R9041在B(39.3,39.4)，90°，Local:R_0402_1005Metric，标准0402。Value为“10k 1% / PEX flash CS pull-up”。pin1在(39.3,39.91)，PEX_SPI_CS_N；pin2在(39.3,38.89)，PEX_1V8。CS新增3.694999mm，供电静态偏置支路11.315001mm，均宽0.1524mm。
- U606.4(40.924999,37.77)用一根B0.1524mm、长2.645681mm地线接既有(42.56,35.69)地via/U502.DH1。锚点via UUID2ae5acec-1bae-4dc1-adef-6828706a0c3f，原已有1882物理地pad簇，完全未改。保留的In28–B深孔不能据本次审查宣称工艺可制造；没有新增盲孔、微孔或普通孔。
- 修复后U606.4加入既有主地簇。CS簇为U606.1+R9041.1；U1.AJ32仍单独，其他Flash SPI信号也未布通。不能称SPI通路或整机启动完成。

## 官方依据与静态预算
本次直接重新下载Winbond W25Q32JW SPI RevisionI，2026-04-27：
https://www.winbond.com/resource-files/W25Q32JW%20SPI%20RevI%2004272026%20Plus.pdf
厂商PDF仅用于独立研究，未随本批复制。

PDF p6/9/12/58/59/61/67/75：SSIQ为208mil SOIC8，VCC1.7–1.95V；pin1/4/8分别CS/GND/VCC。CS在上电及掉电应跟随自身VCC；tVSL至少20µs，写入等待tPUW至少5ms。输入漏电±2µA，VIH至少0.7VCC。

10k±1%仅计算Flash当前隔离CS输入：在1.7V、2µA和10.1kΩ时，电阻压降20.2mV，VCS≥1.6798V，相对VIH1.19V静态余量489.8mV。这不包括未来接入U1后的未知漏电或驱动。新增上拉不是电源斜率、掉电、时序、镜像或运行资格证明。

Native封装本体5.3×5.3mm；pad行距7.000002mm、pitch1.27mm，旋转焊盘长轴1.5mm沿引脚方向，外跨约8.5mm。与官方SS nominal5.28×5.28mm、leadspan7.70–8.10mm包族相符，非150mil本体错配；没有自动获得IPC焊盘/组装认证。

本地去耦仍待优化。电源上已有远端电容；最接近的同网C9028在约34.44mm外，不能替代已验证本地高频旁路。未混入此前没有动态改善依据的长绕线100nF。

## 门禁和源同步
- KiCad10.0.7正式同名pro在LoadBoard和refill前就位。DRC全部track检查零几何error；仅原In23 sliver警告。499未连条目仍为报告上限，非精确全板未连总数。
- PARITY_DRC零parity问题。新增Connectivity_56/Local symbol，COMPONENTS与BOM同步，官方freshXML导出证明6558旧ref.pin逻辑映射完全保留，仅新增R9041两端。
- REGRESSION包含所有原编号物理pad、包括NC；旧身份/净名/簇无退化。VERIFICATION另外审全部旧pad/track/via原簇及UUID净名；无删除、无拆分、无改网。
- DELTA校核全部旧footprint和铜token不变；所有新FP/铜的prefill与postfill意图一致。全部zone定义及边界不变。
- ALL_PLANE包含所有实际电源与地平面，填铜多边形完全不变；旧轨投影0新增参考损失。PAD_INPUT/PAD分别对原/新功能pad审查，均0hits。该增量结果不代表SI/PI资格。

## 可重放交接
DELTA.json携带精确基线/pro、新器件/铜块、全体期望铜净名和所有FP/copper/zone token哈希。SOURCE_DELTA.json携带明确改变的六个项目源文件（含PIN_MAP）前后哈希与内容。BOM.csv与PLACEMENT_PLAN.json为候选表；唯一writer按FILE_GUARDS.json核各文件精确基线后合入，BOM另有BOM_PROOF.json。

使用KiCad10 Python：replay.py EXACT_SOURCE_PROJECT_DIR NEW_PROJECT_DIR。脚本拒绝源PCB/pro不匹配、已存在输出、源文件哈希不匹配；复制完整正式项目，追加新铜与器件，同步明确源文件，原生refill并核所有native块token。集成若叠加其他候选，唯一writer需重跑全门禁并刷新正式原理图netlist与状态/预览。

本小批只恢复一个真实地连接及Flash侧闲置电平。U1真实ballmap、完整SPI、Flash镜像、电源动态/时序、本地旁路和整机启动均未认证。

最终replay-final.log确认重放13451个native块完全一致，且重放PCB文件SHA与候选逐字一致。最终精确源文件守卫为FILE_GUARDS.json，共9项。

## 独立审核后的原理图网格修正
独立writer发现新sheet初版有一项endpoint_off_grid警告，未按baseline隐藏。仅将新R9041符号中心移到原理图(80.01,60.96)，对应pin1(64.77,60.96)、pin2(95.25,60.96)，全部落1.27mm连接网格，符号/label UUID及网络保持。正式重新导出CONNECTIVITY.net，6560逻辑节点完全相同；PCB仍d00db617…完全未变。GRID_ERC.json为43error/212warning，与既有计数一致；GRID_PARITY_DRC.json的parity仍0。SOURCE_DELTA和FILE_GUARDS已绑定修正后新sheet及XML哈希；具体记录GRID_FIX_PROOF.json。原有ERC问题并未被本小批修复，不得称整板ERC通过。

## 发布独立复核
从精确 4a5e068 基线完整重放 PCB、六项项目源文件、BOM、位置表及状态，PCB SHA 逐字相同。发布者最终原生复查 FINAL_DRC 为0几何错误、1项既有sliver，parity0；FINAL_ERC 为43错误/212警告，新增网格警告已修复。独立fresh导出6560逻辑节点与正式 CONNECTIVITY 完全一致。原有6558节点保留，仅新增R9041两端。

ROUTING_STATUS现绑定本次板SHA和实测计数：101个非NC断网、其中98个实装断网。旧STEP及预览未重新生成或验证，属于历史输出，不能作为当前板几何验收。未复验旧状态字段已移到 historical_unrevalidated_fields，原文件保留为 PREVIOUS_ROUTING_STATUS.json。

完整守卫重放入口：scripts/revW/flash_cs_ground/replay_full.py EXACT_SOURCE_REVW_DIR NEW_REVW_DIR，使用官方KiCad10 Python。
