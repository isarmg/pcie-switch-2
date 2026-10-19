import argparse,json,csv,hashlib,collections
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--plan',type=Path,required=True);p.add_argument('--constraints',type=Path,required=True);p.add_argument('--fab-inputs',type=Path,required=True);p.add_argument('--queue',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
x=json.loads(a.plan.read_text());y=json.loads(a.constraints.read_text());z=json.loads(a.fab_inputs.read_text());c=next(c for c in x['candidates'] if c['total_layers']==24);d=y['candidate'];checks={}
checks['source_identical']=x['source']['pcb_sha256']==y['source']['pcb_sha256']==z['source']['pcb_sha256']
checks['roles_identical']=c['sequence']==[l['role'] for l in d['layers']]
checks['counts_identical']=c['budget']==d['role_counts']
checks['SS_identical']=[r['layers'] for r in c['adjacent_SS_risks']]==d['s_s_adjacent_layer_pairs']
checks['references_identical']=all(l.get('reference_ground_layer')==c['layers'][i]['preferred_reference_GND'] for i,l in enumerate(d['layers']))
checks['approvals_false']=all(y[k] is False for k in ['applied_to_current_pcb','fabricator_approved','si_qualified','mechanical_thickness_approved','execution_enabled'])
checks['via_macro_unapproved']=d['allowed_via_macros']==[] and all(v['status']=='UNAPPROVED' for v in y['planning_candidate_via_options'])
checks['all_manufacturing_values_missing']=all(v['value'] is None for v in z['values'].values())
checks['source_still_32']=y['source']['source_copper_layers']==x['source']['actual_copper_layers']==32
rows=list(csv.DictReader(a.queue.open()));checks['907_deep_via_queue']=len(rows)==907
r={'pass':all(checks.values()),'scope':'Independent consistency check only; no PCB edit or qualification','checks':checks,'missing_manufacturing_inputs':len(z['values']),'deep_via_queue_rows':len(rows)};a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r));raise SystemExit(0 if r['pass'] else 1)
