from pathlib import Path
import sys,json,math
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_USB12mm_RevW';F=O/'Main_12E1S';W=R/'work/revW';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
b=p.LoadBoard(str(W/'Main.prepared.kicad_pcb'));a=object.__new__(Board);a.b=b;a.nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
current=p.LoadBoard(str(F/'Main_12E1S.kicad_pcb'));paths={f.GetReference():f.GetPath() for f in current.GetFootprints()}
for f in b.GetFootprints():
 if f.GetReference() in paths:f.SetPath(paths[f.GetReference()])
sd=json.loads((W/'signal_routes.json').read_text(encoding='utf-8'));data=json.loads((W/'route_tasks.json').read_text(encoding='utf-8'));retained={q['task_id'] for q in data['retained']};pd=json.loads((W/'power_geometry.json').read_text(encoding='utf-8'));ctrl=[]
for r in sd['routes']:
 if r['task_id'] in retained:continue
 for x,z in zip(r['points'],r['points'][1:]):
  if v(*x)==v(*z):continue
  t=p.PCB_TRACK(b);t.SetStart(v(*x));t.SetEnd(v(*z));t.SetNet(a.net(r['net']));t.SetLayer(r['layer']);t.SetWidth(p.FromMM(r['width']));b.Add(t)
 if r.get('kind')=='POWER_CONTROL':ctrl.append(r)
pd['control_routes']+=ctrl;sd['routes']=[q for q in sd['routes'] if q.get('kind')!='POWER_CONTROL'];assert len(sd['routes'])==523
print('Fill native power and ground zones...',flush=True);b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(F/'Main_12E1S.kicad_pcb'),b)
(O/'SIGNAL_ROUTES.json').write_text(json.dumps(sd,indent=2),encoding='utf-8');(W/'power_geometry.json').write_text(json.dumps(pd,indent=2),encoding='utf-8')
print('Applied',len(sd['routes']),'signal sections;',len(ctrl),'inner power controls',flush=True)
