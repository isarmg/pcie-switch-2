from pathlib import Path
src=(Path(__file__).resolve().parent.parent/'revQ/q_stepcheck.py').read_text(encoding='utf-8')
src=src.replace('PCIe_E1S_Only_RevQ','PCIe_E1S_82x45_RevR').replace('work/revQ','work/revR')
exec(compile(src,str(__file__),'exec'))
