from pathlib import Path
import sys,json,math
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_12slot_RevU';W=R/'work/revU';F=O/'Main_12E1S';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
b=p.LoadBoard(str(W/'Main.prepared.kicad_pcb'));d=json.loads((W/'route_tasks.json').read_text(encoding='utf-8'));m={q['ref']:q for q in json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'))};f=b.FindFootprintByReference('R5114');f.SetPosition(v(94.75,5.85));m['R5114'].update(x=94.75,y=5.85);seen=set()
for q in d['tasks']+d['retained']:
    for end in ['a','b']:
        e=q[end]
        if e['ref']!='R5114':continue
        pt=xy(pad(f,e['pin']).GetPosition())
        if q['net'] not in seen:
            vv=min((t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()==q['net']),key=lambda t:math.dist(xy(t.GetPosition()),e['pt']));vv.SetPosition(v(*pt));seen.add(q['net'])
        e.update(pt=list(pt),pad_pt=list(pt),fanout_mm=0)
def box(f):
    z=f.GetBoundingBox(False,False);return [p.ToMM(t) for t in [z.GetX(),z.GetY(),z.GetRight(),z.GetBottom()]]
def overlap(a,z):return a[0]<z[2]+.04 and a[2]>z[0]-.04 and a[1]<z[3]+.04 and a[3]>z[1]-.04
for ref in ['R126','R132','R140']:
    f=b.FindFootprintByReference(ref);old=xy(f.GetPosition());z=box(f);sizes=[z[0]-old[0],z[1]-old[1],z[2]-old[0],z[3]-old[1]];others=[box(x) for x in b.GetFootprints() if x.GetLayer()==f.GetLayer() and x.GetReference()!=ref]
    for x,y in sorted(((x/4,y/4) for x in range(4,380) for y in range(4,176)),key=lambda q:math.dist(q,old)):
        zz=[x+sizes[0],y+sizes[1],x+sizes[2],y+sizes[3]]
        if zz[0]<.5 or zz[1]<.5 or zz[2]>95.5 or zz[3]>44.5:continue
        if all(not overlap(zz,q) for q in others):f.SetPosition(v(x,y));m[ref].update(x=x,y=y);break
    else:raise RuntimeError(ref)
cu=[p.F_Cu]+[getattr(p,f'In{i}_Cu') for i in range(1,31)]+[p.B_Cu]
d['vias']=[dict(net=t.GetNetname(),pt=xy(t.GetPosition()),diameter=p.ToMM(t.GetWidth(t.TopLayer())),layers=[ll for ll in cu if t.IsOnLayer(ll)]) for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
(W/'route_tasks.json').write_text(json.dumps(d,indent=2),encoding='utf-8');(F/'COMPONENTS.json').write_text(json.dumps(list(m.values()),indent=2),encoding='utf-8');p.SaveBoard(str(W/'Main.prepared.kicad_pcb'),b)
print('Four small components cleared the restored controller and CC caps.',flush=True)
