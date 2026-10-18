from pathlib import Path
exec(compile(Path(__file__).with_name('w_geometry.py').read_text(encoding='utf-8'),__file__,'exec'),globals())
data=json.loads((W/'route_base.json').read_text(encoding='utf-8'));pd=json.loads((W/'power_geometry.json').read_text(encoding='utf-8'));pd['control_routes']+=[]
tasks=data['tasks'];made={};deferred=pd['deferred_inner_controls'];inner=[]
for q in deferred:
 for end in ['a','b']:
  e=q[end];key=(q['net'],e['ref'],e['pin'],tuple(e['pt']))
  if key in made:continue
  ff=fs[e['ref']];pp=min((pp for pp in ff.Pads() if pp.GetNumber()==e['pin']),key=lambda pp:math.dist(xy(pp.GetPosition()),e['pt']));nn=q['net'];target=p.In1_Cu if ff.GetLayer()==p.B_Cu else p.In30_Cu
  pts=stitch(ff,pp,nn,[target]);assert pts,('control landing failed',key)
  center=xy(pp.GetPosition());made[key]=dict(ref=e['ref'],pin=e['pin'],pad_pt=center,pt=pts[0],fanout_mm=math.dist(center,pts[0]))
for i,q in enumerate(deferred):
 es={end:made[(q['net'],q[end]['ref'],q[end]['pin'],tuple(q[end]['pt']))] for end in ['a','b']}
 tasks.append(dict(net=q['net'],task_id=q['net']+'__POWER_'+str(i),group=q['net'],kind='POWER_CONTROL',paired=False,width=q['width'],layer=36,layer_name='In17.Cu',layer_index=17,**es))
pd['pad_stitches']+=proof;pd['via_records']+=added;pd['failed_pad_stitches']+=failed
vias=[];segments=[]
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):vias.append(dict(net=t.GetNetname(),pt=xy(t.GetPosition()),diameter=p.ToMM(t.GetWidth(t.TopLayer())),layers=[ll for ll in cu if t.IsOnLayer(ll)]))
 else:segments.append(dict(net=t.GetNetname(),a=xy(t.GetStart()),b=xy(t.GetEnd()),width=p.ToMM(t.GetWidth()),layer=t.GetLayer()))
(W/'route_tasks.json').write_text(json.dumps(dict(tasks=tasks,retained=data['retained'],vias=vias,segments=segments,fanouts=data['fanouts'],grid_mm=.05,clearance_mm=.08),indent=2),encoding='utf-8')
(W/'power_geometry.json').write_text(json.dumps(pd,indent=2),encoding='utf-8');p.SaveBoard(str(W/'Main.prepared.kicad_pcb'),b);p.SaveBoard(str(bp),b)
print('Obstacles:',len(vias),'vias;',len(segments),'existing track segments;',len(tasks),'inner tasks',flush=True)
