from pathlib import Path
src=(Path(__file__).resolve().parent.parent/'revM/m_assembly.py').read_text(encoding='utf-8')
src=src.replace('PCIe_Main_RevM','PCIe_AllM2_RevO').replace('Main_10E1S','Main_27M2').replace('110,45,2','120,45,2').replace('four upright','27 upright').replace('four vertical','27 vertical')
exec(compile(src,str(__file__),'exec'))
