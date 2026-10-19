"""Separate exact all-via/all-pair validation of bounded scenario outputs.
No native DRC or impedance/manufacturing signoff is asserted.
"""
from pathlib import Path
import json,os,hashlib,math,itertools
import numpy as np
from shapely import Point,LineString,Polygon,box,STRtree,distance
D=Path(__file__).parent;source=Path(os.environ['E1S_SOURCE']).resolve();d=json.loads((D/'NATIVE_GEOMETRY.json').read_text());e=json.loads((D/'extra_geometry.json').read_text());sha=hashlib.sha256(source.read_bytes()).hexdigest();assert sha==d['sha256']==e['sha256']
vp=np.array([Point(v['xy']) for v in d['vias']],dtype=object);rv=np.array([v['diameter']/2 for v in d['vias']]);vn=np.array([v['net'] for v in d['vias']]);checked=[];summ=[]
paths=sorted(D.glob('SCENARIO_*.json'))+sorted(D.glob('X2_SCENARIO_*.json'))+sorted(D.glob('X2_REPAIR_SCENARIO_*.json'))
for p in paths:
 s=json.loads(p.read_text());assert s['source_sha256']==sha,p
 routes=[s['first'],s['second']] if 'first' in s else s['attempts'];previous=[];details=[]
 for r in routes:
  if not r.get('traces'):
   assert not r['geometry_pass'];details.append({'pair':r['pair'],'candidate_polyline_exists':False,'reason':r.get('search',{}).get('reason',r.get('not_attempted'))});continue
  tracechecks=[];lines=[]
  for t in r['traces']:
   q=LineString(t['points']);lines.append(q);net=t['net'];pads=[p for p in d['pads'] if p['net']==net];ends=[next(p for p in pads if p['ref']=='U1'),next(p for p in pads if p['ref']!='U1')]
   endpoint_error=max(math.dist(a,pad['xy']) for a,pad in zip([t['points'][0],t['points'][-1]],ends));assert endpoint_error<=2e-6
   gaps=distance(q,vp)-.05-rv;gaps[vn==net]=np.inf;mingap=float(np.min(gaps));bad=[{'net':d['vias'][int(i)]['net'],'xy':d['vias'][int(i)]['xy'],'copper_gap_mm':float(gaps[i])} for i in np.flatnonzero(gaps<.1-1e-6)]
   othergap=min([q.distance(x)-.1 for x in previous],default=None);edge=min(q.bounds[0],q.bounds[1],96-q.bounds[2],45-q.bounds[3])-.05
   tracechecks.append({'net':net,'length_mm':q.length,'P_or_N':net[-1],'endpoint_max_error_mm':endpoint_error,'simple':q.is_simple,'minimum_board_edge_copper_gap_mm':edge,'minimum_all_source_via_copper_gap_mm':mingap,'source_via_clearance_violations':bad,'minimum_previously_accepted_channel_copper_gap_mm':othergap})
  pg=lines[0].distance(lines[1])-.1;valid=pg>=.1-1e-6 and all(x['simple'] and not x['source_via_clearance_violations'] and x['minimum_board_edge_copper_gap_mm']>=.25 and (x['minimum_previously_accepted_channel_copper_gap_mm'] is None or x['minimum_previously_accepted_channel_copper_gap_mm']>=.1-1e-6) for x in tracechecks)
  assert valid==r['geometry_pass'],(p.name,r['pair'],'independent exact result disagrees')
  details.append({'pair':r['pair'],'candidate_polyline_exists':True,'independent_exact_pass':valid,'pair_copper_gap_mm':pg,'P_N_length_difference_mm':abs(lines[0].length-lines[1].length),'traces':tracechecks})
  if valid:previous.extend(lines)
 successes=sum(bool(z.get('independent_exact_pass')) for z in details);allgap=min([a.distance(b)-.1 for i in range(0,len(previous),2) for j in range(i+2,len(previous),2) for a in previous[i:i+2] for b in previous[j:j+2]],default=None)
 checked.append({'scenario_file':p.name,'source_sha256':sha,'all_router_pass_fail_labels_confirmed':True,'accepted_directional_channels':successes,'minimum_interchannel_copper_gap_mm':allgap,'routes':details})
 summ.append({'scenario_file':p.name,'order':s['order'],'accepted_directional_channels':successes,'minimum_interchannel_copper_gap_mm':allgap,'failures':[{'pair':r['pair'],'reason':r.get('search',{}).get('reason',r.get('failure',r.get('not_attempted'))),'endpoint_obstacles':r.get('search',{}).get('endpoint_obstacles')} for r in routes if not r['geometry_pass']]})
# Retained F.Cu AC-output sections, both lane 0 and lane 1: actual existing copper.
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
old=json.loads((D/'INDEPENDENT_BASELINES.json').read_text());x1=next(c for c in checked if c['scenario_file']=='SCENARIO_01.json');deviations=[]
for route in x1['routes']:
 for t in route['traces']:
  original=next(o for o in old[route['pair']]['traces'] if o['net']==t['net']);newfile=json.loads((D/'SCENARIO_01.json').read_text());q=next(r for r in [newfile['first'],newfile['second']] if r['pair']==route['pair']);nt=next(x for x in q['traces'] if x['net']==t['net'])
  deviations.append({'net':t['net'],'independent_length_mm':original['length_mm'],'same_plane_joint_length_mm':t['length_mm'],'added_length_mm':t['length_mm']-original['length_mm'],'path_Hausdorff_deviation_mm':LineString(original['points']).hausdorff_distance(LineString(nt['points']))})
best=max((x for x in summ if x['scenario_file'].startswith('X2')),key=lambda x:x['accepted_directional_channels']);assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
result={'status':'bounded same-plane geometry study completed; formal PCB unchanged','source_sha256':sha,'source_vias_preserved':len(d['vias']),'source_pads':len(d['pads']),'source_hash_unchanged':True,'x1_same_plane_exact_pass':True,'x1_target_signal_ordinal':7,'adjacent_continuous_GND_ordinal_required_not_implemented':8,'x1_complete_bidirectional_lanes':1,'x1_directional_channels':2,'x1_onboard_pair_sections_including_AC':3,'x1_minimum_interchannel_copper_gap_mm':x1['minimum_interchannel_copper_gap_mm'],'x2_initial_scenarios_executed':sum(p.name.startswith('X2_SCENARIO_') for p in paths),'x2_endpoint_repair_scenarios_executed':sum(p.name.startswith('X2_REPAIR_SCENARIO_') for p in paths),'x2_best_candidate':best,'x2_complete_four_directional_channels_proven':best['accepted_directional_channels']==4,'all_reported_pass_fail_labels_independently_recomputed':True,'geometry_rules':{'width_mm':.1,'pair_copper_gap_mm':.1,'other_net_copper_gap_mm':.1,'all_source_vias_projected_to_same_plane':True,'existing_other_internal_copper_included':False,'source_vias_moved_or_deleted':False},'scenario_summary':summ,'AC_output_sections_retained_and_checked':ac,'x1_deviation_from_independent_routes':deviations,'limitations':['Not a 24-layer PCB, whole-board native KiCad DRC, SI or manufacturing result.','Fixed source holes from a 32-layer board are all projected, even when real layer spans might not reach the eventual signal plane; a failed search cannot prove actual 24-layer unroutability.','No via position, drill, or span redesigned; no process permission or manufacturer-qualified stack-up assumed.','Successful channel prefixes are not complete x2 lane groups. No x4, two-slot, or 16-channel search was performed.','No new GND plane or return vias were implemented; continuous L8 reference is a requirement, not evidence.','All lengths omit vertical vias and capacitor-package propagation. No delay/skew or impedance acceptance limit is asserted.']}
(D/'EXACT_SCENARIO_CHECKS.json').write_text(json.dumps(checked,indent=2));(D/'JOINT_VALIDATION_SUMMARY.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
