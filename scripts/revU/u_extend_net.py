from pathlib import Path
import sys,json
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');W=R/'work/revU';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
b=p.LoadBoard(str(W/'Main.prepared.kicad_pcb'));d=json.loads((W/'route_tasks.json').read_text(encoding='utf-8'));prefixes=sys.argv[1:];assert prefixes
count=0
for t in b.GetTracks():
    if not isinstance(t,p.PCB_VIA) or not any(t.GetNetname().startswith(s) for s in prefixes):continue
    if t.IsOnLayer(p.B_Cu):t.SetLayerPair(p.In1_Cu,p.B_Cu)
    else:t.SetLayerPair(p.F_Cu,p.In30_Cu)
    t.SetViaType(p.VIATYPE_BLIND);count+=1
cu=[p.F_Cu]+[getattr(p,f'In{i}_Cu') for i in range(1,31)]+[p.B_Cu]
d['vias']=[dict(net=t.GetNetname(),pt=xy(t.GetPosition()),diameter=p.ToMM(t.GetWidth(t.TopLayer())),layers=[ll for ll in cu if t.IsOnLayer(ll)]) for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
(W/'route_tasks.json').write_text(json.dumps(d,indent=2),encoding='utf-8');p.SaveBoard(str(W/'Main.prepared.kicad_pcb'),b)
print('Extended',count,'provisional signal via spans for',prefixes,flush=True)
