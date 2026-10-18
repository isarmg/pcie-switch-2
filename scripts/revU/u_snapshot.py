from pathlib import Path
import sys
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');F=R/'outputs/PCIe_E1S_96x45_12slot_RevU/Main_12E1S';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import p
b=p.LoadBoard(str(R/'work/revU/Main.prepared.kicad_pcb'));old=p.LoadBoard(str(F/'Main_12E1S.kicad_pcb'));paths={f.GetReference():f.GetPath() for f in old.GetFootprints()}
for f in b.GetFootprints():f.SetPath(paths[f.GetReference()])
p.SaveBoard(str(F/'Main_12E1S.kicad_pcb'),b)
