"""96x45 / twelve vertical E1.S, 7.25mm drive-side to bottom-board edge."""
from pathlib import Path
from collections import defaultdict
import sys,json,shutil,math,re,copy
sys.stdout.reconfigure(encoding='utf-8')
STAGE=Path(__file__).resolve().parents[2];R=Path('C:/Users/micro/Desktop/方案/pcie switch 2')
sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
S=R/'outputs/PCIe_E1S_82x45_TB3Host_RevT';O=R/'outputs/PCIe_E1S_96x45_12slot_RevU';W=R/'work/revU';W.mkdir(parents=True,exist_ok=True)
assert O.resolve().parent==(R/'outputs').resolve() and O.name=='PCIe_E1S_96x45_12slot_RevU'
if O.exists():shutil.rmtree(O)
shutil.copytree(S,O,dirs_exist_ok=True)
F=O/'Main_12E1S'
if not F.exists():(O/'Main_10E1S').rename(F)
for f in list(F.glob('Main_10E1S.*')):f.rename(f.with_name(f.name.replace('Main_10E1S','Main_12E1S')))
for f in list(F.glob('Connectivity_*.kicad_sch'))+[F/n for n in ['DRC.json','ERC.json','CONNECTIVITY.net','Main_12E1S.step','preview.png','bottom.png']]+[O/n for n in ['VALIDATION.json','STEP_VALIDATION.json','SHA256SUMS.txt']]:
    if f.is_file():f.unlink()
b=p.LoadBoard(str(F/'Main_12E1S.kicad_pcb'));meta={q['ref']:q for q in json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'))}
a=object.__new__(Board);a.b=b;a.folder=F;a.lib=F/'Local.pretty';a.models=F/'models';a.cs=[];a.newrefs=[];a.w=96;a.h=45;a.name='Main_12E1S';a.plugin=p.PCB_IO_MGR.FindPlugin(p.PCB_IO_MGR.KICAD_SEXP);a.nets={q.GetNetname():q for q in b.GetNetInfo().NetsByNetcode().values()}
oldroutes=json.loads((S/'SIGNAL_ROUTES.json').read_text(encoding='utf-8'))['routes']
Y=26.54;DY=Y-23.5
def pos(ref,x,y,angle=None):
    f=b.FindFootprintByReference(ref);f.SetPosition(v(x,y))
    if angle is not None:f.SetOrientationDegrees(angle)
    meta[ref].update(x=x,y=y,rotation_deg=f.GetOrientationDegrees())
for ref,new in [('J11','J101'),('J12','J102')]:
    f=b.FindFootprintByReference(ref);f.SetReference(new);meta[new]=meta.pop(ref);meta[new]['ref']=new
for ref,q in meta.items():
    f=b.FindFootprintByReference(ref);x,y=xy(f.GetPosition());pos(ref,x+15,y+(DY if (re.fullmatch(r'J(?:[1-9]|10)',ref) or re.fullmatch(r'C40\d\d',ref)) else 0))
for z in list(b.Zones()):remove(b,z)
for g in list(b.GetDrawings()):
    if g.GetLayer()==p.Edge_Cuts:remove(b,g)
    else:g.Move(v(15,0))
rect(b,0,0,96,45,p.Edge_Cuts)

def clone(old,new,pm,x,y,side=None,angle=None):
    q=copy.deepcopy(meta[old]);f=p.Cast_to_FOOTPRINT(b.FindFootprintByReference(old).Duplicate(False));b.Add(f);f.SetReference(new)
    if side and (f.GetLayer()==p.B_Cu)!=(side=='B'):f.Flip(f.GetPosition(),p.FLIP_DIRECTION_LEFT_RIGHT)
    f.SetPosition(v(x,y))
    if angle is not None:f.SetOrientationDegrees(angle)
    for pp in f.Pads():
        if pp.GetNumber():pp.SetNet(a.net(pm[pp.GetNumber()]))
    q.update(ref=new,x=x,y=y,pinmap=pm,side='B' if f.GetLayer()==p.B_Cu else 'F',rotation_deg=f.GetOrientationDegrees());meta[new]=q
    return f
for k,x in [(11,4),(12,12)]:
    conv=lambda n:n.replace('/S01_',f'/S{k:02}_').replace('/P12_SLOT01',f'/P12_SLOT{k:02}').replace('(J1-',f'(J{k}-')
    clone('J1',f'J{k}',{p:conv(n) for p,n in meta['J1']['pinmap'].items()},x,Y)
    # Same per-slot protected power circuit; six SSDs per existing bank.
    bank='/VBANK_A' if k==11 else '/VBANK_B'
    for src,dst in [('U20',f'U{k+10}'),('R146',f'R{151+(k-11)*5}'),('R147',f'R{152+(k-11)*5}'),('R148',f'R{153+(k-11)*5}'),('R149',f'R{154+(k-11)*5}'),('R150',f'R{155+(k-11)*5}'),('C128',f'C{131+(k-11)*3}'),('C130',f'C{133+(k-11)*3}')]:
        cv=lambda n:n.replace('/S10_',f'/S{k:02}_').replace('/P12_SLOT10',f'/P12_SLOT{k:02}').replace('/VBANK_B',bank).replace('(U20-',f'(U{k+10}-')
        clone(src,dst,{p:cv(n) for p,n in meta[src]['pinmap'].items()},5,5)
    for lane in range(4):
        for ip,pol in enumerate('PN'):
            old=f'C{4001+2*lane+ip}';ref=f'C{4081+(k-11)*8+lane*2+ip}';pm={p:n.replace('/S01_',f'/S{k:02}_') for p,n in meta[old]['pinmap'].items()}
            # First two sockets have room for the original horizontal cap bank.
            clone(old,ref,pm,x+4,meta[old]['y'])
# Last socket has insufficient room outside its right signal row. Use a top
# cap bank, with both capacitor ends brought to inner layers through vias.
for i in range(8):pos(f'C{4073+i}',87+2.1*(i%4),8.5+.85*(i//4),180)

fake=json.loads((O/'PEX90064_FAKE_PINOUT.json').read_text(encoding='utf-8'));sw=b.FindFootprintByReference('U1');sr={q['signal']:q for q in fake['ball_records']}
def setpin(ref,pin,nn):
    pad(b.FindFootprintByReference(ref),pin).SetNet(a.net(nn));meta[ref]['pinmap'][pin]=nn
for k in [11,12]:
    for lane in range(4):
        for di in ['TX','RX']:
            for pol in 'PN':
                q=sr[f'{di}{pol}[{44+(k-11)*4+lane}]'];nn=f'/S{k:02}_SW_{di}{lane}_{pol}';q['net']=nn;setpin('U1',q['ball'],nn)
    spare=next(q for q in fake['ball_records'] if q['net'].startswith('unconnected-') and not re.match(r'(?:TX|RX)[PN]\[',q['signal']))
    spare.update(signal=f'FAKE_3V3_PERST_OUT{k:02}_N',net=f'/S{k:02}_PERST0_N');setpin('U1',spare['ball'],spare['net']);meta['U1']['pin_names'][spare['ball']]=spare['signal']
    for pn,pol in zip(([28,29] if k==11 else [32,33]),'PN'):setpin('U602',str(pn),f'/S{k:02}_REFCLK0_{pol}')
fake['allocated_e1s_lanes']=list(range(4,52));fake['unconnected_spare_lanes']=list(range(52,64));fake['fake_3v3_io_outputs']=12
(O/'PEX90064_FAKE_PINOUT.json').write_text(json.dumps(fake,indent=2),encoding='utf-8')

# Repack only non-retained front-side auxiliaries; keep the opposite-side IC
# layout. Moved signal parts are subsequently routed afresh.
routes_nets={q['net'] for q in oldroutes};fixed=set(f'J{k}' for k in range(1,13))|set(ref for ref in meta if re.fullmatch(r'C40\d\d',ref))
fixed |= {'J101','J102','F1','F2'}
for ref in meta:
    f=b.FindFootprintByReference(ref)
    if f.GetLayer()==p.B_Cu:fixed.add(ref)
    elif ref not in fixed and any(nn in routes_nets for nn in meta[ref]['pinmap'].values()):fixed.add(ref)
for ref in ['C5118','C5119','C5120']:
    pos(ref,89+(['C5118','C5119','C5120'].index(ref))*2.3,6.8,0)
pos('C5115',94.9,43,90)
for ref in ['C5116','C5159','C5160']:pos(ref,95.1,meta[ref]['y'])
# The two large inductors fit the new border after a small inward shift.
for ref in ['L501','L502']:pos(ref,meta[ref]['x']-.9,meta[ref]['y'])
def box(f):
    z=f.GetBoundingBox(False,False);return [p.ToMM(x) for x in [z.GetX(),z.GetY(),z.GetRight(),z.GetBottom()]]
def overlap(a,b,g=.025):return a[0]<b[2]+g and a[2]>b[0]-g and a[1]<b[3]+g and a[3]>b[1]-g
for ref in list(fixed):
    f=b.FindFootprintByReference(ref);z=box(f)
    if ref in ['U1','U502','U501','U503']:continue
    if f.GetLayer()!=p.B_Cu or (z[0]>=.4 and z[1]>=.4 and z[2]<=95.6 and z[3]<=44.6):continue
    old=xy(f.GetPosition());dx0,dy0,dx1,dy1=[z[0]-old[0],z[1]-old[1],z[2]-old[0],z[3]-old[1]]
    others=[box(q) for q in b.GetFootprints() if q.GetLayer()==p.B_Cu and q.GetReference()!=ref]
    candidates=sorted(((xx/4,yy/4) for yy in range(3,178) for xx in range(3,381)),key=lambda pt:math.dist(pt,old))
    for x,y in candidates:
        zz=[x+dx0,y+dy0,x+dx1,y+dy1]
        if zz[0]<.5 or zz[1]<.5 or zz[2]>95.5 or zz[3]>44.5:continue
        if all(not overlap(zz,o) for o in others):pos(ref,x,y);break
    else:raise RuntimeError(('B edge packing',ref))
occupied=defaultdict(list)
for ref in fixed:occupied[b.FindFootprintByReference(ref).GetLayer()].append((ref,box(b.FindFootprintByReference(ref))))
mov=[ref for ref in meta if ref not in fixed]
mov.sort(key=lambda ref:-(lambda z:(z[2]-z[0])*(z[3]-z[1]))(box(b.FindFootprintByReference(ref))))
for ref in mov:
    f=b.FindFootprintByReference(ref);old=xy(f.GetPosition());z=box(f);dx0,dy0,dx1,dy1=[z[0]-old[0],z[1]-old[1],z[2]-old[0],z[3]-old[1]]
    candidates=[old]+[(xx/4,yy/4) for yy in range(3,178) for xx in range(3,381)]
    good=None
    for x,y in candidates:
        zz=[x+dx0,y+dy0,x+dx1,y+dy1]
        if zz[0]<.5 or zz[1]<.5 or zz[2]>95.5 or zz[3]>44.5:continue
        if all(not overlap(zz,o) for _,o in occupied[f.GetLayer()]):good=(x,y);break
    assert good,('no packing',ref)
    pos(ref,*good);occupied[f.GetLayer()].append((ref,box(f)))
for ref in meta:
    f=b.FindFootprintByReference(ref);z=box(f);assert z[0]>=0 and z[1]>=0 and z[2]<=96 and z[3]<=45,(ref,z)

# Identify unchanged routed networks and carry their native copper across.
retained=[];affected=set()
for q in oldroutes:
    r=copy.deepcopy(q)
    for e in ['a','b']:
        for key in ['pt','pad_pt']:r[e][key][0]+=15
        actual=xy(pad(b.FindFootprintByReference(r[e]['ref']),r[e]['pin']).GetPosition())
        if math.dist(actual,r[e]['pad_pt'])>.000005:affected.add(r['net'])
    for pt in r['points']:pt[0]+=15
    if re.match('/S\d\d_',r['net']) or any(not(.48<=pt[0]<=95.52 and .48<=pt[1]<=44.52) for pt in r['points']):affected.add(r['net'])
    retained.append(r)
retained=[q for q in retained if q['net'] not in affected]
for t in list(b.GetTracks()):
    if t.GetNetname() in affected or t.GetNetname()=='/GND':remove(b,t)
    else:t.Move(v(15,0))

# New and moved signal networks. Existing CPU/TB3 routes stay in place.
groups={q['net']:{k:q[k] for k in ['group','kind','paired','width','layer_index','layer','layer_name']} for q in oldroutes if q['net'] in affected}
for k in [11,12]:
    for lane in range(4):
        for di in ['SW_RX','SW_TX','SSD_RX']:
            for pol in 'PN':
                nn=f'/S{k:02}_{di}{lane}_{pol}';direct=di=='SSD_RX';groups[nn]=dict(group=f'S{k:02}_{"RX" if di=="SW_RX" else "TX"}{lane}',kind='E1S_DATA',paired=True,width=.10,layer_index=0 if direct else 1,layer=0 if direct else 4,layer_name='F.Cu' if direct else 'In1.Cu')
    for pol in 'PN':groups[f'/S{k:02}_REFCLK0_{pol}']=dict(group=f'S{k:02}_CLK',kind='E1S_CLOCK',paired=True,width=.1,layer_index=1,layer=4,layer_name='In1.Cu')
    groups[f'/S{k:02}_PERST0_N']=dict(group=f'S{k:02}_RESET',kind='E1S_RESET',paired=False,width=.1,layer_index=1,layer=4,layer_name='In1.Cu')
# Last socket's coupling caps are no longer directly aligned with its pins.
for nn,g in groups.items():
    if nn.startswith('/S10_SSD_RX'):g.update(layer=4,layer_index=1,layer_name='In1.Cu')
nodes=defaultdict(list)
for f in b.GetFootprints():
    for pp in f.Pads():
        if pp.GetNumber() and pp.GetNetname() in groups:nodes[pp.GetNetname()].append((f,pp))
cu=[p.F_Cu]+[getattr(p,f'In{i}_Cu') for i in range(1,31)]+[p.B_Cu]
allocated=[]
for t in b.GetTracks():
    if isinstance(t,p.PCB_VIA):allocated.append((xy(t.GetPosition()),set(ll for ll in cu if t.IsOnLayer(ll)),t.GetNetname()))
points=defaultdict(list);fanouts=[]
for nn,pins in sorted(nodes.items()):
    g=groups[nn]
    for f,pp in pins:
        center=xy(pp.GetPosition());side=f.GetLayer();fan=False
        if g['layer']==0:points[nn].append(dict(ref=f.GetReference(),pin=pp.GetNumber(),pt=center,pad_pt=center,fanout_mm=0));continue
        # Full inner-layer accessibility. These remain provisional blind spans.
        span=set(cu[1:]) if side==p.B_Cu else set(cu[:-1]);candidates=[center]
        if f.GetReference() in ['U601','U602']:
            fx,fy=xy(f.GetPosition());dx,dy=center[0]-fx,center[1]-fy;nx,ny=(math.copysign(1,dx),0) if abs(dx)>abs(dy) else (0,math.copysign(1,dy));candidates=[(center[0]+nx*d,center[1]+ny*d) for d in [.65,.95,.5,1.1,.8,1.25]];fan=True
        elif f.GetReference() not in ['U1','U502','U501','U503']:
            candidates +=[(center[0]+dx,center[1]+dy) for off in [.05,.1,.15,.2,.25,.3,.4] for dx,dy in [(off,0),(-off,0),(0,off),(0,-off)]]
            candidates=[pt for pt in candidates if pp.HitTest(v(*pt)) and (f.GetReference().startswith('J') or all(pp.HitTest(v(pt[0]+.10*math.cos(t*math.pi/4),pt[1]+.10*math.sin(t*math.pi/4))) for t in range(8)))]
        valid=[pt for pt in candidates if .55<pt[0]<95.45 and .55<pt[1]<44.45 and all(net==nn or not(span&ls) or math.dist(pt,other)>=.36 for other,ls,net in allocated)]
        assert valid,('no landing',f.GetReference(),pp.GetNumber(),nn,center)
        pt=valid[0];diam=.20 if nn.startswith('/TBT_') else .25;a.via(*pt,nn,p.In1_Cu if side==p.B_Cu else p.F_Cu,p.B_Cu if side==p.B_Cu else p.In30_Cu,diam,.1);allocated.append((pt,span,nn))
        if fan:a.track(center,pt,nn,side,.1);fanouts.append(dict(net=nn,ref=f.GetReference(),pin=pp.GetNumber(),a=center,b=pt,layer=side,width=.1))
        points[nn].append(dict(ref=f.GetReference(),pin=pp.GetNumber(),pt=pt,pad_pt=center,fanout_mm=math.dist(center,pt) if fan else 0))
tasks=[]
for nn,es in sorted(points.items()):
    es.sort(key=lambda q:(q['ref']!='U1',q['ref']))
    linked=[es[0]];todo=es[1:];i=0
    while todo:
        _,aa,bb=min((math.dist(x['pt'],y['pt']),ii,jj) for ii,x in enumerate(linked) for jj,y in enumerate(todo));end=todo.pop(bb)
        tasks.append(dict(net=nn,task_id=nn+f'__{i}',**groups[nn],a=linked[aa],b=end));linked.append(end);i+=1
for ref in ['U1','U502','U501','U503']+[f'J{k}' for k in range(1,13)]:
    f=b.FindFootprintByReference(ref);side=f.GetLayer();span=set(cu[1:]) if side==p.B_Cu else set(cu[:-1]);used=[]
    for j in range(2):
        gs=[pp for pp in f.Pads() if pp.GetNetname()=='/GND' and pp.GetNumber() not in used and all(net=='/GND' or not(span&ls) or math.dist(xy(pp.GetPosition()),other)>=.36 for other,ls,net in allocated)]
        if not gs:break
        pp=gs[0];used.append(pp.GetNumber());pt=xy(pp.GetPosition());a.via(*pt,'/GND',p.In1_Cu,side,.25,.1);allocated.append((pt,span,'/GND'))
vias=[];segments=[]
for t in b.GetTracks():
    if isinstance(t,p.PCB_VIA):vias.append(dict(net=t.GetNetname(),pt=xy(t.GetPosition()),diameter=.20 if t.GetNetname().startswith('/TBT_') else .25,layers=[ll for ll in cu if t.IsOnLayer(ll)]))
    elif t.GetLayer() not in [p.F_Cu,p.B_Cu]:segments.append(dict(net=t.GetNetname(),a=xy(t.GetStart()),b=xy(t.GetEnd()),width=p.ToMM(t.GetWidth()),layer=t.GetLayer()))
for ref,q in meta.items():
    f=b.FindFootprintByReference(ref);q.update(x=xy(f.GetPosition())[0],y=xy(f.GetPosition())[1],rotation_deg=f.GetOrientationDegrees())
(F/'COMPONENTS.json').write_text(json.dumps(list(meta.values()),indent=2),encoding='utf-8')
ports=[]
for k in range(1,13):
    x,y=xy(b.FindFootprintByReference(f'J{k}').GetPosition());ports.append(dict(port=f'S{k:02}',ref=f'J{k}',position_mm=[x,y],rotation_deg=90,side='F',pex_lanes=list(range(4*k,4*k+4)),power_rail=f'/P12_SLOT{k:02}',ssd_power_budget_W=25,signal_and_power_copper_routing_complete=False))
(O/'E1S_PORTS.json').write_text(json.dumps(ports,indent=2),encoding='utf-8')
budget=json.loads((O/'POWER_BUDGET.json').read_text());budget.update(e1s_slots=12,total_ssd_output_W=300,total_ssd_12V_current_A=25,banks_ssd_W=[150,150]);(O/'POWER_BUDGET.json').write_text(json.dumps(budget,indent=2),encoding='utf-8')
mechanical=dict(board_mm=[96,45],e1s_slots=12,e1s_pitch_mm=8,footprint_origin_y_mm=Y,previous_y_mm=23.5,translation_y_mm=DY,device_body_y_min_mm=Y-20.29,device_body_y_max_mm=Y+11.21,pcb_bottom_y_mm=45,nominal_body_side_to_bottom_edge_mm=45-(Y+11.21),nominal_opposite_side_clearance_mm=Y-20.29,body_width_mm=31.5,datum_e_local_x_mm=.020,body_center_local_x_mm=4.54,orientation_deg=90,dimension_interpretation='In-plane distance from seated E1.S lower side edge to PCB bottom edge, not insertion height or Z standoff.',source='SFF-TA-1006 Rev 2.0 Fig 5-1/Table 5-1 and original Samtec footprint A1 datum',source_url='https://members.snia.org/document/dl/26956',ssd_models_in_final_step=False,tolerance_not_included=True)
(O/'MECHANICAL_CLEARANCE.json').write_text(json.dumps(mechanical,indent=2),encoding='utf-8')
(W/'route_tasks.json').write_text(json.dumps(dict(tasks=tasks,retained=retained,vias=vias,segments=segments,fanouts=fanouts,grid_mm=.05,clearance_mm=.08),indent=2),encoding='utf-8')
p.SaveBoard(str(W/'Main.prepared.kicad_pcb'),b);p.SaveBoard(str(F/'Main_12E1S.kicad_pcb'),b)
print('Built',len(meta),'parts,',len(tasks),'new route sections,',len(retained),'retained; mechanical',mechanical,flush=True)
