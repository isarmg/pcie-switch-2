from pathlib import Path
import sys,json
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_12VPower_RevV';F=O/'Main_12E1S';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
b=p.LoadBoard(str(F/'Main_12E1S.kicad_pcb'));drc=json.loads((F/'DRC.json').read_text(encoding='utf-8'));ids={q['uuid'] for vv in drc['violations'] if vv['type']=='via_dangling' for q in vv['items']};removed=[]
for t in list(b.GetTracks()):
    if isinstance(t,p.PCB_VIA) and t.m_Uuid.AsString() in ids:removed.append(dict(net=t.GetNetname(),pt=xy(t.GetPosition())));remove(b,t)
for t in b.GetDrawings():
    if isinstance(t,p.PCB_TEXT):
        print('Board annotation:',t.GetText().replace('\n',' | '))
        if 'ROUTED' in t.GetText() and 'POWER' in t.GetText():t.SetText('REV V - 12V SSD + AUX POWER STUDY; CPU / SWITCH VR PENDING')
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(F/'Main_12E1S.kicad_pcb'),b)
(O/'POWER_CLEANUP.json').write_text(json.dumps(dict(removed_unused_pad_stitches=removed),indent=2),encoding='utf-8');print('Removed',len(removed),'unused vias at old capacitor positions')
