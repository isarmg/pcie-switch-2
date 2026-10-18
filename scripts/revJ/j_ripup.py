from i_common import *
import sys
for name in sys.argv[1:]:
    o=ROOT/name;bp=o/(name+'.kicad_pcb');b=p.LoadBoard(str(bp));a=object.__new__(Board);a.b=b;a.nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
    report=json.loads((o/'DRC.json').read_text());status=json.loads((o/'ROUTING_STATUS.json').read_text());ns={t['net'] for t in status['failed']};byid={t.m_Uuid.AsString():t for t in b.GetTracks()}
    for v0 in report['violations']:
        if v0['type'] not in ['shorting_items','clearance','hole_clearance','hole_to_hole']:continue
        for it in v0['items']:
            t=byid.get(it['uuid'])
            if t is not None and t.GetNetname() not in ['/GND','/CABLE12'] and not t.GetNetname().endswith('_3V3'):ns.add(t.GetNetname())
    if name.startswith('Left'):
        f=b.FindFootprintByReference('J126');old=xy(f.GetPosition());f.SetPosition(v(old[0],35.4))
        ns.update(['/M4_RX3_P','/M4_RX3_N'])
        for t in list(b.GetTracks()):
            if isinstance(t,p.PCB_VIA) and t.GetNetname() in ['/M4_RX3_P','/M4_RX3_N'] and math.dist(xy(t.GetPosition()),(old[0]+(-.45 if t.GetNetname().endswith('_P') else .45),old[1]))<.01:t.Move(v(0,35.4-old[1]))
    # Keep only the terminal via-in-pad escapes. Remove the conflicting routes
    # and their intermediate vias so the router can choose a clean path.
    points={nn:[xy(q.GetPosition()) for f in b.GetFootprints() for q in f.Pads() if q.GetNetname()==nn] for nn in ns}
    for t in list(b.GetTracks()):
        if t.GetNetname() not in ns:continue
        if not isinstance(t,p.PCB_VIA) or not any(math.dist(xy(t.GetPosition()),pt)<.03 for pt in points[t.GetNetname()]):remove(b,t)
    original=json.loads((R/'work/revJ'/f'{name}.tasks.json').read_text());tasks=[t for t in original if t['net'] in ns]
    for t in tasks:
        f=b.FindFootprintByReference(t['ref']);q=pad(f,t['pin']);t['x'],t['y']=xy(q.GetPosition())
        if not t['mode']:t['tx'],t['ty']=xy(pad(b.FindFootprintByReference(t['target_ref']),t['target_pin']).GetPosition())
        if t['net'].endswith('_FB'):t['layer']=t['tl']=8
    tasks.sort(key=lambda t:(0 if t['net'] in {x['net'] for x in status['failed']} else 1,-math.hypot(t['x']-t['tx'],t['y']-t['ty'])))
    status['routed']=status['tasks']-len(tasks);status['failed']=tasks;(o/'ROUTING_STATUS.json').write_text(json.dumps(status,indent=2));p.SaveBoard(str(bp),b);print(name,'rerouting',sorted(ns),len(tasks),flush=True)
