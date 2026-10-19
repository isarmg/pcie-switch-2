import argparse,json,math,itertools,hashlib
from pathlib import Path
from shapely.geometry import LineString,Point
p=argparse.ArgumentParser();p.add_argument('--geometry',type=Path,required=True);p.add_argument('--scenarios',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();g=json.loads(a.geometry.read_text());out=[]
for path in sorted((path for pattern in ('SCENARIO_[0-9][0-9].json','X2_SCENARIO_[0-9][0-9].json','X2_REPAIR_SCENARIO_[0-9][0-9].json') for path in a.scenarios.glob(pattern))):
 s=json.loads(path.read_text());attempts=s.get('attempts') or [s['first'],s['second']];previous=[];checks=[]
 for c in attempts:
  if not c.get('traces'):
   assert not c['geometry_pass'];checks.append({'pair':c['pair'],'result':'no constructed path; bounded-search claim only'});continue
  lines=[];ok=True;tracechecks=[]
  for t in c['traces']:
   n=t['net'];line=LineString(t['points']);lines.append(line);pads=[q for q in g['pads'] if q['net']==n];ids=set();err=[]
   assert len(pads)==2
   for e in (t['points'][0],t['points'][-1]):
    q=min(pads,key=lambda q:math.dist(e,q['xy']));ids.add(q['ref']+':'+q['pin']);err.append(math.dist(e,q['xy']))
   endpoints=ids=={q['ref']+':'+q['pin'] for q in pads} and max(err)<2e-6
   vg=min(line.distance(Point(v['xy']))-.05-v['diameter']/2 for v in g['vias'] if v['net']!=n)
   edge=min(line.bounds[0],line.bounds[1],96-line.bounds[2],45-line.bounds[3])-.05
   cross=min([line.distance(l)-.1 for l in previous],default=None)
   assert abs(line.length-t['length_mm'])<1e-9
   good=endpoints and vg>=.1-1e-6 and edge>=.25 and line.is_simple and (cross is None or cross>=.1-1e-6);ok=ok and good
   tracechecks.append({'net':n,'endpoint_ids':sorted(ids),'endpoint_error_mm':max(err),'length_mm':line.length,'via_gap_mm':vg,'earlier_channel_gap_mm':cross,'edge_mm':edge,'geometric_pass':good})
  pairgap=lines[0].distance(lines[1])-.1;ok=bool(ok and pairgap>=.1-1e-6)
  assert ok==c['geometry_pass'],(path.name,c['pair'],ok,c['geometry_pass'])
  checks.append({'pair':c['pair'],'geometry_pass':ok,'pair_gap_mm':pairgap,'traces':tracechecks})
  if ok:previous.extend(lines)
 summary={'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'checks':checks,'passed_channels':len(previous)//2}
 if 'successfully_routed_channels' in s:assert summary['passed_channels']==s['successfully_routed_channels']
 out.append(summary)
r={'pass':True,'source_sha256':g['sha256'],'scope':'Independent exact geometry against original projected vias and same-plane earlier channels; no complete 24-layer PCB/reference/return/manufacturing/SI qualification','scenarios':out};a.out.write_text(json.dumps(r,indent=2)+'\n');print('Verified',len(out),'scenarios')
