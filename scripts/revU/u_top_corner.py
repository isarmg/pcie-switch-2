from pathlib import Path
import sys,json,math
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_12slot_RevU';W=R/'work/revU';F=O/'Main_12E1S';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
b=p.LoadBoard(str(W/'Main.prepared.kicad_pcb'));d=json.loads((W/'route_tasks.json').read_text(encoding='utf-8'));m={q['ref']:q for q in json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'))};f=b.FindFootprintByReference('R5114');f.SetOrientationDegrees(90);f.SetPosition(v(95.3,5.7));m['R5114'].update(x=95.3,y=5.7,rotation_deg=90);b.FindFootprintByReference('L501').SetPosition(v(93.5,2.9));m['L501'].update(x=93.5,y=2.9);seen=set()
for q in d['tasks']+d['retained']:
    for end in ['a','b']:
        e=q[end]
        if e['ref']!='R5114':continue
        pt=xy(pad(f,e['pin']).GetPosition())
        if q['net'] not in seen:
            vv=min((t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()==q['net']),key=lambda t:math.dist(xy(t.GetPosition()),e['pt']));vv.SetPosition(v(*pt));seen.add(q['net'])
        e.update(pt=list(pt),pad_pt=list(pt),fanout_mm=0)
cu=[p.F_Cu]+[getattr(p,f'In{i}_Cu') for i in range(1,31)]+[p.B_Cu]
d['vias']=[dict(net=t.GetNetname(),pt=xy(t.GetPosition()),diameter=p.ToMM(t.GetWidth(t.TopLayer())),layers=[ll for ll in cu if t.IsOnLayer(ll)]) for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
(W/'route_tasks.json').write_text(json.dumps(d,indent=2),encoding='utf-8');(F/'COMPONENTS.json').write_text(json.dumps(list(m.values()),indent=2),encoding='utf-8');p.SaveBoard(str(W/'Main.prepared.kicad_pcb'),b)
print('R5114 rotated at (95.3,5.7); L501 shifted to (93.5,2.9).',flush=True)
