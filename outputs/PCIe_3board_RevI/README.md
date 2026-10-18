# Rev I：10 槽 E1.S 主板 + 两块直立 M.2 子板

这是 KiCad 10 可编辑的结构、供电和连接布局草案。三个 M.2 2280 硬盘均垂直于子板，插槽已在板面内转为 90°，硬盘平面与主板 E1.S 插槽平行。主板没有 E1.S 硬盘模型。

| 工程 | 板外形 | 铜层 | 接口 |
|---|---|---|---|
| `Main_10E1S` | 80 × 45 mm | 32 | 10 × E1.S x4，8 mm 中心距，虚构 BGA400 |
| `Left_2M2_Vertical` | 52 × 45 mm | 12 | 2 × M-Key 2280，均为 PCIe x4 |
| `Right_M2_Upstream` | 52 × 45 mm | 12 | 1 × M-Key 2280 x4 + 1 × 直立 M-Key x4 上行槽 |
| `Assembly_View` | 三块板和线束组合 | 仅展示 | 3 个直立 SSD 包络 + 线缆包络 |

主板原四个安装孔已删除。保留上一版已按要求取消 E1.S 连接器固定/定位孔的状态，因而当前连接器安装方式仍需机械修改。32 层、1.6 mm 是 CAD 设置，尚无板厂确认的可制造叠层。

左右两块小板的插槽中心均为 (14,17) 和 (38,17) mm，四个连接器均为直立 M-Key、板内旋转 90°。右板 J4 是标注 UPLINK 的上行接口，需通过两端 M.2 金手指的直通转接线/转接模块接主机 M.2 槽；不能在此槽插 SSD 并当作下行使用。装配图显示三个 SSD，UPLINK 槽留空。

## 打开与 STEP

分别打开三个子目录中同名 `.kicad_pro`；`.kicad_pcb`、分层连接图、符号、封装及 STEP 模型都随工程保存。模型使用 `${KIPRJMOD}` 相对路径。

整体装配：`Assembly_View/Assembly_View.step`。各板也有独立同名 `.step`。`Assembly_View.kicad_pcb` 只用于 3D 装配展示，不是可投板的电气工程。SSD 是 22 × 80 × 0.8 mm 板体和芯片包络，线缆是示意外形，没有宣称精确的金手指缺口、螺钉孔或弯曲半径。三个 SSD 包络顶端约在子板顶面以上 81.5 mm，需机壳上部支架固定。

## PCIe 与线缆

总连接规模为 56 lane：40 lane 给 10 个 E1.S，12 lane 给三个 M.2，4 lane 为上行。BGA400 为用户允许的虚构、可布线球阵，保留原 256 球的既有信号，并补入 144 个内部球位。它不对应 PEX88064、PEX90048 或任何真实芯片。

十三个 SSD 共享同一条 x4 上行链路，不能同时获得十三路独立 x4 上行带宽。

左右各 8 lane，每侧需要 **16 对数据 twinax + 2 对 REFCLK twinax**，共 18 对屏蔽差分线；不是每侧八根信号线。另有八芯低速控制/地线，以及独立的 12 V / GND 电源线。左右子板与主板之间约留 30 mm 装配间隙，此值不是完成验证的线缆长度。

`TWINAX_MAP.csv` 给出每对线的主板焊盘、子板焊盘、P/N 和方向。焊盘 P 对 P、N 对 N、G 为屏蔽回流，两端接地。这是自定义直焊端接，不兼容任何未经说明的 MCIO/SFF 接口。候选使用 85 Ω twinax；[Samtec PCIe Gen5 电缆系列](https://www.samtec.com/products/pciec-g5)可作后续实物线束选型依据。

主板 J301 → 左板 J50、主板 J302 → 右板 J50：1 为受保护 12 V，2 为地。低速主板 J303 → 左板 J51、J304 → 右板 J51。1/2/3 为第一端口 PERST/CLKREQ/WAKE，4/5/6 为第二端口，7/8 为地。右板第二端口为 UP；其 CLKREQ 接 J4.52 并保留 TP1 测点。

信号 TX/RX 均从 switch 视角命名。三个下行 M.2 的 PET 接 switch TX，PER 接 switch RX；右板 J4 上行槽相反，PET 接 switch RX，PER 接经交流耦合的 switch TX，以接收直通线传来的主机 PET。上行 REFCLK、PERST 来自主机，CLKREQ/WAKE 返回主机。J4 的所有 3.3 V 电源触点均未连接，不向主机电源轨反灌电；M.2 上行接口中不引入 12 V。原 PCIe 金手指及 PRSNT 回路已去除。

新增 TX 路径放置 220 nF 串联交流耦合电容，位于子板。发送端位置、回流、差分间距、线对内延时和过孔残桩仍须随真实 switch 与叠层重新设计，当前自动走线只表达连接关系。

## 供电与高度

保留主板 12 V、10 × 25 W、总 SSD 目标 250 W 的双路输入、20 A 保险、每槽 eFuse 和 3.3 V AUX 电路。左右子板从对应 12 V 输入分支经新加 TPS259470A eFuse 引出；1.10 kΩ ILM 电阻对应约 3 A 限流目标，UVLO/OVLO 约为 10.33/13.44 V。输入端保护位于线缆之前。

每个 M.2 单独使用 [TPS565201](https://www.ti.com/lit/ds/symlink/tps565201.pdf) 12 V→约 3.3 V 降压电路：芯片额定 5 A，输出电阻 33.2 kΩ / 10 kΩ；2.2 µH [XAL5030-222MEC](https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xal/xal50xx/xal5030-222/)，输入去耦、100 nF 自举电容、两只 22 µF 输出电容和反馈电阻已落板。每个 M.2 暂按 **4 A / 约 13.2 W** 的设计目标预留，不是已验证的持续输出能力。电容需核实直流偏压后的有效容量，电感、铜层、过孔和散热需按实物验证。

三个 M.2 额外约 40 W；考虑降压损耗后，外部电源需求已超过原 250 W。总预算至少应重新覆盖约 295 W 的 SSD 输入负载，再加真实 switch、风扇和余量；本草案没有真实 switch 的核心供电定义。

新增背面降压器件最高约 3.1 mm，主板原器件约 3.5 mm，均低于 8 mm 的器件高度目标。E1.S 连接器约 9.05 mm，按用户要求不计入该限制。M.2 直立连接器暂用 5.3 mm 高度包络；插入后的硬盘高度另计。

## 连接器资料与限制

[KLS KLS1-NGFF01-V1 厂家页面](https://klsele.com/products/connectors/Card-connectors/M-2-NGFF-connectors/10763.html)列出 5.3 mm 高直立 E/M-Key 型号，并标称可满足 Gen5。公开页未提供足以核验本版焊盘的完整尺寸图，电流描述也存在 1 A 与 0.5 A 两处不同表述。因此，本版按较低额定值评估电源触点，**封装名带 `DRAFT`，焊盘布局为占位，不能直接订购后投板**。需向厂家确认 M-Key 完整料号、焊盘、定位结构、镀金、S 参数及额定电流。

`VALIDATION.json` 和三板 `DRC.json` 记录实际检查结果。连接图使用被动类型引脚表达网表，ERC 不验证 switch 逻辑、电源时序或跨电源域行为。没有进行 Gen5 通道仿真、阻抗/损耗/串扰验证、差分等长调谐、热仿真或满载试验。此工程不具备直接生产或宣称 PCIe 5.0 可工作的依据。

## 目录迁移与 Git

项目已迁移至 `C:\Users\micro\Desktop\方案\pcie switch 2`，完整复制后逐文件进行 SHA-256 校验，原位置已无工程文件。项目 `.gitignore` 已补充 KiCad 本机状态、备份、缓存、编译/路由临时文件及发行 ZIP 规则；PCB、连接图、封装和 STEP 模型保留可跟踪。

桌面方案仓库的 `.gitignore` 已备份并追加 `/pcie switch 2/` 规则；原有 `方案\pcie switch` 未修改。`scripts/Move-ToDesktop.ps1` 作为迁移记录保留，无需再次执行。
