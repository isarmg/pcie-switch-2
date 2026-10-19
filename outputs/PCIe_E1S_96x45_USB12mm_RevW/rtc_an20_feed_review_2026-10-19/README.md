# U702 输出至 CPU AN20 的有限 RTC 直流供电修复

基线 PCB SHA256：a34e841f2a74863e0b9467dd5d36f4acfa343592357ff8cc5074abcd419b4a30。
最终候选 SHA256：f7a11f8395f89a8cf62539c9f4f2b3c7325e8fc8373e40ed50a71f843a32ea32。
项目 SHA256：9086611e035a0210cfc1bdfb30769d78d36880dd96954c8f5b869291103f8f30。

## 修改与实际连通
仅新增23段B面CPU_VCCRTC铜，17.356726mm；零新孔、零迁件、零旧铜删除/改变。终点直接到C708.1中心，23段构成连续无分支链。
U702.5、C708.1、U502.AN20原生确认同簇。CPU_VCCRTC由6簇降至5簇；C917、C918、R710、R711仍独立。全板仍98断网、95实装断网，minimum cluster joins为1758。
所有原FP/值/焊盘/NC与旧铜不变；没有需要同步的placement/BOM/schematic字段。

## 官方依据、直流估算与限制
Intel官方829568-004.pdf内电气附件Power_Rail_DC_Specifications行166–169：VCCRTC典型1.5V，包含AC/DC/ripple的总容差±5%，最大2mA，G3最大6µA。附件注1说明数据来自估计/仿真/经验，待后续硅片表征；其余测量说明完整保存在OFFICIAL_EVIDENCE.json，不将2mA改写成实测保证。Ballout原附件确认AN20=VCCRTC。
官方PDF、附件SHA及精确行见OFFICIAL_EVIDENCE.json；厂商PDF/XLS不入仓库。

新线宽度：0.15mm共3.323032mm、0.10mm共5.077984mm、0.075mm共8.955709mm。窄段受真实BGA/局部间隙限制，外侧已有可行加宽。
按铜电阻率1.724e-8Ωm、假设成品铜厚18µm：R=ΣρL/(wt)=0.184222Ω，2mA时压降0.368443mV；按铜温度系数0.00393/°C升至85°C约0.46256mV。铜厚未获板厂确认，此估算不包含地返回电阻、LDO精度、封装接触、负载瞬态或AC阻抗。

走线绕开Y701/Y702的完整courtyard，并在搜索时增加0.1mm边界，不穿晶体下方。独立原生核得新铜缘到Y701 courtyard最小距离0.13943mm。没有移动或接通晶体负载、CT/SS或其它LDO。
新铜投影全部被In28 GND覆盖；相邻In30是AUX电源面，其原有孔避空在新线投影下仍有约0.1246mm²缺口，不能称作紧邻完整GND参考。精确面积见NEW_REFERENCE.json。全部原zone定义和填铜token逐字相同，未新增任何power/GND平面损失。
U702.2/C707.2/C708.2与CPU邻近AM18/AN17地球在同一原生主地簇。原有In28–B地孔保持；In28地面从LDO原锚(65.1375,42.225)到AM18地孔(58.631999,30.6768)存在13.254526mm连续中心线路径示例，见GROUND_PLANE_PATHS.json。这不是唯一返回电流路径或环路电感模型，原深孔工艺仍未经厂家认证。

C708到AN20新供电路径仍约17.36mm，不是近CPU旁路。尚未完成AN20近端电容、真实MLCC有效容量证明、瞬态PDN、CPU电源源头/释放时序或完整RTC启动验证。本包只闭合真实DC负载路径。

## 门禁与重放
DRC.json：零error、零schematic parity差异，仅原In23 sliver警告。
INDEPENDENT_REGRESSION.json：全部6626原物理pad含NC、旧簇、存留铜net保持。
ALL_PLANE.json / PAD_INPUT.json / PAD.json：所有power/GND原track及功能pad投影零新增命中。
VERIFICATION.json：新UUID预期净名、原生负载与地簇、断网计数。
DELTA.json：源/pro hash、23新增精确块及全部原生FP/铜/zone预期token守卫。
用KiCad10 Python执行replay.py EXACT_SOURCE_PROJECT_DIR NEW_PROJECT_DIR；完整项目先复制，再加载/填铜；目标目录须不存在。replay.log记录独立重放结果。

早期只读筛查曾把B铜假想成会挖In30的避空，已撤回该过度保守限制；B层新线无孔不会在另一层挖铜。最终以实际全部zone/fill不变和原生完整门禁为准，不把无路的筛查误报成真实板级阻塞。

## 发布者独立验收
源提交519d37743eab16d22742a2bb6d2a78d537030b0e。重新核读官方Intel PDF及下载附件1.5V/2mA原始行。独立原生全门禁通过：DRC0几何错误/1旧sliver/parity0，ERC仍43错误/212警告，全部旧pad/NC/铜簇/net、全plane与前后功能pad投影通过。FP和全部zone填充/规则块精确不变。完整守卫重放输出PCB字节一致；状态文件更新真实AN20连通及1758joins，其余设计文件未改。

独立新铜检查确认23段全属CPU_VCCRTC、连续无分支链、0孔；真实端簇包含U702.5/C708.1/U502.AN20。Y701铜缘到庭院包围框最小0.13943mm；不等于模拟串扰资格。独立native串联铜估算18µm/20℃为0.184221714Ω、2mA降0.368443mV。同原生地簇和In28连续几何中心线路径已分别检查，不能据此签核实际返回阻抗。

本批可接受为有限DC路径闭合，AN20近端旁路、真实有效C、动态PDN、源电源及时序仍待完成，不能称RTC系统启动合格。STEP及预览仍历史。完整重放入口 scripts/revW/rtc_an20_feed/replay_full.py EXACT_SOURCE_REVW_DIR NEW_REVW_DIR。
