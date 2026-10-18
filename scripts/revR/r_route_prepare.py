from pathlib import Path
src=(Path(__file__).resolve().parent.parent/'revL/l_route_prepare.py').read_text(encoding='utf-8')
src=src.replace('PCIe_3board_RevL','PCIe_E1S_82x45_RevR').replace('work/revL','work/revR')
exec(compile(src,str(__file__),'exec'))
