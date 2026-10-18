from pathlib import Path
import json,shutil,hashlib,zipfile
S=Path(__file__).resolve().parents[2];R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_12VPower_RevV';F=O/'Main_12E1S'
val=json.loads((O/'VALIDATION.json').read_text(encoding='utf-8'));assert val['geometric_drc_violations']==0 and val['step_native_roundtrip_passed'] and val['signal_sections_verified_through_actual_copper']==523 and val['selected_power_nets_all_connected']
shutil.copy2(Path(__file__).with_name('README_RevV.md'),O/'README.md')
reference=O/'references';reference.mkdir(exist_ok=True);shutil.copy2(R/'references/sff1009.pdf',reference/'SFF-TA-1009_Rev4p1a.pdf')
build=dict(revision='V',source_revision='U',board='Main_12E1S',main_mm=[96,45],e1s_slots=12,e1s_pitch_mm=8,e1s_origin_y_mm=26.54,nominal_seated_ssd_side_to_bottom_gap_mm=7.25,m2_slots=0,daughterboards=0,mounting_or_locator_holes=0,cpu='Ultra 9 288V / 32GB MoP',switch='FICTIONAL PEX90064 33x33mm / 1024 balls / 64 lanes',input_V=12,input_feeds='J101 and J102 solder terminals, same supply, independent 20A-budget positive and return cables',main_input_USB_connected=False,ssd_power_budget_W=300,ssd_input_budget_A=25,slot_protection_channels=12,auxiliary_bucks_V=[3.3,5],auxiliary_buck_IC_current_limit_A=[3,3],dedicated_power_layers={'In5.Cu':'VBANK_A','In6.Cu':'VBANK_B'},power_local_controls_copper_connected=True,power_net_count_checked=79,power_pad_connections_checked=1061,signal_sections_copper_verified=523,moved_signal_sections_for_power_planes=27,low_profile_power_components=True,cpu_dynamic_vr_implemented=False,fictional_switch_core_supply_implemented=False,tbt_internal_supply_distribution_complete=False,whole_board_power_routing_complete=False,current_and_thermal_qualified=False,SI_qualified=False,blind_via_stackup_qualified=False,production_ready=False)
(O/'BUILD.json').write_text(json.dumps(build,indent=2),encoding='utf-8');(F/'ROUTING_STATUS.json').write_text(json.dumps({**build,'reported_unconnected':val['reported_unconnected'],'unconnected_report_may_be_capped':True,'erc_errors':val['erc_errors'],'erc_warnings':val['erc_warnings']},indent=2),encoding='utf-8')
ports=json.loads((O/'E1S_PORTS.json').read_text(encoding='utf-8'))
for port in ports:
    port.update(ssd_power_budget_W=25,protected_12V_and_3v3_aux_copper_connected=True,current_capacity_qualified=False)
(O/'E1S_PORTS.json').write_text(json.dumps(ports,indent=2),encoding='utf-8')
budget=json.loads((O/'POWER_BUDGET.json').read_text(encoding='utf-8'));budget.update(edsff_3v3_aux_per_slot_max_A=.025,edsff_3v3_aux_total_max_A=.3,edsff_3v3_current_source='SFF-TA-1009 Rev4.1a Table6-2; PCIe SSD / 1C, not OCP NIC 4C+')
(O/'POWER_BUDGET.json').write_text(json.dumps(budget,indent=2),encoding='utf-8')
indexp=R/'CURRENT_DESIGNS.json';idx=json.loads(indexp.read_text(encoding='utf-8'));idx.update(primary_E1S_design='outputs/'+O.name+'/Main_12E1S/Main_12E1S.kicad_pro',primary_E1S_revision='V',primary_E1S_input_V=12,primary_E1S_protected_SSD_and_aux_power_copper_connected=True,primary_E1S_whole_board_power_complete=False,primary_E1S_power_notes='outputs/'+O.name+'/README.md');indexp.write_text(json.dumps(idx,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'README.txt').write_text('当前 E1.S 方案：outputs/'+O.name+'/Main_12E1S/Main_12E1S.kicad_pro\nRev V：96 x 45 mm，12 个竖直 E1.S，8 mm 中心距，插入后下侧边距名义 7.25 mm。\n输入稳压 12V，J101/J102 两组独立焊线输入，各 20A 预算；J401 自定义 USB-C 与主母线隔离。\n每槽 25W，总 SSD 300W；12 路 eFuse、3.3V / 5V 辅助电源已补铜箔。\nIn5/In6 分别为 A/B 组专用电源层；所选79个电源及局部控制网络、1061处连接已核对。\n保留 523 段信号；几何DRC 0违规；STEP原生导出及重新读取验证通过。\nCPU动态电源、虚构switch核心电源及雷电其余低压分配仍未实现；载流、热、制造及SI未核准，不能直接上电或生产。\nCPU Ultra9 288V / 32GB；33x33mm虚构PEX90064；雷电3主机口方案。\n完整限制见该版本 README.md、VALIDATION.json、POWER_BUDGET.json。\n\n独立全M.2版保留：outputs/PCIe_AllM2_RevP/Main_20M2/Main_20M2.kicad_pro\n120x45mm，20个竖直M.2，6mm中心距。\n旧E1.S Rev U/T原样保留。\n',encoding='utf-8')
ignore=R/'.gitignore';text=ignore.read_text(encoding='utf-8');rule='/outputs/'+O.name+'/*.zip'
if rule not in text:ignore.write_text(text.rstrip()+'\n'+rule+'\n',encoding='utf-8')
for path in Path(__file__).parent.iterdir():
    if path.suffix in ['.py','.md']:
        dest=R/'scripts/revV'/path.name;dest.parent.mkdir(exist_ok=True);shutil.copy2(path,dest)
files=[path for path in O.rglob('*') if path.is_file() and path.suffix not in ['.zip','.lck','.kicad_prl'] and '-backups' not in str(path) and path.name!='SHA256SUMS.txt']
(O/'SHA256SUMS.txt').write_text('\n'.join(hashlib.sha256(path.read_bytes()).hexdigest()+'  '+path.relative_to(O).as_posix() for path in sorted(files))+'\n',encoding='utf-8')
archive=O.with_suffix('.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
    for path in files+[O/'SHA256SUMS.txt']:z.write(path,Path(O.name)/path.relative_to(O))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for line in z.read(O.name+'/SHA256SUMS.txt').decode('utf-8').splitlines():
        digest,name=line.split('  ',1);assert hashlib.sha256(z.read(O.name+'/'+name)).hexdigest()==digest,name
print('Verified release:',archive,archive.stat().st_size,'bytes')
