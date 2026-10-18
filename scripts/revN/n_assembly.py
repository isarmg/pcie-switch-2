from pathlib import Path
src=(Path(__file__).resolve().parent.parent/'revM/m_assembly.py').read_text(encoding='utf-8')
src=src.replace('PCIe_Main_RevM','PCIe_AllM2_RevN').replace("'Main_10E1S'","'Main_23M2'").replace('Main_10E1S.kicad_pcb','Main_23M2.kicad_pcb').replace("110,45,2","120,45,2")
src=src.replace('four upright','23 upright').replace('four vertical','23 vertical').replace('Main_10E1S.','Main_23M2.')
exec(compile(src,str(__file__),'exec'))
