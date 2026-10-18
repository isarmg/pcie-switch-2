from pathlib import Path
base=Path(__file__).resolve().parent.parent/'revL'
src=(base/'l_route_solve.py').read_text(encoding='utf-8').split('\nfor task in sorted')[0]
src=src.replace('work/revL','work/revR').replace('NX=2201;NY=901','NX=1641;NY=901')
src=src.replace('        seen.add(cur);y,x=divmod(cur,NX)',"        if len(seen)>80000:raise RuntimeError(('bounded launch search',task['net']))\n        seen.add(cur);y,x=divmod(cur,NX)")
exec(compile(src,'82mm routing geometry','exec'))
src=(base/'l_route_paired.py').read_text(encoding='utf-8');src=src[src.index('G=.025;'):].replace('NX=4401','NX=3281')
start=src.index('    solution=None;last_error=None')
end=src.index('    center,solved=solution;',start)
src=src[:start]+'''    solution=None;last_error=None;best_solution=None;best_segments=None;best_score=1e99
    start_count=len(segments)
    choices=sorted({min(v,dist*.30) for v in [1.25,1.75,2.5,3.5,4.5]})
    good=False
    for da in choices:
        for db in choices:
            del segments[start_count:]
            gates=[(center_a[0]+ux*da,center_a[1]+uy*da),(center_b[0]-ux*db,center_b[1]-uy*db)]
            fake={**ptask,'net':'CENTER_'+key,'width':.45,'a':{'pt':gates[0]},'b':{'pt':gates[1]},'exempt_nets':[t['net'] for t in ts]}
            try:candidate=solve_coupled(fake,ptask,ntask,center_a)
            except (AssertionError,RuntimeError) as e:last_error=str(e);continue
            lengths=[q['length_mm'] for q in candidate[1]];skew=abs(lengths[0]-lengths[1]);score=sum(lengths)+4*skew
            if score<best_score:best_score=score;best_solution=candidate;best_segments=list(segments[start_count:])
            if skew<=2.0:good=True;break
        if good:break
    del segments[start_count:]
    assert best_solution is not None,('no pair launch corridor',key,last_error)
    solution=best_solution;segments.extend(best_segments)
''' +src[end:]
exec(compile(src,str(__file__),'exec'))
