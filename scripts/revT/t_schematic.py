from pathlib import Path
base=Path(__file__).resolve().parent.parent
ns={'__file__':str(base/'revL/l_schematic.py')}
exec(compile((base/'revL/l_schematic.py').read_text(encoding='utf-8').split('exec(compile(src,')[0],'schematic template','exec'),ns)
src=ns['src'].replace('PCIe_3board_RevL','PCIe_E1S_82x45_TB3Host_RevT').replace('(rev "L")','(rev "T")').replace('(date "2026-10-15")','(date "2026-10-16")')
src=src.replace('True PEX and CPU ball maps; provisional CPU lands; CPU PMIC and full-board routing incomplete','FICTIONAL reordered PEX90064 map; CPU288V 32GB MoP; layout and routing study only')
src=src.replace('REV L: VERIFIED CPU / PEX BALL MAPS - ELECTRICAL DESIGN IN PROGRESS','REV T: 288V 32GB / FICTIONAL PEX90064 / THUNDERBOLT 3 HOST')
src=src.replace('CPU 2833-ball coordinates verified. JHL9580 deferred. CPU PMIC/boot firmware/full-board routing pending.','PEX90064 has an invented 1024-ball map. 10 E1.S x4 plus CPU x4; 20 spare lanes. TB3 host: Alpine Ridge DP + TPS65982. CPU PMIC / BIOS / NVM / SI qualification pending.')
exec(compile(src,str(__file__),'exec'))
