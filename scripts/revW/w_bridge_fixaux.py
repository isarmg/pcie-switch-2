"""Preserve both distinct endpoints of the close auxiliary-power islands."""
from pathlib import Path
import json
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2')
W=R/'work/revW/bridge'
path=W/'route_tasks.json';d=json.loads(path.read_text(encoding='utf-8'))
q=next(q for q in d['tasks'] if q['task_id']=='/AUX_12V_PROTECTED__ISLAND_1')
q['a'].update(pt=[70.25,4.8],pad_pt=[70.25,4.8])
q['b'].update(pt=[68.4625,4.75],pad_pt=[68.4625,4.75])
assert any(v['net']==q['net'] and v['pt']==q['a']['pt'] for v in d['vias'])
path.write_text(json.dumps(d,indent=2),encoding='utf-8')
print('Restored distinct auxiliary bridge endpoints.')
