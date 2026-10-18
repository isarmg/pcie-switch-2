from pathlib import Path
src=(Path(__file__).resolve().parents[2]/'scripts/revM/m_stepcheck.py').read_text(encoding='utf-8')
src=src.replace('PCIe_Main_RevM','PCIe_E1S_96x45_USB12mm_RevW').replace('work/revM','work/revW').replace("['Main_10E1S','Assembly_View']","['Main_12E1S']")
exec(compile(src,__file__,'exec'),globals())
