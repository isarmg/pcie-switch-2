from pathlib import Path
import json,shutil,hashlib,zipfile
STAGE=Path(__file__).resolve().parents[2];R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_12slot_RevU';F=O/'Main_12E1S'
val=json.loads((O/'VALIDATION.json').read_text(encoding='utf-8'));assert val['geometric_drc_violations']==0 and val['step_native_roundtrip_passed'] and val['signal_sections_verified_through_actual_copper']==523
shutil.copy2(Path(__file__).with_name('README_RevU.md'),O/'README.md')
routes=json.loads((O/'SIGNAL_ROUTES.json').read_text(encoding='utf-8'))
build=dict(revision='U',source_revision='T',board='Main_12E1S',main_mm=[96,45],e1s_slots=12,e1s_pitch_mm=8,e1s_origin_y_mm=26.54,nominal_seated_ssd_side_to_bottom_gap_mm=7.25,m2_slots=0,daughterboards=0,mounting_or_locator_holes=0,cpu='Ultra 9 288V 32GB',switch='FICTIONAL PEX90064 / 33x33mm / 64 lanes / 1024 balls',tb3='HOST / Alpine Ridge DP DSL6540 reference + TPS65982',tb3_controller_position_mm=[90.1,11.9],usb_positions_mm={'J401':[93,22.5],'J402':[88,22.5]},allocated_cpu_lanes=4,allocated_ssd_lanes=48,spare_lanes=12,allocated_signal_sections_copper_routed=523,allocated_signal_nets_copper_routed=len({q['net'] for q in routes['routes']}),ssd_power_budget_W=300,ssd_12V_input_budget_A=25,extra_cpu_switch_and_aux_power=True,copper_layers=32,signal_via_copper_diameter_mm=.20,signal_via_drill_mm=.10,floating_ground_islands_removed=True,differential_coupling_and_skew_tuning_complete=False,si_qualified=False,power_routing_complete=False,current_capacity_and_thermal_qualified=False,blind_via_manufacturing_qualified=False,cpu_pmic_and_boot_complete=False,production_ready=False)
(O/'BUILD.json').write_text(json.dumps(build,indent=2),encoding='utf-8');(F/'ROUTING_STATUS.json').write_text(json.dumps({**build,'remaining_reported_unconnected':val['reported_unconnected'],'unconnected_report_may_be_capped':True},indent=2),encoding='utf-8')
usb=json.loads((O/'USB_MOUNTING_STATUS.json').read_text());usb.update(positions_mm={'J401':[93,22.5],'J402':[88,22.5]});(O/'USB_MOUNTING_STATUS.json').write_text(json.dumps(usb,indent=2),encoding='utf-8')
idxp=R/'CURRENT_DESIGNS.json';idx=json.loads(idxp.read_text(encoding='utf-8'));idx.update(primary_E1S_design='outputs/'+O.name+'/Main_12E1S/Main_12E1S.kicad_pro',primary_E1S_size_mm=[96,45],primary_E1S_slots=12,primary_E1S_pitch_mm=8,primary_E1S_revision='U',primary_E1S_e1s_origin_y_mm=26.54,primary_E1S_nominal_ssd_side_to_bottom_gap_mm=7.25,primary_E1S_allocated_pcie_signal_sections_routed=364,primary_E1S_allocated_signal_sections_routed=523);idxp.write_text(json.dumps(idx,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'README.txt').write_text('当前 E1.S 方案：outputs/'+O.name+'/Main_12E1S/Main_12E1S.kicad_pro\n96 x 45 mm；12 个竖直 E1.S，8 mm 中心距；插槽原点 Y=26.54 mm。\n硬盘插入后下侧边距 PCB 底边名义 7.25 mm；另一侧 6.25 mm；尺寸图见 Mechanical_7p25mm.png。\n无 M.2、无子板、无安装或定位孔。\nCPU：Ultra 9 288V / 32 GB；Switch：33 x 33 mm 虚构 PEX90064。\n两个竖直 USB-C 位于 switch 面左侧中部，中心 Y=22.5 mm，全贴片概念固定脚。\n12 槽 SSD 预算 300 W / 12 V 25 A，另计 CPU/switch 功耗，载流和热未核准。\n布局与信号连通草案；整板供电、启动、雷电固件、差分耦合/等长及 SI 未完成，不能直接生产。\nSTEP、PCB和预览同目录，VALIDATION.json 记录检查。\n\n独立全 M.2 方案保留：outputs/PCIe_AllM2_RevP/Main_20M2/Main_20M2.kicad_pro\n120 x 45 mm；20 个竖直 M.2，6 mm 中心距。\n旧 E1.S Rev T 原样保留。\n',encoding='utf-8')
ignore=R/'.gitignore';it=ignore.read_text(encoding='utf-8');rule='/outputs/'+O.name+'/*.zip'
if rule not in it:ignore.write_text(it.rstrip()+'\n'+rule+'\n',encoding='utf-8')
for f in Path(__file__).parent.iterdir():
    if f.suffix in ['.py','.md']:
        dest=R/'scripts/revU'/f.name;dest.parent.mkdir(exist_ok=True);shutil.copy2(f,dest)
files=[q for q in O.rglob('*') if q.is_file() and q.suffix not in ['.zip','.lck','.kicad_prl'] and '-backups' not in str(q) and q.name!='SHA256SUMS.txt']
(O/'SHA256SUMS.txt').write_text('\n'.join(hashlib.sha256(q.read_bytes()).hexdigest()+'  '+q.relative_to(O).as_posix() for q in sorted(files))+'\n',encoding='utf-8')
archive=O.with_suffix('.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
    for q in files+[O/'SHA256SUMS.txt']:z.write(q,Path(O.name)/q.relative_to(O))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for line in z.read(O.name+'/SHA256SUMS.txt').decode('utf-8').splitlines():
        digest,name=line.split('  ',1);assert hashlib.sha256(z.read(O.name+'/'+name)).hexdigest()==digest,name
print('Verified ZIP:',archive,archive.stat().st_size,'bytes',flush=True)
