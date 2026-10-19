"""Bounded x2 algorithm study: select compatible endpoint templates, reserve all
other selected pin-to-gateway P/N fanouts, rebuild each channel. No source edit.
"""
from joint_routing_trial import *
import itertools
PAIRS=['S06_SW_RX0','S06_SW_RX1','S06_SW_TX0','S06_SW_TX1']
SHIFTS=[0.0,.1,-.1,.2];LEFT=[0.0,.2]
ORDERS=[[PAIRS[i] for i in order] for order in [(0,1,2,3),(0,1,3,2),(1,0,3,2),(3,1,0,2)]]
MAX_COMBINATIONS=3

def check_lines(traces,other=()):
 out=[];lines=[LineString(t['points']) for t in traces]
 for t,q in zip(traces,lines):
  mind=1e9;bad=[]
  for i in vt.query(q.buffer(.501)):
   if vn[i]==t['net']:continue
   gap=q.distance(vp[i])-.05-rv[i];mind=min(mind,gap)
   if gap<CLEAR-1e-6:bad.append({'via_index':int(i),'net':vn[i],'xy':list(xy[i]),'copper_gap_mm':gap})
  othergap=min([q.distance(LineString(x['points']))-W for x in other if x['net']!=t['net']],default=None)
  edge=min(q.bounds[0],q.bounds[1],96-q.bounds[2],45-q.bounds[3])-.05
  out.append(dict(t,length_mm=q.length,simple=q.is_simple,minimum_source_via_copper_gap_mm=mind,via_violations=bad,minimum_existing_channel_copper_gap_mm=othergap,board_edge_copper_gap_mm=edge))
 pg=min([a.distance(b)-W for i,a in enumerate(lines) for j,b in enumerate(lines) if i<j and traces[i]['net']!=traces[j]['net']],default=None)
 ok=(pg is None or pg>=GAP-1e-6) and all(t['simple'] and not t['via_violations'] and t['board_edge_copper_gap_mm']>=.25 and (t['minimum_existing_channel_copper_gap_mm'] is None or t['minimum_existing_channel_copper_gap_mm']>=CLEAR-1e-6) for t in out)
 return out,pg,ok

def template(pair,shift,left):
 nets,pads,ev=endpoints(pair);ap,an=[v[0]['xy'] for v in ev];bp,bn=[v[1]['xy'] for v in ev]
 sy=(ap[1]+an[1])/2;dy=round(((bp[1]+bn[1])/2)/G)*G+shift;sx=ap[0];dx=round((bp[0]-.72)/G)*G-left
 start=[sx+.7,sy];end=[dx,dy];sa=[sx+.5,sy];da=[bp[0]-.52,dy]
 source=[ [ap,[ap[0]+.2,ap[1]+.2],[sa[0],sy-.1],[start[0],sy-.1]], [an,[an[0]+.2,an[1]-.2],[sa[0],sy+.1],[start[0],sy+.1]] ]
 if '_TX' in pair:
  dest=[[[dx,dy-.1],[da[0],dy-.1],[bp[0]-.27,bp[1]],bp],[[dx,dy+.1],[da[0],dy+.1],[bn[0]-.27,bn[1]],bn]]
 else:
  dest=[[[dx,dy-.1],[da[0],dy-.1],[bp[0],dy-.1],bp],[[dx,dy+.1],[da[0],dy+.1],[bn[0],dy+.1],bn]]
 fragments=[{'net':nets[i],'end':label,'points':p} for label,ps in [('source',source),('destination',dest)] for i,p in enumerate(ps)]
 checks,pg,ok=check_lines(fragments)
 gateways=[]
 for label,pos in [('start',start),('end',end)]:
  q=Point(pos);hits=[]
  for i in vt.query(q.buffer(.501)):
   if vn[i] not in nets and q.distance(vp[i])<rv[i]+.27-1e-8:hits.append({'net':vn[i],'xy':list(xy[i])})
  gateways.append({'end':label,'xy':pos,'conservative_centerline_via_blockers':hits})
 ok=ok and not any(x['conservative_centerline_via_blockers'] for x in gateways)
 return {'pair':pair,'candidate_id':f'{pair}:dy{shift:+.2f}:left{left:.2f}','destination_y_shift_mm':shift,'destination_entry_left_shift_mm':left,'start':start,'end':end,'source_anchor':sa,'destination_anchor':da,'fragments':checks,'pair_fragment_copper_gap_mm':pg,'gateways':gateways,'local_exact_pass':ok}

def compatibility(a,b):
 gaps=[LineString(x['points']).distance(LineString(y['points']))-W for x in a['fragments'] for y in b['fragments']]
 # Each selected fanout must leave the other channel's raster entry reachable.
 gateway_gap=min(Point(g['xy']).distance(LineString(t['points'])) for p,q in [(a,b),(b,a)] for g in p['gateways'] for t in q['fragments'])
 return {'copper_gap_mm':min(gaps),'gateway_to_foreign_trace_center_mm':gateway_gap,'compatible':min(gaps)>=CLEAR-1e-6 and gateway_gap>=.32-1e-8}

class ReservedRouter(Router):
 def __init__(self,pair,selected,existing=()):
  self.selected=selected;self.template=selected[pair];self.placed=list(existing)
  self.reservations=[{'traces':t['fragments']} for p,t in selected.items() if p!=pair]
  super().__init__(pair,existing=list(existing)+self.reservations)
 def run(self):
  t=self.template;started=time.monotonic();path,search=self.astar(t['start'],t['end'])
  out={'pair':self.pair,'candidate_id':t['candidate_id'],'source_pads':[[p['ref']+':'+p['pin'] for p in pp] for pp in self.pads],'search':search,'geometry_pass':False,'reserved_other_pairs':[p for p in self.selected if p!=self.pair]}
  if path is None:out['seconds']=time.monotonic()-started;return out
  center=[t['source_anchor']]+self.simplify(path)+[t['destination_anchor']];line=LineString(center);traces=[]
  for i,off in enumerate([-.1,.1]):
   points=list(map(list,line.offset_curve(off,join_style='mitre').coords));src=t['fragments'][i]['points'];dest=t['fragments'][i+2]['points'];points=src[:2]+points+dest[2:]
   traces.append({'net':self.nets[i],'points':points})
  other=[x for r in self.placed+self.reservations for x in r['traces']]
  checks,pg,ok=check_lines(traces,other)
  out.update({'centerline':center,'traces':checks,'pair_copper_gap_mm':pg,'P_N_length_difference_mm':abs(checks[0]['length_mm']-checks[1]['length_mm']),'seconds':time.monotonic()-started,'geometry_pass':ok})
  if not ok:out['failure']='exact geometry rejected; source holes and clearances unchanged'
  return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--preflight-only',action='store_true');ap.add_argument('--scenario',type=int);args=ap.parse_args()
 candidates={p:[template(p,s,x) for x in LEFT for s in SHIFTS] for p in PAIRS}
 local={p:[q for q in cs if q['local_exact_pass']] for p,cs in candidates.items()};compatible=[];tested=0
 for combo in itertools.product(*(local[p] for p in PAIRS)):
  tested+=1;checks=[compatibility(a,b) for a,b in itertools.combinations(combo,2)]
  if all(c['compatible'] for c in checks):
   score=sum(abs(t['destination_y_shift_mm'])+t['destination_entry_left_shift_mm'] for t in combo)
   compatible.append({'selected':{t['pair']:t for t in combo},'score':score,'minimum_fragment_interchannel_copper_gap_mm':min(c['copper_gap_mm'] for c in checks),'minimum_gateway_to_foreign_fragment_center_mm':min(c['gateway_to_foreign_trace_center_mm'] for c in checks)})
 compatible.sort(key=lambda c:(c['score'],[c['selected'][p]['candidate_id'] for p in PAIRS]));chosen=compatible[:MAX_COMBINATIONS]
 pre={'source_sha256':d['sha256'],'candidate_offsets':{'destination_y_mm':SHIFTS,'destination_entry_left_mm':LEFT,'source_template':'fixed actual pin to east gateway'},'candidates':candidates,'locally_valid_counts':{p:len(v) for p,v in local.items()},'combinations_checked':tested,'compatible_combinations':len(compatible),'maximum_selected_combinations':MAX_COMBINATIONS,'selected_combinations':chosen,'reservation_policy':'Only one selected fanout per pair in each scenario, source and destination P/N fragments at 0.1mm width, foreign centerlines inflated by0.32mm. Own fragments excluded. Never reserve union of alternatives.'}
 (D/'ENDPOINT_PREFLIGHT.json').write_text(json.dumps(pre,indent=2));print('Preflight',pre['locally_valid_counts'],'compatible',len(compatible),'chosen',len(chosen),flush=True)
 scope={'source_sha256':d['sha256'],'source_vias':len(d['vias']),'width_mm':W,'pair_gap_mm':GAP,'other_net_clearance_mm':CLEAR,'grid_mm':G,'maximum_expanded_nodes_per_channel':MAX_NODES,'maximum_combinations':MAX_COMBINATIONS,'orders':ORDERS,'maximum_declared_scenarios':MAX_COMBINATIONS*len(ORDERS),'stop_policy':'First exact complete four-channel solution or twelve scenarios; each failure stops that scenario. No x4 expansion. Fixed original all-hole projection model. No source via, pad, width, clearance, grid or process changes.','executed_scenarios':[]}
 (D/'RESERVED_SEARCH_SCOPE.json').write_text(json.dumps(scope,indent=2))
 if args.preflight_only:return
 for ci,c in enumerate(chosen):
  for oi,order in enumerate(ORDERS):
   sid=ci*len(ORDERS)+oi
   if args.scenario is not None and sid!=args.scenario:continue
   print('Start reserved scenario',sid,order,flush=True);placed=[];attempts=[]
   for p in order:
    q=ReservedRouter(p,c['selected'],placed).run();attempts.append(q);print(' ',p,q['geometry_pass'],q['search'],q.get('failure'),flush=True)
    if not q['geometry_pass']:break
    placed.append(q)
   gaps=[LineString(a['points']).distance(LineString(b['points']))-W for j,x in enumerate(placed) for y in placed[j+1:] for a in x['traces'] for b in y['traces']]
   result={'source_sha256':d['sha256'],'scenario':sid,'combination_index':ci,'order':order,'selected_candidate_ids':{p:t['candidate_id'] for p,t in c['selected'].items()},'target_plane_ordinal':7,'adjacent_continuous_GND_requirement':8,'attempts':attempts,'successfully_routed_channels':len(placed),'all_four_channels_exact_pass':len(placed)==4,'minimum_interchannel_copper_gap_mm':min(gaps,default=None)}
   (D/f'RESERVED_SCENARIO_{sid:02d}.json').write_text(json.dumps(result,indent=2));scope['executed_scenarios'].append(sid);(D/'RESERVED_SEARCH_SCOPE.json').write_text(json.dumps(scope,indent=2));print('Finish',sid,len(placed),'of4 gap',result['minimum_interchannel_copper_gap_mm'],flush=True)
   if len(placed)==4:assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==d['sha256'];return
 assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==d['sha256']
if __name__=='__main__':main()
