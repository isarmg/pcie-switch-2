"""Route the CPU's x4 interconnect only; report geometric length separately from SI."""
from pathlib import Path
import json,sys,math,heapq,time
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');W=R/'work/revL'
d=json.loads((W/'cpu_route_tasks.json').read_text())
G=d['grid_mm'];CLEAR=d['clearance_mm'];NX=2201;NY=901
vias=d['vias'];segments=[];results=[]

def length(pts):return sum(math.dist(a,b) for a,b in zip(pts,pts[1:]))
def point_segment(q,a,b):
    v=(b[0]-a[0],b[1]-a[1]);den=v[0]*v[0]+v[1]*v[1]
    t=max(0,min(1,((q[0]-a[0])*v[0]+(q[1]-a[1])*v[1])/den)) if den else 0
    return math.dist(q,(a[0]+t*v[0],a[1]+t*v[1]))
def orient(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def distance(a,b,c,e):
    if max(min(a[0],b[0]),min(c[0],e[0]))<=min(max(a[0],b[0]),max(c[0],e[0])) and max(min(a[1],b[1]),min(c[1],e[1]))<=min(max(a[1],b[1]),max(c[1],e[1])) and orient(a,b,c)*orient(a,b,e)<=0 and orient(c,e,a)*orient(c,e,b)<=0:return 0
    return min(point_segment(a,c,e),point_segment(b,c,e),point_segment(c,a,b),point_segment(e,a,b))
def obstacles(task):
    out=[];layer=task['layer'];nn=task['net']
    exempt=set(task.get('exempt_nets',[]))|{nn}
    for vv in vias:
        if vv['net'] not in exempt and layer in vv['layers']:
            out.append((vv['pt'],vv['pt'],max(vv['diameter']/2,.05+.25-CLEAR)))
    for s in segments:
        if s['net'] not in exempt and s['layer']==layer:out.append((s['a'],s['b'],s['width']/2))
    return out
def clear_segment(a,b,obs,radius):return all(distance(a,b,c,e)>=radius+rr+CLEAR-1e-6 for c,e,rr in obs)
def raster(obs,radius):
    arr=np.zeros((NY,NX),dtype=bool);arr[:8,:]=1;arr[-8:,:]=1;arr[:,:8]=1;arr[:,-8:]=1
    for a,b,rr in obs:
        r=rr+radius+CLEAR+.006
        x0=max(0,math.floor((min(a[0],b[0])-r)/G));x1=min(NX-1,math.ceil((max(a[0],b[0])+r)/G))
        y0=max(0,math.floor((min(a[1],b[1])-r)/G));y1=min(NY-1,math.ceil((max(a[1],b[1])+r)/G))
        xs=np.arange(x0,x1+1)*G;ys=np.arange(y0,y1+1)[:,None]*G
        vx=b[0]-a[0];vy=b[1]-a[1];den=vx*vx+vy*vy
        t=np.clip(((xs-a[0])*vx+(ys-a[1])*vy)/den,0,1) if den else 0
        hit=(xs-(a[0]+t*vx))**2+(ys-(a[1]+t*vy))**2<=r*r
        arr[y0:y1+1,x0:x1+1]|=hit
    return arr
def route(task):
    start=task['a']['pt'];end=task['b']['pt'];obs=obstacles(task);w=task['width'];rad=w/2
    if clear_segment(start,end,obs,rad):return [start,end]
    arr=raster(obs,rad);sx,sy=(round(z/G) for z in start);tx,ty=(round(z/G) for z in end)
    assert not arr[sy,sx] and not arr[ty,tx],('blocked endpoint',task['net'],arr[sy,sx],arr[ty,tx])
    st=sy*NX+sx;target=ty*NX+tx
    def h(x,y):
        dx=abs(x-tx);dy=abs(y-ty);return max(dx,dy)+.41421356237*min(dx,dy)
    heap=[(h(sx,sy),0,st)];best={st:0};prev={};seen=set()
    moves=[(1,0,1),(-1,0,1),(0,1,1),(0,-1,1),(1,1,math.sqrt(2)),(1,-1,math.sqrt(2)),(-1,1,math.sqrt(2)),(-1,-1,math.sqrt(2))]
    while heap:
        _,cost,cur=heapq.heappop(heap)
        if cur in seen:continue
        if cur==target:break
        seen.add(cur);y,x=divmod(cur,NX)
        for dx,dy,dist in moves:
            xx=x+dx;yy=y+dy
            if xx<8 or xx>=NX-8 or yy<8 or yy>=NY-8 or arr[yy,xx]:continue
            if dx and dy and (arr[y,xx] or arr[yy,x]):continue
            nxt=yy*NX+xx;nc=cost+dist
            if nc<best.get(nxt,1e30):best[nxt]=nc;prev[nxt]=cur;heapq.heappush(heap,(nc+1.04*h(xx,yy),nc,nxt))
    else:raise RuntimeError(('no path',task['net'],len(seen)))
    ids=[target]
    while ids[-1]!=st:ids.append(prev[ids[-1]])
    pts=[(i%NX*G,i//NX*G) for i in reversed(ids)]
    pts[0]=tuple(start);pts[-1]=tuple(end)
    # Keep only bends; do not shortcut through an obstacle.
    out=[]
    for q in pts:
        if len(out)>1 and abs(orient(out[-2],out[-1],q))<1e-8:out[-1]=q
        else:out.append(q)
    assert all(clear_segment(a,b,obs,rad-.001) for a,b in zip(out,out[1:])),('geometric check',task['net'])
    return out

for task in sorted(d['tasks'],key=lambda t:(t['group'],math.dist(t['a']['pt'],t['b']['pt']))):
    pts=route(task);rec={**task,'points':pts,'length_mm':length(pts)};results.append(rec)
    for a,b in zip(pts,pts[1:]):segments.append(dict(net=task['net'],layer=task['layer'],a=a,b=b,width=task['width']))
    print(task['net'],round(rec['length_mm'],3),'mm',len(pts)-1,'segments',flush=True)

# Match total copper lengths across the two capacitor-separated sections of
# each differential pair. Package delay and real stackup remain unvalidated.
matched=[]
for group in sorted({r['group'] for r in results}):
    qs=[r for r in results if r['group']==group]
    total={pol:sum(r['length_mm'] for r in qs if r['net'].endswith('_'+pol)) for pol in 'PN'}
    short=min(total,key=total.get);delta=abs(total['P']-total['N']);tuned=False
    if delta>.005:
        for r in sorted([r for r in qs if r['net'].endswith('_'+short)],key=lambda t:-t['length_mm']):
            obs=obstacles(r);pts=r['points']
            for i,(a,b) in sorted(enumerate(zip(pts,pts[1:])),key=lambda t:-math.dist(*t[1])):
                dist=math.dist(a,b)
                if dist<2:continue
                ux=(b[0]-a[0])/dist;uy=(b[1]-a[1])/dist
                for sign in [1,-1]:
                    s=(a[0]+(dist/2-.5)*ux,a[1]+(dist/2-.5)*uy);e=(a[0]+(dist/2+.5)*ux,a[1]+(dist/2+.5)*uy)
                    offset=(-uy*delta/2*sign,ux*delta/2*sign)
                    ss=(s[0]+offset[0],s[1]+offset[1]);ee=(e[0]+offset[0],e[1]+offset[1])
                    cand=[a,s,ss,ee,e,b]
                    oldother=[(x,y) for j,(x,y) in enumerate(zip(pts,pts[1:])) if j!=i]
                    self_clear=all(distance(x,y,c,e)>1e-6 for x,y in [(s,ss),(ss,ee),(ee,e)] for c,e in oldother)
                    if self_clear and all(.5<q[0]<109.5 and .5<q[1]<44.5 for q in cand) and all(clear_segment(x,y,obs,r['width']/2) for x,y in zip(cand,cand[1:])):
                        r['points']=pts[:i+1]+cand[1:-1]+pts[i+1:];r['length_mm']=length(r['points']);tuned=True;break
                if tuned:break
            if tuned:break
    total={pol:sum(r['length_mm'] for r in qs if r['net'].endswith('_'+pol)) for pol in 'PN'}
    matched.append({'pair':group,'P_mm':total['P'],'N_mm':total['N'],'geometric_skew_mm':abs(total['P']-total['N']),'tuned':tuned})
    # Refresh obstacle segments after tuning, for subsequent pairs.
    segments=[dict(net=r['net'],layer=r['layer'],a=a,b=b,width=r['width']) for r in results for a,b in zip(r['points'],r['points'][1:])]
(W/'cpu_routes.json').write_text(json.dumps({'routes':results,'pairs':matched,'notes':['Copper geometry only; no package-flight-time compensation','0.10mm widths are provisional until impedance stackup is agreed','Blind-via spans need fabrication approval']},indent=2))
print('Completed',len(results),'connections,',len(matched),'pairs; max geometric skew',max(r['geometric_skew_mm'] for r in matched),flush=True)
