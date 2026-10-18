from pathlib import Path
base=Path(__file__).resolve().parent.parent
ns={'__file__':str(base/'revL/l_schematic.py')}
exec(compile((base/'revL/l_schematic.py').read_text(encoding='utf-8').split('exec(compile(src,')[0],'schematic template','exec'),ns)
src=ns['src']
src=src.replace('PCIe_3board_RevL','PCIe_E1S_Only_RevQ').replace('(rev "L")','(rev "Q")').replace('REV L:','REV Q:')
src=src.replace('CPU 2833-ball coordinates verified. JHL9580 deferred. CPU PMIC/boot firmware/full-board routing pending.','10 E1.S only. No M.2 or daughterboards. CPU/PEX ball maps retained; full-board electrical design pending.')
src=src.replace('(date "2026-10-15")','(date "2026-10-16")')
exec(compile(src,str(__file__),'exec'))
