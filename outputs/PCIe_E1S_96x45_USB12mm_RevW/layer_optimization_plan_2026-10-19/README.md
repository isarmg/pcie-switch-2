# E1.S 层数优化设计计划（尚未实施减层）

正式 PCB 仍为 32 层，源 SHA256 `e33bc9bf7cb41045c3171abd07677bc36ebe7c3960d61349e4ad5ba2437ecb3c`。本批仅提交工程计划与可重放审查，不改板、不改网表、不声称 24 层 PCB 已完成。

## 当前建议

优先验证 **24 层 / 12 信号、8 地、4 电源** 的重新布局布线方案；20 层作为后续有量化余量时的候选。每个信号层都有相邻地，但 L6/7、L12/13、L18/19 相邻信号层的耦合仍须实际叠层与仿真核验。24 层是待验证起点，不是已证全局最优。

12 个 SSD 开关输出必须保持各自网络；共用物理电源层采用隔离铜岛/走廊，不合并电气输出。当前源仍有 97 个非 NC 断网、94 个涉及实装元件。真实器件球位、制造叠层、有效过孔结构及完整 SI/PI/热/机械验证未闭合。

- [中文完整计划](README.zh-CN.md)
- [机器可检查方案](layer_plan.json)
- [逐层现状与重构依据](REPORT.md)
- [制造与过孔独立审查](manufacturing/REPORT.md)
- [24 层实施约束与阶段门](manufacturing/24L_IMPLEMENTATION_CONSTRAINTS.md)
- [板厂/仿真输入模板](manufacturing/FAB_INPUT_TEMPLATE.json)：35 项仍未填写，不是制造参数

## 独立复核

40 项计划一致性检查通过；10 个故意错误反例均被拒。另一个独立交叉检查确认两套方案的 24 层角色、地参考、相邻 S-S 记录完全一致，35 项制造输入仍为空。官方 KiCad 10.0.7 逐一复核原板 3,837 个过孔与文本解析一致；U11–U22 原生输入/输出网确认 bank A 为槽 1–5、11，bank B 为槽 6–10、12，12 路输出分别独立。以上均是计划/源数据核验，不是布通、阻抗、串扰或制造签核。

在本目录运行（将 BOARD 和 OUT 换成实际路径，输出放独立 scratch）：

```sh
python validate_layer_plan.py --board "$BOARD" --plan layer_plan.json --out "$OUT/plan.json"
python test_validate_layer_plan.py --board "$BOARD" --plan layer_plan.json --out "$OUT/negative.json"
python check_cross_constraints.py --plan layer_plan.json --constraints manufacturing/24L_PLAN_CONSTRAINTS.json --fab-inputs manufacturing/FAB_INPUT_TEMPLATE.json --queue manufacturing/DEEP_VIA_REPLACEMENT_QUEUE.csv --out "$OUT/cross.json"
python manufacturing/audit_vias.py --board "$BOARD" --out-dir "$OUT/vias"
/path/KiCad/AppRun python3.11 manufacturing/native.py --board "$BOARD" --out-dir "$OUT/vias"
```

完整逐层几何可按中文说明重建，无须复制 18 MB 冗余中间文件。没有发布任何失败/试验 PCB。后续先做独立代表通道试验；完整重构验收前继续保留本基准工程。
