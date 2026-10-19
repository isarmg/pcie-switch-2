"""Bounded joint rerouting study, no PCB writes and no source-layer mapping.
Eight x1 trials: both orders x {shortest, avoid_other, north, south}.
All source vias are conservatively projected onto one proposed signal plane.
"""
from pathlib import Path
import os,json,math,time,heapq,hashlib,argparse
import numpy as np
from shapely import Point,LineString,STRtree
D=Path(__file__).parent
SOURCE=Path(os.environ['E1S_SOURCE']).resolve()
d=json.loads((D/'NATIVE_GEOMETRY.json').read_text())
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==d['sha256']=='e33bc9bf7cb41045c3171abd07677bc36ebe7c3960d61349e4ad5ba2437ecb3c'
W=.1;GAP=.1;CLEAR=.1;G=.05;NX=1921;NY=901;MAX_NODES=1200000
xy=np.array([v['xy'] for v in d['vias']]);rv=np.array([v['diameter']/2 for v in d['vias']]);vn=[v['net'] for v in d['vias']];vp=[Point(*v['xy']) for v in d['vias']];vt=STRtree(vp)

def stamp(arr,a,b,r,value=1,mode='blocked'):
 x0=max(0,int(math.floor((min(a[0],b[0])-r)/G)));x1=min(NX-1,int(math.ceil((max(a[0],b[0])+r)/G)))
 y0=max(0,int(math.floor((min(a[1],b[1])-r)/G)));y1=min(NY-1,int(math.ceil((max(a[1],b[1])+r)/G)))
 xs=np.arange(x0,x1+1)*G;ys=np.arange(y0,y1+1)[:,None]*G;vx=b[0]-a[0];vy=b[1]-a[1];den=vx*vx+vy*vy
 f=np.clip(((xs-a[0])*vx+(ys-a[1])*vy)/den,0,1) if den else 0
 dist=np.sqrt((xs-(a[0]+f*vx))**2+(ys-(a[1]+f*vy))**2)
 if mode=='blocked':arr[y0:y1+1,x0:x1+1]|=dist<=r
 else:arr[y0:y1+1,x0:x1+1]=np.maximum(arr[y0:y1+1,x0:x1+1],value*np.maximum(0,1-dist/r))

def endpoints(pair):
 nets=['{slash}'+pair+'_'+p for p in ['P','N']];ps=[];vs=[]
 for net in nets:
  pads=[p for p in d['pads'] if p['net']==net];assert len(pads)==2
  source=next(p for p in pads if p['ref']=='U1');dest=next(p for p in pads if p['ref']!='U1')
  own=[v for v in d['vias'] if v['net']==net];assert len(own)==2
  av=min(own,key=lambda v:math.dist(v['xy'],source['xy']));bv=min(own,key=lambda v:math.dist(v['xy'],dest['xy']))
  assert math.dist(av['xy'],source['xy'])<2e-6 and math.dist(bv['xy'],dest['xy'])<2e-6
  ps.append([source,dest]);vs.append([av,bv])
 return nets,ps,vs

class Router:
 def __init__(self,pair,existing=(),mode='shortest',other_baseline=None,terminal_shift_mm=0.0):
  self.pair=pair;self.nets,self.pads,self.ev=endpoints(pair);self.existing=[LineString(t['points']) for r in existing for t in r['traces']];self.existing_trace_nets=[t['net'] for r in existing for t in r['traces']];self.mode=mode;self.terminal_shift_mm=terminal_shift_mm
  self.blocked=np.zeros((NY,NX),dtype=bool)
  for v in d['vias']:
   if v['net'] not in self.nets:stamp(self.blocked,v['xy'],v['xy'],v['diameter']/2+.27)
  for line in self.existing:
   cs=list(line.coords)
   for a,b in zip(cs,cs[1:]):stamp(self.blocked,a,b,.32)
  inset=math.ceil(.4/G);self.blocked[:inset]=1;self.blocked[-inset:]=1;self.blocked[:,:inset]=1;self.blocked[:,-inset:]=1
  self.penalty=np.zeros((NY,NX),dtype=np.float32)
  if mode=='avoid_other':
   assert other_baseline
   cs=other_baseline['centerline']
   for a,b in zip(cs,cs[1:]):stamp(self.penalty,a,b,.8,8,mode='penalty')
  elif mode=='north':self.penalty[:]=np.arange(NY)[:,None]/(NY-1)*3
  elif mode=='south':self.penalty[:]=(1-np.arange(NY)[:,None]/(NY-1))*3
  elif mode!='shortest':raise ValueError(mode)
 def clear(self,a,b):
  line=LineString([a,b]);ids=vt.query(line.buffer(.37+.001))
  return all(vn[i] in self.nets or line.distance(vp[i])>=rv[i]+.27-1e-8 for i in ids) and all(line.distance(q)>=.32-1e-8 for q in self.existing)
 def line_cost(self,a,b):
  n=max(2,math.ceil(math.dist(a,b)/.1));xs=np.linspace(a[0],b[0],n);ys=np.linspace(a[1],b[1],n);ix=np.clip(np.rint(xs/G).astype(int),0,NX-1);iy=np.clip(np.rint(ys/G).astype(int),0,NY-1)
  return math.dist(a,b)*float(np.mean(1+self.penalty[iy,ix]))
 def astar(self,a,b):
  a=tuple(int(round(q/G)) for q in a);b=tuple(int(round(q/G)) for q in b)
  if self.blocked[a[1],a[0]] or self.blocked[b[1],b[0]]:
   details=[]
   for label,u in [('start',a),('end',b)]:
    if not self.blocked[u[1],u[0]]:continue
    point=Point(u[0]*G,u[1]*G);hits=[]
    for ix in vt.query(point.buffer(float(rv.max())+.27+.001)):
     dist=point.distance(vp[ix])
     if vn[ix] not in self.nets and dist<=rv[ix]+.27+1e-8:hits.append({'kind':'source via projection','net':vn[ix],'xy':list(xy[ix]),'center_distance_mm':dist})
    for net,line in zip(self.existing_trace_nets,self.existing):
     dist=point.distance(line)
     if dist<=.32+1e-8:hits.append({'kind':'new earlier channel trace','net':net,'center_distance_mm':dist})
    details.append({'end':label,'grid_xy_mm':[u[0]*G,u[1]*G],'blockers':hits})
   return None,{'reason':'blocked centerline endpoint','expanded_nodes':0,'endpoint_obstacles':details}
  def heuristic(u):
   dx=abs(u[0]-b[0]);dy=abs(u[1]-b[1]);return max(dx,dy)+(math.sqrt(2)-1)*min(dx,dy)
  h=[(heuristic(a),0,a)];cost={a:0};prev={};expanded=0;dirs=[(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)]
  while h:
   _,c,u=heapq.heappop(h)
   if c>cost[u]+1e-8:continue
   expanded+=1
   if u==b:
    p=[u]
    while p[-1]!=a:p.append(prev[p[-1]])
    return [[x*G,y*G] for x,y in reversed(p)],{'expanded_nodes':expanded,'weighted_cost_grid_units':c}
   if expanded>=MAX_NODES:return None,{'reason':'explicit node budget reached','expanded_nodes':expanded}
   for dx,dy in dirs:
    v=(u[0]+dx,u[1]+dy)
    if not(0<=v[0]<NX and 0<=v[1]<NY) or self.blocked[v[1],v[0]]:continue
    if dx and dy and (self.blocked[u[1],v[0]] or self.blocked[v[1],u[0]]):continue
    nc=c+(math.sqrt(2) if dx and dy else 1)*(1+float(self.penalty[v[1],v[0]]))
    if nc+1e-8<cost.get(v,1e99):cost[v]=nc;prev[v]=u;heapq.heappush(h,(nc+heuristic(v),nc,v))
  return None,{'reason':'no path in this conservative raster','expanded_nodes':expanded}
 def simplify(self,p):
  prefix=[0]
  for a,b in zip(p,p[1:]):prefix.append(prefix[-1]+self.line_cost(a,b))
  out=[p[0]];i=0
  while i<len(p)-1:
   j=len(p)-1
   while j>i+1:
    if self.clear(p[i],p[j]) and (self.mode=='shortest' or self.line_cost(p[i],p[j])<=1.01*(prefix[j]-prefix[i])):break
    j-=1
   out.append(p[j]);i=j
  return out
 def run(self):
  started=time.monotonic();ap,an=[v[0]['xy'] for v in self.ev];bp,bn=[v[1]['xy'] for v in self.ev];sy=(ap[1]+an[1])/2;dy=round(((bp[1]+bn[1])/2)/G)*G+self.terminal_shift_mm
  sx=ap[0];dx=round((bp[0]-.72)/G)*G
  path,search=self.astar([sx+.7,sy],[dx,dy]);out={'pair':self.pair,'cost_mode':self.mode,'terminal_shift_mm':self.terminal_shift_mm,'source_pads':[[p['ref']+':'+p['pin'] for p in pp] for pp in self.pads],'search':search,'geometry_pass':False}
  if path is None:out['seconds']=time.monotonic()-started;return out
  center=[[sx+.5,sy]]+self.simplify(path)+[[bp[0]-.52,dy]];line=LineString(center)
  pp=list(map(list,line.offset_curve(-.1,join_style='mitre').coords));nn=list(map(list,line.offset_curve(.1,join_style='mitre').coords))
  pp=[ap,[ap[0]+.2,ap[1]+.2]]+pp;nn=[an,[an[0]+.2,an[1]-.2]]+nn
  if '_TX' in self.pair:pp+=[[bp[0]-.27,bp[1]],bp];nn+=[[bn[0]-.27,bn[1]],bn]
  else:pp+=[[bp[0],dy-.1],bp];nn+=[[bn[0],dy+.1],bn]
  traces=[]
  for points,net in zip([pp,nn],self.nets):
   q=LineString(points);viol=[];mind=1e9
   for i in vt.query(q.buffer(.501)):
    if vn[i]==net:continue
    distance=q.distance(vp[i])-.05-rv[i];mind=min(mind,distance)
    if distance<.1-1e-6:viol.append({'via_index':int(i),'net':vn[i],'xy':list(xy[i]),'copper_gap_mm':distance})
   othergap=min([q.distance(o)-W for o in self.existing],default=None)
   traces.append({'net':net,'points':points,'length_mm':q.length,'simple':q.is_simple,'minimum_source_via_copper_gap_mm':mind,'via_violations':viol,'minimum_existing_channel_copper_gap_mm':othergap,'board_edge_copper_gap_mm':min(q.bounds[0],q.bounds[1],96-q.bounds[2],45-q.bounds[3])-.05})
  pairgap=LineString(pp).distance(LineString(nn))-W
  out.update({'centerline':center,'traces':traces,'pair_copper_gap_mm':pairgap,'P_N_length_difference_mm':abs(traces[0]['length_mm']-traces[1]['length_mm']),'seconds':time.monotonic()-started})
  out['geometry_pass']=pairgap>=.1-1e-6 and all(t['simple'] and not t['via_violations'] and t['board_edge_copper_gap_mm']>=.25 and (t['minimum_existing_channel_copper_gap_mm'] is None or t['minimum_existing_channel_copper_gap_mm']>=.1-1e-6) for t in traces)
  if not out['geometry_pass']:out['failure']='exact geometry check rejected candidate; no clearance was relaxed'
  return out

def summary(a,b):
 return {'channels':len([r for r in [a,b] if r['geometry_pass']]),'same_plane_both_pass':a['geometry_pass'] and b['geometry_pass'],'interchannel_copper_gap_mm':min([LineString(ta['points']).distance(LineString(tb['points']))-W for ta in a.get('traces',[]) for tb in b.get('traces',[])],default=None)}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--scenario',type=int);args=ap.parse_args()
 pairnames=['S06_SW_TX0','S06_SW_RX0'];modes=['shortest','avoid_other','north','south'];scenarios=[(order,mode) for mode in modes for order in [pairnames,pairnames[::-1]]]
 baselinefile=D/'INDEPENDENT_BASELINES.json'
 if baselinefile.exists():baselines=json.loads(baselinefile.read_text())
 else:
  baselines={p:Router(p).run() for p in pairnames};baselinefile.write_text(json.dumps(baselines,indent=2))
 assert all(r['geometry_pass'] for r in baselines.values()),'Independent baseline failed exact geometry checks'
 completed=[]
 for i,(order,mode) in enumerate(scenarios):
  if args.scenario is not None and i!=args.scenario:continue
  print('Start scenario',i,order,mode,flush=True)
  a=Router(order[0],mode=mode,other_baseline=baselines[order[1]]).run()
  if a['geometry_pass']:b=Router(order[1],existing=[a]).run()
  else:b={'pair':order[1],'geometry_pass':False,'not_attempted':'first channel exact geometry did not pass'}
  r={'source_sha256':d['sha256'],'scenario':i,'order':order,'first_cost_mode':mode,'target_plane_ordinal':7,'adjacent_continuous_GND_requirement':8,'first':a,'second':b,**summary(a,b)}
  (D/f'SCENARIO_{i:02d}.json').write_text(json.dumps(r,indent=2));completed.append(r);print('Finished scenario',i,'both pass',r['same_plane_both_pass'],'interchannel gap',r['interchannel_copper_gap_mm'],'reasons',[v.get('search',{}).get('reason',v.get('failure')) for v in [a,b]],flush=True)
  if r['same_plane_both_pass'] and args.scenario is None:break
 assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==d['sha256']
 manifest={'source_sha256':d['sha256'],'source_vias':len(d['vias']),'source_unchanged':True,'plane_model':'all original vias projected, original other copper excluded; one new signal plane, continuous GND reference only required not implemented','grid_mm':G,'width_mm':W,'pair_gap_mm':GAP,'other_net_clearance_mm':CLEAR,'centerline_via_inflation_mm':.27,'centerline_existing_trace_inflation_mm':.32,'maximum_expanded_nodes_per_channel':MAX_NODES,'maximum_declared_x1_scenarios':len(scenarios),'executed_in_this_invocation':[r['scenario'] for r in completed],'cost_modes':{'shortest':'unit geometric step cost','avoid_other':'8 * max(0,1-distance/0.8mm) penalty around other independently routed centerline','north':'3 * y/45mm additional node cost','south':'3 * (1-y/45mm) additional node cost'},'search_policy':'At most both route orders times four first-channel costs, no source hole moves or clearance reductions. First routes may be redesigned; second is fresh shortest route with first as copper obstacle. Stop at first exact same-plane success or eight scenarios. Explicit --scenario can replay one declared scenario. Not an unrestricted global optimization.','x2_expansion_gate':'Only if both x1 channels pass exact checks on the same plane; x2 must have a separately stated bounded scenario set.'}
 (D/'SEARCH_SCOPE.json').write_text(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
