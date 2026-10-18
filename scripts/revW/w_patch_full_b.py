from pathlib import Path
src=Path(__file__).with_name('w_patch_escape.py').read_text(encoding='utf-8')
src=src.replace("ff=fs['J8'];pp=pad(ff,'B6')", "ff=fs['C124'];pp=pad(ff,'1')").replace("q['b'].update", "q['a'].update").replace('pts=stitch(ff,pp,nn,[p.In25_Cu])','pts=stitch(ff,pp,nn,[p.F_Cu])')
exec(compile(src,__file__,'exec'),globals())
