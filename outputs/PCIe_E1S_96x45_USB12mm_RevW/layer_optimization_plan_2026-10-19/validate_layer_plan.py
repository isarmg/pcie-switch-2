#!/usr/bin/env python3
"""Read-only consistency check. Does NOT prove routing, SI/PI or manufacturability."""
import argparse,hashlib,json,re,sys
from pathlib import Path

def validate(plan,board):
 errors=[];checks=[]
 def ck(ok,name):
  checks.append({'check':name,'pass':bool(ok)})
  if not ok:errors.append(name)
 raw=board.read_bytes();text=raw.decode('utf-8');sha=hashlib.sha256(raw).hexdigest()
 ck(sha==plan['source']['pcb_sha256'],'exact_source_sha256')
 # KiCad layer declaration occurs once for each enabled copper layer at top-level.
 names=re.findall(r'^\s*\(\d+\s+"((?:F|B|In\d+)\.Cu)"\s+signal\)',text,re.M)
 ck(len(names)==plan['source']['actual_copper_layers']==32,'source_still_32_copper_layers')
 ck(plan.get('not_a_fabrication_stackup') is True and plan.get('production_ready') is False,'planning_only_and_not_production_ready')
 ck(plan.get('direct_old_layer_index_remapping_allowed') is False,'no_direct_layer_index_remapping')
 ck(all(v is False for v in plan['signoff'].values()),'all_signoffs_explicitly_false')
 st=plan['physical_stackup'];ck(st['provided'] is False and all(st[k] is None for k in ['finished_thickness_mm','dielectric_thicknesses_mm','Dk','Df','copper_weights','material']),'no_invented_physical_stackup')
 ck(plan['source']['disconnected_non_NC_nets']==97 and plan['source']['disconnected_populated_non_NC_nets']==94,'incomplete_source_not_hidden')
 pc=plan['channel_budget']['PCIe'];ck(pc['SSD_slots']*pc['PCIe_lanes_per_SSD']*pc['diff_channels_per_bidirectional_lane']==pc['SSD_channels']==96,'SSD_channels_not_AC_double_counted')
 ck(pc['SSD_channels']+pc['CPU_switch_x4_channels']+pc['CPU_TBT_x4_channels']==pc['total_diff_data_channels']==112 and pc['total_bidirectional_lanes']*2==112,'PCIe_56_lanes_112_differential_data_channels')
 ck(plan['channel_budget']['capacity_verified'] is False,'channel_budget_is_not_verified_capacity')
 expected_bank={'A':{1,2,3,4,5,11},'B':{6,7,8,9,10,12}}
 ck(sorted(c['total_layers'] for c in plan['candidates'])==[20,24],'explicit_20_and_24_candidates')
 for c in plan['candidates']:
  n=c['total_layers'];s=c['sequence'];layers=c['layers'];tag=f'{n}L:'
  ck(len(s)==n and len(layers)==n,tag+'correct_layer_count')
  ck(s==s[::-1],tag+'mirror_role_sequence')
  ck({x:s.count(x) for x in 'SGP'}==c['budget'] and sum(c['budget'].values())==n,tag+'resource_budget')
  ck(c['budget']==({'S':12,'G':8,'P':4} if n==24 else {'S':10,'G':6,'P':4}),tag+'frozen_budget')
  ck([x['physical_layer'] for x in layers]==list(range(1,n+1)) and [x['role'] for x in layers]==s,tag+'layer_records_match_sequence')
  allref=True
  for i,l in enumerate(layers,1):
   adj=[j for j in [i-1,i+1] if 1<=j<=n and s[j-1]=='G']
   if l['adjacent_GND_layers']!=adj:allref=False
   if l['role']=='S' and (not adj or l['preferred_reference_GND'] not in adj):allref=False
  ck(allref,tag+'each_signal_has_recorded_adjacent_GND')
  expected_ss=[[i,i+1] for i in range(1,n) if s[i-1:i+1]==['S','S']]
  ck([r['layers'] for r in c['adjacent_SS_risks']]==expected_ss and all(r['status']=='unresolved' and len(r['requirements'])>=3 for r in c['adjacent_SS_risks']),tag+'all_adjacent_SS_risks_unresolved_and_recorded')
  ck(c['power_layers_without_adjacent_GND']==[l['physical_layer'] for l in layers if l['role']=='P' and not l['adjacent_GND_layers']],tag+'unreferenced_power_layer_risk_recorded')
  power={i for i,v in enumerate(s,1) if v=='P'};domains=c['power_domains'];slots=domains['slot_assignments'];slot_nets=[v['net'] for v in slots]
  ck(len(slots)==12 and sorted(v['slot'] for v in slots)==list(range(1,13)) and len(set(slot_nets))==12 and set(slot_nets)=={f'P12_SLOT{i:02d}' for i in range(1,13)},tag+'12_unique_slot_output_domains')
  ck(domains['electrical_merge_permitted'] is False and all(v['candidate_physical_layer'] in power and v['slot'] in expected_bank[v['bank']] for v in slots),tag+'power_islands_not_shortened_and_banks_preserved')
  ck(all(re.search(r'\(net\s+"(?:\{slash\}|/)?'+re.escape(net)+r'"\)',text) for net in slot_nets+domains['also_keep_distinct']),tag+'all_required_power_nets_exist_in_source')
  ck(c['near_surface_microvia_concept']==[[1,2],[2,3],[n-2,n-1],[n-1,n]],tag+'near_surface_microvia_concept_only')
  ck(c['route_budget_is_not_routability_proof'] is True,tag+'planning_quota_not_routability')
  if n==24:
   r=c['route_reservations'];ck(sum(x['target_diff_channels'] for x in r['SSD_data'])==96 and sum(x['target_diff_channels'] for x in r['CPU_switch_TBT_PCIe'])==16 and sum(x['target_diff_channels'] for x in r['CIO_DP_main'])==8 and r['quota_verified'] is False,tag+'planned_channel_quotas')
   assigned=[x['physical_layer'] for k in ['SSD_data','CPU_switch_TBT_PCIe','CIO_DP_main'] for x in r[k]]+r['clock_control_layers']+r['short_escape_layers']
   ck(sorted(assigned)==[i for i,v in enumerate(s,1) if v=='S'],tag+'each_signal_layer_assigned_once')
 ck(plan['manufacturing']['fabricator_approved'] is False and plan['manufacturing']['inherited_deep_blind_vias_allowed'] is False,'fabricator_approval_and_deep_via_blockers_preserved')
 return {'schema_version':1,'pass':not errors,'validation_scope':'Read-only source identity and proposal consistency only; no board change, routing, SI/PI, timing, current/thermal or manufacturing approval.','source_sha256':sha,'checks':checks,'failures':errors}

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--board',required=True,type=Path);ap.add_argument('--plan',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);args=ap.parse_args()
 if args.out.resolve() in {args.board.resolve(),args.plan.resolve()}:raise SystemExit('Output must not overwrite an input')
 try:r=validate(json.loads(args.plan.read_text()),args.board)
 except Exception as e:r={'pass':False,'failures':[f'{type(e).__name__}: {e}'],'validation_scope':'Proposal consistency only'}
 args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':r['pass'],'checks':len(r.get('checks',[])),'failures':r['failures']}));return 0 if r['pass'] else 1
if __name__=='__main__':sys.exit(main())
