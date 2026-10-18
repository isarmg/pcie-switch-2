"""Portable Rev W schematic generation from the native board and COMPONENTS.json.

Requires KiCad 10 Python. Does not need historical work/ caches or Windows paths.
Regenerates sheet/instance UUIDs and updates footprint paths, so run native
netlist/parity validation after generation. To preserve existing drawing edits,
use w_power_models.py / w_reset_repair.py instead of rebuilding all sheets.
"""
from pathlib import Path
import argparse
import sys
from w_power_models import DESIGN

ROOT=Path(__file__).resolve().parents[2]

def template(folder):
    source=(ROOT/'scripts/revK/k_schematic.py').read_text(encoding='utf-8')
    source=source.replace("R=Path('C:/Users/micro/Desktop/方案/pcie switch 2')",f'R=Path({str(ROOT)!r})')
    source=source.replace("c.ROOT=R/'outputs/PCIe_3board_RevK'",f'c.ROOT=Path({str(folder.parent)!r})')
    source=source.replace("q.GetNetname()", "q.GetNetname().replace('{slash}', '/')")
    old="pinname='~' if nn.startswith('unconnected-') else cs.get(ref,{}).get('pin_names',{}).get(pn,pn)"
    new="pinname=cs.get(ref,{}).get('pin_names',{}).get(pn,pn).split('/')[0];pintype=cs.get(ref,{}).get('pin_types',{}).get(pn,'passive')"
    assert old in source
    source=source.replace(old,new).replace('(pin passive line','(pin {pintype} line')
    source=source.replace('(dnp no)','(dnp {"yes" if c["foot"].IsDNP() else "no"})')
    source=source.replace("prop('Footprint',fp,0,0,True)","prop('Footprint',fp,0,0,True)+prop('Datasheet',cs.get(ref,{}).get('datasheet',''),0,0,True)")
    source=source.replace("prop('Footprint',fp,x,y,True)","prop('Footprint',fp,x,y,True)+prop('Datasheet',cs.get(ref,{}).get('datasheet',''),x,y,True)")
    source=source.replace('(rev "K")','(rev "W")').replace('(date "2026-10-15")','(date "2026-10-18")')
    source=source.replace('Real PEX88096 pinout; CPU and TB5 mechanical reservations only; NOT READY FOR FABRICATION','FICTIONAL PEX90064; CPU288V 32GB; ELECTRICAL DRAFT, NOT FOR FABRICATION')
    source=source.replace('REV K: UNROUTED PLACEMENT / NET-ASSIGNMENT DRAFT','REV W: 12 E1.S / FICTIONAL PEX90064 / THUNDERBOLT 3 HOST')
    source=source.replace('Main routing pending. Intel parts are mechanical reservations, with no verified ball maps.','CPU VR, reset/control routing, firmware, differential routing, stackup and thermal qualification remain incomplete.')
    source=source.replace('Pin types are passive: ERC does not validate power sequencing, firmware, or link behavior.','CPU and reviewed regulator/supervisor pins have ERC types; other passive placeholders remain. ERC cannot qualify function.')
    source=source.replace("header(root,n,'A3')","header(root,n,'A2')")
    source=source[:source.rindex('for n in sys.argv[1:]')]+f'run({folder.name!r})\n'
    return source

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--design-dir',type=Path,default=DESIGN)
    parser.add_argument('--check-template',action='store_true')
    args=parser.parse_args();source=template(args.design_dir.resolve())
    compiled=compile(source,str(__file__),'exec')
    if args.check_template:
        print('Template compiles; no design files changed')
        return
    import pcbnew as p
    if int(p.Version().split('.')[0])<10:raise SystemExit('KiCad 10 or newer is required; do not downgrade the board.')
    from w_power_models import update_metadata
    update_metadata(args.design_dir.resolve())
    exec(compiled,{'__file__':str(__file__),'__name__':'__revw_generator__'})

if __name__=='__main__':main()
