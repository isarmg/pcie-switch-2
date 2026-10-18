from pathlib import Path
import json,csv
base=Path(__file__).resolve().parents[2]
src=(base/'scripts/revU/u_validate.py').read_text(encoding='utf-8').split('drc=json.loads')[0]
src=src.replace('PCIe_E1S_96x45_12slot_RevU','PCIe_E1S_96x45_USB12mm_RevW').replace('==525','==581').replace("[('J401',93),('J402',88)]","[('J401',84),('J402',72)]").replace('(90.1,11.9)','(75.1,11.9)').replace("(35+q['x_mm'],22.5+q['y_mm'])","(20+q['x_mm'],22.5+q['y_mm'])").replace("(69.5-q['y_um']/1000,22.5+q['x_um']/1000)","(54.5-q['y_um']/1000,22.5+q['x_um']/1000)")
src=src.replace('verified=[]',(Path(__file__).with_name('w_signal_contacts.py')).read_text(encoding='utf-8')+'\nverified=[]')
exec(compile(src,'native pads, mechanics, XML and actual signal copper','exec'),globals())
drc=json.loads((F/'DRC.json').read_text(encoding='utf-8'));drc_errors=[q for q in drc['violations'] if q['severity']=='error'];drc_warnings=[q for q in drc['violations'] if q['severity']=='warning'];assert not drc_errors,Counter(q['type'] for q in drc_errors)
power=json.loads((O/'POWER_CONNECTIVITY.json').read_text(encoding='utf-8'));assert power['all_selected_nets_connected'],[(q['net'],q['connected_components']) for q in power['disconnected_nets']]
step=json.loads((O/'STEP_VALIDATION.json').read_text(encoding='utf-8'));assert step['Main_12E1S']['native_reimport_reexport']
res=[(p.In5_Cu,'/VBANK_A'),(p.In6_Cu,'/VBANK_B'),(p.In19_Cu,'/PEX_0V9'),(p.In22_Cu,'/PEX_0V9A'),(p.In4_Cu,'/PEX_1V8'),(p.In7_Cu,'/PEX_1V8A')]
for ll,nn in res:
 assert not any(not isinstance(t,p.PCB_VIA) and t.GetLayer()==ll and t.GetNetname()!=nn for t in b.GetTracks()),(ll,nn)
 z=next(z for z in b.Zones() if z.GetLayer()==ll and z.GetNetname()==nn);assert z.GetFilledPolysList(ll).OutlineCount()==1,(nn,'dedicated plane split')
for ll in [p.In2_Cu,p.In3_Cu,p.In30_Cu]:
 assert not any(not isinstance(t,p.PCB_VIA) and t.GetLayer()==ll for t in b.GetTracks()),('input / auxiliary reserved layer',ll)
native_left_x=96
ports={ref:dict(native_center_mm=xy(fs[ref].GetPosition()),cpu_switch_view_center_from_left_mm=native_left_x-xy(fs[ref].GetPosition())[0],rotation_deg=fs[ref].GetOrientationDegrees(),side='B',shell_mount='SMT') for ref in ['J401','J402']}
assert ports['J401']['cpu_switch_view_center_from_left_mm']==12 and ports['J402']['cpu_switch_view_center_from_left_mm']==24
assert abs(math.dist(xy(fs['J401'].GetPosition()),xy(fs['J402'].GetPosition()))-12)<.000002
(O/'USB_POSITION_VERIFICATION.json').write_text(json.dumps(dict(view='CPU/switch face; native PCB X mirrored',board_mm=[96,45],ports=ports,center_pitch_mm=12,cpu_center_from_view_left_mm=41.5,switch_center_from_view_left_mm=76,controller_electrical_design='Thunderbolt 3 Alpine Ridge DP; no TB4 upgrade implied'),indent=2),encoding='utf-8')
erc=json.loads((F/'ERC.json').read_text(encoding='utf-8'));ev=[q for sh in erc['sheets'] for q in sh['violations']]
report=dict(revision='W',source_revision='V',main_mm=dims,e1s_slots=12,e1s_pitch_mm=8,e1s_origin_y_mm=26.54,nominal_seated_ssd_side_to_bottom_gap_mm=7.25,usb_view='CPU/switch face',power_usb_center_from_left_mm=12,thunderbolt_usb_center_from_left_mm=24,usb_center_pitch_mm=12,cpu='Ultra 9 288V / 32GB MoP',switch='FICTIONAL PEX90064 / 33x33 / 1024 balls',cpu_center_from_view_left_mm=41.5,switch_center_from_view_left_mm=76,m2_slots=0,daughterboards=0,mounting_or_locator_holes=0,input_V=12,ssd_power_budget_W=300,copper_layers=32,footprints=len(fs),schematic_connected_pins_crosschecked=len(pn),signal_sections_verified_through_actual_copper=len(verified),power_and_local_control_nets_checked=power['net_count'],power_and_local_control_pad_connections_checked=power['checked_pad_connections'],selected_power_nets_all_connected=True,geometric_drc_violations=0,reported_unconnected=len(drc['unconnected_items']),unconnected_report_may_be_capped=True,erc_errors=sum(q['severity']=='error' for q in ev),erc_warnings=sum(q['severity']=='warning' for q in ev),step_native_roundtrip_passed=True,reference_switch_core_regulators_added=True,reference_switch_rails_V=[.9004,1.8],reference_switch_regulator_IC_current_A=[40,8],switch_data_and_power_ballmap_fictional=True,cpu_dynamic_vr_implemented=False,cpu_ballmap_changed=False,tbt_version=3,tbt_internal_power_distribution_complete=False,custom_power_usb_main_bus_connected=False,whole_board_electrical_design_complete=False,si_and_impedance_qualified=False,current_and_thermal_qualified=False,blind_via_manufacturing_qualified=False,production_ready=False,input_and_aux_layers_reserved=['In2.Cu','In3.Cu','In30.Cu'])
report.update(geometric_drc_violations=len(drc['violations']),geometric_drc_errors=len(drc_errors),geometric_drc_warnings=len(drc_warnings),geometric_drc_warning_types=dict(Counter(q['type'] for q in drc_warnings)),remaining_copper_sliver_warning=any(q['type']=='copper_sliver' for q in drc_warnings))
(O/'VALIDATION.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
with (O/'BOM.csv').open('w',encoding='utf-8-sig',newline='') as out:
 wr=csv.writer(out);wr.writerow(['Ref','Value','Footprint','Side','X_mm','Y_mm','Rotation_deg','Height_mm'])
 for ref,f in sorted(fs.items()):wr.writerow([ref,f.GetValue(),str(f.GetFPID().GetLibItemName()),'B' if f.GetLayer()==p.B_Cu else 'F',*xy(f.GetPosition()),f.GetOrientationDegrees(),m[ref].get('height_mm','')])
with (F/'PIN_MAP.csv').open('w',encoding='utf-8-sig',newline='') as out:
 wr=csv.writer(out);wr.writerow(['Ref','Pin','Signal','Net','X_mm','Y_mm'])
 for ref,f in sorted(fs.items()):
  for pp in f.Pads():
   if pp.GetNumber():wr.writerow([ref,pp.GetNumber(),m[ref].get('pin_names',{}).get(pp.GetNumber(),''),pp.GetNetname(),*xy(pp.GetPosition())])
(O/'PLACEMENT_PLAN.json').write_text(json.dumps({ref:dict(position_mm=xy(f.GetPosition()),side='B' if f.GetLayer()==p.B_Cu else 'F',rotation_deg=f.GetOrientationDegrees()) for ref,f in fs.items()},indent=2),encoding='utf-8')
paired=defaultdict(list)
for q in routes['routes']:
 if q['paired']:paired[q['group']].append(q)
lengths=[]
for group,rr in sorted(paired.items()):
 lens={pol:sum(q['length_mm'] for q in rr if q['net'].endswith('_'+pol)) for pol in 'PN'}
 lengths.append(dict(pair=group,P_mm=lens['P'],N_mm=lens['N'],geometric_skew_mm=abs(lens['P']-lens['N']),qualified=False))
(O/'SIGNAL_ROUTE_LENGTHS.json').write_text(json.dumps(lengths,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2),flush=True)
