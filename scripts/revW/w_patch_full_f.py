from pathlib import Path
src=Path(__file__).with_name('w_patch_escape.py').read_text(encoding='utf-8').replace('pts=stitch(ff,pp,nn,[p.In25_Cu])','pts=stitch(ff,pp,nn,[p.B_Cu])')
exec(compile(src,__file__,'exec'),globals())
