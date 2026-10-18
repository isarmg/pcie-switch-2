from pathlib import Path
from collections import defaultdict,Counter
import sys,json,re,math
sys.stdout.reconfigure(encoding='utf-8')
STAGE=Path(__file__).resolve().parents[2]
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
O=R/'outputs/PCIe_E1S_82x45_TB3Host_RevT';W=R/'work/revT';W.mkdir(parents=True,exist_ok=True)
folder=O/'Main_10E1S';b=p.LoadBoard(str(folder/'Main_10E1S.kicad_pcb'))
for obj in list(b.GetTracks())+list(b.Zones()):remove(b,obj)
a=object.__new__(Board);a.b=b;a.nets={q.GetNetname():q for q in b.GetNetInfo().NetsByNetcode().values()}
src=(STAGE/'scripts/revS/s_prepare_routes.py').read_text(encoding='utf-8');src=src[src.index('def classify(nn):'):src.index('by_net=defaultdict')]
exec(compile(src,'base signal classification','exec'));base_classify=classify
tbcl={}
for q in json.loads((O/'TB3_LINKS.json').read_text(encoding='utf-8')):
    for nn in q['nets']:tbcl[nn]=dict(group=q['group'],kind=q['kind'],layer_index=q['layer_index'])
# Route discrete TB3 control/bias/flash/reset networks as trees; regulator and
# switched supply domains are deliberately excluded from this signal router.
nodes=defaultdict(list)
for f in b.GetFootprints():
    for pp in f.Pads():
        if pp.GetNumber():nodes[pp.GetNetname()].append((f,pp))
ctl=[nn for nn in sorted(nodes) if nn.startswith('/TBT_') and nn not in tbcl and not nn.startswith(('/TBT_VCC','/TBT_PD_LDO','/TBT_PD_VOUT','/TBT_5V','/TBT_VBUS','/TBT_SVR_SW')) and len(nodes[nn])>1]
lis=[2,3,5,6,8,9,11,12,14,15,17,18,20,21,23,24,26,27,29,30]
for i,nn in enumerate(ctl):tbcl[nn]=dict(group=nn[1:],kind='TB3_CONTROL',layer_index=lis[i%len(lis)])
def classify(nn):return tbcl.get(nn) or base_classify(nn)
by_net=defaultdict(list);groups={};allocated=[];pending=[];fanouts=[]
for f in b.GetFootprints():
    for pp in f.Pads():
        nn=pp.GetNetname();cl=classify(nn)
        if not cl:continue
        idx=cl['layer_index'];layer=p.F_Cu if idx==0 else getattr(p,f'In{idx}_Cu')
        pending.append((f,pp,nn,cl));groups[nn]={**cl,'layer':layer,'layer_name':b.GetLayerName(layer),'paired':cl['kind'] not in ['E1S_RESET','TB3_CONTROL']}
pending.sort(key=lambda z:(z[0].GetLayer()!=p.B_Cu,z[0].GetReference()!='U502',z[0].GetReference(),z[1].GetNumber()))
for f,pp,nn,cl in pending:
    idx=cl['layer_index'];layer=p.F_Cu if idx==0 else getattr(p,f'In{idx}_Cu');is_back=f.GetLayer()==p.B_Cu;side=p.B_Cu if is_back else p.F_Cu;span=(idx,31) if is_back else (0,idx)
    center=xy(pp.GetPosition());candidates=[center];fan=False
    if idx==0:
        assert not is_back;by_net[nn].append(dict(ref=f.GetReference(),pin=pp.GetNumber(),pt=center,pad_pt=center,fanout_mm=0));continue
    if f.GetReference() in ['U601','U602']:
        fx,fy=xy(f.GetPosition());dx,dy=center[0]-fx,center[1]-fy
        nx,ny=(math.copysign(1,dx),0) if abs(dx)>abs(dy) else (0,math.copysign(1,dy))
        candidates=[(center[0]+nx*dist,center[1]+ny*dist) for dist in [.65,.95,.5,1.1,.8,1.25]];fan=True
    elif f.GetReference() in [f'J{k}' for k in range(1,11)]:candidates += [(center[0]+dx,center[1]) for dx in [-.4,.4,-.3,.3,-.2,.2]]
    elif f.GetReference() not in ['U1','U502','U501','U503']:
        candidates += [(center[0]+dx,center[1]+dy) for off in [.05,.1,.15,.2,.25] for dx,dy in [(off,0),(-off,0),(0,off),(0,-off)]]
        candidates=[pt for pt in candidates if pt==center or all(pp.HitTest(v(pt[0]+.12*math.cos(math.pi*j/4),pt[1]+.12*math.sin(math.pi*j/4))) for j in range(8))]
    valid=[pt for pt in candidates if .3<pt[0]<81.7 and .3<pt[1]<44.7 and all(net==nn or hi<span[0] or lo>span[1] or math.dist(pt,other)>=.36 for other,lo,hi,net in allocated)]
    assert valid,('no via landing',f.GetReference(),pp.GetNumber(),center,nn)
    pt=valid[0];allocated.append((pt,*span,nn));diam=.20 if nn.startswith('/TBT_') else .25;a.via(*pt,nn,layer,side,diam,.10)
    if fan:
        a.track(center,pt,nn,side,.10);fanouts.append(dict(net=nn,ref=f.GetReference(),pin=pp.GetNumber(),a=center,b=pt,layer=side,width=.10))
    by_net[nn].append(dict(ref=f.GetReference(),pin=pp.GetNumber(),pt=pt,pad_pt=center,fanout_mm=math.dist(center,pt) if fan else 0))
tasks=[]
for nn,points in sorted(by_net.items()):
    points.sort(key=lambda z:(0 if z['ref']=='U1' else 1,z['ref'][0],z['ref']))
    if groups[nn]['paired']:assert len(points)==2,(nn,points)
    # Euclidean minimum spanning tree for multi-drop control networks.
    linked=[points[0]];unlinked=points[1:];i=0
    while unlinked:
        _,aa,bb=min((math.dist(x['pt'],y['pt']),ii,jj) for ii,x in enumerate(linked) for jj,y in enumerate(unlinked))
        e=unlinked.pop(bb);width=.075 if groups[nn]['kind'].startswith('TB3_') and groups[nn]['kind']!='TB3_CONTROL' else .10
        tasks.append(dict(net=nn,task_id=nn+f'__{i}',**groups[nn],a=linked[aa],b=e,width=width));linked.append(e);i+=1
assert sum(t['kind'].startswith(('E1S','CPU','CLOCK')) for t in tasks)==310,Counter(t['kind'] for t in tasks)
used=set();grounds=[]
for ref in ['U1','U502','U501','U503']+[f'J{k}' for k in range(1,11)]:
    f=b.FindFootprintByReference(ref);gs=[pp for pp in f.Pads() if pp.GetNetname()=='/GND'];pts=[z['pt'] for t in tasks for z in [t['a'],t['b']] if z['ref']==ref];target=[sum(z[k] for z in pts)/len(pts) for k in [0,1]]
    side=p.B_Cu if f.GetLayer()==p.B_Cu else p.F_Cu;span=(1,31) if side==p.B_Cu else (0,1)
    for j in range(4 if ref.startswith('U') else 2):
        choices=[pp for pp in gs if (ref,pp.GetNumber()) not in used and all(math.dist(xy(pp.GetPosition()),z)>.60 for z in pts) and all(net=='/GND' or hi<span[0] or lo>span[1] or math.dist(xy(pp.GetPosition()),other)>=.36 for other,lo,hi,net in allocated)]
        assert choices,ref
        pp=min(choices,key=lambda q:math.dist(xy(q.GetPosition()),(target[0]+(-2 if j%2 else 2),target[1]+(-2 if j<2 else 2))));used.add((ref,pp.GetNumber()));allocated.append((xy(pp.GetPosition()),*span,'/GND'))
        a.via(*xy(pp.GetPosition()),'/GND',p.In1_Cu,side,.25,.10);grounds.append(dict(ref=ref,pin=pp.GetNumber(),pt=xy(pp.GetPosition())))
vias=[];signal_layers={t['layer'] for t in tasks}
for via in b.GetTracks():
    if isinstance(via,p.PCB_VIA):vias.append(dict(net=via.GetNetname(),pt=xy(via.GetPosition()),diameter=.20 if via.GetNetname().startswith('/TBT_') else .25,layers=[l for l in signal_layers if via.IsOnLayer(l)]))
for f in b.GetFootprints():
    for pp in f.Pads():
        if pp.GetAttribute()==p.PAD_ATTRIB_NPTH:vias.append(dict(net='MECHANICAL_HOLE',pt=xy(pp.GetPosition()),diameter=max(xy(pp.GetDrillSize())),layers=list(signal_layers)))
(W/'route_tasks.json').write_text(json.dumps(dict(tasks=tasks,vias=vias,fanouts=fanouts,grid_mm=.025,clearance_mm=.08,selected_ground_balls=grounds,ground_plane_indices=list(range(1,29,3))),indent=2),encoding='utf-8')
p.SaveBoard(str(W/'Main.signal_vias.kicad_pcb'),b)
print('Prepared',len(tasks),'route sections /',len(by_net),'nets;',len(fanouts),'clock surface fanouts;',Counter(t['kind'] for t in tasks),flush=True)
