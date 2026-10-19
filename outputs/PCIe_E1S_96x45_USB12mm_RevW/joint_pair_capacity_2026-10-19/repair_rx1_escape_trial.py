"""Bounded RX1 endpoint repair: at most four declared orders, all four channels rebuilt.
Only enabled after exact same-plane x1 success. No source via or PCB changes.
"""
from joint_routing_trial import *

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--scenario',type=int);args=ap.parse_args()
 gates=[]
 for p in D.glob('SCENARIO_*.json'):
  q=json.loads(p.read_text())
  if q.get('same_plane_both_pass'):gates.append({'file':p.name,'interchannel_copper_gap_mm':q['interchannel_copper_gap_mm']})
 assert gates,'x2 gate blocked: no successful exact x1 result'
 R0='S06_SW_RX0';T0='S06_SW_TX0';R1='S06_SW_RX1';T1='S06_SW_TX1'
 orders=[[R0,R1,T0,T1],[R1,R0,T1,T0],[R1,T1,R0,T0],[R0,T1,R1,T0]]
 executed=[]
 for i,order in enumerate(orders):
  if args.scenario is not None and i!=args.scenario:continue
  print('Start x2 scenario',i,order,flush=True);placed=[];attempts=[]
  for pair in order:
   q=Router(pair,existing=placed,terminal_shift_mm=.10 if pair==R1 else 0.0).run();attempts.append(q)
   print('  channel',pair,'pass',q['geometry_pass'],'nodes',q['search'].get('expanded_nodes'),'reason',q.get('failure',q['search'].get('reason')),flush=True)
   if not q['geometry_pass']:break
   placed.append(q)
  gaps=[LineString(a['points']).distance(LineString(b['points']))-W for j,x in enumerate(placed) for y in placed[j+1:] for a in x['traces'] for b in y['traces']]
  r={'source_sha256':d['sha256'],'scenario':i,'order':order,'target_plane_ordinal':7,'adjacent_continuous_GND_requirement':8,'first_cost_mode':'shortest','RX1_terminal_shift_mm':.10,'repair_reason':'Unshifted RX1 P fanout had only 0.0412mm clearance to original GND via at (57.318794,22.5588); move the paired approach down 0.10mm, not the via','attempts':attempts,'successfully_routed_channels':len(placed),'all_four_channels_exact_pass':len(placed)==4,'minimum_interchannel_copper_gap_mm':min(gaps,default=None)}
  (D/f'X2_REPAIR_SCENARIO_{i:02d}.json').write_text(json.dumps(r,indent=2));executed.append(i)
  print('Finish x2 scenario',i,'routed',len(placed),'of 4','minimum gap',r['minimum_interchannel_copper_gap_mm'],flush=True)
  if r['all_four_channels_exact_pass'] and args.scenario is None:break
 scope={'source_sha256':d['sha256'],'source_vias':len(d['vias']),'x1_success_gate_evidence':gates,'total_declared_scenarios':len(orders),'orders':orders,'executed_in_this_invocation':executed,'first_and_subsequent_channel_cost':'unit geometric step cost','max_expanded_nodes_per_channel':MAX_NODES,'stop_policy':'Try only these four orders after the six original orders, stopping after first exact all-four solution; each scenario stops at first rejected channel. Explicit --scenario can replay one declared scenario.','scope':'one slot S06, two bidirectional x1 lanes = four directional channels; no two-slot or 16-channel result'}
 (D/'X2_REPAIR_SEARCH_SCOPE.json').write_text(json.dumps(scope,indent=2));assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==d['sha256']
if __name__=='__main__':main()
