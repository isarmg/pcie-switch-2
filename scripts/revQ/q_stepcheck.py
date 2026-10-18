from pathlib import Path
src=(Path(__file__).resolve().parent.parent/'revM/m_stepcheck.py').read_text(encoding='utf-8')
src=src.replace('PCIe_Main_RevM','PCIe_E1S_Only_RevQ').replace('work/revM','work/revQ').replace("['Main_10E1S','Assembly_View']","['Main_10E1S']")
exec(compile(src,str(__file__),'exec'))
