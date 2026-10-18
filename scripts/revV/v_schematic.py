from pathlib import Path
base=Path(__file__).resolve().parent.parent
src=(base/'revU/u_schematic.py').read_text(encoding='utf-8')
src=src.replace('PCIe_E1S_96x45_12slot_RevU','PCIe_E1S_96x45_12VPower_RevV').replace('(rev "U")','(rev "V")').replace('REV U:','REV V:').replace('Nominal SSD side/bottom gap 7mm','Nominal SSD side/bottom gap 7.25mm')
src=src.replace('CPU PMIC / BIOS / NVM / SI qualification pending.','12V SSD and 3.3V/5V auxiliary power drawn. CPU VR and fictional switch supplies pending; thermal / current / SI unqualified.')
exec(compile(src,str(__file__),'exec'))
folder=Path('C:/Users/micro/Desktop/方案/pcie switch 2/outputs/PCIe_E1S_96x45_12VPower_RevV/Main_12E1S')
for path in folder.glob('*.kicad_sch'):
    text=path.read_text(encoding='utf-8').replace('(rev "U")','(rev "V")').replace('2026-10-16','2026-10-17')
    path.write_text(text,encoding='utf-8')
