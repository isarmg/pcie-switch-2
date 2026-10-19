"""Cross-check real endpoints, complete AC chain, saved surface copper and lane counts.
Geometry only. Native board DRC and impedance/return-path signoff are NOT claimed.
"""
from pathlib import Path
import json,math,hashlib,collections,re,os
from shapely import LineString,Point,Polygon,box,STRtree
D=Path(__file__).parent;d=json.loads((D/'NATIVE_GEOMETRY.json').read_text());e=json.loads((D/'extra_geometry.json').read_text());tx=json.loads((D/'TRIAL_RESULT.json').read_text());rx=json.loads((D/'RX0_SEPARATE_RESULT.json').read_text());source=Path(os.environ['E1S_SOURCE']).resolve()
assert d['sha256']==e['sha256']==tx['source_sha256']==rx['source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
norm=lambda n:n.replace('{slash}','').lstrip('/')
nettracks=collections.defaultdict(list)
for t in d['tracks']:nettracks[norm(t['net'])].append(t)
def cls(n):
 if re.search(r'REFCLK|CLKBUF[12]_IN|XTAL|REF_KA_(?:X[12]|DIF0[PN])',n):return 'clock'
 if re.match(r'S\d+_(?:SW|SSD)_[RT]X\d|CPU_(?:G5|PEX)_[RT]X\d|TBT_(?:CPU|AR)_TX\d',n):return 'PCIe'
 if re.match(r'TBT_(?:DP_(?:ML|AUX)|PA_AUX)',n):return 'DP'
 if re.match(r'TBT_(?:CIO_[RT]X|USB2_(?:BOTTOM|RP|TOP))',n):return 'USB_TBT'
 return 'other'
sections=[]
for n,ts in nettracks.items():
 if not n.endswith('_P') or cls(n)=='other' or n[:-2]+'_N' not in nettracks:continue
 n2=n[:-2]+'_N';ls=[sorted({t['layer'] for t in nettracks[z] if t['layer'] not in ['F.Cu','B.Cu']}) for z in [n,n2]]
 sections.append({'pair':n[:-2],'class':cls(n),'P_internal_layers':ls[0],'N_internal_layers':ls[1],'mismatched_internal_layers':ls[0]!=ls[1]})
# Sxx_SW_TXn + Sxx_SSD_RXn are two sides of one AC-coupled channel, not two lanes.
slot_tx=sorted({x['pair'] for x in sections if re.fullmatch(r'S\d+_SW_TX[0-3]',x['pair'])});slot_rx=sorted({x['pair'] for x in sections if re.fullmatch(r'S\d+_SW_RX[0-3]',x['pair'])});ac=sorted({x['pair'] for x in sections if re.fullmatch(r'S\d+_SSD_RX[0-3]',x['pair'])})
endpoint_checks=[];via_min=[]
for trial in [tx,rx]:
 for t in trial['traces']:
  net=t['net'];pads=[p for p in d['pads'] if p['net']==net];vias=[v for v in d['vias'] if v['net']==net]
  assert len(pads)==2 and len(vias)==2
  endpoints=[t['points'][0],t['points'][-1]];errs=[]
  for point in endpoints:
   pad=min(pads,key=lambda p:math.dist(point,p['xy']));via=min(vias,key=lambda v:math.dist(point,v['xy']));errs.append({'pad':pad['ref']+':'+pad['pin'],'pad_xy_mm':pad['xy'],'pad_copper_layers':pad['layers'],'route_xy_mm':point,'route_to_pad_center_error_mm':math.dist(point,pad['xy']),'route_to_original_via_error_mm':math.dist(point,via['xy']),'original_via_top':via['top'],'original_via_bottom':via['bottom'],'via_diameter_mm':via['diameter'],'via_drill_mm':via['drill']})
  endpoint_checks.append({'net':net,'assigned_new_plane':trial['new_target']['physical_layer_ordinal'],'endpoints':errs,'pass':all(x['route_to_pad_center_error_mm']<2e-6 and x['route_to_original_via_error_mm']<2e-6 for x in errs)})
  line=LineString(t['points']);minimum=min(line.distance(Point(v['xy']))-.05-v['diameter']/2 for v in d['vias'] if v['net']!=net)
  via_min.append({'net':net,'minimum_other_net_via_copper_edge_gap_mm':minimum})
# Source AC-output traces remain the same two straight, parallel front-side traces.
front=[]
for p in e['pads']:
 if 'F.Cu' in p['layers']:front.append((p['net'],'pad bbox '+p['ref']+':'+p['pin'],box(*p['bbox']),0))
for t in d['tracks']:
 if t['layer']=='F.Cu':front.append((t['net'],'source track',LineString([t['start'],t['end']]),t['width']/2))
for v in d['vias']:
 if v['top']=='F.Cu':front.append((v['net'],'source via',Point(v['xy']),v['diameter']/2))
for z in d['front_copper_zones']:
 for p in z['polygons']:front.append((z['net'],'saved filled front zone',Polygon(p['shell'],p['holes']),0))
ftree=STRtree([v[2] for v in front]);acs=[]
for polarity in ['P','N']:
 net='{slash}S06_SSD_RX0_'+polarity;ts=[t for t in d['tracks'] if t['net']==net];assert len(ts)==1;t=ts[0];line=LineString([t['start'],t['end']]);viol=[];nearest=[]
 for ix in ftree.query(line.buffer(.5)):
  n,kind,g,rad=front[ix]
  if n==net:continue
  dist=line.distance(g)-.05-rad;nearest.append(dist)
  if dist<.1-1e-6:viol.append({'other_net':n,'kind':kind,'copper_edge_gap_mm':dist})
 ps=[p for p in d['pads'] if p['net']==net];assert len(ps)==2
 acs.append({'net':net,'layer':t['layer'],'width_mm':t['width'],'length_mm':t['length'],'points':[t['start'],t['end']],'endpoint_pads':[p['ref']+':'+p['pin'] for p in ps],'other_front_copper_min_edge_gap_mm':min(nearest),'violations_at_0p1mm':viol,'pass':not viol})
old=[]
for base in ['S06_SW_TX0','S06_SW_RX0']:
 ls=[sum(t['length'] for t in nettracks[base+'_'+p]) for p in ['P','N']];old.append({'pair':base,'P_length_mm':ls[0],'N_length_mm':ls[1],'abs_difference_mm':abs(ls[0]-ls[1])})
summary={'status':'bounded geometry prototype, no source PCB changed and no 24-layer PCB produced','source_sha256':d['sha256'],'native_parser_version':d['version'],'source_track_segments':len(d['tracks']),'source_vias_all_retained_as_obstacles':len(d['vias']),'source_pads':len(d['pads']),'source_drilled_pads':sum(any(p['drill']) for p in e['pads']),'source_rule_areas':e['rule_areas'],'pair_section_audit':{'count':len(sections),'mismatched_internal_layer_sets':sum(x['mismatched_internal_layers'] for x in sections),'by_class':dict(collections.Counter(x['class'] for x in sections)),'slot_TX_directional_channels':len(slot_tx),'slot_RX_directional_channels':len(slot_rx),'slot_AC_extra_sections_not_extra_channels':len(ac),'slot_bidirectional_x1_lanes':len(slot_tx)},'selected_scope':{'slot':'S06/J6','bidirectional_x1_lanes':1,'directional_differential_channels':2,'on_board_differential_net_sections':3,'conductors':6,'TX_path':'U1 AH3/AJ3 -> C4041/C4042 pin 1; capacitors; C4041/C4042 pin 2 -> J6 B18/B17','RX_path':'J6 A18/A17 -> U1 AH5/AJ5','TX_long_section_prospective_layer':7,'TX_adjacent_ground_requirement':8,'RX_long_section_prospective_layer':18,'RX_adjacent_ground_requirement':17,'AC_after_section_retained_layer':'F.Cu'},'old_lengths_mm':old,'new_lengths_mm':{'TX_before_AC_P':tx['traces'][0]['length_mm'],'TX_before_AC_N':tx['traces'][1]['length_mm'],'TX_after_AC_P':acs[0]['length_mm'],'TX_after_AC_N':acs[1]['length_mm'],'TX_total_copper_P_excluding_cap_and_via_vertical_lengths':tx['traces'][0]['length_mm']+acs[0]['length_mm'],'TX_total_copper_N_excluding_cap_and_via_vertical_lengths':tx['traces'][1]['length_mm']+acs[1]['length_mm'],'TX_P_N_difference':tx['P_N_length_difference_mm'],'RX_P':rx['traces'][0]['length_mm'],'RX_N':rx['traces'][1]['length_mm'],'RX_P_N_difference':rx['P_N_length_difference_mm']},'geometry_assumptions':tx['geometry_assumptions'],'parallel_bus_estimates_mm':[{'directional_pair_count':n,'pair_to_pair_edge_gap_mm':c,'total_width_with_outer_0p1mm_margins':n*.3+(n-1)*c+.2,'is_SI_approved':False} for n in [1,2,8,16] for c in [.1,.3]],'endpoint_checks':endpoint_checks,'trace_to_source_via_minima':via_min,'AC_after_checks':acs,'source_hash_unchanged':True,'local_geometry_pass':tx['geometry_pass'] and rx['geometry_pass'] and all(x['pass'] for x in endpoint_checks+acs),'same_plane_two_channel_attempt_passed':False,'same_plane_failure_scope':'A* at 0.05mm grid, centerline corridor inflated by 0.27mm to every original via, fixed TX0 route treated as copper, east fanout no path; west fanout blocked endpoint. This is a bounded failed search, not a proof of unroutability.','not_proven':['Two slots / 16 directional differential channels per signal layer','24-layer full-board routing, clearance and connectivity','Filled/continuous electrically connected reference GND or return-via transitions','New 24-layer via span/HDI fabrication sequence or signal via stub behavior','Actual PEX ball map and vendor-validated package escape','Impedance, timing budget, insertion/return loss, crosstalk, eye diagram','Existing other signal and power copper is intentionally absent from each clean-plane trial; no unchanged-net connectivity claim','Ordinary native full-board DRC was not run on a nonexistent 24-layer candidate','Trace skew omits capacitor package paths and vertical via propagation; no acceptance limit is asserted']}
(D/'PAIR_SECTION_AUDIT.json').write_text(json.dumps(sections,indent=2));(D/'VALIDATION_SUMMARY.json').write_text(json.dumps(summary,indent=2));print(json.dumps({k:summary[k] for k in ['pair_section_audit','selected_scope','new_lengths_mm','trace_to_source_via_minima','AC_after_checks','local_geometry_pass']},indent=2));assert summary['local_geometry_pass']
