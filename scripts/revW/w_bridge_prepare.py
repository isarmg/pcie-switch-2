from pathlib import Path
# Build graph from native copper, including finite-width contacts.
ns={'__file__':str(Path(__file__).with_name('w_audit_power.py'))}
exec(compile(Path(__file__).with_name('w_audit_power.py').read_text(encoding='utf-8').split("exec(compile(src,__file__")[0],'audit preparation','exec'),ns)
exec(compile(ns['src'].split('report=[]')[0],'filled copper graph','exec'),globals())
graph_pads=padnodes;graph_parent=parent
exec(compile(Path(__file__).with_name('w_geometry.py').read_text(encoding='utf-8'),__file__,'exec'),globals())
pd=json.loads((W/'power_geometry.json').read_text(encoding='utf-8'));S=W/'bridge';S.mkdir(exist_ok=True)
groups=defaultdict(lambda:defaultdict(list))
for q,nd in graph_pads:groups[q['net']][find(nd)].append(q)
def member(t,nn):
 pt=tuple(round(z,5) for z in xy(t.GetPosition()))
 for ll in cu:
  key=(nn,pt,ll)
  if t.IsOnLayer(ll) and key in parent:return find(key)
 return None
def canextend(t,ll):
 old={l for l in cu if t.IsOnLayer(l)};lo,hi=sorted([t.TopLayer(),t.BottomLayer(),ll],key=lambda l:order[l])[::2];new=set(span(lo,hi))-old;pt=xy(t.GetPosition());nn=t.GetNetname();rad=p.ToMM(t.GetWidth(t.TopLayer()))/2;dr=p.ToMM(t.GetDrillValue())
 for l in new:
  if not clear(pt,pt,nn,l,rad,dr):return False
  if any(kind=='via' and math.dist(pt,x)<(dr+hole)/2+.251 for x,z,rr,net,layer,kind,hole in nearby(l,pt,pt)):return False
 return True
extensions=[]
def extend(t,ll):
 old={l for l in cu if t.IsOnLayer(l)};lo,hi=sorted([t.TopLayer(),t.BottomLayer(),ll],key=lambda l:order[l])[::2];t.SetLayerPair(lo,hi);pt=xy(t.GetPosition());nn=t.GetNetname();rad=p.ToMM(t.GetWidth(t.TopLayer()))/2;dr=p.ToMM(t.GetDrillValue())
 for l in set(span(lo,hi))-old:insert((pt,pt,rad,nn,l,'via',dr))
 extensions.append(dict(net=nn,pt=pt,target=b.GetLayerName(ll)))
reserved={p.In2_Cu,p.In3_Cu,p.In4_Cu,p.In5_Cu,p.In6_Cu,p.In7_Cu,p.In19_Cu,p.In22_Cu,p.In30_Cu}
tasks=[];unresolved=[]
# Join existing reference planes directly, including both 3.3V planes.
for nn,targets in [('/GND',[p.In10_Cu,p.In13_Cu,p.In16_Cu,p.In25_Cu,p.In28_Cu,p.In1_Cu]),('/P3V3_AUX',[p.In2_Cu,p.In30_Cu])]:
 if nn not in groups or len(groups[nn])<2:continue
 gg=groups[nn];main=max(gg,key=lambda rt:len(gg[rt]));vv=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()==nn]
 for root in [rt for rt in gg if rt!=main]:
  done=False
  for t in vv:
   if member(t,nn)!=find(root):continue
   pt=xy(t.GetPosition())
   for ll in targets:
    if t.IsOnLayer(ll) or not canextend(t,ll):continue
    for zi,z in enumerate(b.Zones()):
     if z.GetNetname()!=nn or z.GetLayer()!=ll:continue
     poly=z.GetFilledPolysList(ll)
     if any(poly.Contains(v(*pt),i) and find(('zone',zi,i))==find(main) for i in range(poly.OutlineCount())):extend(t,ll);union(root,main);done=True;break
    if done:break
   if done:break
  if not done and nn=='/GND':
   rc=[t for t in vv if member(t,nn)==find(root) and t.IsOnLayer(p.F_Cu)];mc=[t for t in vv if member(t,nn)==find(main) and t.IsOnLayer(p.F_Cu)]
   pairs=sorted(((math.dist(xy(t.GetPosition()),xy(u.GetPosition())),t,u) for t in rc for u in mc),key=lambda q:q[0])
   for _,t,u in pairs[:25]:
    try:path=localroute(xy(t.GetPosition()),xy(u.GetPosition()),nn,.1,p.F_Cu)
    except RuntimeError:continue
    for x,z in zip(path,path[1:]):track(x,z,nn,p.F_Cu,.1)
    pd.setdefault('ground_island_surface_routes',[]).append(dict(net=nn,layer=p.F_Cu,width=.1,points=path));union(root,main);done=True;break
   if not done:unresolved.append(dict(net=nn,pads=[q['ref']+'.'+q['pin'] for q in gg[root]]))
for nn,gg in groups.items():
 if nn=='/GND' or len({find(rt) for rt in gg})<2:continue
 main=max(gg,key=lambda rt:len(gg[rt]));vv=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()==nn]
 for root in [rt for rt in gg if find(rt)!=find(main)]:
  rc=[t for t in vv if member(t,nn)==find(root)];mc=[t for t in vv if member(t,nn)==find(main)];pairs=sorted(((math.dist(xy(t.GetPosition()),xy(u.GetPosition())),t,u) for t in rc for u in mc),key=lambda it:it[0]);chosen=None
  for _,t,u in pairs[:150]:
   own={ll for ll in cu if b.GetLayerName(ll) in pd['planes'].get(nn,[])}
   ls=[ll for ll in cu[1:-1] if ll not in reserved and ll not in own]
   ls.sort(key=lambda ll:(sum(1 for other in b.GetTracks() if not isinstance(other,p.PCB_VIA) and other.GetLayer()==ll)*.1+abs(order[ll]-order[t.TopLayer()])+abs(order[ll]-order[u.BottomLayer()]),ll))
   for ll in ls:
    if canextend(t,ll) and canextend(u,ll):chosen=(t,u,ll);break
   if chosen:break
  if not chosen:unresolved.append(dict(net=nn,pads=[q['ref']+'.'+q['pin'] for q in gg[root]]));continue
  t,u,ll=chosen;extend(t,ll);extend(u,ll);width=.3 if nn.startswith('/P12_') else .5 if nn in ['/P3V3_AUX','/TBT_5V0'] else .2
  tasks.append(dict(net=nn,task_id=nn+'__ISLAND_'+str(len(tasks)),group=nn,kind='POWER_CONTROL',paired=False,width=width,layer=ll,layer_index=ll//2-1,layer_name=b.GetLayerName(ll),a=dict(ref='ISLAND_SOURCE',pin='1',pt=xy(t.GetPosition()),pad_pt=xy(t.GetPosition()),fanout_mm=0),b=dict(ref='ISLAND_TARGET',pin='1',pt=xy(u.GetPosition()),pad_pt=xy(u.GetPosition()),fanout_mm=0)))
  union(root,main)
assert not unresolved,unresolved
vs=[];segs=[]
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):vs.append(dict(net=t.GetNetname(),pt=xy(t.GetPosition()),diameter=p.ToMM(t.GetWidth(t.TopLayer())),layers=[ll for ll in cu if t.IsOnLayer(ll)]))
 else:segs.append(dict(net=t.GetNetname(),a=xy(t.GetStart()),b=xy(t.GetEnd()),width=p.ToMM(t.GetWidth()),layer=t.GetLayer()))
(S/'route_tasks.json').write_text(json.dumps(dict(tasks=tasks,retained=[],vias=vs,segments=segs,grid_mm=.05,clearance_mm=.08),indent=2),encoding='utf-8');(S/'old_transformed.json').write_text('[]',encoding='utf-8');(S/'extensions.json').write_text(json.dumps(extensions,indent=2),encoding='utf-8');p.SaveBoard(str(S/'Base.kicad_pcb'),b)
(W/'power_geometry.json').write_text(json.dumps(pd,indent=2),encoding='utf-8')
print('Power bridges:',len(tasks),'routes;',len(extensions),'via span extensions',flush=True)
