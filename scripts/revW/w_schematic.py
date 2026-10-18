from pathlib import Path
src=(Path(__file__).resolve().parents[2]/'scripts/revU/u_schematic.py').read_text(encoding='utf-8')
src=src.replace('PCIe_E1S_96x45_12slot_RevU','PCIe_E1S_96x45_USB12mm_RevW').replace('(rev "U")','(rev "W")').replace('REV U:','REV W:').replace('Nominal SSD side/bottom gap 7mm','Nominal SSD side/bottom gap 7.25mm')
src=src.replace('CPU PMIC / BIOS / NVM / SI qualification pending.','USB face positions 12/24mm. Real CPU rails retained; reference fake-switch regulators added. CPU PMIC / BIOS / NVM / SI qualification pending.')
exec(compile(src,__file__,'exec'),globals())
F=Path('C:/Users/micro/Desktop/方案/pcie switch 2/outputs/PCIe_E1S_96x45_USB12mm_RevW/Main_12E1S')
for path in F.glob('*.kicad_sch'):
 text=path.read_text(encoding='utf-8').replace('(rev "U")','(rev "W")').replace('2026-10-16','2026-10-17');path.write_text(text,encoding='utf-8')
