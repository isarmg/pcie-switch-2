from pathlib import Path
import sys,json,math
sys.stdout.reconfigure(encoding='utf-8')
STAGE=Path(__file__).resolve().parents[2];R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_12slot_RevU';W=R/'work/revU';F=O/'Main_12E1S'
sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
b=p.LoadBoard(str(W/'Main.prepared.kicad_pcb'));a=object.__new__(Board);a.b=b;a.nets={q.GetNetname():q for q in b.GetNetInfo().NetsByNetcode().values()}
data=json.loads((W/'signal_routes.json').read_text(encoding='utf-8'));tasks=json.loads((W/'route_tasks.json').read_text(encoding='utf-8'));retained={q['task_id'] for q in tasks['retained']}
current=p.LoadBoard(str(F/'Main_12E1S.kicad_pcb'));paths={f.GetReference():f.GetPath() for f in current.GetFootprints()}
for f in b.GetFootprints():
    if f.GetReference() in paths:f.SetPath(paths[f.GetReference()])
for r in data['routes']:
    if r['task_id'] in retained:continue
    for aa,bb in zip(r['points'],r['points'][1:]):
        start,end=v(*aa),v(*bb)
        if start==end:continue
        t=p.PCB_TRACK(b);t.SetStart(start);t.SetEnd(end);t.SetNet(a.net(r['net']));t.SetLayer(r['layer']);t.SetWidth(p.FromMM(r['width']));b.Add(t)
for idx in range(1,29,3):
    a.zone('/GND',getattr(p,f'In{idx}_Cu'),[(.5,.5),(95.5,.5),(95.5,44.5),(.5,44.5)]);list(b.Zones())[-1].SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(F/'Main_12E1S.kicad_pcb'),b)
(O/'SIGNAL_ROUTES.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
(O/'SIGNAL_ROUTE_LENGTHS.json').write_text(json.dumps(data['pairs'],indent=2),encoding='utf-8')
print('Applied',len(data['routes']),'sections; filled ten ground zones',flush=True)
