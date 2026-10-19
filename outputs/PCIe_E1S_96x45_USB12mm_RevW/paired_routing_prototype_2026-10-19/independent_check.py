import json,math,hashlib,argparse
from pathlib import Path
from shapely.geometry import LineString,Point
p=argparse.ArgumentParser();p.add_argument('--geometry',required=True,type=Path);p.add_argument('--trial-dir',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args();g=json.loads(a.geometry.read_text());d=a.trial_dir
expected={'{slash}S06_SW_TX0_P':{'U1:AH3','C4041:1'},'{slash}S06_SW_TX0_N':{'U1:AJ3','C4042:1'},'{slash}S06_SW_RX0_P':{'U1:AH5','J6:A18'},'{slash}S06_SW_RX0_N':{'U1:AJ5','J6:A17'}}
r=[]
for file in ['TRIAL_RESULT.json','RX0_SEPARATE_RESULT.json']:
 x=json.loads((d/file).read_text());assert x['source_sha256']==g['sha256'];lines=[]
 for t in x['traces']:
  n=t['net'];pts=t['points'];line=LineString(pts);lines.append(line);pads=[q for q in g['pads'] if q['net']==n];ids=set();errs=[]
  for e in [pts[0],pts[-1]]:
   q=min(pads,key=lambda q:math.dist(e,q['xy']));ids.add(q['ref']+':'+q['pin']);errs.append(math.dist(e,q['xy']))
  assert ids==expected[n] and max(errs)<2e-6,(n,ids)
  nearest=min(line.distance(Point(v['xy']))-.05-v['diameter']/2 for v in g['vias'] if v['net']!=n)
  edge=min(line.bounds[0],line.bounds[1],96-line.bounds[2],45-line.bounds[3])-.05
  assert nearest>=.1-1e-6 and edge>=.25 and line.is_simple
  assert abs(line.length-t['length_mm'])<1e-9
  r.append({'net':n,'endpoint_ids':sorted(ids),'max_endpoint_error_mm':max(errs),'length_mm':line.length,'nearest_other_via_edge_mm':nearest,'board_edge_clearance_mm':edge})
 gap=lines[0].distance(lines[1])-.1;assert gap>=.1-1e-6
 assert abs(abs(lines[0].length-lines[1].length)-x['P_N_length_difference_mm'])<1e-9
out={'pass':True,'source_sha256':g['sha256'],'scope':'Independent endpoints, polyline lengths, same-plane P/N gap, all old via projections and board edge; no other internal routes/planes or via-span/return/SI validation','checks':r,'other_internal_copper_accounted':False,'new_reference_plane_verified':False,'native_24_layer_DRC_run':False};a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
