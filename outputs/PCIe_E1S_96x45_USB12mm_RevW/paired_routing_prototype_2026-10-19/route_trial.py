"""Scratch-only paired centerline trial; never writes source PCB or imports its routes.
Conservatively projects ALL original vias onto a hypothetical signal plane.
"""
from pathlib import Path
import json,math,heapq,hashlib,time,collections,sys,os
import numpy as np
from shapely import LineString,Point,box,STRtree
D=Path(__file__).parent; BASE=D.parent
SOURCE=Path(os.environ['E1S_SOURCE']).resolve()
d=json.loads((D/'NATIVE_GEOMETRY.json').read_text());extra=json.loads((D/'extra_geometry.json').read_text())
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==d['sha256']==extra['sha256']
W=.1;GAP=.1;CLEAR=.1;PAIR_HALF=W+GAP/2;GRID=.05;EDGE=.25
NETS=['{slash}S06_SW_TX0_P','{slash}S06_SW_TX0_N']
# The planned target is L7, beside continuous GND L8; this does not map old indexes.
PLAN={'physical_layer_ordinal':7,'role':'SSD signal','adjacent_ground_ordinal':8,'plane_status':'proposed, not fabricated or SI validated'}
xy=np.array([v['xy'] for v in d['vias']]);r=np.array([v['diameter']/2 for v in d['vias']]);nets=[v['net'] for v in d['vias']]
pts=[Point(*v['xy']) for v in d['vias']];tree=STRtree(pts)

# Distance checks evaluate exact line segments; a positive result is not raster-only.
def collisions(points,net=None,rad=W/2,clear=CLEAR,include_partner=True):
 out=[]
 for a,b in zip(points,points[1:]):
  line=LineString([a,b]);ids=tree.query(line.buffer(rad+clear+float(r.max())+.001))
  for i in ids:
   if net is not None and nets[i]==net:continue
   distance=line.distance(pts[i])-rad-r[i]
   if distance<clear-1e-6:out.append({'via_index':int(i),'net':nets[i],'xy':list(xy[i]),'edge_clearance_mm':float(distance),'segment':[a,b]})
 return out

def raster():
 nx=int(96/GRID)+1;ny=int(45/GRID)+1;arr=np.zeros((ny,nx),dtype=np.bool_)
 # .27 reserves the miter corner envelope plus electrical clearance (.15+.10).
 for v in d['vias']:
  if v['net'] in NETS:continue
  x,y=v['xy'];rad=v['diameter']/2+.27
  x0=max(0,int(math.floor((x-rad)/GRID)));x1=min(nx-1,int(math.ceil((x+rad)/GRID)))
  y0=max(0,int(math.floor((y-rad)/GRID)));y1=min(ny-1,int(math.ceil((y+rad)/GRID)))
  xx=np.arange(x0,x1+1)*GRID;yy=np.arange(y0,y1+1)[:,None]*GRID
  arr[y0:y1+1,x0:x1+1]|=(xx-x)**2+(yy-y)**2<=rad**2
 inset=math.ceil((EDGE+PAIR_HALF)/GRID)
 arr[:inset]=1;arr[-inset:]=1;arr[:,:inset]=1;arr[:,-inset:]=1
 return arr

def astar(a,b,arr):
 nx=arr.shape[1];a=tuple(int(round(q/GRID)) for q in a);b=tuple(int(round(q/GRID)) for q in b)
 if arr[a[1],a[0]] or arr[b[1],b[0]]:raise RuntimeError('blocked centerline endpoint')
 def heuristic(x,y):
  dx=abs(x-b[0]);dy=abs(y-b[1]);return max(dx,dy)+(math.sqrt(2)-1)*min(dx,dy)
 h=[(heuristic(*a),0,a)];cost={a:0};came={};visited=0;dirs=[(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)]
 while h:
  _,g,u=heapq.heappop(h)
  if g>cost[u]+1e-8:continue
  visited+=1
  if u==b:
   p=[u]
   while p[-1]!=a:p.append(came[p[-1]])
   print('A* expanded',visited,'nodes',flush=True);return [[x*GRID,y*GRID] for x,y in reversed(p)],visited
  for dx,dy in dirs:
   v=(u[0]+dx,u[1]+dy)
   if not(0<=v[0]<nx and 0<=v[1]<arr.shape[0]) or arr[v[1],v[0]]:continue
   if dx and dy and (arr[u[1],v[0]] or arr[v[1],u[0]]):continue
   ng=g+(math.sqrt(2) if dx and dy else 1)
   if ng+1e-8<cost.get(v,1e99):cost[v]=ng;came[v]=u;heapq.heappush(h,(ng+heuristic(*v),ng,v))
 raise RuntimeError('no path in conservative via-projection centerline raster')

def trunk_clear(a,b):
 line=LineString([a,b]);ids=tree.query(line.buffer(.37+.001))
 return all(nets[i] in NETS or line.distance(pts[i])>=r[i]+.27-1e-8 for i in ids)

def simplify(p):
 out=[p[0]];i=0
 while i<len(p)-1:
  j=len(p)-1
  while j>i+1 and not trunk_clear(p[i],p[j]):j-=1
  out.append(p[j]);i=j
 return out

def metric(points,net):
 line=LineString(points); cs=collisions(points,net);return {'net':net,'points':points,'length_mm':line.length,'is_simple':line.is_simple,'via_clearance_violations':cs,'minimum_board_edge_copper_clearance_mm':min(line.bounds[0],line.bounds[1],96-line.bounds[2],45-line.bounds[3])-W/2}

out={'source_sha256':d['sha256'],'source_copper_layers':32,'scope':'TX0 direction of selected bidirectional S06 lane 0; this file contains new AC-before geometry, and validate_lane.py verifies the retained AC-after section','new_target':PLAN,'geometry_assumptions':{'width_mm':W,'intra_pair_edge_gap_mm':GAP,'other_net_clearance_mm':CLEAR,'pair_copper_envelope_mm':2*W+GAP,'corridor_with_clearance_mm':2*W+GAP+2*CLEAR,'board_edge_copper_clearance_min_mm':EDGE,'grid_mm':GRID},'source_vias_preserved':len(d['vias']),'all_source_vias_projected_conservatively':True,'long_section_source_tracks_reused_or_remapped':False,'AC_after_source_traces_retained':True,'existing_other_tracks_accounted':False,'limits':['This is a new isolated routing corridor geometry feasibility study, not a partially completed 24-layer board.','Existing copper routes and pours must be redesigned in a true 24-layer board; they are deliberately not copied into this clean-plane trial.','All original vias remain obstacles; no source via coordinates, drills, or connectivity changed. No new vias were added.','Actual source via spans refer to a 32-layer stack, so a 24-layer via construction has NOT been defined or qualified.','Continuous GND L8 is a design requirement, not evidence of a filled/connected reference plane.','Fictional switch ball map, vendor escape, stack-up, impedance, return-path and loss/eye validation remain missing.']}
start=time.time()
try:
 a=[7.2,34.5];b=[63.6,24.65]
 path,visited=astar(a,b,raster());path=simplify(path)
 # Fixed incoming/outgoing horizontal orientation makes P/N ordering explicit.
 center=[[7.,34.5]]+path+[[63.8,24.65]]
 line=LineString(center); p=list(map(list,line.offset_curve(-.1,join_style='mitre').coords));n=list(map(list,line.offset_curve(.1,join_style='mitre').coords))
 p=[[6.5,34.0],[6.7,34.2]]+p+[[64.05,24.335],[64.319999,24.335]]
 n=[[6.5,35.0],[6.7,34.8]]+n+[[64.05,24.935],[64.319999,24.935]]
 out['centerline']=center;out['traces']=[metric(p,NETS[0]),metric(n,NETS[1])]
 out['astar_expanded_nodes']=visited
 out['pair_centerline_min_separation_mm']=LineString(p).distance(LineString(n))
 out['pair_copper_min_edge_gap_mm']=out['pair_centerline_min_separation_mm']-W
 out['P_N_length_difference_mm']=abs(out['traces'][0]['length_mm']-out['traces'][1]['length_mm'])
 out['geometry_pass']=all(not t['via_clearance_violations'] and t['is_simple'] and t['minimum_board_edge_copper_clearance_mm']>=EDGE for t in out['traces']) and out['pair_copper_min_edge_gap_mm']>=GAP-1e-6
except Exception as e:out['error']=repr(e);out['geometry_pass']=False
out['seconds']=time.time()-start
out['source_sha256_after']=hashlib.sha256(SOURCE.read_bytes()).hexdigest();assert out['source_sha256_after']==out['source_sha256']
(D/'TRIAL_RESULT.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k not in ['traces','centerline']},indent=2));print('violations',[(x['net'],len(x['via_clearance_violations'])) for x in out.get('traces',[])])
