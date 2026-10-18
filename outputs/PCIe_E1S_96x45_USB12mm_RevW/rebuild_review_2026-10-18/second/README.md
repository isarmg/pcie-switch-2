# 第二组重新审查：局部供电、器件参数与一对差分

源：cfd3a2a3de7bbeedeb94c3c2c9f6a1422be7a8a71141d28c105f218bc0c4ac80。候选：0083dece575e4515719c6dc3248dbae3c60fdb5734550eb05b64d91e5e4ad6b1。

- C9004 按 TPS548D22 要求从 2.2µF 改真实 4.7µF/10V X7R 0603 GRM188Z71A475KE15D；完整官方焊盘/庭院，最大高0.95mm，F面 BP 与 DRGND 各约1.7mm、0.3mm宽直接回路。三件小移、旧PG孔上移0.1mm；实际偏压容量、启动/纹波及机械仍需验证。
- U504/U505 的208mil SS料号与既有150mil封装不符，改官方有效 SNJG料号，8脚/网络/几何不变。
- U511 VCCA/DIR 与 U512 VCCA/VCCB 补本地去耦连接及C5157地；真实CPU1.8V供电源仍未实现。
- U607全部22信号仅单器件焊盘、地址/RESET无偏置且无总线业务连接，明确DNP预留；管理功能仍未实现。U510按TPS3808表5-1纠正六脚ERC类型，模拟CT保持passive。
- S12 TX2 上游重布In14，完整链P/N=15.597297/15.598234mm，原27.235/62.225mm；保留全部原过孔。孔抽头改变，实际叠层/残桩/损耗未知。新In13参考近端反焊盘面积约0.037106/0.037103mm²；原AC后F短线仍各跨0.0301mm²旧In1槽，不能称整链SI合格。

当前组合原生DRC几何0错误、1条既有In23铜毛刺；parity0，ERC43错误212警告；P3V3_AUX未驱动错误代表针从U511.6换到U510.6，未新增未驱动网络。全焊盘仍107断网（104涉及实装）、最少1784次簇连接，未具备生产或上电条件。全原编号pad含NC簇和存留铜UUID网无回退。

REFERENCE_FROM_FIRST.json是原始cfd至候选的10网完整铜宽多边形差集；REFERENCE.json是S12独立候选至组合的差集，不能将后者零增量冒充原始新增层零缺口。此配置覆盖S12四段与六条USB2，不代表全板SI。六个GND层实际lost/gained区域和全部相邻层非GND直线铜也已审查（GROUND_REGION_DELTA.json，无遗漏arc）：3条旧差分交集总约5.97e-9mm²，1/5/10µm敏感性均0；唯一实质新增投影为新PEX09_PG自身移孔近端反焊盘0.015mm²。未发现实质新增既有高速参考缺口；这是二维几何证据，不是SI仿真。

重放：使用KiCad10 Python运行 scripts/revW/w_apply_rebuild_second.py SOURCE/Main_12E1S NEW/Main_12E1S，输入必须是上述cfd且配套正式pro。脚本在新目录复制项目、精确UUID/原块守卫增量、同步原理图/库/元数据/BOM、重填铜。REPLAY_PROOF.json证明重放完整PCB SHA与候选相同。需要重新运行原生DRC/parity/ERC、全pad回归和参考审计，不应将重放成功等同制造验收。

仅保存自写审查及工具、项目使用的KiCad官方封装别名，不分发原厂PDF/附件。详细来源见bp/SOURCE_EVIDENCE.json和MPN_PROOF.json。

归档说明：s12/WORKER_ORIGINAL_MANIFEST.json保留独立候选原始目录的hash清单，部分原始板/中间运行器不重复入仓库；正式重放入口是上述已入库脚本，基线可从已推送5d89f7d取出。最终提交的审查清单会单列实际归档文件。

连续参考审计可用 scripts/revW/rebuild_second/reference_audit.py BOARD REPORT BASELINE_REPORT --python-package-dir SHAPELY_PACKAGE_DIR；需官方Python包Shapely/NumPy，package-dir是本地安装目录而不是仓库必备临时路径。该几何审计明确不执行电磁/时序模拟。
