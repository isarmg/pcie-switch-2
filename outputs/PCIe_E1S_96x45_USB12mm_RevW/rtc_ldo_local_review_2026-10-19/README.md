# RTC LDO 局部旁路修复

冻结源：b55f4d1574bd326f3ed2427b97d6bebb1b297bc1adcbcb14b81572643d5e2d61。
候选：a34e841f2a74863e0b9467dd5d36f4acfa343592357ff8cc5074abcd419b4a30。
正式同名项目 SHA256：9086611e035a0210cfc1bdfb30769d78d36880dd96954c8f5b869291103f8f30，LoadBoard / refill 前已复制。

## 实际修改
U702、C707、C708重新组成 B 面局部 IN/OUT 旁路。R5191仅向下移动0.14mm，仍直接搭接两个原有孔，没有新增CLKREQ铜线。13段新B铜，0新孔。仅删除旧U702.EN和旧C707.IN的两个专用AUX孔，精确UUID及无共享铜支路证明见 DELETION_PROOF.json。原C707地孔及C702共享地枝、U702原IN/地锚、R5191两孔全部保留。

四件位置、角度的旧值/新值与三份权威metadata字段见 METADATA_CHANGES.json；所有值、net、pad UUID、型号保持。原生保存另外归一化C5112/13/14三个FP属性排列并显式补默认字体thickness=0.15，故总计7个FP文本块变化。NATIVE_NORMALIZATION.json逐块证明其全部子项在忽略排列和该默认值后完全相同，包括属性name/value、隐藏、位置、层、模型和pad几何；这三件没有布局或电气变更。

## 本地路径与限制
IN至C707.1为1.268377mm，宽0.15mm；C707地返回U702.2为3.0825mm，宽0.15mm，本地回路长度4.350877mm。
OUT至C708.1为1.757501mm，宽0.15mm；C708地返回U702.2为4.0225mm，宽0.15mm，本地回路长度5.780001mm。
原AUX锚经EN至IN支路4.21mm、宽0.1mm。所有新AUX/RTC铜在相邻In30 AUX面投影完整；NEW_REFERENCE.json另列更远In28地面投影，不能替代实际邻层参考。所有旧电源/地plane的旧track与输入、输出功能pad投影均无新增损失。

U702 IN/EN及C707真实接原AUX簇；C707/C708/U702地真实接原主地。U702.5与C708.1闭合，但CPU_VCCRTC仍6簇，U502.AN20仍单独孤立；本包只完成LDO局部旁路。CPU_VCCRTC从7降至6簇，GND从133降至132簇；98断网、95实装断网。

TI官方TPS7A02 RevC资料的页码、下载地址和文件hash见 OFFICIAL_EVIDENCE.json：DBV引脚匹配；CIN建议1µF，COUT有效值至少0.5µF、降额后不超过22µF，要求近器件。现C707/C708保留名义1µF，尚无已核真实MPN与DC偏压/温度/容差有效容量证明，不能作为完整稳压稳定性或RTC启动签核。晶体、CPU供电时序和AN20负载供电不在本包。

## 验证与重放
DRC.json：0错误、0parity差异，仅既有In23 sliver警告。
INDEPENDENT_REGRESSION.json：6626原物理pad含NC、旧簇与存留铜net全部保持。
ALL_PLANE.json、PAD_INPUT.json、PAD.json：全部旧track及功能pad投影0新增命中。
DELTA.json：精确源与pro hash、2删除、7替换、13新增、预期全部原生对象token hash与新旧铜net守卫。
使用KiCad10 Python执行：replay.py EXACT_SOURCE_PROJECT_DIR NEW_PROJECT_DIR。目标目录必须不存在。完整项目先复制再加载/填铜；replay.log记录全部FP/铜/zone原生块一致。文件顺序可能变化，不要求重放文件byte hash相同。

原厂PDF不入仓库。

## 发布者独立验收
源提交 8e7bbf4c528212ae1e67584769f0a403afabe061。独立重跑官方 KiCad10 原生 DRC（0几何错误/1旧sliver/parity0）、ERC（旧43错误/212警告）、全6626旧pad含NC、旧铜簇与存留net守卫、全部旧参考面和前后功能pad投影，均无回退。独立复核三颗真实MLCC属性归一化等价；其选型内容/隐藏/位置/层/模型保持。TI官方链接及DBV引脚/有效C要求已重新查阅。

四件位置/层/角在 COMPONENTS、BOM、PLACEMENT_PLAN 同步，ROUTING_STATUS 使用新板hash及实测98断网/95实装断网、minimumjoins1759、GND132。旧STEP/预览保持历史状态。C707/C708/U702地同1894物理pad主地簇；OUT+C708.1仅两个pad，U502.AN20仍孤立，未声称RTC启动实现。R5191两原孔与原CLKREQ连接保留。局部0.1mm AUX支线/共享地路径未通过电流、瞬态、噪声或热实测资格。

完整发布重放：scripts/revW/rtc_ldo_local/replay_full.py EXACT_SOURCE_REVW_DIR NEW_REVW_DIR。发布者实测输出PCB字节hash与候选完全一致，同时守卫重放四份元数据文件。原生DRC未连项目499为上限，不是全网统计。
