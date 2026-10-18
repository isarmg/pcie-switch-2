from pathlib import Path
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2')
src=(R/'scripts/revK/k_assembly.py').read_text(encoding='utf-8')
src=src.replace('PCIe_3board_RevK','PCIe_3board_RevL').replace('REV K / MAIN 110 x 45 / PLACEMENT DRAFT','REV L / MAIN 110 x 45 / CPU BGA2833')
exec(compile(src,str(__file__),'exec'))
