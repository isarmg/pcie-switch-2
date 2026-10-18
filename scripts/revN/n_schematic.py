from pathlib import Path
import json
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2')
f=R/'outputs/PCIe_AllM2_RevN/Main_23M2/COMPONENTS.json'
meta=json.loads(f.read_text(encoding='utf-8'))
for q in meta:
    if q['ref'].startswith('U50') and q.get('value','').startswith('TPSM53604'):
        for pin in ['3','10','11']:q['pin_types'][pin]='passive'
        # VOUT pins 7 and 8 are explicitly internally connected (TI table 5-1).
        # Model one power source rather than two competing output drivers.
        q['pin_types']['8']='passive'
f.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
pf=f.parent.parent/'M2_PORTS.json';ports=json.loads(pf.read_text(encoding='utf-8'))
for q in ports:
    if q['port'] in ['M3','M4']:
        base={'M3':56,'M4':52}[q['port']];q['pex_lanes']=list(range(base,base+4))
pf.write_text(json.dumps(ports,ensure_ascii=False,indent=2),encoding='utf-8')
src=(R/'scripts/revK/k_schematic.py').read_text(encoding='utf-8')
src=src.replace('PCIe_3board_RevK','PCIe_AllM2_RevN').replace('(rev "K")','(rev "N")')
src=src.replace('Real PEX88096 pinout; CPU and TB5 mechanical reservations only; NOT READY FOR FABRICATION','23 M.2 x4 port assignments; 4A per-slot power reservations; electrical design and routing incomplete')
src=src.replace("pinname='~' if nn.startswith('unconnected-') else cs.get(ref,{}).get('pin_names',{}).get(pn,pn)","pinname=cs.get(ref,{}).get('pin_names',{}).get(pn,pn).split('/')[0];pintype=cs.get(ref,{}).get('pin_types',{}).get(pn,'passive')")
src=src.replace('(pin passive line','(pin {pintype} line').replace('(dnp no)','(dnp {"yes" if c["foot"].IsDNP() else "no"})')
src=src.replace('REV K: UNROUTED PLACEMENT / NET-ASSIGNMENT DRAFT','REV N: 120 x 45 / 23 UPRIGHT M.2 SLOTS - ELECTRICAL DRAFT')
src=src.replace('Main routing pending. Intel parts are mechanical reservations, with no verified ball maps.','CPU and switch ball maps verified. 19 added 4A converter reservations. Most nets remain unrouted.')
src=src.replace('Pin types are passive: ERC does not validate power sequencing, firmware, or link behavior.','CPU PMIC, reset drivers, switch configuration, clock/PDN/SI/thermal qualification are incomplete.')
src=src.replace("header(root,n,'A3')","header(root,n,'A0')")
exec(compile(src,str(__file__),'exec'))
