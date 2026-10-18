from pathlib import Path
import sys,json,shutil
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2')
sys.path.insert(0,str(R/'scripts/revJ'))
import i_common as c
from i_common import *
O=R/'outputs/PCIe_Main_RevM';c.ROOT=O
a=Board('Assembly_View',110,45,2)
for g in list(a.b.GetDrawings()):remove(a.b,g)
folder=O/'Main_10E1S';b=p.LoadBoard(str(folder/'Main_10E1S.kicad_pcb'))
for f in b.GetFootprints():
    cp=p.Cast_to_FOOTPRINT(f.Duplicate(False));a.b.Add(cp);cp.SetReference('M_'+f.GetReference());mods=[]
    for old in cp.Models():
        m=p.FP_3DMODEL();m.m_Offset=old.m_Offset;m.m_Rotation=old.m_Rotation;m.m_Scale=old.m_Scale
        path=Path(old.m_Filename.replace('${KIPRJMOD}',str(folder)));dest='M_'+path.name
        assert path.exists(),path
        shutil.copy2(path,a.models/dest);m.m_Filename='${KIPRJMOD}/models/'+dest;mods.append(m)
    cp.Models().clear()
    for m in mods:cp.Models().append(m)
    for q in cp.Pads():q.SetNetCode(0)
for g in b.GetDrawings():
    if g.GetLayer()==p.Edge_Cuts:a.b.Add(g.Duplicate())
for row in json.loads((O/'M2_PORTS.json').read_text(encoding='utf-8')):
    f=p.FOOTPRINT(a.b);f.SetReference('SSD_'+row['port']);f.SetValue('M.2 2280 VERTICAL ENVELOPE / NOT MANUFACTURER CAD')
    f.SetAttributes(p.FP_SMD|p.FP_EXCLUDE_FROM_BOM);a.b.Add(f);f.SetPosition(v(*row['position_mm']));f.Reference().SetVisible(False);f.Value().SetVisible(False)
    a.model(f,'M2_2280_vertical_board',22,.8,80,(0,0,2.84),'0.05,0.3,0.14')
    for j in range(4):a.model(f,'SSD_chip_envelope',14,1.2,12,(0,1.0,12+j*16),'0.12,0.13,0.15')
    f.SetOrientationDegrees(90)
p.SaveBoard(str(a.folder/'Assembly_View.kicad_pcb'),a.b)
(a.folder/'Assembly_View.kicad_pro').write_text(json.dumps(a.pro,indent=2),encoding='utf-8')
(a.folder/'ASSEMBLY_ONLY.txt').write_text('Single main PCB with four upright M.2 2280 SSD envelopes. No daughter PCBs or inter-board cables. Visualization only; electrical design is Main_10E1S. SSDs are mechanical envelopes, not manufacturer CAD.\n',encoding='utf-8')
print('Assembly: one main PCB, four vertical M.2 SSD envelopes, zero daughterboards and cables.',flush=True)
