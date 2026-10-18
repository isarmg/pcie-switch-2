"""Place the two end sockets' AC capacitors in their inter-socket gap."""
from pathlib import Path
import sys,json,math
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_12slot_RevU';W=R/'work/revU';F=O/'Main_12E1S';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
b=p.LoadBoard(str(W/'Main.prepared.kicad_pcb'));d=json.loads((W/'route_tasks.json').read_text(encoding='utf-8'));m={q['ref']:q for q in json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'))}
a=object.__new__(Board);a.b=b;a.nets={q.GetNetname():q for q in b.GetNetInfo().NetsByNetcode().values()}
caps={f'C{k}' for k in range(4065,4081)}
for i,ref in enumerate(sorted(caps)):
    f=b.FindFootprintByReference(ref);f.SetOrientationDegrees(90);f.SetPosition(v(88,18+1.4*i));m[ref].update(x=88,y=18+1.4*i,rotation_deg=90)
for q in d['tasks']:
    hascap=any(q[e]['ref'] in caps for e in ['a','b'])
    if not hascap:continue
    oldlayer=q['layer'];q.update(layer=4,layer_index=1,layer_name='In1.Cu')
    for end in ['a','b']:
        e=q[end];f=b.FindFootprintByReference(e['ref']);pp=pad(f,e['pin']);old=e['pt'];center=xy(pp.GetPosition());pt=center
        if e['ref']=='J9':pt=(85.95,center[1])
        if oldlayer==0:a.via(*pt,q['net'],p.F_Cu,p.In30_Cu,.25,.1)
        else:
            vv=min((t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()==q['net']),key=lambda t:math.dist(xy(t.GetPosition()),old));assert math.dist(xy(vv.GetPosition()),old)<.000005;(vv.SetPosition(v(*pt)) if e['ref'] in caps else None)
            if e['ref'] not in caps:pt=xy(vv.GetPosition())
        e.update(pt=list(pt),pad_pt=list(center),fanout_mm=0)
cu=[p.F_Cu]+[getattr(p,f'In{i}_Cu') for i in range(1,31)]+[p.B_Cu]
d['vias']=[dict(net=t.GetNetname(),pt=xy(t.GetPosition()),diameter=p.ToMM(t.GetWidth(t.TopLayer())),layers=[ll for ll in cu if t.IsOnLayer(ll)]) for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
(W/'route_tasks.json').write_text(json.dumps(d,indent=2),encoding='utf-8');(F/'COMPONENTS.json').write_text(json.dumps(list(m.values()),indent=2),encoding='utf-8');p.SaveBoard(str(W/'Main.prepared.kicad_pcb'),b)
print('16 rotated 0201 capacitors in x=88mm socket gap; last two sockets fully use inner-layer AC sections.',flush=True)
