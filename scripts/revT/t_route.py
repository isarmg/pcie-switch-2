"""Route all allocated PCIe data/clock sections, layer by layer, with measured results."""
from pathlib import Path
import sys,json,math,time,concurrent.futures,collections
sys.stdout.reconfigure(encoding='utf-8')
STAGE=Path(__file__).resolve().parents[2]
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');W=R/'work/revT'

def worker(layer):
    src=(STAGE/'scripts/revL/l_route_solve.py').read_text(encoding='utf-8').split('\nfor task in sorted')[0]
    src=src.replace('work/revL','work/revT').replace('cpu_route_tasks.json','route_tasks.json').replace('NX=2201;NY=901','NX=1641;NY=901')
    # Account for both copper clearance and the existing 0.25mm drill-to-copper
    # rule. The effective obstacle radius includes the 0.10mm drill radius.
    src=src.replace('1.04*h','1.35*h').replace('.05+.25-CLEAR','.05+.10-CLEAR')
    # The rightmost cap via is 0.68mm from the board edge. A 0.4mm search
    # inset unnecessarily seals its outer escape; 0.2mm still exceeds the
    # actual 0.1mm edge rule for a 0.1mm trace.
    for old,new in [('[:8,:]','[:4,:]'),('[-8:,:]','[-4:,:]'),('[:,:8]','[:,:4]'),('[:,-8:]','[:,-4:]'),('xx<8','xx<4'),('xx>=NX-8','xx>=NX-4'),('yy<8','yy<4'),('yy>=NY-8','yy>=NY-4')]:src=src.replace(old,new)
    src=src.replace('        seen.add(cur);y,x=divmod(cur,NX)',"        if len(seen)>240000:raise RuntimeError(('bounded search',task['net']))\n        seen.add(cur);y,x=divmod(cur,NX)")
    src=src.replace('[:4,:]','[:INSET,:]').replace('[-4:,:]','[-INSET:,:]').replace('[:,:4]','[:,:INSET]').replace('[:,-4:]','[:,-INSET:]').replace('xx<4','xx<INSET').replace('xx>=NX-4','xx>=NX-INSET').replace('yy<4','yy<INSET').replace('yy>=NY-4','yy>=NY-INSET')
    ns={'__file__':__file__};exec(compile(src,'route geometry','exec'),ns)
    paired=(STAGE/'scripts/revL/l_route_paired.py').read_text(encoding='utf-8');paired=paired[paired.index('G=.025;'):paired.index('metrics=[]')]
    paired=paired.replace('G=.025;NX=4401;NY=1801;CLEAR=.125','G=.05;NX=1641;NY=901;CLEAR=.08')
    paired=paired.replace('bulks=[offset(center,.125*sign),offset(center,-.125*sign)]',"half=(ptask['width']+.15)/2;bulks=[offset(center,half*sign),offset(center,-half*sign)]")
    exec(compile(paired,'paired route geometry','exec'),ns)
    tasks=[t for t in ns['d']['tasks'] if t['layer']==layer];sections=collections.defaultdict(list)
    for t in tasks:
        if t['paired']:sections[t['net'][:-2]].append(t)
    singles=[t for t in tasks if not t['paired']]
    if layer==0:
        result=[];metrics=[]
        for t in tasks:
            assert t['a']['ref'].startswith('C4') and t['b']['ref'].startswith('J')
            assert abs(t['a']['pt'][1]-t['b']['pt'][1])<.000003
            pts=[t['a']['pt'],t['b']['pt']];result.append({**t,'points':pts,'length_mm':math.dist(*pts),'coupled_bulk':False})
        out=dict(layer=0,layer_name='F.Cu',routes=result,coupled_sections=[dict(section=k,coupled_bulk=False,reason='1.38mm direct surface coupling stub') for k in sections],attempt=0,failed_prior_attempts=[])
        (W/'routes_layer_0.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
        return dict(layer=0,connections=len(result),coupled=0,attempt=0)
    failures=[]
    for attempt in range(6):
        ns['G']=.025 if attempt>=4 or all(t['kind'].startswith('TB3_') for t in tasks) else .05;ns['NX']=round(82/ns['G'])+1;ns['NY']=round(45/ns['G'])+1;ns['INSET']=round(.6/ns['G'])
        ns['segments'].clear();result=[];metrics=[]
        if attempt==0:keys=sorted(sections,key=lambda k:-math.dist(sections[k][0]['a']['pt'],sections[k][0]['b']['pt']))
        elif attempt==1:keys=sorted(sections,key=lambda k:(sections[k][0]['group'],math.dist(sections[k][0]['a']['pt'],sections[k][0]['b']['pt'])))
        elif attempt in [2,3]:keys=sorted(sections,key=lambda k:(-sections[k][0]['a']['pt'][1],sections[k][0]['a']['pt'][0]),reverse=attempt==3)
        else:keys=sorted(sections,key=lambda k:math.dist(sections[k][0]['a']['pt'],sections[k][0]['b']['pt']),reverse=attempt==5)
        try:
            for key in keys:
                ts=sections[key];assert len(ts)==2,(key,len(ts))
                pt=next(t for t in ts if t['net'].endswith('_P'));nt=next(t for t in ts if t['net'].endswith('_N'))
                role=lambda ref:'CAP' if ref.startswith('C') else ref
                if role(pt['a']['ref'])!=role(nt['a']['ref']):nt={**nt,'a':nt['b'],'b':nt['a']}
                ca=tuple((pt['a']['pt'][k]+nt['a']['pt'][k])/2 for k in [0,1]);cb=tuple((pt['b']['pt'][k]+nt['b']['pt'][k])/2 for k in [0,1]);dist=math.dist(ca,cb)
                start=len(ns['segments']);solution=None;last=None
                if dist>=5 and attempt<2 and layer not in [60,62]:
                    ux=(cb[0]-ca[0])/dist;uy=(cb[1]-ca[1])/dist
                    choices=[min(1.,dist*.28)] if pt['net'].startswith('/TBT_') else sorted({min(v,dist*.28) for v in [1.,1.75,3.]})
                    for da in choices:
                        for db in choices:
                            fake={**pt,'net':'CENTER_'+key,'width':.38,'a':{'pt':(ca[0]+ux*da,ca[1]+uy*da)},'b':{'pt':(cb[0]-ux*db,cb[1]-uy*db)},'exempt_nets':[pt['net'],nt['net']]}
                            try:solution=ns['solve_coupled'](fake,pt,nt,ca)
                            except (AssertionError,RuntimeError) as e:last=str(e);continue
                            break
                        if solution:break
                if solution:
                    center,solved=solution;result.extend(solved);metrics.append(dict(section=key,coupled_bulk=True,centerline_mm=ns['length'](center),parallel_gap_mm=.15))
                else:
                    del ns['segments'][start:]
                    for t in ([nt,pt] if attempt%2 else [pt,nt]):
                        points=ns['route'](t);ns['add_track'](t['net'],t['layer'],t['width'],points)
                        result.append({**t,'points':points,'length_mm':ns['length'](points),'coupled_bulk':False})
                    metrics.append(dict(section=key,coupled_bulk=False,reason='short fanout' if dist<5 else 'independent clearance-checked escape',pair_search_note=last))
            for t in singles:
                key=t['net'];points=ns['route'](t);ns['add_track'](t['net'],t['layer'],t['width'],points)
                result.append({**t,'points':points,'length_mm':ns['length'](points),'coupled_bulk':False})
            out=dict(layer=layer,layer_name=tasks[0]['layer_name'],routes=result,coupled_sections=metrics,attempt=attempt,failed_prior_attempts=failures)
            (W/f'routes_layer_{layer}.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
            return dict(layer=layer,connections=len(result),coupled=sum(q['coupled_bulk'] for q in metrics),attempt=attempt)
        except (AssertionError,RuntimeError) as e:
            failures.append(dict(attempt=attempt,key=key,error=str(e)));print('retry layer',layer,failures[-1],flush=True)
            (W/f'debug_layer_{layer}.json').write_text(json.dumps(dict(tasks=tasks,segments=ns['segments'],failed_key=key,failures=failures),indent=2),encoding='utf-8')
    raise RuntimeError((layer,failures))

if __name__=='__main__':
    data=json.loads((W/'route_tasks.json').read_text(encoding='utf-8'));layers=sorted({t['layer'] for t in data['tasks']});results=[];errors=[]
    pending=[]
    for layer in layers:
        path=W/f'routes_layer_{layer}.json'
        if '--force' not in sys.argv and path.exists() and path.stat().st_mtime>(W/'route_tasks.json').stat().st_mtime:
            print('reuse layer',layer,flush=True)
        else:pending.append(layer)
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:
        fs={pool.submit(worker,layer):layer for layer in pending}
        for future in concurrent.futures.as_completed(fs):
            try:print('routed',future.result(),flush=True)
            except Exception as e:errors.append(str(e));print('FAILED',str(e),flush=True)
    assert not errors,errors
    sections=[]
    for layer in layers:
        obj=json.loads((W/f'routes_layer_{layer}.json').read_text(encoding='utf-8'));results.extend(obj['routes']);sections.extend(obj['coupled_sections'])
    assert len(results)==len(data['tasks'])
    pairs=[]
    for r in results:r['length_mm']+=r['a'].get('fanout_mm',0)+r['b'].get('fanout_mm',0)
    for group in sorted({q['group'] for q in results if q['paired']}):
        qs=[q for q in results if q['group']==group];totals={pol:sum(q['length_mm'] for q in qs if q['net'].endswith('_'+pol)) for pol in 'PN'}
        pairs.append(dict(pair=group,P_mm=totals['P'],N_mm=totals['N'],geometric_skew_mm=abs(totals['P']-totals['N']),length_tuning_complete=False))
    out=dict(routes=results,pairs=pairs,coupled_sections=sections,notes=['Complete physical connectivity of Allocated E1.S/CPU PCIe and TB3 host data/clock plus control sections; power routing remains incomplete.','Fictional switch ball mapping and invented 3.3V reset outputs. Not a production PEX90064 design.','0.10mm width / 0.15mm coupled bulk gap are provisional; fanouts and some escapes use individual routing.','No SI, impedance, length or package-delay qualification. Remaining board nets are reported separately.'])
    (W/'signal_routes.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
    print('Completed',len(results),'sections /',len(pairs),'differential links. Max untuned skew',max(q['geometric_skew_mm'] for q in pairs),flush=True)
