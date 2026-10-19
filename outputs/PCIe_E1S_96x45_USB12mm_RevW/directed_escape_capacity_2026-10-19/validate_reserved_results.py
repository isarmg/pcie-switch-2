"""Independent exact checks of reserved-port study. Uses all 3837 source via
coordinates and actual source pad endpoints; no router geometry predicates.
"""
from pathlib import Path
import json,os,hashlib,math,itertools
import numpy as np
from shapely import Point,LineString,Polygon,box,STRtree,distance
D=Path(__file__).parent;source=Path(os.environ['E1S_SOURCE']).resolve();d=json.loads((D/'NATIVE_GEOMETRY.json').read_text());e=json.loads((D/'extra_geometry.json').read_text());pre=json.loads((D/'ENDPOINT_PREFLIGHT.json').read_text());sha=hashlib.sha256(source.read_bytes()).hexdigest();assert sha==d['sha256']==e['sha256']==pre['source_sha256']
vp=np.array([Point(v['xy']) for v in d['vias']],dtype=object);rv=np.array([v['diameter']/2 for v in d['vias']]);vn=np.array([v['net'] for v in d['vias']]);checks=[]
port_checks=[]
for pair,ports in pre['candidates'].items():
 for port in ports:
  fragment_checks=[];lines=[];gateway_clear=True
  for t in port['fragments']:
   q=LineString(t['points']);lines.append(q);pads=[p for p in d['pads'] if p['net']==t['net']];pad=next(p for p in pads if (p['ref']=='U1')==(t['end']=='source'));endpoint=t['points'][0] if t['end']=='source' else t['points'][-1];err=math.dist(endpoint,pad['xy']);assert err<=2e-6
   gaps=distance(q,vp)-.05-rv;gaps[vn==t['net']]=np.inf;edge=min(q.bounds[0],q.bounds[1],96-q.bounds[2],45-q.bounds[3])-.05
   fragment_checks.append({'net':t['net'],'end':t['end'],'endpoint_error_mm':err,'simple':q.is_simple,'min_all_via_copper_gap_mm':float(np.min(gaps)),'edge_gap_mm':edge})
  for g in port['gateways']:
   gaps=distance(Point(g['xy']),vp)-rv-.27;gaps[np.isin(vn,[t['net'] for t in port['fragments']])]=np.inf
   gateway_clear=bool(gateway_clear and np.min(gaps)>=-1e-8)
  pg=min(a.distance(b)-.1 for i,a in enumerate(lines) for j,b in enumerate(lines) if i<j and port['fragments'][i]['net']!=port['fragments'][j]['net'])
  valid=pg>=.1-1e-6 and gateway_clear and all(x['simple'] and x['min_all_via_copper_gap_mm']>=.1-1e-6 and x['edge_gap_mm']>=.25 for x in fragment_checks);assert valid==port['local_exact_pass'],port['candidate_id']
  port_checks.append({'candidate_id':port['candidate_id'],'independent_local_pass':valid,'pair_gap_mm':pg,'gateways_clear_of_other_vias':gateway_clear,'fragments':fragment_checks})
for f in sorted(D.glob('RESERVED_SCENARIO_*.json')):
 s=json.loads(f.read_text());assert s['source_sha256']==sha;selected=pre['selected_combinations'][s['combination_index']]['selected'];previous=[];routes=[]
 for r in s['attempts']:
  if not r.get('traces'):assert not r['geometry_pass'];routes.append({'pair':r['pair'],'polyline_exists':False,'failure':r['search']});continue
  details=[];lines=[];reserved=[LineString(t['points']) for p,port in selected.items() if p!=r['pair'] for t in port['fragments']]
  for t in r['traces']:
   q=LineString(t['points']);lines.append(q);pads=[p for p in d['pads'] if p['net']==t['net']];ends=[next(p for p in pads if p['ref']=='U1'),next(p for p in pads if p['ref']!='U1')];err=max(math.dist(a,p['xy']) for a,p in zip([t['points'][0],t['points'][-1]],ends));assert err<=2e-6
   gaps=distance(q,vp)-.05-rv;gaps[vn==t['net']]=np.inf;bad=[{'net':str(vn[i]),'xy':d['vias'][int(i)]['xy'],'copper_gap_mm':float(gaps[i])} for i in np.flatnonzero(gaps<.1-1e-6)]
   existing=min([q.distance(x)-.1 for x in previous],default=None);reservedgap=min(q.distance(x)-.1 for x in reserved);edge=min(q.bounds[0],q.bounds[1],96-q.bounds[2],45-q.bounds[3])-.05
   details.append({'net':t['net'],'length_mm':q.length,'endpoint_max_error_mm':err,'simple':q.is_simple,'minimum_all_source_via_copper_gap_mm':float(np.min(gaps)),'source_via_violations':bad,'minimum_accepted_channel_copper_gap_mm':existing,'minimum_other_selected_fanout_copper_gap_mm':reservedgap,'board_edge_copper_gap_mm':edge})
  pg=lines[0].distance(lines[1])-.1;valid=pg>=.1-1e-6 and all(t['simple'] and not t['source_via_violations'] and t['board_edge_copper_gap_mm']>=.25 and t['minimum_other_selected_fanout_copper_gap_mm']>=.1-1e-6 and (t['minimum_accepted_channel_copper_gap_mm'] is None or t['minimum_accepted_channel_copper_gap_mm']>=.1-1e-6) for t in details);assert valid==r['geometry_pass'],(f.name,r['pair'])
  routes.append({'pair':r['pair'],'polyline_exists':True,'independent_exact_pass':valid,'pair_copper_gap_mm':pg,'P_N_length_difference_mm':abs(lines[0].length-lines[1].length),'traces':details})
  if valid:previous.extend(lines)
 n=sum(bool(r.get('independent_exact_pass')) for r in routes);assert n==s['successfully_routed_channels'];assert (n==4)==s['all_four_channels_exact_pass']
 mingap=min([a.distance(b)-.1 for i in range(0,len(previous),2) for j in range(i+2,len(previous),2) for a in previous[i:i+2] for b in previous[j:j+2]],default=None)
 checks.append({'scenario_file':f.name,'source_sha256':sha,'all_pass_fail_labels_confirmed':True,'accepted_channels':n,'minimum_interchannel_copper_gap_mm':mingap,'routes':routes})
# Retained F.Cu AC-output sections, both lane 0 and lane 1, against actual source copper.
front=[]
for p in e['pads']:
 if 'F.Cu' in p['layers']:front.append((p['net'],'pad bbox '+p['ref']+':'+p['pin'],box(*p['bbox']),0))
for t in d['tracks']:
 if t['layer']=='F.Cu':front.append((t['net'],'source track',LineString([t['start'],t['end']]),t['width']/2))
for v in d['vias']:
 if v['top']=='F.Cu':front.append((v['net'],'source via',Point(v['xy']),v['diameter']/2))
for z in d['front_copper_zones']:
 for p in z['polygons']:front.append((z['net'],'saved filled front zone',Polygon(p['shell'],p['holes']),0))
ftree=STRtree([v[2] for v in front]);ac=[]
for lane,polarity in itertools.product([0,1],['P','N']):
 net=f'{{slash}}S06_SSD_RX{lane}_{polarity}';ts=[t for t in d['tracks'] if t['net']==net];assert len(ts)==1;t=ts[0];q=LineString([t['start'],t['end']]);gaps=[];bad=[]
 for ix in ftree.query(q.buffer(.6)):
  n,kind,g,rad=front[ix]
  if n==net:continue
  gap=q.distance(g)-.05-rad;gaps.append(gap)
  if gap<.1-1e-6:bad.append({'net':n,'kind':kind,'gap_mm':gap})
 ac.append({'net':net,'layer':t['layer'],'length_mm':q.length,'minimum_other_front_copper_gap_mm':min(gaps),'violations':bad,'pass':not bad});assert not bad
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
result={'source_sha256':sha,'source_unchanged':True,'source_vias_preserved':len(d['vias']),'scenario_count':len(checks),'best_accepted_channels':max([r['accepted_channels'] for r in checks],default=0),'complete_x2_same_plane_exact_pass':any(r['accepted_channels']==4 for r in checks),'all_pass_fail_labels_confirmed':True,'all_32_local_fanout_candidate_labels_confirmed':True,'fanout_candidate_checks':port_checks,'AC_output_sections_retained_and_checked':ac,'scenarios':checks,'limitations':['Geometry only; no 24-layer PCB, native whole-board DRC, actual GND reference, impedance, SI or manufacturing verification.','All original source vias projected but old internal tracks/pours omitted.','No x4/two-slot/16-directional-channel capacity result.','Bounded unsuccessful search does not prove impossibility.']}
(D/'RESERVED_EXACT_CHECKS.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ['scenarios','fanout_candidate_checks']},indent=2))
