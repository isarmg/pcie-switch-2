from pathlib import Path
import json,shutil,hashlib,zipfile,csv
S=Path(__file__).resolve().parents[2];R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_USB12mm_RevW';F=O/'Main_12E1S'
assert O.resolve().parent==(R/'outputs').resolve() and O.name=='PCIe_E1S_96x45_USB12mm_RevW'
val=json.loads((O/'VALIDATION.json').read_text(encoding='utf-8'));assert val['geometric_drc_errors']==0 and val['step_native_roundtrip_passed'] and val['signal_sections_verified_through_actual_copper']==523 and val['selected_power_nets_all_connected']
shutil.copy2(Path(__file__).with_name('README_RevW.md'),O/'README.md')
build={**val,'board':'Main_12E1S','source_revision':'V','main_input_USB_connected':False,'whole_board_power_routing_complete':False,'low_profile_power_components':True,'protected_SSD_and_aux_and_reference_switch_power_copper_connected':True}
(O/'BUILD.json').write_text(json.dumps(build,indent=2),encoding='utf-8');(F/'ROUTING_STATUS.json').write_text(json.dumps(build,indent=2),encoding='utf-8')
budget=json.loads((O/'POWER_BUDGET.json').read_text(encoding='utf-8'));budget.update(fictional_switch_core_regulators_implemented=True,switch_current_reference_model='PEX88096 worst-case Table29; NOT a PEX90064 specification',switch_0v9_current_budget_A=37.427,switch_1v8_current_budget_A=6.903,switch_regulator_IC_current_A=[40,8],switch_regulator_output_V=[.9004,1.8],switch_regulator_efficiency_budget=.85,switch_reference_input_W=(.9004*37.427+1.8*6.903)/.85,cpu_dynamic_vr_implemented=False,whole_board_power_routing_complete=False,custom_power_usb_C_main_bus_connected=False,current_capacity_and_thermal_qualified=False)
budget['ssd_plus_aux_plus_switch_input_A_budget']=(300+budget['aux_input_W_budget']+budget['switch_reference_input_W'])/12
(O/'POWER_BUDGET.json').write_text(json.dumps(budget,indent=2),encoding='utf-8')
res={'In5.Cu':'/VBANK_A','In6.Cu':'/VBANK_B','In19.Cu':'/PEX_0V9','In22.Cu':'/PEX_0V9A','In4.Cu':'/PEX_1V8','In7.Cu':'/PEX_1V8A'}
(O/'POWER_LAYER_RESERVATION.json').write_text(json.dumps(dict(revision='W',exclusive_layers=res,all_each_single_continuous_island_verified=True,current_capacity_qualified=False),indent=2),encoding='utf-8')
for name in ['POWER_LAYER_RESERVATION_B.json','POWER_CLEANUP.json','POWER_ISLAND_BRIDGES.json']:
 path=O/name
 if path.exists():path.unlink()
meta=json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'))
for name in ['TB3_STATUS.json','USB_MOUNTING_STATUS.json','CPU_DEVICE_SELECTION.json']:
 path=O/name;info=json.loads(path.read_text(encoding='utf-8'));info.update(revision='W',current_positions_in='PLACEMENT_PLAN.json',cpu_switch_view='mirrored native PCB X; power USB at12mm, TB USB at24mm',electrical_revision_note='Existing TB3 circuitry retained; real CPU balls unchanged. Reference fictional-switch power added.')
 if name=='USB_MOUNTING_STATUS.json':info.update(positions_mm={'J401':[84,22.5],'J402':[72,22.5]},center_pitch_mm=12,power_USB_center_from_face_left_mm=12,TB_USB_center_from_face_left_mm=24)
 path.write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
ports=json.loads((O/'E1S_PORTS.json').read_text(encoding='utf-8'))
for port in ports:port.update(protected_12V_and_3v3_aux_copper_connected=True,current_capacity_qualified=False)
(O/'E1S_PORTS.json').write_text(json.dumps(ports,indent=2),encoding='utf-8')
coupling=[dict(ref=q['ref'],pinmap=q['pinmap'],position_mm=[q['x'],q['y']],rotation_deg=q.get('rotation_deg',0)) for q in meta if q['ref'].startswith('C40')]
(O/'E1S_TX_AC_COUPLING.json').write_text(json.dumps(coupling,indent=2),encoding='utf-8')
idxp=R/'CURRENT_DESIGNS.json';idx=json.loads(idxp.read_text(encoding='utf-8'));idx.update(primary_E1S_design='outputs/'+O.name+'/Main_12E1S/Main_12E1S.kicad_pro',primary_E1S_revision='W',primary_E1S_usb_face='CPU/switch',primary_E1S_power_usb_distance_from_left_mm=12,primary_E1S_thunderbolt_usb_distance_from_left_mm=24,primary_E1S_usb_center_pitch_mm=12,primary_E1S_protected_SSD_and_aux_power_copper_connected=True,primary_E1S_reference_fake_switch_power_copper_connected=True,primary_E1S_whole_board_power_complete=False,primary_E1S_power_notes='outputs/'+O.name+'/README.md');idxp.write_text(json.dumps(idx,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'README.txt').write_text('当前 E1.S：outputs/'+O.name+'/Main_12E1S/Main_12E1S.kicad_pro\nRev W：96x45mm，12个竖直 E1.S，8mm间距，名义侧边距7.25mm。\n按 CPU/switch 面：供电 USB-C 距左边12mm，雷电口24mm，中心间距12mm；CPU中部、switch右侧。\n两口竖直安装、贴片固定脚；电路仍沿用雷电3主机口。\n12V焊线输入，SSD总300W；已补原SSD/辅助电源和虚构switch参考电源铜线。\n保留真实CPU电源接口；CPU动态供电、完整雷电内部电源、固件、SI、热和制造审核仍待完成。\n几何/连通/STEP检查见版本内VALIDATION.json；此草案不能直接生产或上电。\n旧版和独立全M.2版保留不变。\n',encoding='utf-8')
ignore=R/'.gitignore';txt=ignore.read_text(encoding='utf-8');rules=['/outputs/'+O.name+'/*.zip','/work/revW/','/tmp/route_deps/']
for rule in rules:
 if rule not in txt:txt=txt.rstrip()+'\n'+rule+'\n'
ignore.write_text(txt,encoding='utf-8')
for path in Path(__file__).parent.iterdir():
 if path.suffix in ['.py','.md']:
  dest=R/'scripts/revW'/path.name;dest.parent.mkdir(exist_ok=True);shutil.copy2(path,dest)
files=[p for p in O.rglob('*') if p.is_file() and p.suffix not in ['.zip','.lck','.kicad_prl'] and '-backups' not in str(p) and p.name!='SHA256SUMS.txt']
(O/'SHA256SUMS.txt').write_text('\n'.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(O).as_posix() for p in sorted(files))+'\n',encoding='utf-8')
archive=O.with_suffix('.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
 for p in files+[O/'SHA256SUMS.txt']:z.write(p,Path(O.name)/p.relative_to(O))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for line in z.read(O.name+'/SHA256SUMS.txt').decode('utf-8').splitlines():
  digest,name=line.split('  ',1);assert hashlib.sha256(z.read(O.name+'/'+name)).hexdigest()==digest,name
print('Verified ZIP + SHA256:',archive,archive.stat().st_size,'bytes',flush=True)
