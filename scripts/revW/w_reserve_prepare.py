from pathlib import Path
exec(compile(Path(__file__).with_name('w_geometry.py').read_text(encoding='utf-8'),__file__,'exec'),globals())
S=W/'reserve';S.mkdir(exist_ok=True);sd=json.loads((O/'SIGNAL_ROUTES.json').read_text(encoding='utf-8'));pd=json.loads((W/'power_geometry.json').read_text(encoding='utf-8'));layers={p.In2_Cu,p.In3_Cu,p.In30_Cu}
qs=[q for q in sd['routes'] if q['layer'] in layers]+[q for q in pd['control_routes'] if q['layer'] in layers and q.get('task_id')]
assert len(qs)>=40
for t in list(b.GetTracks()):
 if not isinstance(t,p.PCB_VIA) and t.GetLayer() in layers:remove(b,t)
vs=[];segs=[]
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):vs.append(dict(net=t.GetNetname(),pt=xy(t.GetPosition()),diameter=p.ToMM(t.GetWidth(t.TopLayer())),layers=[ll for ll in cu if t.IsOnLayer(ll)]))
 else:segs.append(dict(net=t.GetNetname(),a=xy(t.GetStart()),b=xy(t.GetEnd()),width=p.ToMM(t.GetWidth()),layer=t.GetLayer()))
(S/'route_tasks.json').write_text(json.dumps(dict(tasks=qs,retained=[],vias=vs,segments=segs,grid_mm=.05,clearance_mm=.08),indent=2),encoding='utf-8');(S/'old_transformed.json').write_text(json.dumps(qs,indent=2),encoding='utf-8');p.SaveBoard(str(S/'Base.kicad_pcb'),b)
print('Reserve VIN and both 3.3V layers;',len(qs),'sections to move.',flush=True)
