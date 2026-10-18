from pathlib import Path
src=(Path(__file__).resolve().parent.parent/'revN/n_schematic.py').read_text(encoding='utf-8')
src=src.replace('PCIe_AllM2_RevN','PCIe_AllM2_RevO').replace('Main_23M2','Main_27M2').replace('(rev "N")','(rev "O")').replace('REV N:','REV O:')
src=src.replace('23 M.2 x4 port assignments; 4A per-slot power reservations; electrical design and routing incomplete','27 upright M.2: 23 x4 and 4 power-only. Power/routing/platform qualification incomplete')
src=src.replace('23 UPRIGHT M.2 SLOTS','27 UPRIGHT M.2: 23 x4 + 4 POWER ONLY')
exec(compile(src,str(__file__),'exec'))
