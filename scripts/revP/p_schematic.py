from pathlib import Path
src=(Path(__file__).resolve().parent.parent/'revN/n_schematic.py').read_text(encoding='utf-8')
src=src.replace('PCIe_AllM2_RevN','PCIe_AllM2_RevP').replace('Main_23M2','Main_20M2').replace('(rev "N")','(rev "P")').replace('REV N:','REV P:')
src=src.replace('23 M.2 x4 port assignments','20 M.2 x4 port assignments / 6 mm pitch').replace('23 UPRIGHT M.2 SLOTS','20 UPRIGHT M.2 / 6 mm PITCH').replace('19 added 4A','16 added 4A')
exec(compile(src,str(__file__),'exec'))
