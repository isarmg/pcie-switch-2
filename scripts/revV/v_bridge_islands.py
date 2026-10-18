from pathlib import Path
from collections import defaultdict
import sys,json,math
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_12VPower_RevV';F=O/'Main_12E1S';W=R/'work/revV';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
audit=Path(__file__).with_name('v_audit_power.py').read_text(encoding='utf-8').split('report=[]')[0]
exec(compile(audit,'native filled copper graph','exec'),globals())
graph_points=points;graph_pads=padnodes
helper=Path(__file__).with_name('v_repair.py').read_text(encoding='utf-8');helper=helper[helper.index("src=Path(__file__).with_name('v_power.py')"):helper.index('bridged=[]')]
exec(compile(helper,'collision geometry','exec'),globals())
groups=defaultdict(lambda:defaultdict(list))
for q,n in graph_pads:groups[q['net']][find(n)].append(q)
results=[];unresolved=[]
for nn,gg in groups.items():
    if len(gg)<2:continue
    ordered=sorted(gg,key=lambda root:-len(gg[root]));main=ordered[0]
    for root in ordered[1:]:
        candidates=[]
        for t in b.GetTracks():
            if not isinstance(t,p.PCB_VIA) or t.GetNetname()!=nn:continue
            pt=xy(t.GetPosition());polytuple=tuple(round(z,5) for z in pt)
            for ll in cu:
                key=(nn,polytuple,ll)
                if t.IsOnLayer(ll) and key in parent:
                    rr=find(key)
                    if rr in [find(root),find(main)]:candidates.append((pt,ll,rr))
        pairs=[]
        for pt,ll,rr in candidates:
            if rr!=find(root):continue
            for qt,layer,rt in candidates:
                if layer==ll and rt==find(main):pairs.append((math.dist(pt,qt),ll,pt,qt))
        pairs.sort();success=False
        # Current plane first, then another shared existing span to cross a cut.
        perlayer=defaultdict(list)
        for pair in pairs:
            if len(perlayer[pair[1]])<3:perlayer[pair[1]].append(pair)
        choices=sorted((q for ps in perlayer.values() for q in ps),key=lambda q:(q[1] in [p.F_Cu,p.B_Cu],q[0]))
        errors=[]
        for width in ([.5,.3,.15,.1] if nn=='/VBANK_A' else [.15,.1]):
            for _,ll,start,end in choices:
                try:path=localroute(start,end,nn,width,ll)
                except RuntimeError as e:errors.append(str(e));continue
                for x,z in zip(path,path[1:]):track(x,z,nn,ll,width)
                union((nn,tuple(round(z,5) for z in start),ll),(nn,tuple(round(z,5) for z in end),ll))
                results.append(dict(net=nn,layer=b.GetLayerName(ll),width_mm=width,points=path,length_mm=sum(math.dist(x,z) for x,z in zip(path,path[1:])),joined_pads=[q['ref']+'.'+q['pin'] for q in gg[root]]));success=True;break
            if success:break
        if not success:unresolved.append(dict(net=nn,pads=[q['ref']+'.'+q['pin'] for q in gg[root]],errors=errors[-5:]))
        print('Island',nn,[q['ref']+'.'+q['pin'] for q in gg[root]][:3],success,flush=True)
print('Refill...',flush=True);b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(F/'Main_12E1S.kicad_pcb'),b)
(O/'POWER_ISLAND_BRIDGES.json').write_text(json.dumps(dict(bridges=results,unresolved=unresolved,current_capacity_qualified=False),indent=2),encoding='utf-8')
print('Copper island bridges:',len(results),'unresolved',len(unresolved),flush=True)
