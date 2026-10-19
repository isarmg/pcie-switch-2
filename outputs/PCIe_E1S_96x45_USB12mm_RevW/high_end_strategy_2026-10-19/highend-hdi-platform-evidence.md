# E1.S 高端 PCB 平台公开证据核查

核查日期：2026-10-19。范围：只读公开一手资料；没有联系厂商、下单或修改板文件。项目假设：96 × 45 mm，候选 24 层（12S/8G/4P），PCIe 5 / Thunderbolt，尚无厂方批准 stackup。

## 结论

24 层高阶 HDI 是已有明确商业化证据的 PCB 路线；mSAP、低损耗材料和高阶 HDI 也有同一厂家同一产品族的公开组合证据。不能据此宣称本项目 24L、指定厚度、指定激光孔/landing、12S8G4P 和任意层互连全部已获量产批准。

最强组合证据来自胜宏科技 2026 正式招股书；AT&S 的 HLC-HDI 海报更适合证明低损耗材料、高层数和 HDI 属于同一公开平台。AT&S 的 mSAP 数据应单独保留，不拼成“38L + 90µm pad + 任意层 + 25/25µm 已同时量产”。

## 1. AT&S：HLC-HDI 2025 海报，已看原图核对合并单元格

[官方 PDF](https://ats.net/wp-content/uploads/HLC-HDI-poster_591x841mm-ATS-2025-03.pdf)，1 页。

| 参数 | Standard | Advanced | 核读说明 |
|---|---|---|---|
| 材料 | Meg6、Meg7、Tachyon 100G、Astra | 同左 | 横跨两列 |
| 层数 / HDI | 4–38L；最高 6-N-6 | 同左 | 横跨两列 |
| 板厚 | 0.5–3.2 mm | 0.5–5 mm | 分列 |
| 最大工作拼板 | 21.3 × 24.25 in | 21 × 27 in | 分列 |
| 线宽 / 间距 | 最小 40/40 µm，Cu 13 µm | 同左 | 横跨两列 |
| 背钻 | Yes | 同左 | 横跨两列 |
| Via size | 最小 0.15 mm | 同左 | 未标注为 laser |
| 孔径 / 深度比原文 | 1:12 | 1:19 | 不能当作微盲孔 AR |
| Fine pitch | 0.4 mm | 0.3 mm | 分列 |

边界：同一 General design rules 表是平台级能力，不是每项极限可同时采用的承诺；未标明此表所有组合均为量产。上部 ZiC 的 ≥250 µm 互连直径、≥550 µm pad、90–100 µm 介质和 9 mm 总互连厚度是板间 Z-interconnect 参数，不能当作 HDI 激光孔规则。

## 2. AT&S：mSAP 量产、低损耗和 laser pad 的真实对应

[Miniaturization 2023 官方 PDF](https://ats.net/wp-content/uploads/Miniaturization-poster_591x841mm-ATS-2023-02.pdf)，1 页；原图已核。

- mSAP 栏：25/25 µm @ Cu 15 µm 是量产；20/20 µm 是样品。
- Laser pad 90 µm；该字段是焊盘，不是激光孔直径。最小铜厚 12 µm、最小介质厚 20 µm。
- Dk 3.4 / Df 0.004 一格横跨 Subtractive 与 mSAP；不能误读为 mSAP 材料空白。该格未给测试频率或具体牌号。
- IC-Substrate 是独立一栏，77 µm pad、9/12 µm L/S 不纳入本项目 PCB 规则。
- 此海报没有给 mSAP 总层数、24L 结构或本项目叠孔验证。

[2023-07-27 光模块官方说明](https://ats.net/en/ats-empowers-high-speed-optical-module-pcb-manufacturing/)提供额外生产背景：100G–400G PCB 已量产，800G 当时通过客户验证；列出 mSAP、低粗糙度铜面处理及 laser blind via 与 mechanical buried via（FV2）叠接能力。没有最大同轴叠孔级数、IST/TCT 条件或寿命分布，因此不能当作特定高层板可靠性合格证。

[AT&S 工厂平台](https://ats.net/en/company/ats-worldwide/?_sfm_l_type=production)将重庆 II 的 HDI 6-N-6、anylayer 14L、SLP 18/22 µm、高速高频板列在同一工厂技术清单中。这比跨公司拼接强，但仍不能证明这些极限同一板件同时成立；同页重庆 I/III 的 FCBGA 能力排除。

## 3. 胜宏科技：最强的同产品族组合与量产证据

[2026-04-13 港交所正式招股书](https://www.hkexnews.hk/listedco/listconews/sehk/2026/0413/2026041300005.pdf)。以下为紧凑事实摘要，页码均为印刷页：

- p.121 / 125：截至 2026 年 4 月，24L、6+12+6 明确商业化/量产；30L、10+10+10 为技术能力及研发验证；36L、14+8+14 为研发。
- p.133：advanced HDI 同一产品段落组合 M8/M9、25/25 µm mSAP、112/224 Gbps；紧接披露 6+N+6 及以上量产，并占 2025 HDI 收入约 75%。这是产品族级强证据，未给指定 24L SKU 的完整合格叠构。
- p.130：AI/HPC HDI 为 20–30L、4+N+4 至 10+N+10，厚度上限 4.5 mm。75 µm 激光孔、pad D+100 µm、AR 1.1:1 属于另行的 Smart Devices anylayer，不得搬到 AI/HPC。
- p.225：拟募资 mSAP 项目当时仍在建设；不能称所有新产线均已量产。

本项目 laser/landing、同轴最大堆叠、铜厚、具体材料型号、各层介质、成品厚度、coupon 结果均未获该文件批准。公开可采购组合存在的判断为“产品族级支持”；本项目厂方确认仍为 null。

更新核对：[2026 半年度正式报告，2026-08-28](https://static.cninfo.com.cn/finalpage/2026-08-28/1225522515.PDF)，印刷 p.19，继续明确 24L/6 阶大规模生产；30L/10 阶与 36L/14 阶改称已攻克核心制造工艺。后两者没有单独给量产/交付认定，因此当前不能再只说 36L“未突破、仅规划”，也不能升级为已获大规模量产证据。

## 4. Unimicron：高层 HDI 与 mSAP 分开取证

[多层 PCB 官方产品页](https://www.uniflex.com.tw/product_Multilayer.html)明确列 2–68 层、HDI+HLC、高频高速材料混压、背钻，并面向高阶服务器、OAM/UBB、加速卡；未披露该平台的 mSAP 线规或 laser/landing 数字。

[HDI ELIC 官方 roadmap](https://www.uniflex.com.tw/rd03_01.html)已核 HTML 表头：2019 分 Production / Sample 两列；2020、2021 不再标状态。2019 量产 mSAP L/S/microvia = 30/30/70 µm，2019 样品 25/25/70；后列 20/20/60 是历史 roadmap 数字，不据此认定当前已量产。低 Dk 3 不能替代未披露的 Df；本表无总层数和完整叠构。

[ELIC 官方产品页](https://www.uniflex.com.tw/product_ELIC.html)明确全层互连、电镀填孔、长期生产与 SLP 技术，但没有证明“24L + mSAP + 指定低损耗材料”的同一量产组合。结论：厂家能力可信、同一具体组合仍待确认。

## 5. 深南电路：不要把封装基板数字搬到 PCB

[官方 PCB 页面](https://www.scc.com.cn/scc/cpjs/PCB/index.html)区分批量/样品。通用批量激光孔 100 µm、样品 50 µm；历史 2019 HDI 行为 anylayer 10L 批量、16L 样品。材料总表列 Megtron6/7，不能推导其与所有 HDI 极限同板成立。产品实例给 14L、1.1 mm、4 阶 HDI 企业级 SSD 刚挠板，但材料是高 Tg FR4+PI，不能当作低损耗 mSAP 24L 样例。

[2026 半年度正式报告](https://static.cninfo.com.cn/finalpage/2026-08-27/1225512708.PDF)印刷 p.12 将数据中心 PCB、高速材料、高多层、多阶 HDI、细密线路列为业务能力；没有给所需组合的 mSAP、laser/landing 或可靠性试验参数。22L/24L FC-BGA 等封装基板量产/研发数字完全排除。

## 6. 本项目应保持 null 的字段

对所有候选厂商，在没有本项目正式厂方 stackup 前：

- approved_24L_12S8G4P_stackup = null
- approved_finished_thickness_and_tolerance = null
- approved_material_per_layer_and_copper_roughness = null
- approved_copper_thickness_per_layer = null
- approved_microvia_drill_capture_target_for_this_stackup = null
- approved_max_coaxial_stack_count = null
- approved_stack_on_buried_via_structure = null
- approved_backdrill_residual_stub_and_keepout = null
- approved_impedance_and_insertion_loss_coupon_limits = null
- qualified_reflow_IST_TCT_HATS_CAF_results_for_this_structure = null
- prototype_and_production_yield = null

这些 null 表示没有公开确认，不表示厂家做不到。应先选具体材料/工厂/层序与 interconnect topology，再让同一工厂提供联合设计规则及匹配 coupon，不能用不同平台最小值拼出设计。

## 本地核源附件

- ats-hlc-hdi-2025.pdf / .png / .txt：原 PDF、整页核图、layout 提取文本
- ats-miniaturization-2023.pdf / .png / .txt：原 PDF、整页核图、layout 提取文本
- victory-giant-hkex-prospectus-2026.pdf / .txt：原招股书及 layout 文本
- unimicron-hdi-roadmap.html：原 HTML，用于核 Production/Sample 列跨度
- source-sha256.txt：下载 PDF 校验值

外部研究结果与工程推论已区分；未发现可替代厂方 DFM 放行的公开材料。

归档说明：上述原始 PDF/核图/HTML 为研究时的核源附件，不随本轻量审查批提交；官方链接保留于正文。此批仅提交计划、来源摘要和可重放检查。
