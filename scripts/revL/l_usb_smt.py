"""Apply the requested SMT shell concept without mislabelling it as a stock part."""
from pathlib import Path
import json,sys
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2')
sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
O=R/'outputs/PCIe_3board_RevL';folder=O/'Main_10E1S'
bp=folder/'Main_10E1S.kicad_pcb';b=p.LoadBoard(str(bp))
pro=(folder/'Main_10E1S.kicad_pro').read_bytes()
meta={q['ref']:q for q in json.loads((folder/'COMPONENTS.json').read_text(encoding='utf-8'))}
old='GCT_USB4160_24P_Vertical_7p46_DRAFT_TB5_UNQUALIFIED'
name='USB_C_24P_Vertical_SMT_Shell_7p46_CUSTOM_DRAFT'
uf=p.FootprintLoad(str(folder/'Local.pretty'),old)
assert uf
uf.SetFPID(p.LIB_ID('Local',name));uf.SetAttributes(p.FP_SMD)
uf.SetLibDescription('CUSTOM MECHANICAL CONCEPT: 24 signal contacts and four SMT shell feet. 7.46mm vertical envelope, two 0.71mm plastic locating holes retained. Based on USB4160 geometry but NOT compatible with the original through-hole shell part. Actual part, retention, current and TB5 qualification pending.')
for q in uf.Pads():
    if q.GetNumber()=='SH':
        q.SetAttribute(p.PAD_ATTRIB_SMD);q.SetLayerSet(layers(p.F_Cu,p.F_Mask,p.F_Paste))
        q.SetDrillSize(v(0,0));q.SetShape(p.PAD_SHAPE_ROUNDRECT);q.SetRoundRectRadiusRatio(.1)
a=object.__new__(Board);a.folder=folder;a.lib=folder/'Local.pretty';a.plugin=p.PCB_IO_MGR.FindPlugin(p.PCB_IO_MGR.KICAD_SEXP)
for xx in [-4,4]:
    for yy in [-1.43,1.43]:
        a.model(uf,'Custom_USB_C_SMT_shell_foot',1.4,.9,.2,(xx,yy,0),'0.63,0.65,0.68')
a.savefoot(uf)
for ref in ['J401','J402']:
    f=b.FindFootprintByReference(ref);f.SetFPID(p.LIB_ID('Local',name));f.SetAttributes(p.FP_SMD)
    for q in f.Pads():
        if q.GetNumber()=='SH':
            q.SetAttribute(p.PAD_ATTRIB_SMD);q.SetLayerSet(layers(p.B_Cu,p.B_Mask,p.B_Paste))
            q.SetDrillSize(v(0,0));q.SetShape(p.PAD_SHAPE_ROUNDRECT);q.SetRoundRectRadiusRatio(.1)
    f.Models().clear()
    for m in uf.Models():
        mm=p.FP_3DMODEL();mm.m_Filename=m.m_Filename;mm.m_Offset=m.m_Offset;mm.m_Rotation=m.m_Rotation;mm.m_Scale=m.m_Scale;f.Models().append(mm)
    val='CUSTOM 12V POWER / SMT SHELL DRAFT' if ref=='J401' else 'TB5 PORT / SMT SHELL DRAFT / PART TBD'
    f.SetValue(val)
    meta[ref].update(value=val,footprint=name,datasheet='',shell_mounting='four SMT pads; no metal-stake drill holes',plastic_locators='two 0.71mm NPTH retained',actual_orderable_part_verified=False,tb5_qualified=False,height_mm=7.46)
p.SaveBoard(str(bp),b);(folder/'Main_10E1S.kicad_pro').write_bytes(pro)
(folder/'COMPONENTS.json').write_text(json.dumps(list(meta.values()),ensure_ascii=False,indent=2),encoding='utf-8')
(O/'USB_MOUNTING_STATUS.json').write_text(json.dumps({'ports':['J401','J402'],'shell_pads_per_port':4,'shell_pad_type':'SMD','shell_holes_per_port':0,'plastic_locator_holes_per_port':2,'vertical':True,'pcb_rotation_degrees':90,'height_mm':7.46,'part_status':'custom mechanical draft; original USB4160 is not footprint compatible','tb5_qualified':False},indent=2),encoding='utf-8')
print('Both USB-C ports: four SMT shell pads each, zero metal-stake holes; plastic locators retained.')
