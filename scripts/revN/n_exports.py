from pathlib import Path
src=(Path(__file__).resolve().parent.parent/'revL/l_exports.py').read_text(encoding='utf-8')
src=src.replace('PCIe_3board_RevL','PCIe_AllM2_RevN').replace('work/revL','work/revN')
exec(compile(src,str(__file__),'exec'))
