from pathlib import Path
src=(Path(__file__).resolve().parent.parent/'revU/u_exports.py').read_text(encoding='utf-8')
src=src.replace('PCIe_E1S_96x45_12slot_RevU','PCIe_E1S_96x45_12VPower_RevV').replace('work/revU','work/revV')
exec(compile(src,str(__file__),'exec'))
