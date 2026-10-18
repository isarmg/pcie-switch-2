"""Preserve verified E1.S copper; assign TB3 pairs to accessible inner layers."""
from pathlib import Path
from collections import defaultdict,Counter
import sys,json,math,textwrap,time
sys.stdout.reconfigure(encoding='utf-8')
STAGE=Path(__file__).resolve().parents[2];R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');W=R/'work/revT'
sys.path.insert(0,str(Path(__file__).parent));import t_route
full=json.loads((W/'route_tasks.json').read_text(encoding='utf-8'))
if len(full['tasks'])!=469:
    full=json.loads((W/'route_tasks_full.json').read_text(encoding='utf-8'));assert len(full['tasks'])==469
    (W/'route_tasks.json').write_text(json.dumps(full,indent=2),encoding='utf-8')
deferred=[q for q in full['tasks'] if (q['paired'] and q['kind'].startswith('TB3_')) or q['net']=='/TBT_POC_GPIO_5'];base=[q for q in full['tasks'] if q not in deferred]
assert len(base)==392 and len(deferred)==77
(W/'route_tasks_full.json').write_text(json.dumps(full,indent=2),encoding='utf-8')
source=(Path(__file__).with_name('t_route.py')).read_text(encoding='utf-8');prefix=source[source.index('    src=(STAGE'):source.index("    tasks=[t for t in ns")].replace('1.35*h','1.8*h').replace('240000','60000')
scope=dict(STAGE=STAGE,__file__=__file__);exec(compile(textwrap.dedent(prefix),'routing geometry','exec'),scope);ns=scope['ns'];ns.update(G=.05,NX=1641,NY=901,INSET=12,CLEAR=.08)
changed=json.loads((W/'changed_direct_vias.json').read_text(encoding='utf-8'));ids={q['task_id']:q for q in base};results=[];sections=[];reused=[]
base_layers=sorted({q['layer'] for q in base})
try:
    # Existing routes are retained only if their endpoints match and no newly
    # extended via infringes the measured copper clearance on that layer.
    (W/'route_tasks.json').write_text(json.dumps({**full,'tasks':base},indent=2),encoding='utf-8')
    for ll in base_layers:
        path=W/f'routes_layer_{ll}.json';valid=path.exists()
        if valid:
            obj=json.loads(path.read_text(encoding='utf-8'));current={k for k,q in ids.items() if q['layer']==ll}
            valid={q.get('task_id') for q in obj['routes']}==current
            for q in obj['routes']:
                target=ids.get(q.get('task_id'))
                if not target or any(q.get(k)!=target.get(k) for k in ['net','layer','width','a','b']):valid=False;break
                for vv in changed:
                    if ll not in vv['layers'] or vv['net']==q['net']:continue
                    threshold=vv['diameter']/2+q['width']/2+.08-.000001
                    if any(ns['point_segment'](vv['pt'],aa,bb)<threshold for aa,bb in zip(q['points'],q['points'][1:])):valid=False;break
                if not valid:break
        if not valid:
            print('Re-route base layer',ll,flush=True);t_route.worker(ll);obj=json.loads(path.read_text(encoding='utf-8'))
        else:reused.append(ll)
        results.extend(obj['routes']);sections.extend(obj['coupled_sections'])
finally:(W/'route_tasks.json').write_text(json.dumps(full,indent=2),encoding='utf-8')
print('Base complete:',len(results),'sections; audited/reused layers',reused,flush=True)
assert len(results)==392
for r in results:ns['add_track'](r['net'],r['layer'],r['width'],r['points'])
groups=defaultdict(list)
for q in deferred:groups[q['net'][:-2] if q['paired'] else q['task_id']].append(q)
checkpoint=W/'adaptive_progress.json';restored=[]
if checkpoint.exists():
    try:
        saved=json.loads(checkpoint.read_text(encoding='utf-8'));by_id={q['task_id']:q for q in deferred}
        extras=[q for q in saved['routes'] if q['task_id'] in by_id];valid=True
        for r in extras:
            q=by_id[r['task_id']]
            if any(r.get(k)!=q.get(k) for k in ['net','width','a','b']) or not q['layer_index']<=r['layer_index']<=30:valid=False;break
            for e in ['a','b']:
                vv=next(vv for vv in full['vias'] if vv['net']==r['net'] and math.dist(vv['pt'],r[e]['pt'])<.000003)
                if r['layer'] not in vv['layers']:valid=False;break
        if valid:
            restored=extras;results.extend(extras)
            for r in extras:ns['add_track'](r['net'],r['layer'],r['width'],r['points'])
            keys={q['net'][:-2] if q['paired'] else q['task_id'] for q in extras}
            sections.extend(q for q in saved['sections'] if q.get('section') in keys)
            print('Resumed',len(extras),'matching TB3 sections; native DRC and copper graph will recheck all routes.',flush=True)
    except (ValueError,KeyError,StopIteration):pass
done={q['task_id'] for q in restored}
ordered=sorted(groups,key=lambda k:(-groups[k][0]['layer_index'],-math.dist(groups[k][0]['a']['pt'],groups[k][0]['b']['pt'])))
failures=[]
for section in ordered:
    qs=groups[section];assert len(qs)==(2 if qs[0]['paired'] else 1)
    if all(q['task_id'] in done for q in qs):continue
    lo=max(q['layer_index'] for q in qs);preferred=qs[0].get('preferred_layer_index',lo)
    # Congestion-aware choice among layers already reached by both endpoint
    # vias; no extra blind vias are invented by the routing solver.
    choices=sorted(range(lo,31),key=lambda i:(sum(math.dist(z['a'],z['b']) for z in ns['segments'] if z['layer']==2*(i+1) and max(z['a'][0],z['b'][0])>38)+(0 if i==preferred else 2),i))
    solved=None;attempts=[]
    for idx in choices:
        ll=2*(idx+1)
        for grid in [.05,.025]:
            ns.update(G=grid,NX=round(82/grid)+1,NY=round(45/grid)+1,INSET=round(.6/grid))
            for reverse in [False,True]:
                start=len(ns['segments']);trial=[]
                try:
                    for original in sorted(qs,key=lambda q:q['net'],reverse=reverse):
                        t={**original,'preferred_layer_index':preferred,'layer_index':idx,'layer':ll,'layer_name':f'In{idx}.Cu'}
                        pts=ns['route'](t);ns['add_track'](t['net'],ll,t['width'],pts);trial.append({**t,'points':pts,'length_mm':ns['length'](pts),'coupled_bulk':False,'routing_method':'adaptive inner-layer assignment / individually routed'})
                    solved=trial;break
                except (AssertionError,RuntimeError) as e:attempts.append(dict(layer_index=idx,grid=grid,reverse=reverse,error=str(e)));del ns['segments'][start:]
            if solved:break
        if solved:break
    if not solved:
        failures.append(dict(section=section,attempts=attempts));(W/'adaptive_failures.json').write_text(json.dumps(failures,indent=2),encoding='utf-8');raise RuntimeError((section,attempts))
    results.extend(solved);sections.append(dict(section=section,coupled_bulk=False,layer_index=idx,reason='TB3 connectivity draft; differential coupling, length and impedance require a later SI routing pass'))
    (W/'adaptive_progress.json').write_text(json.dumps(dict(routes=results,sections=sections),indent=2),encoding='utf-8')
    print('TB3 pair',section,'In'+str(idx),'Cu /',len(results),'of 469 sections',flush=True)
assert len(results)==469 and len({q['task_id'] for q in results})==469
for r in results:r['length_mm']+=r['a'].get('fanout_mm',0)+r['b'].get('fanout_mm',0)
pairs=[]
for group in sorted({q['group'] for q in results if q['paired']}):
    rows=[q for q in results if q['group']==group];lens={pol:sum(q['length_mm'] for q in rows if q['net'].endswith('_'+pol)) for pol in 'PN'}
    pairs.append(dict(pair=group,P_mm=lens['P'],N_mm=lens['N'],geometric_skew_mm=abs(lens['P']-lens['N']),length_tuning_complete=False))
out=dict(routes=results,pairs=pairs,coupled_sections=sections,notes=['469 physical signal/control sections. Whole-board power and boot design remain incomplete.','TB3 pairs are assigned only to inner layers already covered by both endpoint vias.','New TB3 differential nets are individually routed connectivity drafts; coupling, skew, SI and impedance are NOT qualified.','Original E1.S/CPU paired bulk remains where the geometry allows it.','Fictional switch ball map, HDI layer buildup and blind-via manufacturing remain unqualified.'])
(W/'signal_routes.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('Completed 469 sections /',len(pairs),'end-to-end differential groups; max untuned skew',max(q['geometric_skew_mm'] for q in pairs),flush=True)
