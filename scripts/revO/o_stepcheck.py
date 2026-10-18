from pathlib import Path
src=(Path(__file__).resolve().parent.parent/'revM/m_stepcheck.py').read_text(encoding='utf-8')
src=src.replace('PCIe_Main_RevM','PCIe_AllM2_RevO').replace('work/revM','work/revO').replace('Main_10E1S','Main_27M2')
exec(compile(src,str(__file__),'exec'))
