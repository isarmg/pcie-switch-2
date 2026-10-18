from pathlib import Path
from collections import defaultdict
import sys,json,math
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_12VPower_RevV';F=O/'Main_12E1S';W=R/'work/revV';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
bp=F/'Main_12E1S.kicad_pcb';b=p.LoadBoard(str(bp));m={q['ref']:q for q in json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'))};d=json.loads((W/'power_geometry.json').read_text(encoding='utf-8'));drc=json.loads((F/'DRC.json').read_text(encoding='utf-8'))
badnets={f'/S{k:02}_PWR_OV' for k in [4,6,9,10,11,12]}|{'/TBT_5V_PG','/TBT_5V_SS'}
for t in list(b.GetTracks()):
    if not isinstance(t,p.PCB_VIA) and t.GetNetname() in badnets:remove(b,t)
redirect=[];removed=set()
for vv in drc['violations']:
    if vv['type'] not in ['holes_co_located','hole_to_hole']:continue
    ids=[q['uuid'] for q in vv['items']];vs=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.m_Uuid.AsString() in ids]
    if len(vs)!=2:continue
    one,two=sorted(vs,key=lambda t:abs(t.BottomLayer()-t.TopLayer()),reverse=True)
    assert one.GetNetname()==two.GetNetname()
    old,pt=xy(two.GetPosition()),xy(one.GetPosition())
    if math.dist(old,pt)>.000004:redirect.append((one.GetNetname(),old,pt,p.F_Cu if one.IsOnLayer(p.F_Cu) and two.IsOnLayer(p.F_Cu) else p.B_Cu))
    removed.add(two.m_Uuid.AsString());remove(b,two)
# Small number of unrouted support parts needed room for the new local bypasses.
moved=['C1','C102','C726','U603']
for ref,x,y,ang in [('C1',8,41,0),('C102',8,4,0),('C726',12,4,0),('U603',8,10,0)]:
    f=b.FindFootprintByReference(ref)
    if f.GetLayer()!=p.B_Cu:f.Flip(f.GetPosition(),p.FLIP_DIRECTION_LEFT_RIGHT)
    f.SetOrientationDegrees(ang);f.SetPosition(v(x,y));m[ref].update(x=x,y=y,side='B',rotation_deg=ang)
p.SaveBoard(str(bp),b)
# Reuse the independently collision-tested power routing primitives.
src=Path(__file__).with_name('v_power.py').read_text(encoding='utf-8');prefix=src.split('# Source and return rail pad stitches.')[0]
prefix=prefix.replace("assert not (W/'power_geometry.json').exists(),'Do not duplicate routed power'",'')
prefix=prefix.replace("insert((x,z,rad,nn,ll,'pad',0))","insert((x,z,rad,nn,ll,'pad',0));insert(((p.ToMM(bb.GetX()),p.ToMM(bb.GetY())),(p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom())),0,nn,ll,'rect',0))")
prefix=prefix.replace('        limit=rad+rr+.079', '''        if kind=='rect':
            if (c[0]<=x[0]<=e[0] and c[1]<=x[1]<=e[1]) or (c[0]<=z[0]<=e[0] and c[1]<=z[1]<=e[1]):return False
            corners=[c,(e[0],c[1]),e,(c[0],e[1])]
            if any(dist(x,z,q,t)<rad+.079 for q,t in zip(corners,corners[1:]+corners[:1])):return False
            continue
        limit=rad+rr+.079''')
exec(compile(prefix,'power collision primitives','exec'),globals())
local=src[src.index('def localroute('):src.index('controlfailed=[]')].replace('def localroute(start,end,nn,width):','def localroute(start,end,nn,width,side=p.F_Cu):').replace('    side=p.F_Cu;rad=width/2','    rad=width/2')
exec(compile(local,'local routing','exec'),globals())
def legal_via(pt,nn,side,target,dia,dr):
    for ll in span(side,target):
        if not clear(pt,pt,nn,ll,dia/2,dr):return False
        for x,z,rr,net,layer,kind,hole in nearby(ll,pt,pt):
            if kind=='via' and math.dist(pt,x)<(dr+hole)/2+.251:return False
    return True
bridged=[]
for nn,old,pt,ll in redirect:
    path=localroute(old,pt,nn,.1,ll)
    for x,z in zip(path,path[1:]):track(x,z,nn,ll,.1)
    bridged.append(dict(net=nn,old_pt=old,new_pt=pt,layer=ll,points=path))
for ref in moved:
    f=fs[ref]
    for pp in f.Pads():
        nn=pp.GetNetname()
        if nn in planes:stitch(f,pp,nn,planes[nn])
        elif nn=='/GND':stitch(f,pp,nn,[p.In28_Cu])
newcontrols=[]
for nn in sorted(badnets):
    pts=list(dict.fromkeys(xy(pp.GetPosition()) for f in fs.values() for pp in f.Pads() if pp.GetNetname()==nn));connected=[pts[0]]
    for end in pts[1:]:
        start=min(connected,key=lambda pt:math.dist(pt,end));path=localroute(start,end,nn,.1)
        for x,z in zip(path,path[1:]):track(x,z,nn,p.F_Cu,.1)
        newcontrols.append(dict(net=nn,points=path,width=.1,layer=p.F_Cu));connected.append(end)
    print('Rerouted',nn,flush=True)
# Join the initial ground islands to another existing ground reference layer.
audit=json.loads((O/'POWER_CONNECTIVITY.json').read_text(encoding='utf-8'));extensions=[]
for item in audit['disconnected_nets']:
    if item['net']!='/GND':continue
    for group in item['groups'][1:]:
        success=False
        for key in group:
            ref,pn=key.split('.');f=fs[ref];pp=pad(f,pn);side=f.GetLayer();pt=xy(pp.GetPosition())
            vs=sorted((t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()=='/GND' and math.dist(xy(t.GetPosition()),pt)<2.5),key=lambda t:math.dist(xy(t.GetPosition()),pt))
            for t in vs[:8]:
                existing=set(ll for ll in cu if t.IsOnLayer(ll));newtargets=[p.In4_Cu,p.In7_Cu,p.In10_Cu] if side==p.F_Cu else [p.In25_Cu,p.In22_Cu,p.In19_Cu]
                for target in newtargets:
                    if target in existing:continue
                    lo,hi=sorted([t.TopLayer(),t.BottomLayer(),target],key=lambda ll:order[ll])[::2];newlayers=set(span(lo,hi))-existing
                    if all(clear(xy(t.GetPosition()),xy(t.GetPosition()),'/GND',ll,p.ToMM(t.GetWidth(t.TopLayer()))/2,p.ToMM(t.GetDrillValue())) for ll in newlayers):
                        t.SetLayerPair(lo,hi)
                        for ll in newlayers:insert((xy(t.GetPosition()),xy(t.GetPosition()),p.ToMM(t.GetWidth(t.TopLayer()))/2,'/GND',ll,'via',p.ToMM(t.GetDrillValue())))
                        extensions.append(dict(ref=ref,pin=pn,pt=xy(t.GetPosition()),target=b.GetLayerName(target)));success=True;break
                if success:break
            if success:break
        print('Ground island extension',group[:2],success,flush=True)
print('Refilling planes...',flush=True);b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(bp),b)
olddata=json.loads((W/'power_geometry.json').read_text(encoding='utf-8'));olddata['pad_stitches']=[q for q in olddata['pad_stitches'] if q['ref'] not in moved]+proof;olddata['control_routes']=[q for q in olddata['control_routes'] if q['net'] not in badnets]+newcontrols;olddata['removed_overlapping_vias']=len(removed);olddata['same_net_via_fanout_bridges']=bridged;olddata['ground_island_extensions']=extensions;olddata['failed_pad_stitches']=failed
(W/'power_geometry.json').write_text(json.dumps(olddata,indent=2),encoding='utf-8');(F/'COMPONENTS.json').write_text(json.dumps(list(m.values()),indent=2),encoding='utf-8')
print('Removed',len(removed),'overlapping vias; stitched moved pads',len(proof),'failed',len(failed),'ground extensions',len(extensions),flush=True)
