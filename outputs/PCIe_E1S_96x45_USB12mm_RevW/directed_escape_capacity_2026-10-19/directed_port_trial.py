"""Direction-aware bounded x2 prototype. Exact same geometry baseline and
selected three endpoint combinations; no physical pin or source hole changes.
"""
import reserved_escape_trial as base
from reserved_escape_trial import *
from scipy.ndimage import label
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
DIRS=[(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)]
MIN_STRAIGHT_STEPS=4;HEURISTIC_WEIGHT=1.5;TURN_COST=.2

def compact_collinear(points):
 out=[]
 for p in points:
  p=list(p)
  if out and math.dist(out[-1],p)<1e-9:continue
  while len(out)>=2:
   a,b=out[-2:];u=(b[0]-a[0],b[1]-a[1]);v=(p[0]-b[0],p[1]-b[1])
   if abs(u[0]*v[1]-u[1]*v[0])<1e-9 and u[0]*v[0]+u[1]*v[1]>0:out.pop()
   else:break
  out.append(p)
 return out

def directed_offset(points,offset):
 """Explicit miters, never a library repair/clip of self-intersecting offset."""
 points=compact_collinear(points);units=[]
 for a,b in zip(points,points[1:]):
  length=math.dist(a,b)
  if length<1e-9:raise ValueError('zero length centerline segment')
  units.append(((b[0]-a[0])/length,(b[1]-a[1])/length))
 if not units:raise ValueError('empty centerline')
 if math.dist(units[0],(1,0))>1e-7 or math.dist(units[-1],(1,0))>1e-7:raise ValueError('port approach/departure must be east, fixed P/N order')
 out=[[points[0][0]-offset*units[0][1],points[0][1]+offset*units[0][0]]]
 for p,u,v in zip(points[1:-1],units,units[1:]):
  dot=u[0]*v[0]+u[1]*v[1]
  if dot<-1e-7:raise ValueError('turn exceeds 90 degrees or U-turn')
  den=1+dot;out.append([p[0]+offset*(-u[1]-v[1])/den,p[1]+offset*(u[0]+v[0])/den])
 out.append([points[-1][0]-offset*units[-1][1],points[-1][1]+offset*units[-1][0]])
 if not LineString(out).is_simple:raise ValueError('explicit offset self-intersects')
 return out

def relaxed_distance_field(blocked,goal):
 """Compiled 2D graph shortest distance; same no-corner-cut raster, headings
 relaxed. Guides heading-state search around holes without changing clearance."""
 free=~blocked;rows=[];cols=[];values=[]
 specs=[(free[:,:-1]&free[:,1:],0,1,1.),(free[:-1,:]&free[1:,:],0,NX,1.),(free[:-1,:-1]&free[1:,1:]&free[:-1,1:]&free[1:,:-1],0,NX+1,math.sqrt(2)),(free[:-1,1:]&free[1:,:-1]&free[:-1,:-1]&free[1:,1:],1,NX-1,math.sqrt(2))]
 for mask,xoffset,delta,c in specs:
  yy,xx=np.nonzero(mask);src=(yy*NX+xx+xoffset).astype(np.int32);rows.append(src);cols.append(src+delta);values.append(np.full(len(src),c,dtype=np.float32))
 graph=coo_matrix((np.concatenate(values),(np.concatenate(rows),np.concatenate(cols))),shape=(NX*NY,NX*NY)).tocsr()
 return dijkstra(graph,directed=False,indices=goal[1]*NX+goal[0]).reshape(NY,NX)

class DirectedRouter(ReservedRouter):
 def __init__(self,pair,selected,existing=()):
  super().__init__(pair,selected,existing)
  # The global centerline stays away from its own endpoint holes too. Actual
  # pin-to-gateway connections are explicit validated fanouts, not raster paths.
  for via in d['vias']:
   if via['net'] in self.nets:stamp(self.blocked,via['xy'],via['xy'],via['diameter']/2+.27)
  # Do not traverse behind the destination gateway, where the pair spreads
  # onto physical pins. The legitimate final eastward attachment is appended
  # only after search termination. This prevents heading-fixing loops through
  # the channel's own terminal copper/partner via.
  own=np.zeros_like(self.blocked)
  for fragment in self.template['fragments']:
   if fragment['end']!='destination':continue
   for a,b in zip(fragment['points'],fragment['points'][1:]):stamp(own,a,b,.32)
  gate_x=self.template['end'][0];own[:,:int(round(gate_x/G))+1]=False
  self.blocked|=own
 def astar(self,a,b):
  start=tuple(int(round(q/G)) for q in a);goal=tuple(int(round(q/G)) for q in b)
  meta={'heading_state':True,'source_departure_direction':'east','destination_arrival_direction':'east','maximum_turn_degrees':90,'minimum_straight_grid_steps_between_turns':MIN_STRAIGHT_STEPS,'heuristic_weight':HEURISTIC_WEIGHT,'turn_cost_grid_units':TURN_COST}
  if self.blocked[start[1],start[0]] or self.blocked[goal[1],goal[0]]:
   return None,dict(meta,reason='blocked centerline endpoint',expanded_nodes=0)
  # Eight-neighbor moves require both orthogonal cells free, so no 4-connected
  # path is a sufficient proof of no raster path before direction constraints.
  labels,n=label(~self.blocked);sa=int(labels[start[1],start[0]]);sb=int(labels[goal[1],goal[0]])
  if sa!=sb:return None,dict(meta,reason='no path in conservative raster connectivity precheck',expanded_nodes=0,free_components=int(n),start_component=sa,end_component=sb)
  distance_field=relaxed_distance_field(self.blocked,goal)
  meta['heuristic_field']='exact relaxed 2D raster shortest distance, multiplied by declared weight'
  def pack(x,y,h,run):return ((y*NX+x)*8+h)*(MIN_STRAIGHT_STEPS+1)+run
  def unpack(k):
   run=k%(MIN_STRAIGHT_STEPS+1);k//=MIN_STRAIGHT_STEPS+1;h=k%8;k//=8;return k%NX,k//NX,h,run
  def heuristic(x,y):
   return float(distance_field[y,x])
  root=pack(*start,0,MIN_STRAIGHT_STEPS);heap=[(HEURISTIC_WEIGHT*heuristic(*start),0,root)];cost={root:0};previous={};expanded=0
  while heap:
   _,c,k=heapq.heappop(heap)
   if c>cost[k]+1e-8:continue
   expanded+=1;x,y,h,run=unpack(k)
   if (x,y)==goal and h==0 and run==MIN_STRAIGHT_STEPS:
    path=[k]
    while path[-1]!=root:path.append(previous[path[-1]])
    result=[[unpack(t)[0]*G,unpack(t)[1]*G] for t in reversed(path)]
    return result,dict(meta,expanded_nodes=expanded,weighted_cost_grid_units=c,terminal_arrival_heading_index=h,terminal_straight_steps=run)
   if expanded>=MAX_NODES:return None,dict(meta,reason='explicit direction-state node budget reached',expanded_nodes=expanded)
   headings=[h] if run<MIN_STRAIGHT_STEPS else [h,(h-1)%8,(h+1)%8,(h-2)%8,(h+2)%8]
   for nh in headings:
    dx,dy=DIRS[nh];xx=x+dx;yy=y+dy
    if not(0<=xx<NX and 0<=yy<NY) or self.blocked[yy,xx] or (xx,yy)==start:continue
    if dx and dy and (self.blocked[y,xx] or self.blocked[yy,x]):continue
    nr=min(MIN_STRAIGHT_STEPS,run+1) if nh==h else 1
    if (xx,yy)==goal and not(nh==0 and nr==MIN_STRAIGHT_STEPS):continue
    nk=pack(xx,yy,nh,nr);nc=c+(math.sqrt(2) if dx and dy else 1)+(TURN_COST if nh!=h else 0)
    if nc+1e-8<cost.get(nk,1e99):cost[nk]=nc;previous[nk]=k;heapq.heappush(heap,(nc+HEURISTIC_WEIGHT*heuristic(xx,yy),nc,nk))
  return None,dict(meta,reason='no path with declared heading and straight-run constraints',expanded_nodes=expanded)
 def run(self):
  t=self.template;started=time.monotonic();path,search=self.astar(t['start'],t['end'])
  out={'pair':self.pair,'candidate_id':t['candidate_id'],'source_pads':[[p['ref']+':'+p['pin'] for p in pp] for pp in self.pads],'search':search,'geometry_pass':False,'reserved_other_pairs':[p for p in self.selected if p!=self.pair],'algorithm':'direction-state A*, explicit un-repaired miter offsets'}
  if path is None:out['seconds']=time.monotonic()-started;return out
  center=compact_collinear([t['source_anchor']]+path+[t['destination_anchor']]);out['centerline']=center
  try:
   traces=[]
   for i,off in enumerate([-.1,.1]):
    points=directed_offset(center,off);src=t['fragments'][i]['points'];dest=t['fragments'][i+2]['points'];points=src[:2]+points+dest[2:]
    traces.append({'net':self.nets[i],'points':points})
  except ValueError as ex:out.update(failure=str(ex),seconds=time.monotonic()-started);return out
  other=[x for r in self.placed+self.reservations for x in r['traces']];checks,pg,ok=check_lines(traces,other)
  out.update({'traces':checks,'pair_copper_gap_mm':pg,'P_N_length_difference_mm':abs(checks[0]['length_mm']-checks[1]['length_mm']),'seconds':time.monotonic()-started,'geometry_pass':ok})
  if not ok:out['failure']='complete explicit P/N polyline geometry rejected; no repair or relaxed clearance'
  return out

def main():
 # Reuse the identical finite candidate/combination/order selection. Only the
 # router implementation changes; this copy is a distinct experiment directory.
 base.ReservedRouter=DirectedRouter;base.main()
 scope=json.loads((D/'RESERVED_SEARCH_SCOPE.json').read_text());scope['algorithm_version']='directed-ports-v1';scope['algorithm_changes']={'direction_state':True,'own_endpoint_vias_in_centerline_obstacles':True,'own_destination_fanout_blocked_beyond_gateway':True,'port_directions':'east departure and arrival; P/N order unchanged','max_turn_degrees':90,'minimum_straight_grid_steps_between_turns':MIN_STRAIGHT_STEPS,'heuristic_weight':HEURISTIC_WEIGHT,'turn_cost_grid_units':TURN_COST,'simplification':'collinear compression only, no angle-changing shortcut','offset':'explicit miters; no library self-intersection repair; full polylines checked','raster_connectivity_precheck':'4-connected free-cell components, sufficient no-path test for 8-neighbor graph with no corner cutting'};scope['source_geometry_or_fanout_candidate_changes_from_reserved_v1']=False
 (D/'RESERVED_SEARCH_SCOPE.json').write_text(json.dumps(scope,indent=2))
if __name__=='__main__':main()
