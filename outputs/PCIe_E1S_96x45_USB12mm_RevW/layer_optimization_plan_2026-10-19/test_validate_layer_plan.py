#!/usr/bin/env python3
import argparse,copy,json,importlib.util
from pathlib import Path
ap=argparse.ArgumentParser(description='Negative controls for layer-plan validator; source board remains read-only.');ap.add_argument('--board',required=True,type=Path);ap.add_argument('--plan',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);a=ap.parse_args()
s=importlib.util.spec_from_file_location('validator',Path(__file__).with_name('validate_layer_plan.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);original=json.loads(a.plan.read_text())
cases=[]
def run(name,mutator):
 p=copy.deepcopy(original);mutator(p);r=m.validate(p,a.board);cases.append({'case':name,'rejected':not r['pass'],'failures':r['failures']})
run('wrong_source_sha',lambda p:p['source'].update(pcb_sha256='0'*64))
run('claim_SI_signoff',lambda p:p['signoff'].update(signal_integrity=True))
run('invent_Dk',lambda p:p['physical_stackup'].update(Dk=4.0))
run('merge_slot_domains',lambda p:p['candidates'][0]['power_domains']['slot_assignments'][1].update(net='P12_SLOT01'))
run('remove_signal_reference',lambda p:p['candidates'][0]['layers'][0].update(adjacent_GND_layers=[],preferred_reference_GND=None))
run('silently_pass_SS',lambda p:p['candidates'][0]['adjacent_SS_risks'][0].update(status='passed'))
run('hide_20_power_reference_risk',lambda p:p['candidates'][1].update(power_layers_without_adjacent_GND=[]))
run('double_count_AC_channels',lambda p:p['channel_budget']['PCIe'].update(total_diff_data_channels=176))
run('allow_deep_blind_inheritance',lambda p:p['manufacturing'].update(inherited_deep_blind_vias_allowed=True))
run('allow_index_remapping',lambda p:p.update(direct_old_layer_index_remapping_allowed=True))
r={'pass':all(c['rejected'] for c in cases),'negative_controls':cases};a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'pass':r['pass'],'negative_controls':len(cases)}));raise SystemExit(0 if r['pass'] else 1)
