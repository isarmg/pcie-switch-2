from pathlib import Path
import sys,json,math
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_12slot_RevU';W=R/'work/revU';F=O/'Main_12E1S';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
b=p.LoadBoard(str(W/'Main.prepared.kicad_pcb'));d=json.loads((W/'route_tasks.json').read_text(encoding='utf-8'));m={q['ref']:q for q in json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'))};caps={f'C{k}' for k in range(4065,4081)};vv=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA)];moving=[];ends=[]
for q in d['tasks']:
    for end in ['a','b']:
        e=q[end]
        if e['ref'] not in caps:continue
        t=min((t for t in vv if t.GetNetname()==q['net']),key=lambda t:math.dist(xy(t.GetPosition()),e['pt']));moving.append(t);ends.append(e)
other=[t for t in vv if t not in moving];shift=None
for dy in [.30,.35,.25,.4,.45,.5,-.3,-.35]:
    if all(math.dist((xy(t.GetPosition())[0],xy(t.GetPosition())[1]+dy),xy(z.GetPosition()))>=.355 for t in moving for z in other if t.GetNetname()!=z.GetNetname()):shift=dy;break
assert shift is not None
for t in moving:t.Move(v(0,shift))
for e in ends:
    for k in ['pt','pad_pt']:e[k][1]+=shift
for ref in caps:
    f=b.FindFootprintByReference(ref);f.Move(v(0,shift));m[ref]['y']=xy(f.GetPosition())[1]
cu=[p.F_Cu]+[getattr(p,f'In{i}_Cu') for i in range(1,31)]+[p.B_Cu]
d['vias']=[dict(net=t.GetNetname(),pt=xy(t.GetPosition()),diameter=p.ToMM(t.GetWidth(t.TopLayer())),layers=[ll for ll in cu if t.IsOnLayer(ll)]) for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
(W/'route_tasks.json').write_text(json.dumps(d,indent=2),encoding='utf-8');(F/'COMPONENTS.json').write_text(json.dumps(list(m.values()),indent=2),encoding='utf-8');p.SaveBoard(str(W/'Main.prepared.kicad_pcb'),b)
print('Capacitor bank shift',shift,'mm; all cross-net via center clearances >=0.355mm',flush=True)
