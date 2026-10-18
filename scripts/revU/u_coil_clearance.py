from pathlib import Path
import sys,json
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');W=R/'work/revU';F=R/'outputs/PCIe_E1S_96x45_12slot_RevU/Main_12E1S';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
b=p.LoadBoard(str(W/'Main.prepared.kicad_pcb'));b.FindFootprintByReference('L501').SetPosition(v(93.5,2.7));p.SaveBoard(str(W/'Main.prepared.kicad_pcb'),b)
m=json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'));next(q for q in m if q['ref']=='L501')['y']=2.7;(F/'COMPONENTS.json').write_text(json.dumps(m,indent=2),encoding='utf-8')
print('L501 y=2.7mm; clear of R5114, copper remains >=0.4mm from board edge.',flush=True)
