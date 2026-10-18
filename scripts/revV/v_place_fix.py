from pathlib import Path
import sys,json
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');F=R/'outputs/PCIe_E1S_96x45_12VPower_RevV/Main_12E1S';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
b=p.LoadBoard(str(F/'Main_12E1S.kicad_pcb'));m={q['ref']:q for q in json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'))}
for k in range(1,13):
    f=b.FindFootprintByReference(f'C{9100+k}');f.SetOrientationDegrees(90);f.Move(v(1.1,0))
    if k in [1,7]:
        for j in range(1,5):b.FindFootprintByReference(f'R{100+5*(k-1)+j}').Move(v(.1,0))
f=b.FindFootprintByReference('C9130');f.SetOrientationDegrees(90);f.Move(v(1.1,0))
for ref,x,y,ang in [('D2',91.5,42.4,0),('C5161',92.1,3.4,90),('C5162',94.4,3.4,0)]:
    f=b.FindFootprintByReference(ref);f.SetOrientationDegrees(ang);f.SetPosition(v(x,y))
for ref,q in m.items():
    f=b.FindFootprintByReference(ref);q.update(x=xy(f.GetPosition())[0],y=xy(f.GetPosition())[1],rotation_deg=f.GetOrientationDegrees())
(F/'COMPONENTS.json').write_text(json.dumps(list(m.values()),indent=2),encoding='utf-8');p.SaveBoard(str(F/'Main_12E1S.kicad_pcb'),b)
print('Adjusted local input caps, edge resistors, TVS and 5V input bypass.')
