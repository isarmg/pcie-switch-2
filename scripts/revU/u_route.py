"""Incremental inner-layer connectivity study, preserving unchanged copper."""
from pathlib import Path
from collections import defaultdict
import sys,json,math,copy
sys.stdout.reconfigure(encoding='utf-8')
STAGE=Path(__file__).resolve().parents[2];R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');W=R/'work/revU'
d=json.loads((W/'route_tasks.json').read_text(encoding='utf-8'))
src=(STAGE/'scripts/revL/l_route_solve.py').read_text(encoding='utf-8').split('\nfor task in sorted')[0]
src=src.replace('work/revL','work/revU').replace('cpu_route_tasks.json','route_tasks.json').replace('NX=2201;NY=901','NX=1921;NY=901').replace('.05+.25-CLEAR','.05+.10-CLEAR').replace('1.04*h','2.0*h').replace('CLEAR+.006','CLEAR+.001')
src=src.replace('        seen.add(cur);y,x=divmod(cur,NX)',"        if len(seen)>SEARCH_LIMIT:raise RuntimeError(('bounded search',task['net']))\n        seen.add(cur);y,x=divmod(cur,NX)")
for a,b in [('[:8,:]','[:INSET,:]'),('[-8:,:]','[-INSET:,:]'),('[:,:8]','[:,:INSET]'),('[:,-8:]','[:,-INSET:]'),('xx<8','xx<INSET'),('xx>=NX-8','xx>=NX-INSET'),('yy<8','yy<INSET'),('yy>=NY-8','yy>=NY-INSET')]:src=src.replace(a,b)
ns={'__file__':__file__};exec(compile(src,'route geometry','exec'),ns);ns['INSET']=10;ns['CLEAR']=.077;ns['SEARCH_LIMIT']=100000
def fast_clear(a,b,obs,radius):
    x0,x1=min(a[0],b[0]),max(a[0],b[0]);y0,y1=min(a[1],b[1]),max(a[1],b[1])
    for c,e,rr in obs:
        r=radius+rr+ns['CLEAR']-.000001
        if min(c[0],e[0])>x1+r or max(c[0],e[0])<x0-r or min(c[1],e[1])>y1+r or max(c[1],e[1])<y0-r:continue
        if ns['distance'](a,b,c,e)<r:return False
    return True
ns['clear_segment']=fast_clear
original={q['task_id']:q for q in json.loads((R/'outputs/PCIe_E1S_82x45_TB3Host_RevT/SIGNAL_ROUTES.json').read_text(encoding='utf-8'))['routes']}
def add(r):
    for aa,bb in zip(r['points'],r['points'][1:]):ns['segments'].append(dict(net=r['net'],a=aa,b=bb,layer=r['layer'],width=r['width']))
def route_task(t,fast_only=False):
    obs=ns['obstacles'](t);rad=t['width']/2;aa=t['a']['pt'];bb=t['b']['pt']
    old=original.get(t['task_id'])
    if old and len(old['points'])>1:
        pp=[[q[0]+15,q[1]] for q in old['points']];dd=[math.dist(a,b) for a,b in zip(pp,pp[1:])];total=sum(dd);at=0;candidate=[]
        da=[aa[k]-pp[0][k] for k in [0,1]];db=[bb[k]-pp[-1][k] for k in [0,1]]
        for i,q in enumerate(pp):
            if i:at+=dd[i-1]
            f=at/total if total else 0;candidate.append([q[k]+da[k]*(1-f)+db[k]*f for k in [0,1]])
        if all(.48<=q[0]<=95.52 and .48<=q[1]<=44.52 for q in candidate) and all(fast_clear(a,b,obs,rad) for a,b in zip(candidate,candidate[1:])):return candidate
        if math.dist(pp[-1],aa)<.00001:pp=pp[::-1]
        if math.dist(pp[0],aa)<.00001:
            dd=[math.dist(a,b) for a,b in zip(pp,pp[1:])];total=sum(dd)
            for cut in [4,6,8,12]:
                keep=max(.5,total-cut);at=0;prefix=[aa]
                for i,dist in enumerate(dd):
                    if at+dist<keep:prefix.append(pp[i+1]);at+=dist;continue
                    f=(keep-at)/dist;prefix.append([pp[i][k]+f*(pp[i+1][k]-pp[i][k]) for k in [0,1]]);break
                if not all(.48<=q[0]<=95.52 and .48<=q[1]<=44.52 for q in prefix):continue
                if not all(fast_clear(a,b,obs,rad) for a,b in zip(prefix,prefix[1:])):continue
                if fast_clear(prefix[-1],bb,obs,rad):return prefix+[bb]
                if not fast_only:
                    try:return prefix+ns['route']({**t,'a':{'pt':prefix[-1]},'b':{'pt':bb}})[1:]
                    except (AssertionError,RuntimeError):pass
    if fast_clear(aa,bb,obs,rad):return [aa,bb]
    if t['net'].startswith('/S'):
        # Escape between BGA columns, then use a clear horizontal edge corridor.
        for yy in [44.5,43.9,43.3,42.7,1.35,.65,1.95]:
            ends=[]
            for end in [aa,bb]:
                choices=[]
                for dx in [0,.5,-.5,.25,-.25,.75,-.75,1,-1]:
                    p1=(end[0]+dx,end[1]);p2=(p1[0],yy)
                    if not(.5<p1[0]<95.5):continue
                    if fast_clear(end,p1,obs,rad) and fast_clear(p1,p2,obs,rad):choices.append((p1,p2))
                ends.append(choices)
            for e1 in ends[0]:
                for e2 in ends[1]:
                    if fast_clear(e1[1],e2[1],obs,rad):return [aa,*e1,e2[1],e2[0],bb]
    if t['net'].startswith('/S') and 'REFCLK' in t['net'] and bb[1]<1.5:
        way=[aa,(1,28),(1,.65),(bb[0],.65),bb]
        if all(fast_clear(a,b,obs,rad) for a,b in zip(way,way[1:])):return way
        if not fast_only:
            pts=[]
            for start,end in zip(way,way[1:]):
                part=ns['route']({**t,'a':{'pt':start},'b':{'pt':end}});pts.extend(part if not pts else part[1:])
            return pts
    if fast_only:raise RuntimeError('no quick corridor')
    if t['net'].startswith(('/S11_REFCLK','/S12_REFCLK')):
        way=[aa,(17,28),(17,1.35),(73,1.35),bb];pts=[]
        for start,end in zip(way,way[1:]):
            part=ns['route']({**t,'a':{'pt':start},'b':{'pt':end}});pts.extend(part if not pts else part[1:])
        return pts
    if t['b'].get('ref') in ['U1','U502','U501','U503']:
        return ns['route']({**t,'a':t['b'],'b':t['a']})[::-1]
    return ns['route'](t)
ns['segments'].extend(d['segments']);results=list(d['retained']);completed=[]
checkpoint=W/'progress.json';ids={q['task_id']:q for q in d['tasks']}
if checkpoint.exists():
    for r in json.loads(checkpoint.read_text())['routes']:
        q=ids.get(r['task_id'])
        if q and all(r.get(k)==q.get(k) for k in ['net','a','b','width']):
            obs=ns['obstacles'](r)
            if all(ns['clear_segment'](aa,bb,obs,r['width']/2-.000001) for aa,bb in zip(r['points'],r['points'][1:])):results.append(r);completed.append(r);add(r)
done={q['task_id'] for q in completed};groups=defaultdict(list)
for q in d['tasks']:
    if q['task_id'] not in done:groups[(q['task_id'],q['net'].split('_')[1] if q['net'].startswith('/S') else '')].append(q)
via={(q['net'],tuple(q['pt'])):set(q['layers']) for q in d['vias']}
ordered=sorted(groups,key=lambda key:(groups[key][0]['layer']==0, -math.dist(groups[key][0]['a']['pt'],groups[key][0]['b']['pt'])))
for key in ordered:
    qs=groups[key];candidates=set(range(4,64,2))
    print('Start',key[0],flush=True)
    for q in qs:
        if q['layer']==0:continue
        for end in ['a','b']:
            vv=next((vv for vv in d['vias'] if vv['net']==q['net'] and math.dist(vv['pt'],q[end]['pt'])<.000003),None)
            assert vv,(q['net'],q[end]);candidates &= set(vv['layers'])
    if all(q['layer']==0 for q in qs):
        solved=[{**q,'points':[q['a']['pt'],q['b']['pt']],'length_mm':math.dist(q['a']['pt'],q['b']['pt']),'coupled_bulk':False} for q in qs]
    else:
        preferred=qs[0]['layer'];layers=sorted(candidates,key=lambda ll:(sum(math.dist(s['a'],s['b']) for s in ns['segments'] if s['layer']==ll)+(0 if ll==preferred else 5),ll));solved=None;errors=[]
        # Test clear corridors on every accessible layer before an expensive
        # search on one layer that may be divided by previous long routes.
        for ll in layers:
            start=len(ns['segments']);trial=[]
            try:
                for q in qs:
                    t={**q,'layer':ll,'layer_index':ll//2-1,'layer_name':f'In{ll//2-1}.Cu'};pts=route_task(t,True);r={**t,'points':pts,'length_mm':ns['length'](pts)+sum(t[e].get('fanout_mm',0) for e in ['a','b']),'coupled_bulk':False,'routing_method':'clear corridor connectivity / no differential qualification'};trial.append(r);add(r)
                solved=trial;break
            except (AssertionError,RuntimeError):del ns['segments'][start:]
        for ll in ([] if solved else sorted(layers,key=lambda ll:(ll!=preferred,ll))):
            for grid in [.1,.05,.025]:
                ns.update(G=grid,NX=round(96/grid)+1,NY=round(45/grid)+1,INSET=round(.5/grid),SEARCH_LIMIT=50000 if grid>=.1 else 100000 if grid>=.05 else 220000)
                for reverse in ([False] if len(qs)==1 else [False,True]):
                    start=len(ns['segments']);trial=[]
                    try:
                        for q in sorted(qs,key=lambda q:q['net'],reverse=reverse):
                            t={**q,'layer':ll,'layer_index':ll//2-1,'layer_name':f'In{ll//2-1}.Cu'};pts=route_task(t);r={**t,'points':pts,'length_mm':ns['length'](pts)+sum(t[e].get('fanout_mm',0) for e in ['a','b']),'coupled_bulk':False,'routing_method':'individual inner-layer connectivity; SI and pair tuning pending'};trial.append(r);add(r)
                        solved=trial;break
                    except (AssertionError,RuntimeError) as e:errors.append(str(e));del ns['segments'][start:]
                if solved:break
            if solved:break
        if not solved and len(qs)>1:
            trial=[]
            for q in qs:
                found=None
                for ll in layers:
                    for grid in [.05,.025]:
                        ns.update(G=grid,NX=round(96/grid)+1,NY=round(45/grid)+1,INSET=round(.5/grid))
                        t={**q,'layer':ll,'layer_index':ll//2-1,'layer_name':f'In{ll//2-1}.Cu'}
                        try:
                            pts=route_task(t);found={**t,'points':pts,'length_mm':ns['length'](pts)+sum(t[e].get('fanout_mm',0) for e in ['a','b']),'coupled_bulk':False,'routing_method':'independent layer fallback; not a qualified differential route'};break
                        except (AssertionError,RuntimeError):pass
                    if found:break
                assert found,(key,q['net'],'no independent route');add(found);trial.append(found)
            solved=trial
        assert solved,(key,errors[-10:])
    results.extend(solved);completed.extend(solved)
    checkpoint.write_text(json.dumps(dict(routes=completed),indent=2),encoding='utf-8')
    print('Routed',key[0],len(results),'/',len(d['tasks'])+len(d['retained']),flush=True)
pairs=[]
for group in sorted({q['group'] for q in results if q['paired']}):
    rr=[q for q in results if q['group']==group];lengths={pol:sum(q['length_mm'] for q in rr if q['net'].endswith('_'+pol)) for pol in 'PN'};pairs.append(dict(pair=group,P_mm=lengths['P'],N_mm=lengths['N'],geometric_skew_mm=abs(lengths['P']-lengths['N']),length_tuning_complete=False))
(W/'signal_routes.json').write_text(json.dumps(dict(routes=results,pairs=pairs,notes=['Twelve E1.S x4 plus CPU and TB3 host physical signal sections.','New/moved E1.S differential nets individually routed; no impedance, coupling, loss, package delay or skew qualification.','Power/management/CPU PMIC/boot remain incomplete. Fictional switch.']),indent=2),encoding='utf-8')
print('Completed',len(results),'sections;',len(pairs),'differential groups',flush=True)
