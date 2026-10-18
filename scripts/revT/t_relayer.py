from pathlib import Path
import json,sys
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_82x45_TB3Host_RevT';F=O/'Main_10E1S'
sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import p,v,xy
links=json.loads((O/'TB3_LINKS.json').read_text(encoding='utf-8'))
for q in links:
    if not q.get('cap'):continue
    q['layer_index']=19 if q['group'].startswith('TBT_CPU_TX') else 22 if q['group'].startswith('TBT_AR_TX') else 25 if q['kind']=='TB3_DP' else 28
(O/'TB3_LINKS.json').write_text(json.dumps(links,indent=2),encoding='utf-8')
b=p.LoadBoard(str(F/'Main_10E1S.kicad_pcb'));meta={q['ref']:q for q in json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'))}
for i in range(4):
    ref=f'R{5111+i}';f=b.FindFootprintByReference(ref)
    if f.GetLayer()!=p.B_Cu:f.Flip(f.GetPosition(),p.FLIP_DIRECTION_LEFT_RIGHT)
    f.SetOrientationDegrees(0);f.SetPosition(v(76.95+1.2*i,5.85));meta[ref].update(x=76.95+1.2*i,y=5.85,side='B',rotation_deg=0)
p.SaveBoard(str(F/'Main_10E1S.kicad_pcb'),b);(F/'COMPONENTS.json').write_text(json.dumps(list(meta.values()),ensure_ascii=False,indent=2),encoding='utf-8')
print('TB3 high-speed groups on In19 / In22 / In25 / In28; local DP pull-downs; other placements preserved.')
