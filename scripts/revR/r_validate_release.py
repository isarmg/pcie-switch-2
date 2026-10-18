from pathlib import Path
base=Path(__file__).resolve().parent.parent
src=(base/'revL/l_validate_release.py').read_text(encoding='utf-8')
src=src.replace("['Main_10E1S','Left_2M2_Vertical','Right_M2_Upstream']","['Main_10E1S']")
src=src.replace("['Main_10E1S','Assembly_View','Left_2M2_Vertical','Right_M2_Upstream']","['Main_10E1S']")
src=src.replace('PCIe_3board_RevL','PCIe_E1S_82x45_RevR').replace("'revision':'L'","'revision':'R'")
src=src.replace('[110,45]','[82,45]').replace('xx=[110-','xx=[82-')
src=src.replace('(19+(k-1)*8,22.5)','(5+(k-1)*8,23.5)')
src=src.replace("64.5-q['y_um']/1000","54.5-q['y_um']/1000").replace("22.5+q['x_mm']","20+q['x_mm']")
src=src.replace("R/'work/revL/cpu_routes.json'","R/'work/revR/cpu_routes.json'")
start=src.index("rows=list(csv.DictReader((O/'TWINAX_MAP.csv')")
end=src.index("step=json.loads((O/'STEP_VALIDATION.json')",start)
src=src[:start]+'''
assert len(fs)==len(list(b.GetFootprints()))==277
assert not any('MKey' in str(f.GetFPID().GetLibItemName()) or 'Twinax_' in str(f.GetFPID().GetLibItemName()) for f in fs.values())
assert not (O/'Left_2M2_Vertical').exists() and not (O/'Right_M2_Upstream').exists() and not (O/'Assembly_View').exists()
assert json.loads((O/'M2_PORTS.json').read_text(encoding='utf-8'))==[]
assert not any(re.match(r'/M[1-5]_',q.GetNetname()) or q.GetNetname().startswith(('/CABLE','/UP_','/EXT_41','/EXT_42')) for f in fs.values() for q in f.Pads())
for f in fs.values():
    bb=f.GetBoundingBox(False,False);coords=[p.ToMM(z) for z in [bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom()]]
    assert coords[0]>=0 and coords[1]>=0 and coords[2]<=82 and coords[3]<=45,(f.GetReference(),coords)
plan=json.loads((O/'PLACEMENT_PLAN.json').read_text(encoding='utf-8'))
for ref,row in plan.items():
    f=fs[ref];assert math.dist(xy(f.GetPosition()),row['position_mm'])<.000003 and f.GetLayer()==row['layer'] and f.GetOrientationDegrees()==row['rotation_deg'],ref
removed=json.loads((O/'REMOVAL_REPORT.json').read_text(encoding='utf-8'))
assert len(removed['removed_footprints'])==100 and len(removed['disconnected_switch_and_clock_pads'])==72
assert not set(q['ref'] for q in removed['removed_footprints']).intersection(fs)
source=json.loads((O/'PEX88096_PINOUT.json').read_text(encoding='utf-8'))['ball_records'];by_signal={q['signal']:q['ball'] for q in source}
original=json.loads((R/'outputs/PCIe_Main_RevM/Main_10E1S/COMPONENTS.json').read_text(encoding='utf-8'));original={q['ref']:q for q in original}
ports=json.loads((O/'E1S_PORTS.json').read_text(encoding='utf-8'));assert len(ports)==10
net_count=0;rows=[]
for k,row in enumerate(ports,1):
    assert row['ref']==f'J{k}' and row['pex_lanes']==list(range(k*4,k*4+4))
    f=fs[row['ref']];pm={q.GetNumber():q.GetNetname() for q in f.Pads() if q.GetNumber()}
    assert pm==original[row['ref']]['pinmap'],row['ref']
    assert f.GetLayer()==p.F_Cu and f.GetOrientationDegrees()==90
    for lane in range(4):
        for direction in ['TX','RX']:
            for pol in 'PN':
                nn=f'/S{k:02}_SW_{direction}{lane}_{pol}';ball=by_signal[f'{direction}{pol}[{k*4+lane}]'];assert pins['Main_10E1S'][('U1',ball)]==nn
                hits=[(ff.GetReference(),q.GetNumber()) for ff in fs.values() for q in ff.Pads() if q.GetNetname()==nn]
                assert len(hits)==2 and row['ref'] in {z[0] for z in hits},(nn,hits);net_count+=1
    assert all(pm[f'B{i}']==f'/P12_SLOT{k:02}' for i in range(1,7))
    rows.append([row['ref'],*xy(f.GetPosition()),8,' '.join(map(str,row['pex_lanes'])),12,25])
for lane in range(44,96):
    for direction in ['TX','RX']:
        for pol in 'PN':assert pins['Main_10E1S'][('U1',by_signal[f'{direction}{pol}[{lane}]'])].startswith('unconnected-')
with (O/'E1S_PORT_PLAN.csv').open('w',encoding='utf-8-sig',newline='') as fh:
    w=csv.writer(fh);w.writerow(['Ref','X_mm','Y_mm','Pitch_mm','PEX_lanes','Supply_V','SSD_design_W']);w.writerows(rows)
for ref in [f'C{i}' for i in list(range(801,809))+list(range(811,819))]:
    assert str(fs[ref].GetFPID().GetLibItemName())=='C_0201_0603Metric' and '220nF 16V' in fs[ref].GetValue()
out.update(boards_count=1,daughter_boards=0,inter_board_cable_pairs=0,m2_slots=0,e1s_slots=10,e1s_pitch_mm=8,
    removed_m2_and_branch_footprints=100,unused_switch_main_lanes=52,e1s_data_nets_crosschecked=net_count,
    source_e1s_pinmaps_preserved=True,cpu_link_rerouted_after_resize=True,all_footprints_within_board=True,
    main_data_lanes_allocated=44,host_link_lanes=4,e1s_downstream_lanes=40,
    ssd_design_budget_W=250,input_V=12,power_copper_and_thermal_qualified=False,
    all_usb_vertical=True,usb_pcb_rotation_deg=90,usb_shell_mounting='four SMD pads each',usb_metal_stake_holes=0,
    usb_plastic_locator_holes_per_port=2,usb_actual_part_qualified=False,custom_power_main_bus_connected=False)
''' +src[end:]
src=src.replace('import sys,json,csv,hashlib,zipfile,collections,xml.etree.ElementTree as ET,shutil,math','import sys,json,csv,hashlib,zipfile,collections,xml.etree.ElementTree as ET,shutil,math,re')
src=src.replace("R/'scripts/revL'","R/'scripts/revR'").replace('README_RevL.md','README_RevR.md')
debug=Path(__file__).resolve().parents[2]/'work/revR';debug.mkdir(parents=True,exist_ok=True)
(debug/'validate_source.py').write_text(src,encoding='utf-8')
exec(compile(src,str(__file__),'exec'))
