from pathlib import Path
import sys,json,math
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');W=R/'work/revT';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import p,xy
fp=W/'route_tasks.json';d=json.loads(fp.read_text(encoding='utf-8'));b=p.LoadBoard(str(W/'Main.signal_vias.kicad_pcb'))
direct={q['net'] for q in d['tasks'] if (q['paired'] and q['kind'].startswith('TB3_') and not any(s in q['group'] for s in ['TBT_CPU_TX','TBT_AR_TX','TBT_DP_ML','TBT_CIO_'])) or q['net']=='/TBT_POC_GPIO_5'}
layers={q['layer'] for q in d['tasks']}|{getattr(p,f'In{i}_Cu') for i in range(19,31)};changed=[]
for t in b.GetTracks():
    if isinstance(t,p.PCB_VIA) and t.GetNetname() in direct:
        ep=next(e for q in d['tasks'] if q['net']==t.GetNetname() for e in [q['a'],q['b']] if math.dist(e['pt'],xy(t.GetPosition()))<.000003)
        if b.FindFootprintByReference(ep['ref']).GetLayer()==p.B_Cu:t.SetLayerPair(p.In19_Cu,p.B_Cu)
        changed.append(dict(net=t.GetNetname(),pt=xy(t.GetPosition()),diameter=.2,layers=[ll for ll in layers if t.IsOnLayer(ll)]))
for q in d['tasks']:
    if q['net'] in direct:q.update(preferred_layer_index=q.get('preferred_layer_index',q['layer_index']),layer_index=19,layer=p.In19_Cu,layer_name='In19.Cu')
for vv in d['vias']:
    if vv['net'] in direct:
        q=next(z for z in changed if z['net']==vv['net'] and math.dist(z['pt'],vv['pt'])<.000003);vv['layers']=q['layers']
fp.write_text(json.dumps(d,indent=2),encoding='utf-8');(W/'changed_direct_vias.json').write_text(json.dumps(changed,indent=2),encoding='utf-8');p.SaveBoard(str(W/'Main.signal_vias.kicad_pcb'),b)
print('Extended',len(changed),'B-side clock/USB/AUX vias to In19; routing can choose higher inner layers.')
