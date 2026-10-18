from pathlib import Path
src=Path(__file__).with_name('w_bridge_route.py').read_text(encoding='utf-8').replace('work/revW/bridge','work/revW/finalpatch')
src=src.replace("(set(range(4,64,2))|{0,2})-{6,8,10,12,14,16,40,46,62}", "{0,2,4,22,28,34,52,58}")
exec(compile(src,__file__,'exec'),globals())
