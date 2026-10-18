"""Synchronize via IU coordinates after dimensional edits, then repick grounds."""
from pathlib import Path
import sys,json,math
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_12slot_RevU';W=R/'work/revU';F=O/'Main_12E1S';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
b=p.LoadBoard(str(W/'Main.prepared.kicad_pcb'));d=json.loads((W/'route_tasks.json').read_text(encoding='utf-8'));allvias=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA)];seen=set();changed=0
for q in d['tasks']+d['retained']:
    if q['layer']==0:continue
    for end in ['a','b']:
        e=q[end];key=(q['net'],tuple(e['pt']))
        if key in seen:continue
        seen.add(key);vv=min((t for t in allvias if t.GetNetname()==q['net']),key=lambda t:math.dist(xy(t.GetPosition()),e['pt']));dist=math.dist(xy(vv.GetPosition()),e['pt']);assert dist<.251,(q['net'],end,dist)
        if dist>.000003:vv.SetPosition(v(*e['pt']));changed+=1
# A small X offset escapes the existing CPU via without changing the slot.
for q in d['tasks']:
    if q['net']!='/S05_REFCLK0_P':continue
    e=next(q[k] for k in ['a','b'] if q[k]['ref']=='J5');old=e['pt'];e['pt']=[e['pad_pt'][0]-.35,e['pad_pt'][1]]
    vv=min((t for t in allvias if t.GetNetname()==q['net']),key=lambda t:math.dist(xy(t.GetPosition()),old));vv.SetPosition(v(*e['pt']))
for t in list(b.GetTracks()):
    if isinstance(t,p.PCB_VIA) and t.GetNetname()=='/GND':remove(b,t)
allvias=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
a=object.__new__(Board);a.b=b;a.nets={q.GetNetname():q for q in b.GetNetInfo().NetsByNetcode().values()}
cu=[p.F_Cu]+[getattr(p,f'In{i}_Cu') for i in range(1,31)]+[p.B_Cu]
for ref in ['U1','U502','U501','U503']+[f'J{k}' for k in range(1,13)]:
    f=b.FindFootprintByReference(ref);side=f.GetLayer();used=set()
    for i in range(2):
        pads=[pp for pp in f.Pads() if pp.GetNetname()=='/GND' and pp.GetNumber() not in used and all(t.GetNetname()=='/GND' or math.dist(xy(pp.GetPosition()),xy(t.GetPosition()))>=.365 for t in allvias)]
        assert pads,('ground',ref);pp=pads[0];used.add(pp.GetNumber());a.via(*xy(pp.GetPosition()),'/GND',p.In1_Cu,side,.25,.1);allvias=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
d['vias']=[dict(net=t.GetNetname(),pt=xy(t.GetPosition()),diameter=p.ToMM(t.GetWidth(t.TopLayer())),layers=[ll for ll in cu if t.IsOnLayer(ll)]) for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
(W/'route_tasks.json').write_text(json.dumps(d,indent=2),encoding='utf-8');p.SaveBoard(str(W/'Main.prepared.kicad_pcb'),b)
print('Corrected',changed,'via coordinates, offset S05 clock landing, repicked ground vias.',flush=True)
