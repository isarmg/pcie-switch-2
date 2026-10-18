from pathlib import Path
src=Path(__file__).with_name('w_route.py').read_text(encoding='utf-8')
src=src.replace("exec(compile(src,__file__,'exec'),globals())","src=src.replace('work/revW','work/revW/reserve').replace('set(range(4,64,2))-{10,12,14,16,40,46}','set(range(4,64,2))-{6,8,10,12,14,16,40,46,62}')\nexec(compile(src,__file__,'exec'),globals())")
exec(compile(src,__file__,'exec'),globals())
