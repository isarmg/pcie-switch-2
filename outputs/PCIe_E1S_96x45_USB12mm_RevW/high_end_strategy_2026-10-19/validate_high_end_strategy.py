#!/usr/bin/env python3
"""Read-only arithmetic/scope checks. No physical PCB, fabrication or SI qualification."""
import json,hashlib,argparse,copy
from pathlib import Path

def validate(p,board):
 checks=[]
 def ck(ok,why):checks.append({'check':why,'pass':bool(ok)})
 ck(hashlib.sha256(board.read_bytes()).hexdigest()==p['source_pcb_sha256'],'unchanged exact PCB source')
 ck(p['source_pcb_changed'] is False and p['production_ready'] is False and p['physical_stackup_approved'] is False,'no source or production promotion')
 ck(p['existing_24_plan_replaced'] is False and p['proposed_28_is_optimal'] is False,'28 added for comparison only')
 ck(all(v is False for v in p['claimed_signoffs'].values()),'all physical qualification flags false')
 ck(p['single_platform_rule']['cross_vendor_limit_composition_allowed'] is False and p['single_platform_rule']['mSAP_or_SAP_assumed_compatible_with_HLC_platform'] is False,'no mixed-vendor or assumed SAP compatibility')
 ck(all(v is None for v in p['process_selection']['physical_stackup_fields'].values()),'no invented physical stackup')
 ck(p['process_selection']['buildup_count_is_not_stacked_microvia_depth'] is True and p['process_selection']['arbitrary_stacked_microvias_allowed'] is False,'no implicit deep stacked microvias')
 by={v['id']:v for v in p['variants']};ck(set(by)=={'24_BASELINE','24_HDI4','28_ISOLATION_HDI4'},'three distinct comparison variants')
 for name,v in by.items():
  s=v['sequence'];n=v['total_layers'];ck(len(s)==n and s==s[::-1],name+' count and symmetry')
  ck(v['budget']=={x:s.count(x) for x in 'SGP'} and v['budget']['S']==12 and v['budget']['P']==4,name+' resource count')
  ck([l['layer'] for l in v['layers']]==list(range(1,n+1)) and [l['role'] for l in v['layers']]==s,name+' layer records')
  ck(all(l['adjacent_GND']==[j for j in [l['layer']-1,l['layer']+1] if 1<=j<=n and s[j-1]=='G'] and (l['role']!='S' or bool(l['adjacent_GND'])) for l in v['layers']),name+' every signal adjacent dedicated GND')
  ss=[[i,i+1] for i in range(1,n) if s[i-1:i+1]==['S','S']];ck(ss==v['adjacent_SS_pairs'],name+' complete SS inventory')
  b=v['buildup_concept'];ck(b['top']==b['bottom'] and b['top']+b['core_copper_layers']+b['bottom']==n and b['project_approval']=='pending' and b['continuous_stacked_microvia_depth_approved'] is None,name+' buildup pending, no implicit stack depth')
  ck(v['signal_layers_accessible_by_near_surface_buildup_plus_core_face']=={'top':[i for i,x in enumerate(s,1) if x=='S' and i<=b['top']+1],'bottom':[i for i,x in enumerate(s,1) if x=='S' and i>=n-b['bottom']]},name+' actual reachable signal ordinals')
  ck(v['routing_capacity_verified'] is False and v['PDN_capacity_verified'] is False and all(l['actual_ground_continuity_verified'] is False for l in v['layers']),name+' no geometry or PDN promotion')
  slots=v['slot_power_domains'];ck(len(slots)==12 and {q['net'] for q in slots}=={f'P12_SLOT{i:02d}' for i in range(1,13)} and sorted(q['slot'] for q in slots)==list(range(1,13)) and all(q['electrically_isolated_from_other_outputs'] is True for q in slots) and v['electrical_slot_output_merge_permitted'] is False,name+' twelve isolated slot outputs')
  ck(all(s[q['candidate_plane']-1]=='P' and q['bank']==('A' if q['slot'] in {1,2,3,4,5,11} else 'B') for q in slots),name+' power planes and original banks')
 ck(by['28_ISOLATION_HDI4']['budget']=={'S':12,'G':12,'P':4} and by['28_ISOLATION_HDI4']['adjacent_SS_pairs']==[],'28 is 12S12G4P without SS')
 ck(by['28_ISOLATION_HDI4']['sequence'][:5]==['S','G','S','G','S'],'28 four-buildup face actually reaches additional signal layer')
 ck(by['24_HDI4']['sequence'][:5]==['S','G','S','S','G'],'24 HDI4 near-surface role change explicit')
 f=p['existing_failure_evidence'];ck(f['direct_blocker']=='new prior S06_SW_TX0 P/N traces, not a source via' and f['expanded_nodes']==0 and f['capacity_impossibility_proved'] is False,'blocked fixed trial port is not global capacity failure')
 a=p['next_stages'][0];i=a['invariants'];ck(a['ready_now'] is True and i['source_vias']==3837 and i['line_width_mm']==i['PN_edge_gap_mm']==i['other_net_gap_mm']==.1 and i['grid_mm']==.05,'joint-port baseline holds process constants')
 ck(p['next_stages'][-1]['ready_now'] is False,'real hardware qualification still blocked')
 return {'pass':all(x['pass'] for x in checks),'scope':'Planning arithmetic and scope only; not routability, SI/PI or manufacturing qualification','checks':checks,'failures':[x['check'] for x in checks if not x['pass']]}

if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--board',required=True,type=Path);ap.add_argument('--strategy',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);ap.add_argument('--negative-tests',action='store_true');a=ap.parse_args()
 if a.out.resolve() in [a.board.resolve(),a.strategy.resolve()]:raise SystemExit('Output cannot overwrite input')
 p=json.loads(a.strategy.read_text());r=validate(p,a.board)
 if a.negative_tests:
  mutations=[('source changed',lambda p:p.update(source_pcb_changed=True)),('production promoted',lambda p:p.update(production_ready=True)),('28 declared optimum',lambda p:p.update(proposed_28_is_optimal=True)),('mixed-vendor limits',lambda p:p['single_platform_rule'].update(cross_vendor_limit_composition_allowed=True)),('assumed SAP compatibility',lambda p:p['single_platform_rule'].update(mSAP_or_SAP_assumed_compatible_with_HLC_platform=True)),('invent Dk',lambda p:p['process_selection']['physical_stackup_fields'].update(Dk_Df_vs_frequency=4)),('allow arbitrary stacking',lambda p:p['process_selection'].update(arbitrary_stacked_microvias_allowed=True)),('merge slot outputs',lambda p:p['variants'][2]['slot_power_domains'][1].update(net='P12_SLOT01')),('drop G reference',lambda p:p['variants'][2]['layers'][0].update(adjacent_GND=[])),('hide SS',lambda p:p['variants'][1].update(adjacent_SS_pairs=[])),('fab concept approved',lambda p:p['variants'][2]['buildup_concept'].update(project_approval='approved')),('process baseline changed',lambda p:p['next_stages'][0]['invariants'].update(line_width_mm=.04)),('hardware qualification enabled',lambda p:p['next_stages'][-1].update(ready_now=True))]
  r['negative_tests']=[]
  for name,mut in mutations:
   q=copy.deepcopy(p);mut(q);t=validate(q,a.board);r['negative_tests'].append({'name':name,'rejected':not t['pass'],'failures':t['failures']})
  r['pass']=r['pass'] and all(x['rejected'] for x in r['negative_tests'])
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':r['pass'],'checks':len(r['checks']),'negative_tests':len(r.get('negative_tests',[])),'failures':r['failures']}));raise SystemExit(0 if r['pass'] else 1)
