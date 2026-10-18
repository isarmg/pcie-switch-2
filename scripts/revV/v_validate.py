from pathlib import Path
from collections import Counter,defaultdict
import sys,json,csv
sys.stdout.reconfigure(encoding='utf-8')
# Reuse independent native pad coordinates, XML netlist, mechanics, heights and
# all 523 actual-copper signal graph checks from Rev U.
src=(Path(__file__).resolve().parent.parent/'revU/u_validate.py').read_text(encoding='utf-8').split("drc=json.loads")[0]
src=src.replace('PCIe_E1S_96x45_12slot_RevU','PCIe_E1S_96x45_12VPower_RevV').replace('==525','==539')
exec(compile(src,'native mechanics / netlist / signals','exec'),globals())
drc=json.loads((F/'DRC.json').read_text(encoding='utf-8'));assert not drc['violations'],Counter(q['type'] for q in drc['violations'])
power=json.loads((O/'POWER_CONNECTIVITY.json').read_text(encoding='utf-8'));assert power['all_selected_nets_connected'],power['disconnected_nets']
step=json.loads((O/'STEP_VALIDATION.json').read_text(encoding='utf-8'));assert step['Main_12E1S']['native_reimport_reexport']
for ll,nn in [(p.In5_Cu,'/VBANK_A'),(p.In6_Cu,'/VBANK_B')]:
    assert not any(not isinstance(t,p.PCB_VIA) and t.GetLayer()==ll and t.GetNetname()!=nn for t in b.GetTracks())
    z=next(z for z in b.Zones() if z.GetLayer()==ll and z.GetNetname()==nn)
    assert z.GetFilledPolysList(ll).OutlineCount()==1,(nn,'power plane disconnected')
budget=json.loads((O/'POWER_BUDGET.json').read_text(encoding='utf-8'));assert budget['input_V']==12 and budget['total_ssd_output_W']==300
erc=json.loads((F/'ERC.json').read_text(encoding='utf-8'));ev=[q for sh in erc['sheets'] for q in sh['violations']]
report=dict(revision='V',source_revision='U',main_mm=dims,e1s_slots=12,e1s_pitch_mm=8,e1s_origin_y_mm=26.54,nominal_seated_ssd_side_to_bottom_gap_mm=7.25,m2_slots=0,daughterboards=0,mounting_or_locator_holes=0,cpu='Ultra 9 288V / 32GB MoP',switch='FICTIONAL PEX90064 33x33mm / 1024 balls',input_V=12,input_feed_current_budget_A=[20,20],input_current_rating_qualified=False,ssd_power_budget_W=300,ssd_12V_current_budget_A=25,aux_rails_V=[3.3,5],aux_rail_ic_limit_A=[3,3],copper_layers=32,dedicated_bank_power_layers=['In5.Cu','In6.Cu'],dedicated_bank_planes_each_single_continuous_island=True,footprints=len(fs),schematic_connected_pins_crosschecked=len(pn),signal_sections_verified_through_actual_copper=len(verified),power_and_local_control_nets_checked=power['net_count'],power_and_local_control_pad_connections_checked=power['checked_pad_connections'],selected_power_nets_all_connected=True,geometric_drc_violations=0,reported_unconnected=len(drc['unconnected_items']),unconnected_report_may_be_capped=True,erc_errors=sum(q['severity']=='error' for q in ev),erc_warnings=sum(q['severity']=='warning' for q in ev),step_native_roundtrip_passed=True,low_profile_power_components=True,cpu_dynamic_vr_implemented=False,fictional_switch_core_regulators_implemented=False,tbt_internal_power_distribution_complete=False,whole_board_electrical_design_complete=False,current_and_thermal_qualified=False,si_and_impedance_qualified=False,blind_via_manufacturing_qualified=False,production_ready=False)
(O/'VALIDATION.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
with (O/'BOM.csv').open('w',encoding='utf-8-sig',newline='') as out:
    wr=csv.writer(out);wr.writerow(['Ref','Value','Footprint','Side','X_mm','Y_mm','Rotation_deg','Height_mm'])
    for ref,f in sorted(fs.items()):wr.writerow([ref,f.GetValue(),str(f.GetFPID().GetLibItemName()),'B' if f.GetLayer()==p.B_Cu else 'F',*xy(f.GetPosition()),f.GetOrientationDegrees(),m[ref].get('height_mm','')])
with (F/'PIN_MAP.csv').open('w',encoding='utf-8-sig',newline='') as out:
    wr=csv.writer(out);wr.writerow(['Ref','Pin','Signal','Net','X_mm','Y_mm'])
    for ref,f in sorted(fs.items()):
        for pp in f.Pads():
            if pp.GetNumber():wr.writerow([ref,pp.GetNumber(),m[ref].get('pin_names',{}).get(pp.GetNumber(),''),pp.GetNetname(),*xy(pp.GetPosition())])
paired=defaultdict(list)
for q in routes['routes']:
    if q['paired']:paired[q['group']].append(q)
lengths=[]
for group,rr in sorted(paired.items()):
    lens={pol:sum(q['length_mm'] for q in rr if q['net'].endswith('_'+pol)) for pol in 'PN'};lengths.append(dict(pair=group,P_mm=lens['P'],N_mm=lens['N'],geometric_skew_mm=abs(lens['P']-lens['N']),qualified=False))
(O/'SIGNAL_ROUTE_LENGTHS.json').write_text(json.dumps(lengths,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2),flush=True)
