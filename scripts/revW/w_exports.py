from pathlib import Path
src=(Path(__file__).resolve().parents[2]/'scripts/revU/u_exports.py').read_text(encoding='utf-8')
src=src.replace('PCIe_E1S_96x45_12slot_RevU','PCIe_E1S_96x45_USB12mm_RevW').replace('work/revU','work/revW')
exec(compile(src,__file__,'exec'),globals())
