"""Rip up retained signal paths infringed by newly added/moved blind vias."""
from pathlib import Path
from collections import Counter
import sys,json,math
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');W=R/'work/revU';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
d=json.loads((W/'route_tasks.json').read_text(encoding='utf-8'));b=p.LoadBoard(str(W/'Main.prepared.kicad_pcb'))
def dist(q,a,z):
    dx,dy=z[0]-a[0],z[1]-a[1];den=dx*dx+dy*dy;t=max(0,min(1,((q[0]-a[0])*dx+(q[1]-a[1])*dy)/den)) if den else 0
    return math.dist(q,(a[0]+t*dx,a[1]+t*dy))
bad=set()
for s in d['segments']:
    for vv in d['vias']:
        if vv['net']!=s['net'] and s['layer'] in vv['layers'] and dist(vv['pt'],s['a'],s['b'])<s['width']/2+vv['diameter']/2+.077:bad.add(s['net']);break
new=[]
for q in d['retained']:
    if q['net'] in bad:
        t={k:v for k,v in q.items() if k not in ['points','length_mm','coupled_bulk','routing_method']};d['tasks'].append(t);new.append(t['task_id'])
d['retained']=[q for q in d['retained'] if q['net'] not in bad];d['segments']=[s for s in d['segments'] if s['net'] not in bad]
for t in list(b.GetTracks()):
    if not isinstance(t,p.PCB_VIA) and t.GetLayer() not in [p.F_Cu,p.B_Cu] and t.GetNetname() in bad:remove(b,t)
(W/'route_tasks.json').write_text(json.dumps(d,indent=2),encoding='utf-8');p.SaveBoard(str(W/'Main.prepared.kicad_pcb'),b)
print('Retained nets affected by new via obstacles:',len(bad),'/',len(new),'sections;',len(d['retained']),'unchanged sections remain',flush=True)
