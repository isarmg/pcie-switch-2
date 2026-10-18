"""Bridge remaining audited copper groups using vias belonging to those groups."""
from pathlib import Path
exec(compile(Path(__file__).with_name('w_geometry.py').read_text(encoding='utf-8'),__file__,'exec'),globals())
pd=json.loads((W/'power_geometry.json').read_text(encoding='utf-8'))
bad=next(q for q in pd['control_routes'] if q.get('task_id')=='/P12_SLOT05__ISLAND_6')
for t in list(b.GetTracks()):
 if isinstance(t,p.PCB_VIA) or t.GetNetname()!=bad['net'] or t.GetLayer()!=bad['layer']:continue
 if any((math.dist(xy(t.GetStart()),x)<.000003 and math.dist(xy(t.GetEnd()),z)<.000003) or (math.dist(xy(t.GetStart()),z)<.000003 and math.dist(xy(t.GetEnd()),x)<.000003) for x,z in zip(bad['points'],bad['points'][1:])):remove(b,t)
pd['control_routes']=[q for q in pd['control_routes'] if q.get('task_id')!=bad['task_id']]
p.SaveBoard(str(bp),b)
exec(compile(Path(__file__).with_name('w_geometry.py').read_text(encoding='utf-8'),__file__,'exec'),globals())
audit=json.loads((O/'POWER_CONNECTIVITY.json').read_text(encoding='utf-8'))
S=W/'finalpatch';S.mkdir(exist_ok=True);tasks=[];extensions=[]

def canextend(t,ll):
 old={l for l in cu if t.IsOnLayer(l)};lo,hi=sorted([t.TopLayer(),t.BottomLayer(),ll],key=lambda l:order[l])[::2];pt=xy(t.GetPosition());nn=t.GetNetname();rad=p.ToMM(t.GetWidth(t.TopLayer()))/2;dr=p.ToMM(t.GetDrillValue())
 for l in set(span(lo,hi))-old:
  if not clear(pt,pt,nn,l,rad,dr):return False
  if any(kind=='via' and math.dist(pt,x)<(dr+hole)/2+.251 for x,z,rr,net,layer,kind,hole in nearby(l,pt,pt)):return False
 return True

def extend(t,ll):
 old={l for l in cu if t.IsOnLayer(l)};lo,hi=sorted([t.TopLayer(),t.BottomLayer(),ll],key=lambda l:order[l])[::2];t.SetLayerPair(lo,hi);pt=xy(t.GetPosition());rad=p.ToMM(t.GetWidth(t.TopLayer()))/2;dr=p.ToMM(t.GetDrillValue())
 for l in set(span(lo,hi))-old:insert((pt,pt,rad,t.GetNetname(),l,'via',dr))
 extensions.append(dict(net=t.GetNetname(),pt=pt,target=b.GetLayerName(ll)))

def group_vias(nn,group):
 pads=set(group);pts=[pt for q in pd['pad_stitches'] if q['net']==nn and q['ref']+'.'+q['pin'] in pads for pt in q['via_centers_mm']]
 return [t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()==nn and any(math.dist(xy(t.GetPosition()),pt)<.000003 for pt in pts)]

for entry in audit['disconnected_nets']:
 nn=entry['net'];gg=sorted(entry['groups'],key=lambda g:-len(set(g)));main=group_vias(nn,gg[0]);assert main,entry
 for group in gg[1:]:
  vv=group_vias(nn,group);assert vv,group
  pairs=sorted([(math.dist(xy(t.GetPosition()),xy(u.GetPosition())),t,u) for t in vv for u in main],key=lambda q:q[0]);chosen=None
  for ll in [p.In25_Cu,p.In28_Cu,p.In16_Cu,p.In13_Cu,p.In10_Cu,p.In1_Cu]:
   for _,t,u in pairs:
    if canextend(t,ll) and canextend(u,ll):chosen=(t,u,ll);break
   if chosen:break
  assert chosen,(nn,group)
  t,u,ll=chosen;extend(t,ll);extend(u,ll)
  tasks.append(dict(net=nn,task_id=nn+'__FINALPATCH_'+str(len(tasks)),group=nn,kind='POWER_CONTROL',paired=False,width=.3 if nn.startswith('/P12_') else .2,layer=ll,layer_index=ll//2-1,layer_name=b.GetLayerName(ll),a=dict(ref='AUDITED_SOURCE',pin='1',pt=xy(t.GetPosition()),pad_pt=xy(t.GetPosition()),fanout_mm=0),b=dict(ref='AUDITED_TARGET',pin='1',pt=xy(u.GetPosition()),pad_pt=xy(u.GetPosition()),fanout_mm=0)))
  main.extend(vv)
tasks.append({**bad,'task_id':'/P12_SLOT05__FINALPATCH_SURFACE','points':[],'layer':p.In25_Cu,'layer_name':'In25.Cu','layer_index':25})
vs=[];segs=[]
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):vs.append(dict(net=t.GetNetname(),pt=xy(t.GetPosition()),diameter=p.ToMM(t.GetWidth(t.TopLayer())),layers=[ll for ll in cu if t.IsOnLayer(ll)]))
 else:segs.append(dict(net=t.GetNetname(),a=xy(t.GetStart()),b=xy(t.GetEnd()),width=p.ToMM(t.GetWidth()),layer=t.GetLayer()))
for x,z,rad,nn,ll,kind,dr in objects:
 if kind=='pad':segs.append(dict(net=nn,a=x,b=z,width=2*rad+.08,layer=ll,pad_obstacle=True))
 if kind=='rect':
  corners=[x,(z[0],x[1]),z,(x[0],z[1])]
  for aa,bb in zip(corners,corners[1:]+corners[:1]):segs.append(dict(net=nn,a=aa,b=bb,width=.08,layer=ll,pad_obstacle=True))
(S/'route_tasks.json').write_text(json.dumps(dict(tasks=tasks,retained=[],vias=vs,segments=segs,grid_mm=.05,clearance_mm=.08),indent=2),encoding='utf-8');(S/'old_transformed.json').write_text('[]',encoding='utf-8');(S/'extensions.json').write_text(json.dumps(extensions,indent=2),encoding='utf-8');p.SaveBoard(str(S/'Base.kicad_pcb'),b)
(W/'power_geometry.json').write_text(json.dumps(pd,indent=2),encoding='utf-8')
print('Remaining audited copper patches:',len(tasks),flush=True)
