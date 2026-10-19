# 高端工艺与层数比较审查

正式 PCB 仍为 32 层、源 SHA e33bc9bf7cb41045c3171abd07677bc36ebe7c3960d61349e4ad5ba2437ecb3c。本批只提交设计计划与检查记录。

- [层策略说明](README.zh-CN.md)：24 基线、24-HDI4、28 隔离优先。三者均 12 个信号层，其中 10 个内层信号层；28 增加 4 个地层，未增加信号层。
- [工艺请求与依据](HIGH_END_DESIGN_RECOMMENDATION.md)：同平台能力、工程假设与厂方批准字段严格区分。50/50 µm 局部逃线、100/275 µm 微孔、≤75 µm 单级深、最多两级连续同轴及 150 µm 背钻残段均为试验请求；47 项厂方字段保持 null。
- [公开资料核查](highend-hdi-platform-evidence.md)：来源及量产/样品边界。
- INDEPENDENT_PLAN_VALIDATION.json：44 正项、13 反例。
- INDEPENDENT_COMBINED_CHECKS.json：17 个跨文件与假设隔离检查。
- REPLAY_PROOF.json：在独立目录重放工艺生成脚本，两个 JSON 字节一致。

没有完成 24/28 层 PCB，没有制造、阻抗、SI/PI 或可靠性签核。原 24 层目标仍保留用于比较，28 未被宣布最优。

重放：将 build_design_profile.py 复制到空的临时目录后运行；它在脚本目录生成两个 JSON。validate_high_end_strategy.py 接收 --board、--strategy、--out、--negative-tests。check_combined.py 接收 --directory（本目录）、--board（正式源板）、--out（临时输出）。
