# 第三组：复位区域重布局与PLTRST上游

基线0083dece；候选c350871d495780568e12e64cd4d33fe8ec5ce248fe5f51ea87519bf3b767b92e。

U605及四个本地RC从左上拥挤区迁到B面约34,41mm，MR、CT、RESET真实闭合。CPU F24→U511.3→草案U1.AM32同域上游补接；CPU供电源与真实PEX输入负载仍未定义，不能据此声称启动完成。R725原10k外上拉与Intel公开GPIO附件所述电源过渡HiZ内部20k±30%下拉竞争，改为DNP，保留焊盘/网名/原阻值。正常主动输出不依赖此上拉；完整掉电/上电时序、AXC过渡区与未知负载仍待验证。

共迁5件、R725改装配状态，新增8普通通孔及2个B–In30相邻层逃线孔；原有14个失去用途的叶/孤立铜对象经精确依赖核查后移除，包括旧深盲孔。所有7118 pad shape身份保持；全编号pad含NC原簇及存留铜网无回退。孔型、叠层、盘中孔与机械未获制造签核。

本轮原生DRC0几何错误/1既有In23铜毛刺、parity0、ERC43错误212警告；104个非NC断网，最少1777次簇合并。R725信号焊盘成为有意DNP-only支路，不以清零统计为目标。

MR约49.3mm在In1地层，地铜损失15.709mm²必须保留为回流布局风险。已检其与全部旧F/In2轨迹投影无交集，F面功能信号焊盘也无实质交集；只涉及局部GND/NC机械pad及极小数值边缘。完整六地层及所有相邻层非GND直线铜增量见GROUND_REGION_DELTA.json：唯一旧CIO RX0 N投影约9.04e-9mm²、1/5/10µm敏感性均0，其余全部新增0且无遗漏arc；其余地层各约1.674mm²避空保持原始数据。二维投影无新增缺口不等于返回电感/辐射/SI已验证。

可重放入口：KiCad10 Python scripts/revW/w_apply_rebuild_reset.py SOURCE/Main_12E1S NEW/Main_12E1S。要求基线0083及同名正式项目，逐原块hash守卫；不改输入目录。随后用官方CLI重新导出kicadxml，并用w_refresh_native_netlist.py在全6558 ref.pin映射不变与全部Value/Footprint/DNP一致门禁下更新CONNECTIVITY.net缓存。此步同时更正历史缓存仍含旧U510类型和U607装配状态，真实原理图已在第二组修正。

所有原厂PDF/附件不随仓库分发；Intel官方来源和页/行证据见upstream及独立R725审查。
