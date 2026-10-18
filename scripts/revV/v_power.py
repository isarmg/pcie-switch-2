"""Draw protected SSD power, actual 3.3V/5V auxiliaries and their local controls.
Plane / via geometry is a study; no current or fabrication rating is inferred.
"""
from pathlib import Path
from collections import defaultdict
import sys,json,math,heapq
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_12VPower_RevV';F=O/'Main_12E1S';W=R/'work/revV';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
bp=F/'Main_12E1S.kicad_pcb';b=p.LoadBoard(str(bp));a=object.__new__(Board);a.b=b;a.nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
fs={f.GetReference():f for f in b.GetFootprints()};power=set(json.loads((W/'power_refs.json').read_text(encoding='utf-8')))
assert not (W/'power_geometry.json').exists(),'Do not duplicate routed power'
cu=[p.F_Cu]+[getattr(p,f'In{i}_Cu') for i in range(1,31)]+[p.B_Cu];order={ll:i for i,ll in enumerate(cu)}
planes={'/VIN_A':[p.In3_Cu],'/VIN_B':[p.In3_Cu],'/VBANK_A':[p.In5_Cu],'/VBANK_B':[p.In6_Cu],'/AUX_12V_PROTECTED':[p.In26_Cu],'/P3V3_AUX':[p.In2_Cu,p.In30_Cu],'/TBT_5V0':[p.In27_Cu],'/TBT_VBUS':[p.In29_Cu]}
for k,n in enumerate([8,9,11,12,14,15,17,18,20,21,23,24],1):planes[f'/P12_SLOT{k:02}']=[getattr(p,f'In{n}_Cu')]
def span(lo,hi):
    i,j=sorted([order[lo],order[hi]]);return cu[i:j+1]
def pointseg(q,x,z):
    dx,dy=z[0]-x[0],z[1]-x[1];den=dx*dx+dy*dy;t=max(0,min(1,((q[0]-x[0])*dx+(q[1]-x[1])*dy)/den)) if den else 0
    return math.dist(q,(x[0]+dx*t,x[1]+dy*t))
def ori(x,y,z):return (y[0]-x[0])*(z[1]-x[1])-(y[1]-x[1])*(z[0]-x[0])
def dist(x,z,c,e):
    if max(min(x[0],z[0]),min(c[0],e[0]))<=min(max(x[0],z[0]),max(c[0],e[0])) and max(min(x[1],z[1]),min(c[1],e[1]))<=min(max(x[1],z[1]),max(c[1],e[1])) and ori(x,z,c)*ori(x,z,e)<=0 and ori(c,e,x)*ori(c,e,z)<=0:return 0
    return min(pointseg(x,c,e),pointseg(z,c,e),pointseg(c,x,z),pointseg(e,x,z))
index=defaultdict(list);objects=[];CELL=2
def insert(obj):
    ix=len(objects);objects.append(obj);x,z,rad,nn,ll,kind,dr=obj
    for xx in range(math.floor((min(x[0],z[0])-rad-.5)/CELL),math.floor((max(x[0],z[0])+rad+.5)/CELL)+1):
        for yy in range(math.floor((min(x[1],z[1])-rad-.5)/CELL),math.floor((max(x[1],z[1])+rad+.5)/CELL)+1):index[(ll,xx,yy)].append(ix)
def nearby(ll,x,z):
    ids=set()
    for xx in range(math.floor(min(x[0],z[0])/CELL),math.floor(max(x[0],z[0])/CELL)+1):
        for yy in range(math.floor(min(x[1],z[1])/CELL),math.floor(max(x[1],z[1])/CELL)+1):ids.update(index[(ll,xx,yy)])
    return (objects[i] for i in ids)
for t in b.GetTracks():
    if isinstance(t,p.PCB_VIA):
        pt=xy(t.GetPosition())
        for ll in cu:
            if t.IsOnLayer(ll):insert((pt,pt,p.ToMM(t.GetWidth(t.TopLayer()))/2,t.GetNetname(),ll,'via',p.ToMM(t.GetDrillValue())))
    else:insert((xy(t.GetStart()),xy(t.GetEnd()),p.ToMM(t.GetWidth())/2,t.GetNetname(),t.GetLayer(),'track',0))
# Exact pad shapes are conservatively represented by their enclosing capsule.
for f in fs.values():
    for pp in f.Pads():
        if not pp.IsOnLayer(f.GetLayer()):continue
        bb=pp.GetBoundingBox();cx,cy=xy(pp.GetPosition());ww=p.ToMM(bb.GetWidth());hh=p.ToMM(bb.GetHeight());nn=pp.GetNetname();ll=f.GetLayer()
        if ww>=hh:x=(cx-(ww-hh)/2,cy);z=(cx+(ww-hh)/2,cy);rad=hh/2
        else:x=(cx,cy-(hh-ww)/2);z=(cx,cy+(hh-ww)/2);rad=ww/2
        insert((x,z,rad,nn,ll,'pad',0))
def clear(x,z,nn,ll,rad,dr=0):
    if min(x[0],z[0],x[1],z[1])<.4+rad or max(x[0],z[0])>95.6-rad or max(x[1],z[1])>44.6-rad:return False
    for c,e,rr,net,layer,kind,hole in nearby(ll,x,z):
        if net==nn:continue
        limit=rad+rr+.079
        if dr and kind=='via':limit=max(limit,(dr+hole)/2+.251)
        if dist(x,z,c,e)<limit:return False
    return True
def track(x,z,nn,ll,w):
    if v(*x)==v(*z):return
    t=p.PCB_TRACK(b);t.SetStart(v(*x));t.SetEnd(v(*z));t.SetNet(a.net(nn));t.SetLayer(ll);t.SetWidth(p.FromMM(w));b.Add(t);insert((x,z,w/2,nn,ll,'track',0))
added=[];proof=[];failed=[];controls=[]
def via(pt,nn,side,target,d=.2,dr=.1):
    lo,hi=sorted([side,target],key=lambda ll:order[ll]);a.via(*pt,nn,lo,hi,d,dr)
    for ll in span(lo,hi):insert((pt,pt,d/2,nn,ll,'via',dr))
    added.append(dict(net=nn,pt=pt,diameter=d,drill=dr,lo=lo,hi=hi))
def legal_via(pt,nn,side,target,d,dr):return all(clear(pt,pt,nn,ll,d/2,dr) for ll in span(side,target))
def stitch(f,pp,nn,targets):
    side=f.GetLayer();center=xy(pp.GetPosition());bb=pp.GetBoundingBox();ww=p.ToMM(bb.GetWidth());hh=p.ToMM(bb.GetHeight());ref=f.GetReference()
    large=min(ww,hh)>2.5;long=max(ww,hh)>1.5;d,dr=(.45,.25) if large else (.2,.1)
    wanted=24 if large else (5 if long else 1);candidates=[]
    if large:
        for dx in [0,-.7,.7,-1.4,1.4,-2.1,2.1,-2.8,2.8]:
            for dy in [0,-.7,.7,-1.4,1.4,-2.1,2.1]:
                pt=(center[0]+dx,center[1]+dy)
                if abs(dx)<ww/2-d/2-.04 and abs(dy)<hh/2-d/2-.04:candidates.append(pt)
    elif long:
        for off in [0,-.45,.45,-.9,.9,-1.35,1.35]:
            pt=(center[0]+(off if ww>=hh else 0),center[1]+(off if hh>ww else 0))
            if abs(off)<max(ww,hh)/2-d/2-.015:candidates.append(pt)
    else:candidates=[center]
    made=[];target=min(targets,key=lambda ll:abs(order[side]-order[ll]))
    for pt in candidates:
        if any(math.dist(pt,q)<dr+.251 for q in made):continue
        if legal_via(pt,nn,side,target,d,dr):via(pt,nn,side,target,d,dr);made.append(pt)
        if len(made)>=wanted:break
    if not made:
        # Short surface fanout to a legal blind via; keep the old signal copper intact.
        for radius in [.2,.4,.6,.8,1,1.4,1.8,2.3,3]:
            for ang in range(0,360,15):
                pt=(center[0]+radius*math.cos(math.radians(ang)),center[1]+radius*math.sin(math.radians(ang)))
                if legal_via(pt,nn,side,target,.2,.1) and clear(center,pt,nn,side,.05):
                    via(pt,nn,side,target);track(center,pt,nn,side,.1);made=[pt];break
            if made:break
    rec=dict(ref=ref,pin=pp.GetNumber(),net=nn,pad_pt=center,side=side,target_layer=target,via_centers_mm=made,desired_parallel_vias=wanted,parallel_via_target_met=len(made)>=wanted)
    (proof if made else failed).append(rec)
    return made
# Source and return rail pad stitches. Do not silently power unknown CPU or fake switch rails.
extra={'U601','U602','U501','U503','U510','U511','U512','U702','U607'}
groundrefs=power|extra|{f'J{k}' for k in range(1,13)}|{'J402'}
selected=[]
for f in fs.values():
    seen=set()
    for pp in f.Pads():
        nn=pp.GetNetname();key=(pp.GetNumber(),xy(pp.GetPosition()))
        if not pp.GetNumber() or key in seen:continue
        seen.add(key)
        if nn in planes:selected.append((f,pp,nn,planes[nn]))
        elif nn=='/GND' and (f.GetReference() in groundrefs or (f.GetReference().startswith('C') and any(q.GetNetname() in planes for q in f.Pads()))):selected.append((f,pp,nn,[p.In1_Cu] if f.GetLayer()==p.F_Cu else [p.In28_Cu]))
selected.sort(key=lambda z:(min(p.ToMM(z[1].GetSize().x),p.ToMM(z[1].GetSize().y))<2.5,z[2],z[0].GetReference()))
for i,(f,pp,nn,targets) in enumerate(selected):
    stitch(f,pp,nn,targets)
    if i%50==0:print('Power pad',i,'/',len(selected),'failed',len(failed),flush=True)
# Stitch both 3.3 V planes at substantial output pads, choosing legal locations.
bridges=[]
for ref in ['L31','C314','C315']:
    pp=next(q for q in fs[ref].Pads() if q.GetNetname()=='/P3V3_AUX');cx,cy=xy(pp.GetPosition())
    for dx in [0,-.3,.3]:
        for dy in [0,-.5,.5,-1,1]:
            pt=(cx+dx,cy+dy)
            if pp.HitTest(v(*pt)) and legal_via(pt,'/P3V3_AUX',p.F_Cu,p.In30_Cu,.2,.1):via(pt,'/P3V3_AUX',p.F_Cu,p.In30_Cu);bridges.append(pt)
# Route all short local eFuse control networks and both compact switch loops.
by=defaultdict(list)
for ref in power:
    for pp in fs[ref].Pads():
        nn=pp.GetNetname()
        if nn in planes or nn=='/GND' or nn.startswith('unconnected-') or not nn:continue
        if any(s in nn for s in ['_PWR_','/AUX_','/BUCK_','/TBT_5V_']):
            pt=xy(pp.GetPosition())
            if not any(math.dist(pt,z)<.000002 for z in by[nn]):by[nn].append(pt)
def localroute(start,end,nn,width):
    side=p.F_Cu;rad=width/2
    if clear(start,end,nn,side,rad):return [start,end]
    # Dense local search only: the grouped circuits occupy a few mm.
    grid=.05;x0=max(.5,min(start[0],end[0])-3);x1=min(95.5,max(start[0],end[0])+3);y0=max(.5,min(start[1],end[1])-3);y1=min(44.5,max(start[1],end[1])+3)
    sx,sy=(round(z/grid) for z in start);ex,ey=(round(z/grid) for z in end);s=(sx,sy);e=(ex,ey);best={s:0};prev={};heap=[(math.dist(s,e),0,s)];seen=set();cache={}
    def free(q):
        if q in [s,e]:return True
        if q not in cache:pt=(q[0]*grid,q[1]*grid);cache[q]=clear(pt,pt,nn,side,rad+.002)
        return cache[q]
    while heap:
        _,g,cur=heapq.heappop(heap)
        if cur in seen:continue
        if cur==e:break
        seen.add(cur)
        if len(seen)>70000:raise RuntimeError('bounded local power search')
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
            z=(cur[0]+dx,cur[1]+dy)
            if not(x0<=z[0]*grid<=x1 and y0<=z[1]*grid<=y1) or not free(z):continue
            if dx and dy and (not free((cur[0]+dx,cur[1])) or not free((cur[0],cur[1]+dy))):continue
            ng=g+math.hypot(dx,dy)
            if ng<best.get(z,1e90):best[z]=ng;prev[z]=cur;heapq.heappush(heap,(ng+1.3*math.dist(z,e),ng,z))
    else:raise RuntimeError('local power path unavailable')
    pts=[e]
    while pts[-1]!=s:pts.append(prev[pts[-1]])
    pts=[start]+[(x*grid,y*grid) for x,y in pts[::-1]]+[end];out=[]
    for pt in pts:
        if out and math.dist(out[-1],pt)<.0000001:continue
        while len(out)>1 and abs(ori(out[-2],out[-1],pt))<1e-9:out.pop()
        out.append(pt)
    if not all(clear(x,z,nn,side,rad-.000001) for x,z in zip(out,out[1:])):raise RuntimeError('power exact geometry check')
    return out
controlfailed=[]
for nn,pts in sorted(by.items(),key=lambda kv:('SW' not in kv[0],kv[0])):
    connected=[pts[0]];todo=pts[1:];width=.35 if nn in ['/BUCK_SW','/TBT_5V_SW'] else .1
    while todo:
        start,end=min(((x,z) for x in connected for z in todo),key=lambda q:math.dist(*q))
        try:
            path=localroute(start,end,nn,width)
            for x,z in zip(path,path[1:]):track(x,z,nn,p.F_Cu,width)
            controls.append(dict(net=nn,points=path,width=width,layer=p.F_Cu));connected.append(end);todo.remove(end)
        except RuntimeError as e:controlfailed.append(dict(net=nn,start=start,end=end,error=str(e)));connected.append(end);todo.remove(end)
    print('Control',nn,'remaining failed',len(controlfailed),flush=True)
for nn,ls in planes.items():
    for ll in ls:
        x0,x1=(.5,44.5) if nn=='/VIN_A' else (44.9,95.5) if nn=='/VIN_B' else (.5,95.5)
        a.zone(nn,ll,[(x0,.5),(x1,.5),(x1,44.5),(x0,44.5)])
        z=list(b.Zones())[-1];z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS);z.SetMinThickness(p.FromMM(.12));z.SetLocalClearance(p.FromMM(.1))
print('Filling power planes...',flush=True);b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(bp),b)
data=dict(planes={nn:[b.GetLayerName(ll) for ll in ls] for nn,ls in planes.items()},via_records=added,pad_stitches=proof,failed_pad_stitches=failed,control_routes=controls,failed_control_routes=controlfailed,aux_3v3_plane_bridges=bridges,thermal_and_current_capacity_qualified=False,blind_via_stackup_qualified=False,cpu_dynamic_vr_implemented=False,fictional_switch_regulators_implemented=False)
(W/'power_geometry.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
print('Power geometry:',len(added),'vias;',len(proof),'stitched pads;',len(failed),'failed pads;',len(controls),'controls;',len(controlfailed),'failed controls;',len(bridges),'3V3 plane bridges',flush=True)
