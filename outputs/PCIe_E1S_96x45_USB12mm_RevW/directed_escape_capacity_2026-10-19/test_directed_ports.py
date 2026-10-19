"""Regression tests: frozen old RX1->RX0 rejection plus direction and explicit
(non-repaired) offset invariants. No PCB write, no altered physical geometry.
"""
from directed_port_trial import *

def main():
 results=[]
 old=json.loads((D/'REGRESSION_OLD_RX1_THEN_RX0.json').read_text());assert old['source_sha256']==d['sha256'];bad=old['attempts'][1];assert bad['pair']=='S06_SW_RX0' and not bad['geometry_pass'];p,n=[LineString(t['points']) for t in bad['traces']];gap=p.distance(n)-W;assert not p.is_simple and gap<CLEAR
 u=np.array(bad['centerline'][-2])-np.array(bad['centerline'][-3]);v=np.array(bad['centerline'][-1])-np.array(bad['centerline'][-2]);cosine=float(u.dot(v)/(np.linalg.norm(u)*np.linalg.norm(v)));assert cosine<0
 results.append({'test':'frozen real RX1-before-RX0 regression reproduced','passed':True,'P_simple':p.is_simple,'pair_copper_gap_mm':gap,'last_join_cosine':cosine})
 try:directed_offset([[0,0],[1,0],[.5,0],[2,0]],-.1);raise AssertionError('U-turn accepted')
 except ValueError as e:results.append({'test':'immediate reversal rejected','passed':True,'reason':str(e)})
 good=[[0,0],[1,0],[1,1],[2,1],[2,0],[3,0]];p,n=[LineString(directed_offset(good,x)) for x in [-.1,.1]];assert p.is_simple and n.is_simple and p.distance(n)-W>=GAP-1e-8
 results.append({'test':'explicit 90-degree miter preserves simple separated P/N','passed':True,'pair_copper_gap_mm':p.distance(n)-W})
 router=DirectedRouter.__new__(DirectedRouter);router.blocked=np.ones((NY,NX),dtype=bool);router.blocked[5:70,5:90]=False;router.blocked[22:32,30:35]=True
 path,s=router.astar([1,1],[3,2]);assert path and s['terminal_arrival_heading_index']==0 and s['terminal_straight_steps']==MIN_STRAIGHT_STEPS
 center=compact_collinear([[.8,1]]+path+[[3.2,2]]);p,n=[LineString(directed_offset(center,x)) for x in [-.1,.1]];assert p.is_simple and n.is_simple and p.distance(n)-W>=GAP-1e-8
 results.append({'test':'heading search reaches east-only destination with valid P/N offsets','passed':True,'expanded_nodes':s['expanded_nodes'],'pair_copper_gap_mm':p.distance(n)-W})
 router.blocked[:]=True;router.blocked[20,20:61]=False;path,s=router.astar([3,1],[1,1]);assert path is None
 results.append({'test':'connected reverse-only corridor does not reverse P/N port order','passed':True,'search':s})
 real=D/'RESERVED_SCENARIO_02.json'
 if real.exists():
  r=json.loads(real.read_text());prefix=r['attempts'][:2]
  if len(prefix)==2 and prefix[0]['pair']=='S06_SW_RX1' and prefix[1]['pair']=='S06_SW_RX0':
   assert all(q['geometry_pass'] for q in prefix)
   assert all(LineString(t['points']).is_simple and not t['via_violations'] for q in prefix for t in q['traces'])
   results.append({'test':'real RX1-before-RX0 direction-aware routes pass complete explicit geometry','passed':True,'source_scenario':'RESERVED_SCENARIO_02.json','RX0_pair_gap_mm':prefix[1]['pair_copper_gap_mm']})
 result={'source_sha256':d['sha256'],'all_tests_passed':True,'tests':results,'scope':'Unit and frozen-failure regression tests; not proof of complete four-channel PCB routing'};(D/'DIRECTION_UNIT_TESTS.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
