"""Native PCB, netlist and actual copper graph audit. Does not assert SI readiness."""
from pathlib import Path
from collections import defaultdict,Counter
import sys,json,math,csv,xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_12slot_RevU';F=O/'Main_12E1S';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
b=p.LoadBoard(str(F/'Main_12E1S.kicad_pcb'));fs={f.GetReference():f for f in b.GetFootprints()};m={q['ref']:q for q in json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'))};assert len(fs)==len(m)==525
edges=[xy(q) for g in b.GetDrawings() if g.GetLayer()==p.Edge_Cuts for q in [g.GetStart(),g.GetEnd()]];dims=[round(max(q[i] for q in edges)-min(q[i] for q in edges),3) for i in [0,1]];assert dims==[96,45]
slots=sorted([xy(fs[f'J{k}'].GetPosition()) for k in range(1,13)]);assert all(math.dist(q,(4+8*i,26.54))<.000004 for i,q in enumerate(slots))
assert abs(45-(26.54+11.21)-7.25)<1e-6
for k in range(1,13):assert abs(45-(xy(pad(fs[f'J{k}'],'A1').GetPosition())[1]+3.215)-7.25)<.000005
allpins={}
for ref,f in fs.items():
    bb=f.GetBoundingBox(False,False);box=[p.ToMM(z) for z in [bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom()]];assert box[0]>=0 and box[1]>=0 and box[2]<=96 and box[3]<=45,(ref,box)
    assert not any(pp.GetAttribute()==p.PAD_ATTRIB_NPTH for pp in f.Pads()),ref
    assert math.dist(xy(f.GetPosition()),(m[ref]['x'],m[ref]['y']))<.000004
    for pp in f.Pads():
        if pp.GetNumber():assert pp.GetNetname()==m[ref]['pinmap'][pp.GetNumber()],(ref,pp.GetNumber());allpins[(ref,pp.GetNumber())]=pp.GetNetname()
    for mod in f.Models():assert Path(mod.m_Filename.replace('${KIPRJMOD}',str(F))).exists()
    if ref not in [f'J{k}' for k in range(1,13)]:assert m[ref].get('height_mm',0)<=(8 if f.GetLayer()==p.B_Cu else 9)
for ref,x in [('J401',93),('J402',88)]:assert xy(fs[ref].GetPosition())==(x,22.5) and fs[ref].GetOrientationDegrees()==90
assert math.dist(xy(fs['U501'].GetPosition()),(90.1,11.9))<.000004
fake=json.loads((O/'PEX90064_FAKE_PINOUT.json').read_text(encoding='utf-8'));assert len(fake['ball_records'])==1024 and fake['fictional'] and fake['unconnected_spare_lanes']==list(range(52,64))
for q in fake['ball_records']:
    pp=pad(fs['U1'],q['ball']);assert math.dist(xy(pp.GetPosition()),(35+q['x_mm'],22.5+q['y_mm']))<.000004 and pp.GetNetname()==q['net']
cpu=json.loads((O/'INTEL_288V_PINOUT.json').read_text(encoding='utf-8'))['pins'];assert len(cpu)==2833
for q in cpu:assert math.dist(xy(pad(fs['U502'],q['ball']).GetPosition()),(69.5-q['y_um']/1000,22.5+q['x_um']/1000))<.000004
net=ET.parse(F/'CONNECTIVITY.net').getroot();sn={(q.get('ref'),q.get('pin')):n.get('name') for n in net.findall('nets/net') for q in n.findall('node')};pn={k:v for k,v in allpins.items() if v and not v.startswith('unconnected-')};bad=[(k,v,sn.get(k)) for k,v in pn.items() if sn.get(k)!=v];assert not bad,bad[:8]
assert len(net.findall('components/comp'))==525
routes=json.loads((O/'SIGNAL_ROUTES.json').read_text(encoding='utf-8'));assert len(routes['routes'])==523
def pt(q):return tuple(round(z,5) for z in q)
graph=defaultdict(lambda:defaultdict(set));nodes=defaultdict(set)
def link(nn,a,z):graph[nn][a].add(z);graph[nn][z].add(a);nodes[nn].add(a);nodes[nn].add(z)
cu=[p.F_Cu]+[getattr(p,f'In{i}_Cu') for i in range(1,31)]+[p.B_Cu]
for t in b.GetTracks():
    nn=t.GetNetname()
    if isinstance(t,p.PCB_VIA):
        a=pt(xy(t.GetPosition()));ls=[ll for ll in cu if t.IsOnLayer(ll)]
        for ll in ls[1:]:link(nn,(a,ls[0]),(a,ll))
    else:link(nn,(pt(xy(t.GetStart())),t.GetLayer()),(pt(xy(t.GetEnd())),t.GetLayer()))
verified=[]
for r in routes['routes']:
    nn=r['net'];ends=[]
    for end in ['a','b']:
        e=r[end];f=fs[e['ref']];pp=pad(f,e['pin']);a=(pt(xy(pp.GetPosition())),f.GetLayer());assert pp.GetNetname()==nn and math.dist(xy(pp.GetPosition()),e['pad_pt'])<.000005
        for node in list(nodes[nn]):
            if node[1]==f.GetLayer() and pp.HitTest(v(*node[0])):link(nn,a,node)
        ends.append(a)
    seen={ends[0]};todo=[ends[0]]
    while todo:
        for z in graph[nn][todo.pop()]:
            if z not in seen:seen.add(z);todo.append(z)
    assert ends[1] in seen,(nn,'copper graph open',ends);verified.append(r['task_id'])
drc=json.loads((F/'DRC.json').read_text(encoding='utf-8'));erc=json.loads((F/'ERC.json').read_text(encoding='utf-8'));ev=[q for sh in erc['sheets'] for q in sh['violations']]
assert not drc['violations'],Counter(q['type'] for q in drc['violations'])
step=json.loads((O/'STEP_VALIDATION.json').read_text(encoding='utf-8'));assert step['Main_12E1S']['native_reimport_reexport']
report=dict(revision='U',main_mm=dims,e1s_slots=12,e1s_pitch_mm=8,e1s_origin_y_mm=26.54,nominal_seated_ssd_side_to_bottom_gap_mm=7.25,nominal_opposite_side_gap_mm=6.25,side_clearance_includes_manufacturing_tolerances=False,m2_slots=0,daughterboards=0,mounting_or_locator_holes=0,cpu='Ultra 9 288V 32GB',switch='FICTIONAL PEX90064 33x33mm / 1024 balls / 64 lanes',allocated_lanes_cpu=4,allocated_lanes_ssd=48,spare_lanes=12,ssd_power_budget_W=300,ssd_12V_current_budget_A=25,power_routing_and_thermal_qualified=False,copper_layers=b.GetCopperLayerCount(),footprints=525,schematic_connected_pins_crosschecked=len(pn),signal_sections_verified_through_actual_copper=len(verified),geometric_drc_violations=len(drc['violations']),reported_unconnected=len(drc['unconnected_items']),unconnected_report_may_be_capped=True,erc_errors=sum(q['severity']=='error' for q in ev),erc_warnings=sum(q['severity']=='warning' for q in ev),step_native_roundtrip_passed=True,whole_board_power_cpu_pmic_boot_firmware_complete=False,si_impedance_coupling_skew_qualified=False,blind_via_buildup_qualified=False,production_ready=False)
paired_layers=defaultdict(dict)
for q in routes['routes']:
    if q['paired'] and q['net'].endswith(('_P','_N')):paired_layers[q['net'][:-2]][q['net'][-1]]=q['layer_name']
report['differential_sections_with_P_N_on_different_layers']={key:ls for key,ls in paired_layers.items() if len(set(ls.values()))>1}
report['e1s_A1_pad_to_nominal_drive_side_mm']=3.215
(O/'VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
with (O/'BOM.csv').open('w',encoding='utf-8-sig',newline='') as fh:
    wr=csv.writer(fh);wr.writerow(['Ref','Value','Footprint','Side','X_mm','Y_mm','Rotation_deg','Height_mm'])
    for ref,f in sorted(fs.items()):wr.writerow([ref,f.GetValue(),str(f.GetFPID().GetLibItemName()),'B' if f.GetLayer()==p.B_Cu else 'F',*xy(f.GetPosition()),f.GetOrientationDegrees(),m[ref].get('height_mm','')])
with (F/'PIN_MAP.csv').open('w',encoding='utf-8-sig',newline='') as fh:
    wr=csv.writer(fh);wr.writerow(['Ref','Pin','Signal','Net','X_mm','Y_mm'])
    for ref,f in sorted(fs.items()):
        for pp in f.Pads():
            if pp.GetNumber():wr.writerow([ref,pp.GetNumber(),m[ref].get('pin_names',{}).get(pp.GetNumber(),''),pp.GetNetname(),*xy(pp.GetPosition())])
with (O/'PEX90064_FAKE_BALLS.csv').open('w',encoding='utf-8-sig',newline='') as fh:
    keys=list(fake['ball_records'][0]);wr=csv.DictWriter(fh,fieldnames=keys);wr.writeheader();wr.writerows(fake['ball_records'])
coupling=[]
for ref,q in m.items():
    if re.fullmatch(r'C40\d\d',ref):coupling.append(dict(ref=ref,pinmap=q['pinmap'],position_mm=[q['x'],q['y']],rotation_deg=q['rotation_deg']))
(O/'E1S_TX_AC_COUPLING.json').write_text(json.dumps(coupling,indent=2),encoding='utf-8')
(O/'PLACEMENT_PLAN.json').write_text(json.dumps({ref:dict(position_mm=xy(f.GetPosition()),side='B' if f.GetLayer()==p.B_Cu else 'F',rotation_deg=f.GetOrientationDegrees()) for ref,f in fs.items()},indent=2),encoding='utf-8')
for path in [O/'BUILD.json',F/'ROUTING_STATUS.json']:
    info=json.loads(path.read_text(encoding='utf-8'));info.update(revision='U',main_mm=[96,45],e1s_slots=12,e1s_pitch_mm=8,e1s_origin_y_mm=26.54,nominal_ssd_side_clearance_mm=7.25,allocated_signal_sections_copper_routed=523,allocated_signal_nets_copper_routed=len({q['net'] for q in routes['routes']}),whole_board_routing_complete=False,production_ready=False);path.write_text(json.dumps(info,indent=2),encoding='utf-8')
summary={k:v for k,v in report.items() if k!='differential_sections_with_P_N_on_different_layers'}
summary['different_layer_differential_section_count']=len(report['differential_sections_with_P_N_on_different_layers'])
print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
