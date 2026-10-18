from pathlib import Path
import sys,json
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
F=R/'outputs/PCIe_E1S_96x45_12VPower_RevV/Main_12E1S'
b=p.LoadBoard(str(F/'Main_12E1S.kicad_pcb'));m={q['ref']:q for q in json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'))}
for ref in ['J1','J11','U1','U502','U501','U503','J401','J402','U11','C101','R101','C1','C102','C726','U603','U604','L501']:
 f=b.FindFootprintByReference(ref);bb=f.GetBoundingBox(False,False)
 print(ref,xy(f.GetPosition()),f.GetLayer(),f.GetOrientationDegrees(),[round(p.ToMM(t),4) for t in [bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom()]],m[ref]['footprint'])
 print('nets',[(pp.GetNumber(),pp.GetNetname()) for pp in f.Pads()][:12])
print('Routes',len(json.loads((F.parent/'SIGNAL_ROUTES.json').read_text(encoding='utf-8'))['routes']))
