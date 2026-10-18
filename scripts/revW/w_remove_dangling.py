"""Remove relocation-only dead stubs on the still-unimplemented CPU decoupler."""
from pathlib import Path
import sys,json,math
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_USB12mm_RevW';F=O/'Main_12E1S';W=R/'work/revW';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
b=p.LoadBoard(str(F/'Main_12E1S.kicad_pcb'));drc=json.loads((F/'DRC.json').read_text(encoding='utf-8'));ids={item['uuid'] for q in drc['violations'] if q['type']=='track_dangling' for item in q['items']};removed=[]
for t in list(b.GetTracks()):
 if str(t.m_Uuid.AsString()) in ids:removed.append((t.GetNetname(),xy(t.GetStart()),xy(t.GetEnd())));remove(b,t)
assert len(removed)==2,removed
d=json.loads((W/'power_geometry.json').read_text(encoding='utf-8'))
def matches(q):
 return len(q.get('points',[]))==2 and any(q['net']==nn and ((math.dist(q['points'][0],x)<.000003 and math.dist(q['points'][1],z)<.000003) or (math.dist(q['points'][0],z)<.000003 and math.dist(q['points'][1],x)<.000003)) for nn,x,z in removed)
for key in ['ground_island_surface_routes','pending_cpu_rail_relocation_stubs']:d[key]=[q for q in d.get(key,[]) if not matches(q)]
p.SaveBoard(str(F/'Main_12E1S.kicad_pcb'),b);(W/'power_geometry.json').write_text(json.dumps(d,indent=2),encoding='utf-8');print('Removed',len(removed),'dead relocation stubs; real CPU supply still pending.',flush=True)
