"""Independent native copper and filled-island connectivity, not a current rating."""
from pathlib import Path
from collections import defaultdict,Counter
import sys,json,math
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_12VPower_RevV';F=O/'Main_12E1S';W=R/'work/revV';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
b=p.LoadBoard(str(F/'Main_12E1S.kicad_pcb'));d=json.loads((W/'power_geometry.json').read_text(encoding='utf-8'));fs={f.GetReference():f for f in b.GetFootprints()}
rails=set(d['planes'])|{'/GND'};controls={q['net'] for q in d['control_routes']};nets=rails|controls
cu=[p.F_Cu]+[getattr(p,f'In{i}_Cu') for i in range(1,31)]+[p.B_Cu]
parent={};points=defaultdict(set)
def find(k):
    if k not in parent:parent[k]=k
    while parent[k]!=k:parent[k]=parent[parent[k]];k=parent[k]
    return k
def union(x,z):parent[find(x)]=find(z)
def node(nn,pt,ll):
    key=(nn,tuple(round(z,5) for z in pt),ll);find(key);points[(nn,ll)].add(key);return key
for t in b.GetTracks():
    nn=t.GetNetname()
    if nn not in nets:continue
    if isinstance(t,p.PCB_VIA):
        ns=[node(nn,xy(t.GetPosition()),ll) for ll in cu if t.IsOnLayer(ll)]
        for z in ns[1:]:union(ns[0],z)
    else:union(node(nn,xy(t.GetStart()),t.GetLayer()),node(nn,xy(t.GetEnd()),t.GetLayer()))
checks=d['pad_stitches'][:]
for nn in controls:
    for ref,f in fs.items():
        for pp in f.Pads():
            if pp.GetNetname()==nn and pp.GetNumber():checks.append(dict(ref=ref,pin=pp.GetNumber(),net=nn,pad_pt=xy(pp.GetPosition()),side=f.GetLayer()))
by=defaultdict(set);padnodes=[]
for q in checks:
    pp=min((pp for pp in fs[q['ref']].Pads() if pp.GetNumber()==q['pin']),key=lambda pp:math.dist(xy(pp.GetPosition()),q['pad_pt']));ll=fs[q['ref']].GetLayer();nn=q['net'];nd=node(nn,xy(pp.GetPosition()),ll)
    # Native pad shape, including overlapping multi-piece QFN pads.
    for other in list(points[(nn,ll)]):
        if pp.HitTest(v(*other[1])):union(nd,other)
    by[nn].add(nd);padnodes.append((q,nd))
islands=[]
for zi,z in enumerate(b.Zones()):
    nn=z.GetNetname();ll=z.GetLayer()
    if nn not in rails:continue
    poly=z.GetFilledPolysList(ll);count=poly.OutlineCount();touched=set()
    for nd in list(points[(nn,ll)]):
        pt=v(*nd[1])
        for i in range(count):
            if poly.Contains(pt,i):union(nd,('zone',zi,i));touched.add(i)
    islands.append(dict(net=nn,layer=b.GetLayerName(ll),filled_islands=count,touched_islands=len(touched)))
report=[];bad=[]
for nn,nd in sorted(by.items()):
    groups=defaultdict(list)
    for q,n in padnodes:
        if q['net']==nn:groups[str(find(n))].append(q['ref']+'.'+q['pin'])
    entry=dict(net=nn,pads=sum(len(q) for q in groups.values()),connected_components=len(groups),groups=list(groups.values()))
    report.append(entry)
    if len(groups)!=1:bad.append(entry)
result=dict(checked_pad_connections=len(checks),net_count=len(report),all_selected_nets_connected=not bad,disconnected_nets=bad,nets=report,filled_zones=islands,current_and_thermal_validation=False,signal_integrity_validation=False,cpu_and_switch_vr_complete=False)
(O/'POWER_CONNECTIVITY.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('Audited',len(checks),'pads /',len(report),'power and local control nets; disconnected:',[(q['net'],q['connected_components']) for q in bad],flush=True)
