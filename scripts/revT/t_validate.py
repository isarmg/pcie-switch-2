"""Native KiCad project/ball-map/copper continuity checks and draft release."""
from pathlib import Path
from collections import defaultdict,Counter
import sys,json,math,csv,shutil,hashlib,zipfile,xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding='utf-8')
STAGE=Path(__file__).resolve().parents[2];R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_82x45_TB3Host_RevT';F=O/'Main_10E1S'
sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import p,xy,v
b=p.LoadBoard(str(F/'Main_10E1S.kicad_pcb'));fs={f.GetReference():f for f in b.GetFootprints()};meta={q['ref']:q for q in json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'))}
assert len(fs)==len(meta)==491
edges=[xy(q) for g in b.GetDrawings() if g.GetLayer()==p.Edge_Cuts for q in [g.GetStart(),g.GetEnd()]];dims=[round(max(q[i] for q in edges)-min(q[i] for q in edges),3) for i in [0,1]]
assert dims==[82,45] and b.GetCopperLayerCount()==32 and len(list(b.Zones()))==10
pin_nets={};nonempty=0
for ref,f in fs.items():
    bb=f.GetBoundingBox(False,False);box=[p.ToMM(z) for z in [bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom()]]
    assert box[0]>=0 and box[1]>=0 and box[2]<=82 and box[3]<=45,(ref,box)
    pads=[q for q in f.Pads() if q.GetNumber()];nonempty+=bool(pads)
    assert {q.GetNumber() for q in pads}==set(meta[ref]['pinmap']),ref
    for pp in pads:
        nn=pp.GetNetname();assert nn==meta[ref]['pinmap'][pp.GetNumber()],(ref,pp.GetNumber());pin_nets[(ref,pp.GetNumber())]=nn
    assert not any(q.GetAttribute()==p.PAD_ATTRIB_NPTH for q in f.Pads()),ref
    for mm in f.Models():assert Path(mm.m_Filename.replace('${KIPRJMOD}',str(F))).exists(),mm.m_Filename
    assert 'MKey' not in str(f.GetFPID()) and 'Twinax_' not in str(f.GetFPID())
    h=meta[ref].get('height_mm',0)
    if h and ref not in [f'J{k}' for k in range(1,11)]:assert h<=(8 if f.GetLayer()==p.B_Cu else 9),(ref,h)
for k in range(1,11):assert xy(fs[f'J{k}'].GetPosition())==(5+8*(k-1),23.5) and fs[f'J{k}'].GetOrientationDegrees()==90
for ref,xx in [('J401',78),('J402',73)]:
    f=fs[ref];assert xy(f.GetPosition())==(xx,22.5) and f.GetLayer()==p.B_Cu and f.GetOrientationDegrees()==90
    shell=[q for q in f.Pads() if q.GetNumber()=='SH'];assert len(shell)==4 and all(q.GetAttribute()==p.PAD_ATTRIB_SMD for q in shell)
assert xy(fs['U501'].GetPosition())==(75.1,11.9) and fs['U501'].GetOrientationDegrees()==180
assert '288V' in fs['U502'].GetValue() and '32GB' in fs['U502'].GetValue()
cpu=json.loads((O/'INTEL_288V_PINOUT.json').read_text(encoding='utf-8'))['pins'];cp={q.GetNumber():q for q in fs['U502'].Pads()};assert len(cp)==len(cpu)==2833
for q in cpu:assert math.dist(xy(cp[q['ball']].GetPosition()),(54.5-q['y_um']/1000,22.5+q['x_um']/1000))<.000003
fake=json.loads((O/'PEX90064_FAKE_PINOUT.json').read_text(encoding='utf-8'));sw={q.GetNumber():q for q in fs['U1'].Pads()};assert fake['fictional'] and len(sw)==1024 and fake['main_lanes']==64
for q in fake['ball_records']:assert math.dist(xy(sw[q['ball']].GetPosition()),(20+q['x_mm'],22.5+q['y_mm']))<.000003 and sw[q['ball']].GetNetname()==q['net']
for name,ref,n,xx,yy,angle in [('ALPINE_RIDGE_PINOUT.json','U501',337,75.1,11.9,180),('TPS65982_PINOUT.json','U503',96,76,35.2,0)]:
    info=json.loads((O/name).read_text(encoding='utf-8'));pp={q.GetNumber():q for q in fs[ref].Pads()};assert len(pp)==len(info['pins'])==n
    for q in info['pins']:
        target=(xx-q['x_mm'],yy+q['y_mm']) if angle==180 else (xx+q['x_mm'],yy-q['y_mm'])
        assert math.dist(xy(pp[q['ball']].GetPosition()),target)<.000003,(ref,q['ball'],xy(pp[q['ball']].GetPosition()),target)
        assert pp[q['ball']].GetNetname()==q['net'] and meta[ref]['pin_names'][q['ball']]==q['signal']
nettree=ET.parse(F/'CONNECTIVITY.net').getroot();sn={(q.get('ref'),q.get('pin')):n.get('name') for n in nettree.findall('nets/net') for q in n.findall('node')}
connected={k:v for k,v in pin_nets.items() if v and not v.startswith('unconnected-')}
bad=[(k,v,sn.get(k)) for k,v in connected.items() if sn.get(k)!=v];assert not bad,(len(bad),bad[:8])
assert len(nettree.findall('components/comp'))==nonempty==491
routes=json.loads((O/'SIGNAL_ROUTES.json').read_text(encoding='utf-8'));assert len(routes['routes'])==469
tracks=defaultdict(list);vias=defaultdict(list);graph=defaultdict(lambda:defaultdict(set));segments=set()
def link(nn,aa,bb):graph[nn][aa].add(bb);graph[nn][bb].add(aa)
cu=[p.F_Cu]+[getattr(p,f'In{k}_Cu') for k in range(1,31)]+[p.B_Cu]
for t in b.GetTracks():
    nn=t.GetNetname()
    if isinstance(t,p.PCB_VIA):
        vias[nn].append(t);pt=xy(t.GetPosition());ls=[ll for ll in cu if t.IsOnLayer(ll)]
        for ll in ls[1:]:link(nn,(pt,ls[0]),(pt,ll))
    else:
        tracks[nn].append(t);aa,bb=xy(t.GetStart()),xy(t.GetEnd());ll=t.GetLayer();link(nn,(aa,ll),(bb,ll));segments.add((nn,ll,aa,bb));segments.add((nn,ll,bb,aa))
verified=[]
for r in routes['routes']:
    nn=r['net'];ll=r['layer'];pts=[xy(v(*q)) for q in r['points']]
    for aa,bb in zip(pts,pts[1:]):
        if math.dist(aa,bb)>.002:assert (nn,ll,aa,bb) in segments,(nn,'missing track',aa,bb)
    total=sum(math.dist(aa,bb) for aa,bb in zip(pts,pts[1:]))+sum(r[e].get('fanout_mm',0) for e in ['a','b']);assert abs(total-r['length_mm'])<.0001,(nn,total,r['length_mm'])
    ends=[]
    for e in ['a','b']:
        q=r[e];f=fs[q['ref']];pad=next(z for z in f.Pads() if z.GetNumber()==q['pin']);pos=xy(pad.GetPosition());pt=xy(v(*q['pt']));assert math.dist(pos,q['pad_pt'])<.000003 and pad.GetNetname()==nn
        if pad.HitTest(p.VECTOR2I(p.FromMM(pt[0]),p.FromMM(pt[1]))):link(nn,(pos,f.GetLayer()),(pt,f.GetLayer()))
        else:
            start=xy(v(*q['pad_pt']));assert q.get('fanout_mm',0)>0 and ((nn,f.GetLayer(),start,pt) in segments),(nn,'fanout open')
            assert pad.HitTest(v(*start)),(nn,'fanout misses the pad');link(nn,(pos,f.GetLayer()),(start,f.GetLayer()))
        ends.append((pos,f.GetLayer()))
    seen={ends[0]};todo=[ends[0]]
    while todo:
        for z in graph[nn][todo.pop()]:
            if z not in seen:seen.add(z);todo.append(z)
    assert ends[1] in seen,(nn,'not connected through real copper and vias');verified.append(r['task_id'])
drc=json.loads((F/'DRC.json').read_text(encoding='utf-8'));assert not drc['violations'],Counter(q['type'] for q in drc['violations'])
assert (F/'DRC.json').stat().st_mtime>=(F/'Main_10E1S.kicad_pcb').stat().st_mtime
erc=json.loads((F/'ERC.json').read_text(encoding='utf-8'));ev=[q for sh in erc['sheets'] for q in sh['violations']]
step=json.loads((O/'STEP_VALIDATION.json').read_text(encoding='utf-8'));assert step['Main_10E1S']['native_reimport_reexport']
report=dict(revision='T',main_mm=dims,e1s_slots=10,e1s_pitch_mm=8,daughterboards=0,m2_slots=0,corner_mounting_holes=0,usb_locator_holes=0,usb_switch_side_view='left, centers at y=22.5mm',usb_positions_mm={'J401':[78,22.5],'J402':[73,22.5]},usb_vertical=True,usb_rotation_deg=90,usb_shell_smt=True,usb_model='locator-free closed STEP concept; unverified orderable part',copper_layers=32,footprints=len(fs),schematic_components=nonempty,schematic_connected_pins_crosschecked=len(connected),cpu='Ultra 9 288V 32GB on-package LPDDR5X',cpu_balls_crosschecked=2833,switch='FICTIONAL PEX90064 33x33mm / 64 lanes',switch_balls_crosschecked=1024,thunderbolt_controller='Alpine Ridge DP / DSL6540 reference',tb3_controller_balls_crosschecked=337,pd_controller='TPS65982',pd_balls_crosschecked=96,host_role=True,allocated_copper_route_sections_verified=len(verified),allocated_signal_nets_verified=len({q['net'] for q in routes['routes']}),route_sections_by_kind=dict(Counter(q['kind'] for q in routes['routes'])),geometric_drc_violations=len(drc['violations']),hdi_rules_provisional={'copper_clearance_mm':.075,'via_diameter_mm':[.20,.25],'drill_mm':.10,'hole_to_copper_mm':.10,'hole_to_hole_mm':.25,'edge_to_copper_mm':.4},remaining_reported_unconnected=len(drc['unconnected_items']),unconnected_report_capped=True,erc_errors=sum(q['severity']=='error' for q in ev),erc_warnings=sum(q['severity']=='warning' for q in ev),erc_by_type=dict(Counter(q['type'] for q in ev)),native_step_roundtrip_passed=True,max_untuned_pair_skew_mm=max(q['geometric_skew_mm'] for q in routes['pairs']),whole_board_power_and_management_routing_complete=False,cpu_pmic_and_boot_design_complete=False,thunderbolt_firmware_and_bios_validated=False,si_impedance_and_length_tuning_complete=False,hdi_manufacturing_process_qualified=False,production_ready=False)
(O/'VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
with (O/'BOM.csv').open('w',encoding='utf-8-sig',newline='') as fh:
    wr=csv.writer(fh);wr.writerow(['Ref','Value','Footprint','Side','X_mm','Y_mm','Rotation_deg','Height_mm','Fictional'])
    for ref,f in sorted(fs.items()):wr.writerow([ref,f.GetValue(),str(f.GetFPID().GetLibItemName()),'B' if f.GetLayer()==p.B_Cu else 'F',*xy(f.GetPosition()),f.GetOrientationDegrees(),meta[ref].get('height_mm',''),meta[ref].get('fictional',False)])
with (F/'PIN_MAP.csv').open('w',encoding='utf-8-sig',newline='') as fh:
    wr=csv.writer(fh);wr.writerow(['Ref','Ball','Signal','Net','X_mm','Y_mm'])
    for ref,f in sorted(fs.items()):
        for q in f.Pads():
            if q.GetNumber():wr.writerow([ref,q.GetNumber(),meta[ref].get('pin_names',{}).get(q.GetNumber(),''),q.GetNetname(),*xy(q.GetPosition())])
shutil.copy2(Path(__file__).with_name('README_RevT.md'),O/'README.md')
(O/'USB_MOUNTING_STATUS.json').write_text(json.dumps(dict(upright=True,rotation_deg=90,side='B / switch face',y_center_mm=22.5,view_position='left edge as viewed from switch face',shell_pads_smt=True,locator_holes=0,model='simplified locator-free frame; vendor part pending'),indent=2),encoding='utf-8')
status=json.loads((F/'ROUTING_STATUS.json').read_text(encoding='utf-8'));status.update(allocated_signal_sections_copper_routed=469,allocated_signal_nets_copper_routed=457,tb3_signal_and_control_sections=159,tb3_host_data_clock_routed=True,whole_board_routing_complete=False,production_ready=False)
status.pop('active_data_differential_pairs',None);status.update(core_pcie_data_differential_pairs=88,allocated_nonclock_differential_groups=109,reference_clock_differential_pairs=15,allocated_differential_groups=124,new_tb3_data_individually_routed=True,floating_ground_islands_removed=True)
(F/'ROUTING_STATUS.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
build=json.loads((O/'BUILD.json').read_text(encoding='utf-8'));build.update(allocated_signal_sections_copper_routed=469,allocated_signal_nets_copper_routed=457,tb3_host_signal_control_sections=159,tb3_new_data_individually_routed=True,tb3_actual_inner_layers=sorted({q['layer_index'] for q in routes['routes'] if q['kind'].startswith('TB3_') and q['paired']}),whole_board_routing_complete=False,electrical_design_complete=False,production_ready=False)
(O/'BUILD.json').write_text(json.dumps(build,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'PLACEMENT_PLAN.json').write_text(json.dumps({ref:dict(position_mm=xy(f.GetPosition()),side='B' if f.GetLayer()==p.B_Cu else 'F',rotation_deg=f.GetOrientationDegrees()) for ref,f in fs.items()},indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
if '--check-only' in sys.argv:raise SystemExit(0)
for src in Path(__file__).parent.iterdir():
    if src.suffix in ['.py','.md']:
        dest=R/'scripts/revT'/src.name;dest.parent.mkdir(exist_ok=True);shutil.copy2(src,dest)
idxp=R/'CURRENT_DESIGNS.json';idx=json.loads(idxp.read_text(encoding='utf-8'));idx.update(primary_E1S_design='outputs/'+O.name+'/Main_10E1S/Main_10E1S.kicad_pro',primary_E1S_size_mm=[82,45],primary_E1S_switch='PEX90064 FICTIONAL 33x33 / 64 lanes',primary_E1S_cpu='288V 32GB',primary_E1S_tb='Thunderbolt 3 HOST',primary_E1S_usb_centers_y_mm=22.5)
idx.update(primary_E1S_revision='T',primary_E1S_allocated_pcie_signal_sections_routed=310,primary_E1S_allocated_signal_sections_routed=469)
idxp.write_text(json.dumps(idx,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'README.txt').write_text('当前 E1.S 方案：outputs/'+O.name+'/Main_10E1S/Main_10E1S.kicad_pro\n82 x 45 mm，10 个竖直 E1.S，8 mm 中心距，无 M.2、无子板。\nCPU：Ultra 9 288V，封装内集成 32 GB 内存。\nSwitch：33 x 33 mm 虚构 PEX90064，重排 1024 焊球、64 lane。\n雷电 3 主机口：Alpine Ridge DP / DSL6540 参考 + TPS65982。\n两个竖直 USB-C 位于 switch 面左侧中部，中心 Y=22.5 mm，90度，全贴片概念固定脚。\n本版为布局及信号布线草案；整板供电、启动、雷电固件及SI未完成，不能直接生产。\nSTEP 与PCB同目录；详细检查结果见 VALIDATION.json。\n\n独立全 M.2 方案保留：outputs/PCIe_AllM2_RevP/Main_20M2/Main_20M2.kicad_pro\n120 x 45 mm，20 个竖直 M.2，6 mm 中心距。\n',encoding='utf-8')
ignore=R/'.gitignore';it=ignore.read_text(encoding='utf-8');rule='/outputs/'+O.name+'/*.zip'
if rule not in it:ignore.write_text(it.rstrip()+'\n'+rule+'\n',encoding='utf-8')
files=[q for q in O.rglob('*') if q.is_file() and q.suffix not in ['.zip','.lck','.kicad_prl'] and '-backups' not in str(q) and q.name!='SHA256SUMS.txt']
(O/'SHA256SUMS.txt').write_text('\n'.join(hashlib.sha256(q.read_bytes()).hexdigest()+'  '+q.relative_to(O).as_posix() for q in sorted(files))+'\n',encoding='utf-8')
archive=O.with_suffix('.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
    for q in O.rglob('*'):
        if q.is_file() and q.suffix not in ['.zip','.lck','.kicad_prl'] and '-backups' not in str(q):z.write(q,Path(O.name)/q.relative_to(O))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for line in z.read(O.name+'/SHA256SUMS.txt').decode('utf-8').splitlines():
        digest,name=line.split('  ',1);assert hashlib.sha256(z.read(O.name+'/'+name)).hexdigest()==digest,name
print('Draft release archive verified:',archive,archive.stat().st_size,flush=True)
