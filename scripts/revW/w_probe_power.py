from pathlib import Path
import json,sys
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
F=R/'outputs/PCIe_E1S_96x45_USB12mm_RevW/Main_12E1S';b=p.LoadBoard(str(F/'Main_12E1S.kicad_pcb'))
for nn in ['/PEX09_FSEL','/PEX09_VSEL','/PEX09_SW']:
 print('NET',nn)
 for f in b.GetFootprints():
  for pp in f.Pads():
   if pp.GetNetname()==nn:print('PAD',f.GetReference(),pp.GetNumber(),xy(pp.GetPosition()),xy(pp.GetSize()),f.GetLayer())
 for t in b.GetTracks():
  if t.GetNetname()!=nn:continue
  if isinstance(t,p.PCB_VIA):print('VIA',xy(t.GetPosition()),t.TopLayer(),t.BottomLayer())
  else:print('TRACK',xy(t.GetStart()),xy(t.GetEnd()),t.GetLayer())
