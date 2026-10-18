"""Route power-island bridges using actual segment widths and accessible surfaces."""
from pathlib import Path

loader=Path(__file__).with_name('w_route.py').read_text(encoding='utf-8')
loader=loader.replace("exec(compile(src,__file__,'exec'),globals())", "pass")
exec(compile(loader,__file__,'exec'),globals())
# The loader has produced the fully transformed router in src.
src=src.replace('work/revW','work/revW/bridge')
src=src.replace('set(range(4,64,2))-{10,12,14,16,40,46}',
                '(set(range(4,64,2))|{0,2})-{6,8,10,12,14,16,40,46,62}')
src=src.replace("def add(r):\n    for aa,bb in zip(r['points'],r['points'][1:]):ns['segments'].append(dict(net=r['net'],a=aa,b=bb,layer=r['layer'],width=r['width']))",
"""def add(r):
    obs=ns['obstacles'](r)
    r['segment_widths']=[r['width'] if fast_clear(aa,bb,obs,r['width']/2) else .1 for aa,bb in zip(r['points'],r['points'][1:])]
    for i,(aa,bb) in enumerate(zip(r['points'],r['points'][1:])):ns['segments'].append(dict(net=r['net'],a=aa,b=bb,layer=r['layer'],width=r['segment_widths'][i]))""")
src=src.replace("all(ns['clear_segment'](aa,bb,obs,r['width']/2-.000001) for aa,bb in zip(r['points'],r['points'][1:]))",
                "all(ns['clear_segment'](aa,bb,obs,r.get('segment_widths',[r['width']]*(len(r['points'])-1))[i]/2-.000001) for i,(aa,bb) in enumerate(zip(r['points'],r['points'][1:])))")
src=src.replace("'layer_name':f'In{ll//2-1}.Cu'", "'layer_name':({0:'F.Cu',2:'B.Cu'}.get(ll,f'In{ll//2-1}.Cu'))")
exec(compile(src,__file__,'exec'),globals())
