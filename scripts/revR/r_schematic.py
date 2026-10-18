from pathlib import Path
src=(Path(__file__).resolve().parent.parent/'revQ/q_schematic.py').read_text(encoding='utf-8')
src=src.replace('PCIe_E1S_Only_RevQ','PCIe_E1S_82x45_RevR').replace('(rev "Q")','(rev "R")').replace('REV Q:','REV R:').replace('10 E1.S only.','82 x 45 mm / 10 E1.S only.')
exec(compile(src,str(__file__),'exec'))
