from pathlib import Path
import sys
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
b=p.LoadBoard(str(R/'outputs/PCIe_E1S_96x45_USB12mm_RevW/Main_12E1S/Main_12E1S.kicad_pcb'))
for f in b.GetFootprints():
 x,y=xy(f.GetPosition())
 if not(16<x<29 and 1<y<13 and f.GetLayer()==p.F_Cu):continue
 boxes=[g.GetBoundingBox() for g in f.GraphicalItems() if g.GetLayer()==p.F_CrtYd]
 print(f.GetReference(),xy(f.GetPosition()),str(f.GetFPID().GetLibItemName()),[(p.ToMM(q.GetX()),p.ToMM(q.GetY()),p.ToMM(q.GetRight()),p.ToMM(q.GetBottom())) for q in boxes],flush=True)
