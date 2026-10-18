"""Rev W ECO: level-shift CPU PERST into the always-on 3.3-V supervisor domain.

Requires KiCad 10 pcbnew. Reuses the independent U511 AXC translator, not a
Thunderbolt state machine. A 10k pulldown keeps MR low when that translator is
isolated. Brownout transitions and all load leakage remain unqualified.
"""
from pathlib import Path
import json,re,uuid
import pcbnew as p
from w_power_models import DESIGN

F=DESIGN
SOURCE='https://www.ti.com/lit/ds/symlink/tps3808.pdf'
RAIL='/P3V3_AUX'
MR='/TBT_PCIE_PERST_3V3_N'
CAP='C9040'
FOOT='C_0201_DenseCourtyard_1p0x0p4'
VALUE='100nF 6.3V X5R / U605 local bypass'
UID=str(uuid.uuid5(uuid.NAMESPACE_URL,'pcie-switch-2/RevW/U605-bypass'))

def v(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def display_name(name):return name.replace('{slash}','/')
def xy(q):return (p.ToMM(q.x),p.ToMM(q.y))
def end(text,start):
    depth=0;quoted=False;escaped=False
    for i in range(start,len(text)):
        ch=text[i]
        if quoted:
            if escaped:escaped=False
            elif ch=='\\':escaped=True
            elif ch=='"':quoted=False
        elif ch=='"':quoted=True
        elif ch=='(':depth+=1
        elif ch==')':
            depth-=1
            if depth==0:return i+1
    raise ValueError('unbalanced expression')

def schematic():
    path=F/'Connectivity_54.kicad_sch';text=path.read_text()
    for oldnet in ['/P3V3_AUX','/CPU_VCCPRIM_1P8']:
        text=text.replace(f'(global_label "{oldnet}" (shape passive) (at 233.68 204.47 0)',f'(global_label "{RAIL}" (shape passive) (at 233.68 204.47 0)')
    text=text.replace('(global_label "/CPU_PERST_1V8_N" (shape passive) (at 203.2 204.47 180)',f'(global_label "{MR}" (shape passive) (at 203.2 204.47 180)')
    path.write_text(text)
    path=F/'Connectivity_55.kicad_sch';text=path.read_text()
    root=re.search(r'\(uuid "([^"]+)"',text).group(1)
    projectpath=re.search(r'\(instances \(project "Main_12E1S" \(path "([^"]+)"',text).group(1)
    if f'PART_{CAP}' not in text:
        fx='(effects (font (size 0.8 0.8)))'
        definition=f'''(symbol "PART_{CAP}" (pin_names (offset .5)) (in_bom yes) (on_board yes)
(property "Reference" "C" (at 0 0 0) {fx})
(property "Value" "{VALUE}" (at 0 0 0) {fx})
(property "Footprint" "Local:{FOOT}" (at 0 0 0) {fx})
(symbol "PART_{CAP}_1_1" (rectangle (start -12.7 3.81) (end 12.7 -3.81) (stroke (width .254) (type default)) (fill (type background)))
(pin passive line (at -15.24 0 0) (length 2.54) (name "1" {fx}) (number "1" {fx}))
(pin passive line (at 15.24 0 180) (length 2.54) (name "2" {fx}) (number "2" {fx}))))'''
        i=end(text,text.index('(lib_symbols'))-1
        text=text[:i]+definition.replace(f'"PART_{CAP}"',f'"Local:PART_{CAP}"',1)+'\n'+text[i:]
        instance=f'''(symbol (lib_id "Local:PART_{CAP}") (at 218.44 201.93 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{UID}")
(property "Reference" "{CAP}" (at 218.44 193.12 0) {fx})
(property "Value" "{VALUE}" (at 218.44 190.12 0) {fx})
(property "Footprint" "Local:{FOOT}" (at 218.44 201.93 0) {fx})
(pin "1" (uuid "{uuid.uuid5(uuid.UUID(UID),'pin1')}")) (pin "2" (uuid "{uuid.uuid5(uuid.UUID(UID),'pin2')}"))
(instances (project "Main_12E1S" (path "{projectpath}" (reference "{CAP}") (unit 1)))))
(global_label "{RAIL}" (shape passive) (at 203.2 201.93 180) (effects (font (size .8 .8)) (justify right)) (uuid "{uuid.uuid5(uuid.UUID(UID),'label1')}"))
(global_label "/GND" (shape passive) (at 233.68 201.93 0) (effects (font (size .8 .8)) (justify left)) (uuid "{uuid.uuid5(uuid.UUID(UID),'label2')}"))
(text "U605 VDD/MR share CPU 1.8V domain; minimum VDD >=1.7V required. CPU rail and reset routing remain incomplete." (at 20.32 238.76 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{uuid.uuid5(uuid.UUID(UID),'note')}"))
'''
        text=text.rstrip()[:-1]+instance+')\n';path.write_text(text)
        path=F/'Local.kicad_sym';lib=path.read_text();path.write_text(lib.rstrip()[:-1]+definition+'\n)\n')
    # Existing ECO capacitor label and note must follow the final supply choice.
    path=F/'Connectivity_55.kicad_sch';text=path.read_text()
    text=text.replace('(global_label "/CPU_VCCPRIM_1P8" (shape passive) (at 203.2 201.93 180)',f'(global_label "{RAIL}" (shape passive) (at 203.2 201.93 180)')
    text=text.replace('U605 VDD/MR share CPU 1.8V domain; minimum VDD >=1.7V required. CPU rail and reset routing remain incomplete.',
        'U605 uses 3.3V AUX and U511 CPU PERST level translation with R9040 10k pulldown. Brownout/rail sequencing remain unqualified.')
    if 'PART_R9040' not in text:
        definition='(symbol "PART_R9040" (pin_names (offset .5)) (in_bom yes) (on_board yes) (property "Reference" "R" (at 0 0 0) (effects (font (size 1 1)))) (property "Value" "10k 1% / reset fail-low" (at 0 0 0) (effects (font (size 1 1)))) (property "Footprint" "Local:R_0201_DenseCourtyard_1p0x0p4" (at 0 0 0) (effects (font (size 1 1)))) (symbol "PART_R9040_1_1" (rectangle (start -12.7 3.81) (end 12.7 -3.81) (stroke (width .254) (type default)) (fill (type background))) (pin passive line (at -15.24 0 0) (length 2.54) (name "1" (effects (font (size .8 .8)))) (number "1" (effects (font (size .8 .8))))) (pin passive line (at 15.24 0 180) (length 2.54) (name "2" (effects (font (size .8 .8)))) (number "2" (effects (font (size .8 .8)))))))'
        i=end(text,text.index('(lib_symbols'))-1;text=text[:i]+definition.replace('"PART_R9040"','"Local:PART_R9040"',1)+text[i:]
        rid=str(uuid.uuid5(uuid.NAMESPACE_URL,'pcie-switch-2/RevW/U605-pulldown'))
        instance=f'(symbol (lib_id "Local:PART_R9040") (at 504.19 201.93 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{rid}") (property "Reference" "R9040" (at 504.19 193.12 0) (effects (font (size 1 1)))) (property "Value" "10k 1% / reset fail-low" (at 504.19 190.12 0) (effects (font (size 1 1)))) (property "Footprint" "Local:R_0201_DenseCourtyard_1p0x0p4" (at 504.19 201.93 0) (effects (font (size 1 1)) (hide yes))) (pin "1" (uuid "{uuid.uuid5(uuid.UUID(rid),"pin1")}")) (pin "2" (uuid "{uuid.uuid5(uuid.UUID(rid),"pin2")}")) (instances (project "Main_12E1S" (path "{projectpath}" (reference "R9040") (unit 1)))))'
        for net,x,angle in [(MR,488.95,180),('/GND',519.43,0)]:
            instance+=f'\n(global_label "{net}" (shape passive) (at {x} 201.93 {angle}) (effects (font (size .8 .8)) (justify {"right" if angle else "left"})) (uuid "{uuid.uuid5(uuid.UUID(rid),net)}"))'
        text=text.rstrip()[:-1]+instance+'\n)\n'
        libpath=F/'Local.kicad_sym';lib=libpath.read_text();libpath.write_text(lib.rstrip()[:-1]+definition+'\n)\n')
    path.write_text(text)
    return projectpath

def repair():
    boardpath=F/'Main_12E1S.kicad_pcb';b=p.LoadBoard(str(boardpath));fs={f.GetReference():f for f in b.GetFootprints()}
    metadata=json.loads((F/'COMPONENTS.json').read_text());meta={q['ref']:q for q in metadata}
    nets={display_name(n.GetNetname()):n for n in b.GetNetInfo().NetsByNetcode().values()}
    target,ground,reset=nets[RAIL],nets['/GND'],nets[MR]
    f=fs['U605'];supply=next(q for q in f.Pads() if q.GetNumber()=='6');mr=next(q for q in f.Pads() if q.GetNumber()=='3')
    projectpath=schematic();keep=[]
    # Only prior ECO supply/bypass tracks within this local area are replaced.
    for t in list(b.GetTracks()):
        pts=[xy(t.GetStart()),xy(t.GetEnd())]
        oldlocal=all(.5<x<4.8 and .5<y<4.65 for x,y in pts)
        own=t.m_Uuid.AsString() in {str(uuid.uuid5(uuid.UUID(UID),'route'+str(i))) for i in range(20)}
        if own or (oldlocal and not isinstance(t,p.PCB_VIA) and display_name(t.GetNetname()) in [RAIL,'/CPU_VCCPRIM_1P8']):
            keep.append(t);b.Remove(t)
    supply.SetNet(target);mr.SetNet(reset)
    if CAP not in fs:
        cap=p.FootprintLoad(str(F/'Local.pretty'),FOOT);assert cap
        cap.SetFPID(p.LIB_ID('Local',FOOT));cap.SetReference(CAP);cap.SetValue(VALUE);cap.Reference().SetVisible(False);cap.Value().SetVisible(False)
        b.Add(cap);cap.Flip(v(0,0),p.FLIP_DIRECTION_LEFT_RIGHT)
        path=p.KIID_PATH()
        for z in projectpath.strip('/').split('/')+[UID]:path.push_back(p.KIID(z))
        cap.SetPath(path);fs[CAP]=cap
        entry=dict(ref=CAP,value=VALUE,footprint=FOOT,x=4.45,y=4.05,side='B',rotation_deg=270,pinmap={'1':RAIL,'2':'/GND'},height_mm=.33,datasheet='',pin_names={},dnp=False)
        metadata.append(entry);meta[CAP]=entry
    cap=fs['C9040'];cap.SetPosition(v(4.45,4.05));cap.SetOrientationDegrees(270)
    cp={q.GetNumber():q for q in cap.Pads()};cp['1'].SetNet(target);cp['2'].SetNet(ground)
    # The existing bypass ground via moves with the capacitor.
    for t in b.GetTracks():
        if isinstance(t,p.PCB_VIA) and display_name(t.GetNetname())=='/GND' and xy(t.GetPosition()) in [(4.2,4.29),(4.45,4.29)]:t.SetPosition(v(4.2,4.29))
    if 'R9040' not in fs:
        r=p.FootprintLoad(str(F/'Local.pretty'),'R_0201_DenseCourtyard_1p0x0p4');assert r
        r.SetFPID(p.LIB_ID('Local','R_0201_DenseCourtyard_1p0x0p4'));r.SetReference('R9040');r.SetValue('10k 1% / reset fail-low');r.Reference().SetVisible(False);r.Value().SetVisible(False)
        b.Add(r);r.Flip(v(0,0),p.FLIP_DIRECTION_LEFT_RIGHT)
        path=p.KIID_PATH()
        for z in projectpath.strip('/').split('/')+[str(uuid.uuid5(uuid.NAMESPACE_URL,'pcie-switch-2/RevW/U605-pulldown'))]:path.push_back(p.KIID(z))
        r.SetPath(path);fs['R9040']=r
        entry=dict(ref='R9040',value=r.GetValue(),footprint='R_0201_DenseCourtyard_1p0x0p4',x=3.95,y=4.05,side='B',rotation_deg=270,pinmap={'1':MR,'2':'/GND'},height_mm=.33,datasheet='',pin_names={},dnp=False)
        metadata.append(entry);meta['R9040']=entry
    r=fs['R9040'];r.SetPosition(v(3.95,4.05));r.SetOrientationDegrees(270)
    rp={q.GetNumber():q for q in r.Pads()};rp['1'].SetNet(reset);rp['2'].SetNet(ground)
    index=0
    def track(points,net,width=.15):
        nonlocal index
        for a,z in zip(points,points[1:]):
            t=p.PCB_TRACK(b);t.SetStart(v(*a));t.SetEnd(v(*z));t.SetLayer(p.B_Cu);t.SetWidth(p.FromMM(width));t.SetNet(net);t.SetUuid(p.KIID(str(uuid.uuid5(uuid.UUID(UID),'route'+str(index)))));index+=1;b.Add(t)
    track([xy(supply.GetPosition()),(4.45,3.5),xy(cp['1'].GetPosition())],target)
    track([xy(mr.GetPosition()),(2.4,1.074999),(2.6,1.274999),(2.6,3.35),(2.85,3.6),(3.95,3.6),xy(rp['1'].GetPosition())],reset,.1)
    track([xy(rp['2'].GetPosition()),xy(cp['2'].GetPosition())],ground,.1)
    existing=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetPosition()==supply.GetPosition() and display_name(t.GetNetname())==RAIL]
    if not existing:
        via=p.PCB_VIA(b);via.SetPosition(supply.GetPosition());via.SetWidth(p.FromMM(.2));via.SetDrill(p.FromMM(.1));via.SetViaType(p.VIATYPE_BLIND);via.SetLayerPair(p.In30_Cu,p.B_Cu);via.SetNet(target);b.Add(via)
    for pos in [(4.2,4.29),(.9,2.1)]:
        if not any(isinstance(t,p.PCB_VIA) and xy(t.GetPosition())==pos and display_name(t.GetNetname())=='/GND' for t in b.GetTracks()):
            via=p.PCB_VIA(b);via.SetPosition(v(*pos));via.SetWidth(p.FromMM(.2));via.SetDrill(p.FromMM(.1));via.SetViaType(p.VIATYPE_BLIND);via.SetLayerPair(p.In28_Cu,p.B_Cu);via.SetNet(ground);b.Add(via)
    meta['U605']['pinmap']['6']=RAIL;meta['U605']['pinmap']['3']=MR;meta['U605']['datasheet']=SOURCE
    meta['U605'].pop('supply_constraint',None)
    meta['U605']['reset_constraint']='U511 isolates only when CPU VCCA <0.1V; brownout, U501 leakage and rail sequencing require validation'
    meta['C9040'].update(x=4.45,y=4.05,rotation_deg=270,pinmap={'1':RAIL,'2':'/GND'})
    (F/'COMPONENTS.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
    p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(boardpath),b)
    report=dict(source=SOURCE,translator_source='https://www.ti.com/lit/ds/symlink/sn74axc1t45.pdf',
        changed_MR={'ref':'U605','pin':'3','old':'/CPU_PERST_1V8_N','new':MR},supervisor_VDD=RAIL,
        local_bypass='C9040',fail_low_resistor='R9040 10k 1%',old_MR_VIH_min_V=2.31,
        translated_high_nominal_V=3.3,MR_long_branch_routed=False,reset_functional_completion=False,reset_sequence_qualified=False,whole_board_power_complete=False,
        notes=['U511 is an independent CPU PERST translator; no TB state machine is in the signal path.',
        '10k pulldown opposes supervisor internal >=70k pullup when U511 is isolated.',
        'AXC guaranteed isolation applies only below VCCA=0.1V. Brownout transition and U501 L4 leakage are not validated.',
        'U605 stays on auxiliary 3.3V; auxiliary/PEX rail power sequence still requires validation.',
        'SENSE remains PEX_0V9; RESET pullup remains PEX_1V8; CT remains 47nF.',
        'Earlier intermediate CPU-domain VDD experiment is superseded; no final claim relies on it.'])
    (F.parent/'RESET_DOMAIN_REPAIR.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':repair()
