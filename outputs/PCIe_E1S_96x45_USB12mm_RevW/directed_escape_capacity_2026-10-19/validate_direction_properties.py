"""Independent direction and un-clipped miter reconstruction. No imports from
router implementations. Complements all-via/real-pad exact geometry validation.
"""
from pathlib import Path
import json,math,hashlib,os
import numpy as np
from shapely import LineString
D=Path(__file__).parent;pre=json.loads((D/'ENDPOINT_PREFLIGHT.json').read_text());sha=hashlib.sha256(Path(os.environ['E1S_SOURCE']).read_bytes()).hexdigest();assert sha==pre['source_sha256'];checks=[]
for f in sorted(D.glob('RESERVED_SCENARIO_*.json')):
 s=json.loads(f.read_text());selected=pre['selected_combinations'][s['combination_index']]['selected'];assert s['source_sha256']==sha
 for r in s['attempts']:
  if 'centerline' not in r:continue
  c=np.asarray(r['centerline'],dtype=float);v=np.diff(c,axis=0);length=np.linalg.norm(v,axis=1);assert min(length)>1e-8;u=v/length[:,None];assert np.linalg.norm(u[0]-[1,0])<1e-7 and np.linalg.norm(u[-1]-[1,0])<1e-7;dots=np.sum(u[:-1]*u[1:],axis=1);assert min(dots,default=1)>=-1e-7
  item={'scenario_file':f.name,'pair':r['pair'],'source_departure_and_destination_arrival_east':True,'maximum_centerline_turn_degrees':math.degrees(math.acos(float(np.clip(min(dots,default=1),-1,1)))),'centerline_simple':LineString(c).is_simple,'accepted':r['geometry_pass'],'traces':[]}
  for k,t in enumerate(r.get('traces',[])):
   offset=[-.1,.1][k];n=np.column_stack([-u[:,1],u[:,0]]);expected=[c[0]+offset*n[0]]
   for i in range(1,len(c)-1):
    # Intersect the two independently displaced consecutive support lines.
    matrix=np.column_stack([u[i-1],-u[i]]);rhs=offset*(n[i]-n[i-1]);step=np.linalg.solve(matrix,rhs);expected.append(c[i]+offset*n[i-1]+step[0]*u[i-1])
   expected.append(c[-1]+offset*n[-1]);template=selected[r['pair']]['fragments'];allpoints=template[k]['points'][:2]+[list(q) for q in expected]+template[k+2]['points'][2:];assert len(allpoints)==len(t['points']);err=float(np.max(np.linalg.norm(np.asarray(allpoints)-np.asarray(t['points']),axis=1)));assert err<1e-7
   q=LineString(t['points']);assert not r['geometry_pass'] or q.is_simple
   item['traces'].append({'net':t['net'],'unclipped_miter_point_count':len(expected),'maximum_reconstruction_error_mm':err,'full_pin_to_pin_polyline_simple':q.is_simple})
  assert not r['geometry_pass'] or item['centerline_simple'];checks.append(item)
result={'source_sha256':sha,'all_reconstructed_directions_and_offsets_match':True,'checks':checks,'method':'Independent support-line intersections; no router offset construction or Shapely offset_curve called.'};(D/'DIRECTION_INDEPENDENT_CHECKS.json').write_text(json.dumps(result,indent=2));print('Direction and unclipped miter checks passed:',len(checks),'route candidates')
