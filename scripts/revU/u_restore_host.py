"""Restore host controller above the USB ports, allowing its courtyard at x95.675."""
from pathlib import Path
import sys,json,math
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_12slot_RevU';W=R/'work/revU';F=O/'Main_12E1S';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
b=p.LoadBoard(str(W/'Main.prepared.kicad_pcb'));d=json.loads((W/'route_tasks.json').read_text(encoding='utf-8'));m={q['ref']:q for q in json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'))};f=b.FindFootprintByReference('U501');old=xy(f.GetPosition());gnds=[pp for pp in f.Pads() if pp.GetNetname()=='/GND'];groundvias=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()=='/GND' and any(pp.HitTest(t.GetPosition()) for pp in gnds)];delta=(90.1-old[0],11.9-old[1]);f.SetPosition(v(90.1,11.9));m['U501'].update(x=90.1,y=11.9)
for t in groundvias:t.Move(v(*delta))
for ref,xx in [('C5119',91.3),('C5120',93.6)]:
    q=b.FindFootprintByReference(ref);q.SetPosition(v(xx,5.5));m[ref].update(x=xx,y=5.5)
moving={'U501','C5119','C5120'};seen=set();changed=0
for q in d['tasks']+d['retained']:
    for end in ['a','b']:
        e=q[end]
        if e['ref'] not in moving:continue
        target=xy(pad(b.FindFootprintByReference(e['ref']),e['pin']).GetPosition());key=(q['net'],e['ref'],e['pin'])
        if key not in seen:
            vv=min((t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()==q['net']),key=lambda t:math.dist(xy(t.GetPosition()),e['pt']));assert math.dist(xy(vv.GetPosition()),e['pt'])<.000005;vv.SetPosition(v(*target));seen.add(key);changed+=1
        e.update(pt=list(target),pad_pt=list(target),fanout_mm=0)
cu=[p.F_Cu]+[getattr(p,f'In{i}_Cu') for i in range(1,31)]+[p.B_Cu]
d['vias']=[dict(net=t.GetNetname(),pt=xy(t.GetPosition()),diameter=p.ToMM(t.GetWidth(t.TopLayer())),layers=[ll for ll in cu if t.IsOnLayer(ll)]) for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
near=[]
for i,a in enumerate(d['vias']):
    for z in d['vias'][:i]:
        if a['net']!=z['net'] and set(a['layers'])&set(z['layers']) and math.dist(a['pt'],z['pt'])<.35-.000003:near.append((a['net'],a['pt'],z['net'],z['pt']))
assert not near,near[:8]
(W/'route_tasks.json').write_text(json.dumps(d,indent=2),encoding='utf-8');(F/'COMPONENTS.json').write_text(json.dumps(list(m.values()),indent=2),encoding='utf-8');p.SaveBoard(str(W/'Main.prepared.kicad_pcb'),b)
print('Restored U501 to (90.1,11.9); updated',changed,'signal via landings; no via drill spacing conflicts.',flush=True)
