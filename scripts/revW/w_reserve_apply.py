from pathlib import Path
import sys,json
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_USB12mm_RevW';F=O/'Main_12E1S';W=R/'work/revW';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
b=p.LoadBoard(str(W/'reserve/Base.kicad_pcb'));a=object.__new__(Board);a.b=b;a.nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
new=json.loads((W/'reserve/signal_routes.json').read_text(encoding='utf-8'))['routes'];sd=json.loads((O/'SIGNAL_ROUTES.json').read_text(encoding='utf-8'));pd=json.loads((W/'power_geometry.json').read_text(encoding='utf-8'));by={q['task_id']:q for q in new}
for r in new:
 for x,z in zip(r['points'],r['points'][1:]):
  if v(*x)==v(*z):continue
  t=p.PCB_TRACK(b);t.SetStart(v(*x));t.SetEnd(v(*z));t.SetNet(a.net(r['net']));t.SetLayer(r['layer']);t.SetWidth(p.FromMM(r['width']));b.Add(t)
sd['routes']=[by.get(q['task_id'],q) for q in sd['routes']];pd['control_routes']=[by.get(q.get('task_id'),q) for q in pd['control_routes']]
print('Fill continuous input and 3.3V planes...',flush=True);b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(F/'Main_12E1S.kicad_pcb'),b)
(O/'SIGNAL_ROUTES.json').write_text(json.dumps(sd,indent=2),encoding='utf-8');(W/'power_geometry.json').write_text(json.dumps(pd,indent=2),encoding='utf-8')
print('Moved',len(new),'sections off input and 3.3V planes.',flush=True)
