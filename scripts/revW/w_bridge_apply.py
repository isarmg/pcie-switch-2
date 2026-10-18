from pathlib import Path
import sys,json
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_USB12mm_RevW';F=O/'Main_12E1S';W=R/'work/revW';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
b=p.LoadBoard(str(W/'bridge/Base.kicad_pcb'));a=object.__new__(Board);a.b=b;a.nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()};pd=json.loads((W/'power_geometry.json').read_text(encoding='utf-8'));rr=json.loads((W/'bridge/signal_routes.json').read_text(encoding='utf-8'))['routes']
for r in rr:
 for i,(x,z) in enumerate(zip(r['points'],r['points'][1:])):
  if v(*x)==v(*z):continue
  t=p.PCB_TRACK(b);t.SetStart(v(*x));t.SetEnd(v(*z));t.SetNet(a.net(r['net']));t.SetLayer(r['layer']);t.SetWidth(p.FromMM(r.get('segment_widths',[r['width']]*(len(r['points'])-1))[i]));b.Add(t)
pd.setdefault('ground_island_surface_routes',[]).extend([q for q in pd['control_routes'] if q['net']=='/GND']);pd['control_routes']=[q for q in pd['control_routes'] if q['net']!='/GND']
pd['control_routes']+=rr;pd['island_bridge_via_extensions']=json.loads((W/'bridge/extensions.json').read_text(encoding='utf-8'))
print('Fill corrected power islands...',flush=True);b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(F/'Main_12E1S.kicad_pcb'),b);(W/'power_geometry.json').write_text(json.dumps(pd,indent=2),encoding='utf-8')
print('Applied',len(rr),'power continuity bridges.',flush=True)
