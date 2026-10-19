"""Add the opposite-direction channel of S06 lane 0 to the same new signal plane.
Uses the independently solved TX0 geometry as copper obstacles, preserving every via.
"""
from pathlib import Path
import json,math,time,hashlib
D=Path(__file__).parent
ns={'__file__':str(D/'route_trial.py')};exec(compile((D/'route_trial.py').read_text().split("out={'source_sha256'")[0],str(D/'route_trial.py'),'exec'),ns)
globals().update(ns)
TX=json.loads((D/'TRIAL_RESULT.json').read_text()); assert TX['geometry_pass']
NETS=['{slash}S06_SW_RX0_P','{slash}S06_SW_RX0_N'];ns['NETS']=NETS
existing=[]
old_raster=ns['raster'];old_clear=ns['trunk_clear'];old_collisions=ns['collisions']
def raster():
 arr=old_raster();ny,nx=arr.shape
 for line in existing:
  for a,b in zip(line.coords,list(line.coords)[1:]):
   rad=.32;x0=max(0,int(math.floor((min(a[0],b[0])-rad)/GRID)));x1=min(nx-1,int(math.ceil((max(a[0],b[0])+rad)/GRID)))
   y0=max(0,int(math.floor((min(a[1],b[1])-rad)/GRID)));y1=min(ny-1,int(math.ceil((max(a[1],b[1])+rad)/GRID)))
   xs=np.arange(x0,x1+1)*GRID;ys=np.arange(y0,y1+1)[:,None]*GRID;vx=b[0]-a[0];vy=b[1]-a[1];den=vx*vx+vy*vy
   frac=np.clip(((xs-a[0])*vx+(ys-a[1])*vy)/den,0,1) if den else 0
   arr[y0:y1+1,x0:x1+1]|=(xs-(a[0]+frac*vx))**2+(ys-(a[1]+frac*vy))**2<=rad**2
 return arr
def trunk_clear(a,b):
 line=LineString([a,b]);return old_clear(a,b) and all(line.distance(ob)>=.32-1e-8 for ob in existing)
ns['trunk_clear']=trunk_clear
out={'source_sha256':d['sha256'],'source_copper_layers':32,'new_target':{**PLAN,'physical_layer_ordinal':18,'adjacent_ground_ordinal':17},'scope':'S06 lane 0 RX channel, on a separate prospective L18','obstacle_source':'all 3837 original vias; TX0 is on separate prospective L7','existing_source_tracks_accounted':False}
start=time.time()
try:
 path,visited=ns['astar']([9.2,34.5],[57.0,24.65],raster());path=ns['simplify'](path)
 center=[[9.,34.5]]+path+[[57.18,24.65]]
 line=LineString(center);p=list(map(list,line.offset_curve(-.1,join_style='mitre').coords));n=list(map(list,line.offset_curve(.1,join_style='mitre').coords))
 p=[[8.5,34.0],[8.7,34.2]]+p+[[57.7,24.55],[57.7,24.335]]
 n=[[8.5,35.0],[8.7,34.8]]+n+[[57.7,24.75],[57.7,24.935]]
 out['centerline']=center;out['traces']=[ns['metric'](p,NETS[0]),ns['metric'](n,NETS[1])]
 out['astar_expanded_nodes']=visited
 out['pair_copper_min_edge_gap_mm']=LineString(p).distance(LineString(n))-W
 out['P_N_length_difference_mm']=abs(out['traces'][0]['length_mm']-out['traces'][1]['length_mm'])
 out['minimum_pair_to_pair_copper_edge_gap_mm']=min([LineString(p).distance(ob)-W for p in [p,n] for ob in existing],default=1e9)
 out['geometry_pass']=all(not t['via_clearance_violations'] and t['is_simple'] and t['minimum_board_edge_copper_clearance_mm']>=EDGE for t in out['traces']) and out['pair_copper_min_edge_gap_mm']>=GAP-1e-6 and out['minimum_pair_to_pair_copper_edge_gap_mm']>=CLEAR-1e-6
except Exception as e:out['error']=repr(e);out['geometry_pass']=False
out['minimum_pair_to_pair_copper_edge_gap_mm']=None
out['seconds']=time.time()-start;out['source_sha256_after']=hashlib.sha256(SOURCE.read_bytes()).hexdigest();assert out['source_sha256_after']==d['sha256']
(D/'RX0_SEPARATE_RESULT.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k not in ['traces','centerline']},indent=2));print('violations',[(x['net'],len(x['via_clearance_violations'])) for x in out.get('traces',[])])
