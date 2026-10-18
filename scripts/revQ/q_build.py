"""Independent E1.S-only derivative of the validated Rev M main board."""
from pathlib import Path
import sys,json,shutil,re,hashlib,math
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');sys.path.insert(0,str(R/'scripts/revJ'))
import i_common as c
from i_common import *
S=R/'outputs/PCIe_Main_RevM';O=R/'outputs/PCIe_E1S_Only_RevQ';c.ROOT=O
O.mkdir(parents=True,exist_ok=True);folder=O/'Main_10E1S'
shutil.copytree(S/'Main_10E1S',folder,dirs_exist_ok=True)
shutil.copytree(S/'references',O/'references',dirs_exist_ok=True)
for name in ['INTEL_268V_PINOUT.json','PEX88096_PINOUT.json','PEX88096_BALLS.csv','CPU_LINK_LENGTHS.json','CPU_PEX_LINK.json','CPU_POWER_DOMAINS.csv','CUSTOM_POWER_PINOUT.csv','USB_MOUNTING_STATUS.json']:
    shutil.copy2(S/name,O/name)
# Clear only generated files in this new derivative, including old child sheets.
for f in list(folder.glob('Connectivity_*.kicad_sch'))+[folder/n for n in ['DRC.json','ERC.json','CONNECTIVITY.net','Main_10E1S.step','preview.png','bottom.png','PIN_MAP.csv','Local.kicad_sym','Main_10E1S.kicad_sch','Main_10E1S.kicad_prl']]:
    assert f.resolve().parent==folder.resolve()
    if f.is_file():f.unlink()
bp=folder/'Main_10E1S.kicad_pcb';b=p.LoadBoard(str(bp))
pro=(folder/'Main_10E1S.kicad_pro').read_bytes()
meta={q['ref']:q for q in json.loads((folder/'COMPONENTS.json').read_text(encoding='utf-8'))}
delete={f'J{501+k}' for k in range(4)}|{f'U{3001+k}' for k in range(4)}|{f'L{3001+k}' for k in range(4)}
delete|={f'C{3000+10*k+i}' for k in range(4) for i in range(1,7)}
delete|={f'C{3050+10*k+i}' for k in range(4) for i in range(1,9)}
delete|={f'R{3000+10*k+i}' for k in range(4) for i in range(1,5)}
delete|={'U41','U42','C411','C412','C421','C422'}|{f'R{i}' for i in list(range(411,416))+list(range(421,426))}
assert len(delete)==100
removed=[]
for f in list(b.GetFootprints()):
    if f.GetReference() in delete:removed.append(meta.pop(f.GetReference()));remove(b,f)
assert {q['ref'] for q in removed}==delete
baseline={f.GetReference():{'position_mm':xy(f.GetPosition()),'rotation_deg':f.GetOrientationDegrees(),'layer':f.GetLayer()} for f in b.GetFootprints()}
assert len(baseline)==277
a=object.__new__(Board);a.b=b;a.nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
changed=[]
for f in b.GetFootprints():
    for q in f.Pads():
        nn=q.GetNetname()
        if re.match(r'/M[1-5]_',nn) or nn.startswith(('/UP_','/M2_12V_','/CABLE','/EXT_41','/EXT_42')):
            assert f.GetReference() in ['U1','U602'],(f.GetReference(),q.GetNumber(),nn)
            new=c.nc(f.GetReference(),q.GetNumber());q.SetNet(a.net(new));changed.append({'ref':f.GetReference(),'pad':q.GetNumber(),'old_net':nn,'new_net':new})
for t in b.GetTracks():assert not re.match(r'/M[1-5]_',t.GetNetname()),t.GetNetname()
for f in b.GetFootprints():
    assert 'MKey' not in str(f.GetFPID().GetLibItemName()) and 'Twinax_' not in str(f.GetFPID().GetLibItemName())
    e=meta[f.GetReference()];e.update(x=xy(f.GetPosition())[0],y=xy(f.GetPosition())[1],side='B' if f.GetLayer()==p.B_Cu else 'F',rotation_deg=f.GetOrientationDegrees(),pinmap={q.GetNumber():q.GetNetname() for q in f.Pads() if q.GetNumber()},value=f.GetValue(),footprint=str(f.GetFPID().GetLibItemName()))
    assert math.dist(xy(f.GetPosition()),baseline[f.GetReference()]['position_mm'])<.000003
# Remove unused portable footprint/model files from this derivative only.
used_footprints={str(f.GetFPID().GetLibItemName()) for f in b.GetFootprints()}
for f in (folder/'Local.pretty').glob('*.kicad_mod'):
    if f.stem not in used_footprints:
        assert f.resolve().parent==(folder/'Local.pretty').resolve();f.unlink()
used_models={Path(m.m_Filename.replace('${KIPRJMOD}',str(folder))).resolve() for f in b.GetFootprints() for m in f.Models()}
for f in (folder/'models').iterdir():
    if f.is_file() and f.resolve() not in used_models:
        assert f.resolve().parent==(folder/'models').resolve();f.unlink()
title=b.GetTitleBlock();title.SetTitle('10 E1.S only / no M.2 or daughterboards');title.SetRevision('Q');title.SetDate('2026-10-16')
p.SaveBoard(str(bp),b);(folder/'Main_10E1S.kicad_pro').write_bytes(pro)
(folder/'COMPONENTS.json').write_text(json.dumps(list(meta.values()),ensure_ascii=False,indent=2),encoding='utf-8')
(O/'GEOMETRY_BASELINE.json').write_text(json.dumps(baseline,indent=2),encoding='utf-8')
(O/'REMOVAL_REPORT.json').write_text(json.dumps({'source_revision':'M','removed_footprints':removed,'disconnected_switch_and_clock_pads':changed,'daughterboards_in_derivative':0,'m2_sockets_in_derivative':0},ensure_ascii=False,indent=2),encoding='utf-8')
(O/'M2_PORTS.json').write_text('[]\n',encoding='utf-8')
ports=[{'port':f'S{k:02}','ref':f'J{k}','position_mm':[19+8*(k-1),22.5],'rotation_deg':90,'side':'F','pex_lanes':list(range(4*k,4*k+4)),'power_rail':f'/P12_SLOT{k:02}','ssd_power_budget_W':25,'signal_and_power_copper_routing_complete':False} for k in range(1,11)]
(O/'E1S_PORTS.json').write_text(json.dumps(ports,indent=2),encoding='utf-8')
(O/'POWER_BUDGET.json').write_text(json.dumps({'input_V':12,'e1s_slots':10,'ssd_per_slot_budget_W':25,'total_ssd_output_W':250,'total_ssd_12V_current_A':round(250/12,3),'input_feed_existing_annotations_A':[15,15],'fuse_existing_annotations_A':[20,20],'cpu_switch_and_auxiliary_power_extra':True,'whole_board_power_routing_complete':False,'current_capacity_and_thermal_qualified':False,'m2_power_stages':0},indent=2),encoding='utf-8')
(O/'BUILD.json').write_text(json.dumps({'revision':'Q','source_revision':'M','source_board_sha256':hashlib.sha256((S/'Main_10E1S/Main_10E1S.kicad_pcb').read_bytes()).hexdigest(),'main_mm':[110,45],'boards':1,'daughter_boards':0,'cable_connections':0,'e1s_slots':10,'e1s_pitch_mm':8,'m2_slots':0,'removed_m2_and_branch_footprints':100,'retained_footprint_positions':277,'e1s_drive_models':0,'cpu_bga_balls':2833,'pex_bga_balls':1550,'cpu_pmic_implemented':False,'main_routing_complete':False,'electrical_design_complete':False,'production_ready':False},indent=2),encoding='utf-8')
(folder/'ROUTING_STATUS.json').write_text(json.dumps({'cpu_x4_and_refclock_copper_connections':34,'e1s_slots':10,'m2_slots':0,'daughter_boards':0,'e1s_network_assignments_preserved':True,'e1s_copper_routing_complete':False,'power_loop_routing_complete':False,'length_tuning_complete':False,'impedance_validated':False,'blind_via_stackup_validated':False,'production_ready':False},indent=2),encoding='utf-8')
print('Rev Q: 110x45, ten E1.S at 8mm. Removed 4 M.2 sockets, 80 support parts and 16 branch-power parts. 277 placements preserved.',flush=True)
