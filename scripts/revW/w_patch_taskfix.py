from pathlib import Path
import json
path=Path('C:/Users/micro/Desktop/方案/pcie switch 2/work/revW/finalpatch/route_tasks.json')
d=json.loads(path.read_text(encoding='utf-8'))
for q in d['tasks']:
 if q['task_id']=='/P12_SLOT05__FINALPATCH_SURFACE':q.update(layer=52,layer_name='In25.Cu',layer_index=25)
 print(q['net'],q['a']['pt'],q['b']['pt'],q['layer_name'])
path.write_text(json.dumps(d,indent=2),encoding='utf-8')
