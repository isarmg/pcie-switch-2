from pathlib import Path
import sys,json
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');W=R/'work/revU';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import p
b=p.LoadBoard(str(W/'Main.prepared.kicad_pcb'));d=json.loads((W/'route_tasks.json').read_text(encoding='utf-8'));count=0
for t in b.GetTracks():
    if isinstance(t,p.PCB_VIA) and t.GetNetname()!='/GND':t.SetWidth(p.FromMM(.20));count+=1
for vv in d['vias']:
    if vv['net']!='/GND':vv['diameter']=.20
(W/'route_tasks.json').write_text(json.dumps(d,indent=2),encoding='utf-8');p.SaveBoard(str(W/'Main.prepared.kicad_pcb'),b)
print(count,'signal vias use provisional 0.20mm copper / 0.10mm drill; grounds remain 0.25mm.',flush=True)
