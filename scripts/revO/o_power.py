"""Copper for the four extra power-only ports, including isolated FB nets.

The six dedicated supply layers are geometry reservations, not an approved
high-current stackup. No protocol pads on the added ports receive copper.
"""
from pathlib import Path
import sys,json,math,heapq,collections
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');sys.path.insert(0,str(R/'scripts/revJ'))
import i_common as c
from i_common import *
O=R/'outputs/PCIe_AllM2_RevO';folder=O/'Main_27M2';bp=folder/'Main_27M2.kicad_pcb'
b=p.LoadBoard(str(bp));a=object.__new__(Board);a.b=b;a.nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
fs={f.GetReference():f for f in b.GetFootprints()};added=[];proof=[];points=collections.defaultdict(list)
source_layers={'/VBANK_B':p.In9_Cu,'/VIN_B':p.In11_Cu,'/GND':p.In12_Cu}
for k in range(1,5):source_layers[f'/P{k:02}_3V3']=getattr(p,f'In{2*k-1}_Cu');source_layers[f'/P{k:02}_FB']=getattr(p,f'In{2*k-1}_Cu')
# Through holes must be respected even when their copper does not span a
# particular power layer. Existing CPU blind vias remain unchanged.
holes=[(xy(t.GetPosition()),p.ToMM(t.GetDrillValue())) for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
for f in b.GetFootprints():
    for q in f.Pads():
        if q.GetDrillSize().x:holes.append((xy(q.GetPosition()),max(xy(q.GetDrillSize()))))
def stitch(f,q):
    nn=q.GetNetname();target=source_layers[nn];bb=q.GetBoundingBox();ww=p.ToMM(bb.GetWidth());hh=p.ToMM(bb.GetHeight());cx,cy=xy(q.GetPosition())
    def axis(sz):
        if sz>=1.65:return [-.6,0,.6]
        if sz>=1.15:return [-.42,0,.42]
        return [0]
    candidates=[(cx+dx,cy+dy) for dx in axis(ww) for dy in axis(hh)]
    made=[]
    for pt in candidates:
        if any(math.dist(pt,h)<.25+(.15+dr)/2-1e-6 for h,dr in holes):continue
        lo,hi=(p.F_Cu,target) if f.GetLayer()==p.F_Cu else (target,p.B_Cu)
        a.via(*pt,nn,lo,hi,d=.25,dr=.15);holes.append((pt,.15));made.append(pt);added.append((pt,nn,lo,hi))
    assert made,('no legal via center in pad',f.GetReference(),q.GetNumber(),xy(q.GetPosition()))
    points[nn].extend(made);proof.append({'reference':f.GetReference(),'pad':q.GetNumber(),'net':nn,'via_centers_mm':made,'plane':b.GetLayerName(target)})
targets=[]
for k in range(1,5):
    refs=[f'J{7000+k}',f'U{7000+k}']+[f'C{7000+k*20+i}' for i in range(1,7)]+[f'R{7000+k*10+i}' for i in [1,2]]
    for ref in refs:
        f=fs[ref]
        for q in f.Pads():
            if q.GetNetname() in source_layers:targets.append((f,q))
targets += [(fs['J12'],q) for q in fs['J12'].Pads()]+[(fs['F2'],q) for q in fs['F2'].Pads()]
for f,q in targets:stitch(f,q)

# Route each feedback divider on its dedicated output layer. A small grid
# search avoids the new via barrels; the power zone subsequently clears it.
step=.1;nx=1200;ny=450
def route(nn,start,end,layer):
    obstacles=[(xy(t.GetPosition()),p.ToMM(t.GetWidth())/2+.075+.075+.025) for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.IsOnLayer(layer) and t.GetNetname()!=nn]
    blocked=set()
    for (x,y),rad in obstacles:
        for ix in range(max(4,math.floor((x-rad)/step)),min(nx-4,math.ceil((x+rad)/step))+1):
            for iy in range(max(4,math.floor((y-rad)/step)),min(ny-4,math.ceil((y+rad)/step))+1):
                if math.hypot(ix*step-x,iy*step-y)<rad:blocked.add((ix,iy))
    s=tuple(round(x/step) for x in start);e=tuple(round(x/step) for x in end)
    assert s not in blocked and e not in blocked,(nn,start,end,'blocked endpoint')
    costs={s:0};prev={};todo=[(math.dist(s,e),0,s)]
    while todo:
        _,g,cur=heapq.heappop(todo)
        if g!=costs.get(cur):continue
        if cur==e:break
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
            q=(cur[0]+dx,cur[1]+dy)
            if not (4<=q[0]<=nx-4 and 4<=q[1]<=ny-4) or q in blocked:continue
            if dx and dy and ((cur[0]+dx,cur[1]) in blocked or (cur[0],cur[1]+dy) in blocked):continue
            ng=g+(math.sqrt(2) if dx and dy else 1)
            if ng<costs.get(q,1e99):costs[q]=ng;prev[q]=cur;heapq.heappush(todo,(ng+math.dist(q,e),ng,q))
    assert e in costs,(nn,'feedback path unavailable')
    routepts=[e]
    while routepts[-1]!=s:routepts.append(prev[routepts[-1]])
    routepts.reverse();path=[start]+[(x*step,y*step) for x,y in routepts]+[end]
    # Collapse collinear grid runs, preserving exact via centers at the ends.
    compact=[]
    for q in path:
        if compact and math.dist(compact[-1],q)<1e-8:continue
        while len(compact)>1:
            aa,zz=compact[-2:];cross=(zz[0]-aa[0])*(q[1]-zz[1])-(zz[1]-aa[1])*(q[0]-zz[0])
            if abs(cross)>1e-8:break
            compact.pop()
        compact.append(q)
    for aa,zz in zip(compact,compact[1:]):a.track(aa,zz,nn,layer,.15)
    return compact
fbproof=[]
for k in range(1,5):
    nn=f'/P{k:02}_FB';layer=source_layers[nn];pts=points[nn];connected=[pts[0]]
    for target in pts[1:]:
        start=min(connected,key=lambda q:math.dist(q,target));path=route(nn,start,target,layer);fbproof.append({'net':nn,'path_mm':path,'layer':b.GetLayerName(layer)});connected.append(target)
for nn,layer in source_layers.items():
    if nn=='/GND' or nn.endswith('_FB'):continue
    a.zone(nn,layer,[(.4,.4),(119.6,.4),(119.6,44.6),(.4,44.6)])
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(bp),b)
proofobj={'ports':['P01','P02','P03','P04'],'power_vias_added':len(added),'pad_connections':proof,'feedback_routes':fbproof,'plane_assignments':{nn:b.GetLayerName(ll) for nn,ll in source_layers.items()},'via_diameter_mm':.25,'via_drill_mm':.15,'stackup_fabrication_and_current_rating_qualified':False,'all_protocol_pads_on_power_only_ports_NC':True,'thermal_qualified':False}
(O/'POWER_ONLY_ROUTING.json').write_text(json.dumps(proofobj,indent=2),encoding='utf-8')
status={'cpu_x4_and_refclock_copper_connections':34,'data_slots':23,'power_only_slots':4,'slot_data_net_assignments_complete':True,'slot_protocol_routing_complete':False,'new_power_only_planes_and_pad_stitches_drawn':True,'new_power_feedback_routes_drawn':True,'whole_board_power_routing_complete':False,'impedance_validated':False,'thermal_qualified':False,'production_ready':False}
(folder/'ROUTING_STATUS.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
print('Power-only copper:',len(added),'vias,',len(proof),'pad connections,',len(fbproof),'feedback paths.',flush=True)
