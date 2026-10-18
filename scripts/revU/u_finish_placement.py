from pathlib import Path
import sys,json,math
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_12slot_RevU';W=R/'work/revU';F=O/'Main_12E1S';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
b=p.LoadBoard(str(W/'Main.prepared.kicad_pcb'));d=json.loads((W/'route_tasks.json').read_text(encoding='utf-8'));m={q['ref']:q for q in json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'))}
for nn in ['/S10_SW_RX0_N','/S10_SW_RX0_P','/S10_SW_RX2_P']:
    for q in d['tasks']:
        if q['net']!=nn:continue
        e=next(q[k] for k in ['a','b'] if q[k]['ref']=='J10');old=e['pt'];e['pt']=[89.95,e['pad_pt'][1]]
        vv=min((t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()==nn),key=lambda t:math.dist(xy(t.GetPosition()),old));vv.SetPosition(v(*e['pt']))
def box(f):
    z=f.GetBoundingBox(False,False);return [p.ToMM(t) for t in [z.GetX(),z.GetY(),z.GetRight(),z.GetBottom()]]
def overlap(a,z):return a[0]<z[2]+.03 and a[2]>z[0]-.03 and a[1]<z[3]+.03 and a[3]>z[1]-.03
for ref in ['TP701','TP703']:
    f=b.FindFootprintByReference(ref);old=xy(f.GetPosition());z=box(f);sz=[z[0]-old[0],z[1]-old[1],z[2]-old[0],z[3]-old[1]];other=[box(q) for q in b.GetFootprints() if q.GetLayer()==f.GetLayer() and q.GetReference()!=ref]
    choices=sorted(((x/4,y/4) for y in range(4,176) for x in range(4,380)),key=lambda t:math.dist(t,old))
    for x,y in choices:
        zz=[x+sz[0],y+sz[1],x+sz[2],y+sz[3]]
        if zz[0]<.5 or zz[1]<.5 or zz[2]>95.5 or zz[3]>44.5:continue
        if all(not overlap(zz,bb) for bb in other):f.SetPosition(v(x,y));m[ref].update(x=x,y=y);break
    else:raise RuntimeError(ref)
cu=[p.F_Cu]+[getattr(p,f'In{i}_Cu') for i in range(1,31)]+[p.B_Cu]
d['vias']=[dict(net=t.GetNetname(),pt=xy(t.GetPosition()),diameter=p.ToMM(t.GetWidth(t.TopLayer())),layers=[ll for ll in cu if t.IsOnLayer(ll)]) for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
(W/'route_tasks.json').write_text(json.dumps(d,indent=2),encoding='utf-8');(F/'COMPONENTS.json').write_text(json.dumps(list(m.values()),indent=2),encoding='utf-8');p.SaveBoard(str(W/'Main.prepared.kicad_pcb'),b)
print('Fixed three via drill clearances and two test-point placements.',flush=True)
