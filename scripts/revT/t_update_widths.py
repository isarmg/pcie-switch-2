"""Incremental routing update: retain only caches matching unchanged tasks."""
from pathlib import Path
import json,math,os,time
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');W=R/'work/revT';file=W/'route_tasks.json';d=json.loads(file.read_text(encoding='utf-8'))
for q in d['tasks']:
    if q['kind'].startswith('TB3_') and q['kind']!='TB3_CONTROL':q['width']=.075
file.write_text(json.dumps(d,indent=2),encoding='utf-8');by={q['task_id']:q for q in d['tasks']};retained=[]
for path in W.glob('routes_layer_*.json'):
    obj=json.loads(path.read_text(encoding='utf-8'));valid=True
    current={k for k,q in by.items() if q['layer']==obj['layer']}
    if {q.get('task_id') for q in obj['routes']}!=current:valid=False
    for q in obj['routes']:
        target=by.get(q.get('task_id'))
        if not target or any(q.get(k)!=target.get(k) for k in ['net','layer','width','a','b']):valid=False;break
    if valid:os.utime(path,(time.time()+1,time.time()+1));retained.append(obj['layer'])
print('TB3 fine-pitch traces 0.075mm; retained audited caches',retained,flush=True)
