from pathlib import Path
src=(Path(__file__).resolve().parent.parent/'revM/m_stepcheck.py').read_text(encoding='utf-8')
src=src.replace('PCIe_Main_RevM','PCIe_E1S_96x45_12slot_RevU').replace('work/revM','work/revU').replace("['Main_10E1S','Assembly_View']","['Main_12E1S']")
exec(compile(src,str(__file__),'exec'))
