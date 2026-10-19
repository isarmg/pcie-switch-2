#!/usr/bin/env python3
"""Check proposal arithmetic and separation of assumptions; no manufacturing qualification."""
import argparse,json,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);p.add_argument('--board',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
s=json.loads((a.directory/'HIGH_END_LAYER_STRATEGY.json').read_text());m=json.loads((a.directory/'HIGH_END_PROCESS_CANDIDATE.json').read_text());checks=[]
def ck(ok,label):
 assert ok,label
 checks.append(label)
ck(hashlib.sha256(a.board.read_bytes()).hexdigest()==s['source_pcb_sha256']==m['source_board_sha256'],'exact unchanged source')
v={x['id']:x for x in s['variants']}
for x in m['architecture_candidates']:
 key='28_ISOLATION_HDI4' if x['id']=='28_HDI4' else x['id'];q=v[key]
 ck(x['role_sequence']==q['sequence'],key+' cross-file exact sequence')
 seq=q['sequence'];ck(seq==seq[::-1] and seq[1:-1].count('S')==10,key+' mirror and ten internal S')
 ck(all((i>0 and seq[i-1]=='G') or (i+1<len(seq) and seq[i+1]=='G') for i,z in enumerate(seq) if z=='S'),key+' every S has adjacent G role')
 ck(len({z['net'] for z in q['slot_power_domains']})==12 and all(z['electrically_isolated_from_other_outputs'] for z in q['slot_power_domains']),key+' twelve isolated output declarations')
ck(len(m['fabricator_approved_inputs'])==47 and all(z is None for z in m['fabricator_approved_inputs'].values()),'all 47 fabrication approvals absent')
t=m['engineering_trial_profile'];ck(not t['vendor_guaranteed'] and not t['can_write_manufacturing_rules'],'trial not vendor rule')
l=t['single_step_laser'];ck((l['drill_nominal_um'],l['capture_pad_nominal_um'],l['landing_pad_nominal_um'],l['effective_drill_depth_max_um'])==(100,275,275,75),'explicit trial laser geometry')
ck(l['adjacent_layers_only'] and t['microvia_chain']['max_consecutive_coaxial_steps_trial']==2 and t['microvia_chain']['approved_max_coaxial_stack_count'] is None,'whole macro qualification remains pending')
b=t['mechanical_transition_trial'];ck(b['requested_max_residual_stub_um']==150 and b['approved_max_residual_stub_um'] is None,'150um stub is request only')
ck(b['backdrill_antipad_diameter_um']>=b['backdrill_bit_um']+2*b['backdrill_to_copper_clearance_um'],'hypothetical backdrill radial clearance arithmetic')
ck(t['thickness_and_copper_sweep']['finished_thickness_approved_mm'] is None,'thickness sweep is unselected')
ck(all(z is False for z in s['claimed_signoffs'].values()),'no physical qualification promoted')
a.out.write_text(json.dumps({'pass':True,'checks':checks,'source_sha256':s['source_pcb_sha256'],'qualification':'Planning scope and arithmetic only; manufacturing/SI/PI not qualified'},indent=2)+'\n');print(len(checks),'combined checks passed')
