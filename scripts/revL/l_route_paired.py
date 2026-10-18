from pathlib import Path
import json,math,sys
src=Path(__file__).with_name('l_route_solve.py').read_text(encoding='utf-8').split('\nfor task in sorted')[0]
exec(compile(src,'routing_geometry','exec'))
G=.025;NX=4401;NY=1801;CLEAR=.125
sections={}
for t in d['tasks']:sections.setdefault(t['net'][:-2],[]).append(t)
def add_track(nn,layer,width,pts):
    for a,b in zip(pts,pts[1:]):segments.append(dict(net=nn,layer=layer,width=width,a=a,b=b))
def offset(pts,amount):
    normals=[]
    for a,b in zip(pts,pts[1:]):
        dist=math.dist(a,b);normals.append((-(b[1]-a[1])/dist,(b[0]-a[0])/dist))
    out=[]
    for i,pt in enumerate(pts):
        if i==0:n=normals[0];scale=amount
        elif i==len(pts)-1:n=normals[-1];scale=amount
        else:
            a=normals[i-1];b=normals[i];s=(a[0]+b[0],a[1]+b[1]);dist=math.hypot(*s);n=(s[0]/dist,s[1]/dist);scale=amount/(n[0]*b[0]+n[1]*b[1])
        out.append((pt[0]+n[0]*scale,pt[1]+n[1]*scale))
    return out
def simplify(pts):
    out=[]
    for q in pts:
        if out and math.dist(out[-1],q)<1e-7:continue
        if len(out)>1 and abs(orient(out[-2],out[-1],q))<1e-8 and sum((out[-1][k]-out[-2][k])*(q[k]-out[-1][k]) for k in [0,1])>=0:out[-1]=q
        else:out.append(q)
    return out
def solve_coupled(fake,ptask,ntask,center_a):
    start_count=len(segments)
    try:
        center=route(fake);obs=obstacles(fake);smooth=[center[0]];i=0
        while i<len(center)-1:
            j=len(center)-1
            while j>i+1 and not clear_segment(center[i],center[j],obs,fake['width']/2):j-=1
            smooth.append(center[j]);i=j
        center=smooth
        n=(-(center[1][1]-center[0][1]),center[1][0]-center[0][0]);projection=sum((ptask['a']['pt'][k]-center_a[k])*n[k] for k in [0,1]);sign=1 if projection>=0 else -1
        bulks=[offset(center,.125*sign),offset(center,-.125*sign)]
        for t,bulk in zip([ptask,ntask],bulks):
            assert all(clear_segment(x,y,obstacles(t),t['width']/2) for x,y in zip(bulk,bulk[1:])),('bulk clearance',t['net'])
            add_track(t['net'],t['layer'],t['width'],bulk)
        fans={}
        for which in ['a','b']:
            for t,bulk in zip([ptask,ntask],bulks):
                gate=bulk[0 if which=='a' else -1];ftask={**t,'a':{'pt':t[which]['pt']},'b':{'pt':gate}}
                fan=route(ftask);fans[(t['net'],which)]=fan;add_track(t['net'],t['layer'],t['width'],fan)
        solved=[]
        for t,bulk in zip([ptask,ntask],bulks):
            pts=simplify(fans[(t['net'],'a')]+bulk[1:]+list(reversed(fans[(t['net'],'b')]))[1:])
            solved.append({**t,'points':pts,'length_mm':length(pts),'coupled_bulk':True,'bulk_centerline':center})
        return center,solved
    except (AssertionError,RuntimeError):
        del segments[start_count:]
        raise
metrics=[]
for key,ts in sorted(sections.items(),key=lambda z:(z[1][0]['group'],math.dist(z[1][0]['a']['pt'],z[1][0]['b']['pt']))):
    assert len(ts)==2
    ptask=next(t for t in ts if t['net'].endswith('_P'));ntask=next(t for t in ts if t['net'].endswith('_N'))
    # The prepare pass normally emits both polarities with the same endpoint
    # reference order. Explicitly align them if footprint pad iteration differs.
    def role(ref):return 'CAP' if ref.startswith('C') else ref
    if role(ptask['a']['ref'])!=role(ntask['a']['ref']):ntask={**ntask,'a':ntask['b'],'b':ntask['a']}
    center_a=tuple((ptask['a']['pt'][k]+ntask['a']['pt'][k])/2 for k in [0,1]);center_b=tuple((ptask['b']['pt'][k]+ntask['b']['pt'][k])/2 for k in [0,1])
    dist=math.dist(center_a,center_b)
    if dist<8.0:
        for t in ts:
            pts=route(t);results.append({**t,'points':pts,'length_mm':length(pts),'coupled_bulk':False});add_track(t['net'],t['layer'],t['width'],pts)
        metrics.append({'section':key,'short_fanout_only':True,'centerline_mm':0});continue
    ux=(center_b[0]-center_a[0])/dist;uy=(center_b[1]-center_a[1])/dist
    solution=None;last_error=None
    choices=sorted({min(v,dist*.30) for v in [1.25,1.75,2.5,3.5,4.5]})
    for da in choices:
        for db in choices:
            gates=[(center_a[0]+ux*da,center_a[1]+uy*da),(center_b[0]-ux*db,center_b[1]-uy*db)]
            fake={**ptask,'net':'CENTER_'+key,'width':.45,'a':{'pt':gates[0]},'b':{'pt':gates[1]},'exempt_nets':[t['net'] for t in ts]}
            try:solution=solve_coupled(fake,ptask,ntask,center_a)
            except (AssertionError,RuntimeError) as e:last_error=str(e);continue
            if solution is not None:break
        if solution is not None:break
    assert solution is not None,('no pair launch corridor',key,last_error)
    center,solved=solution;results.extend(solved)
    metrics.append({'section':key,'short_fanout_only':False,'centerline_mm':length(center),'trace_width_mm':.10,'parallel_gap_mm':.15})
    print(key,'coupled bulk',round(length(center),3),'mm',flush=True)

# Keep honest measured lengths. A standalone copper length match does not
# compensate silicon package delays, nor does it validate the impedance.
matched=[]
for group in sorted({r['group'] for r in results}):
    qs=[r for r in results if r['group']==group]
    total={pol:sum(r['length_mm'] for r in qs if r['net'].endswith('_'+pol)) for pol in 'PN'}
    matched.append({'pair':group,'P_mm':total['P'],'N_mm':total['N'],'geometric_skew_mm':abs(total['P']-total['N']),'length_tuning_complete':False})
(W/'cpu_routes.json').write_text(json.dumps({'routes':results,'pairs':matched,'coupled_sections':metrics,'notes':['0.10mm trace and 0.15mm parallel gap are provisional geometry; impedance not validated','BGA/capacitor fanouts are not uniformly coupled','Length tuning and package-delay compensation remain incomplete','Blind-via spans need fabrication approval']},indent=2))
print('Coupled route sections',len(metrics),'connections',len(results),'max untuned copper skew mm',max(q['geometric_skew_mm'] for q in matched),flush=True)
