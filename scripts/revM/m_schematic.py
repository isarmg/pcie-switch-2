from pathlib import Path
src=(Path(__file__).resolve().parent.parent/'revL/l_schematic.py').read_text(encoding='utf-8')
src=src.replace('PCIe_3board_RevL','PCIe_Main_RevM').replace("'(rev \"L\")'","'(rev \"M\")'").replace('REV L:','REV M:')
src=src.replace('CPU PMIC/boot firmware/full-board routing pending.','Four upright M.2 sockets on carrier. CPU PMIC/boot firmware/full-board routing pending.')
exec(compile(src,str(__file__),'exec'))
