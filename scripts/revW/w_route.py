from pathlib import Path
base=Path(__file__).resolve().parents[2]
src=(base/'scripts/revU/u_route.py').read_text(encoding='utf-8')
src=src.replace('work/revU','work/revW')
line=next(s for s in src.splitlines() if s.startswith('original={'))
src=src.replace(line,"original={q['task_id']:q for q in json.loads((W/'old_transformed.json').read_text(encoding='utf-8'))}")
src=src.replace("pp=[[q[0]+15,q[1]] for q in old['points']]","pp=[q[:] for q in old['points']]")
src=src.replace('candidates=set(range(4,64,2))','candidates=set(range(4,64,2))-{10,12,14,16,40,46}')
start=src.index("        if math.dist(pp[-1],aa)<.00001:")
end=src.index("    if fast_clear(aa,bb,obs,rad):",start)
src=src[:start]+src[end:]
start=src.index("    if t['net'].startswith('/S'):")
end=src.index("    if fast_only:raise RuntimeError('no quick corridor')",start)
# Test simple edge corridors only; bounded A* handles an obstructed route once.
src=src[:start]+src[start:end].replace("        if not fast_only:","        if False:")+src[end:]
start=src.index("    if t['net'].startswith(('/S11_REFCLK','/S12_REFCLK')):")
end=src.index("    if t['b'].get('ref')",start)
src=src[:start]+src[end:]
src=src.replace("for grid in [.1,.05,.025]:","for grid in [.05,.025]:")
src=src.replace("for ll in ([] if solved else sorted(layers,key=lambda ll:(ll!=preferred,ll))):","for ll in ([] if solved else sorted(layers,key=lambda ll:(sum(ll in vv['layers'] for vv in d['vias'])+4*sum(s['layer']==ll for s in ns['segments']),ll!=preferred,ll))):")
src=src.replace("checkpoint=W/'progress.json'","checkpoint=W/'progress.json'")
src=src.replace("['net','a','b','width']","['net','a','b']")
src=src.replace("t={**q,'layer':ll,","t={**q,'width':min(q['width'],.08) if q.get('kind')!='POWER_CONTROL' else q['width'],'layer':ll,")
src=src.replace('SEARCH_LIMIT=50000 if grid>=.1 else 100000 if grid>=.05 else 220000','SEARCH_LIMIT=10000 if grid>=.1 else 20000 if grid>=.05 else 60000')
src=src.replace("ns['clear_segment']=fast_clear","ns['clear_segment']=fast_clear\nexec(compile((STAGE/'scripts/revW/w_fast_geometry.py').read_text(encoding='utf-8'),'cached geometry','exec'),globals())")
exec(compile(src,__file__,'exec'),globals())
