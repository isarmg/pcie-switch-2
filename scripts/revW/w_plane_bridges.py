from pathlib import Path
import shutil
import json
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');W=R/'work/revW';F=R/'outputs/PCIe_E1S_96x45_USB12mm_RevW/Main_12E1S'
# The prepared board includes the verified ground repair and safe via extensions.
shutil.copy2(W/'bridge/Base.kicad_pcb',F/'Main_12E1S.kicad_pcb')
initial=json.loads((W/'power_geometry.json').read_text(encoding='utf-8'))
initial.setdefault('ground_island_surface_routes',[]).extend([q for q in initial['control_routes'] if q['net']=='/GND'])
initial['control_routes']=[q for q in initial['control_routes'] if q['net']!='/GND']
(W/'power_geometry.json').write_text(json.dumps(initial,indent=2),encoding='utf-8')
ns={'__file__':str(Path(__file__).with_name('w_audit_power.py'))}
exec(compile(Path(__file__).with_name('w_audit_power.py').read_text(encoding='utf-8').split("exec(compile(src,__file__")[0],'audit preparation','exec'),ns)
exec(compile(ns['src'].split('report=[]')[0],'actual filled copper graph','exec'),globals())
graph_pads=padnodes
exec(compile(Path(__file__).with_name('w_geometry.py').read_text(encoding='utf-8'),__file__,'exec'),globals())
pd=json.loads((W/'power_geometry.json').read_text(encoding='utf-8'));pd.setdefault('ground_island_surface_routes',[]).extend([q for q in pd['control_routes'] if q['net']=='/GND']);pd['control_routes']=[q for q in pd['control_routes'] if q['net']!='/GND']
groups=defaultdict(lambda:defaultdict(list))
for q,nd in graph_pads:groups[q['net']][find(nd)].append(q)
reserved={p.In2_Cu,p.In3_Cu,p.In4_Cu,p.In5_Cu,p.In6_Cu,p.In7_Cu,p.In19_Cu,p.In22_Cu,p.In30_Cu}
def member(t,nn):
 pt=tuple(round(z,5) for z in xy(t.GetPosition()))
 for ll in cu:
  key=(nn,pt,ll)
  if t.IsOnLayer(ll) and key in parent:return find(key)
 return None
done=[];failed=[]
for nn,gg in groups.items():
 roots={find(rt) for rt in gg}
 if len(roots)<2:continue
 counts={rt:sum(len(items) for old,items in gg.items() if find(old)==rt) for rt in roots};main=max(roots,key=lambda rt:counts[rt]);vv=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()==nn]
 for root in sorted(roots,key=str):
  if find(root)==find(main):continue
  print('Repair power component',nn,counts[root],'pads',flush=True)
  # A nearby surface fanout can reach the main plane outside a local cut.
  success=False
  sourcepads=[q for rt,items in gg.items() if find(rt)==find(root) for q in items]
  sourcepads.sort(key=lambda q:(not q['ref'].startswith('C'),q['ref']))
  destinations=[]
  for zi,z in enumerate(b.Zones()):
   if z.GetNetname()!=nn:continue
   poly=z.GetFilledPolysList(z.GetLayer())
   ids=[i for i in range(poly.OutlineCount()) if find(('zone',zi,i))==find(main)]
   if ids:destinations.append((z.GetLayer(),poly,ids))
  for source in sourcepads[:6]:
   ff=fs[source['ref']];pp=min((pp for pp in ff.Pads() if pp.GetNumber()==source['pin']),key=lambda pp:math.dist(xy(pp.GetPosition()),source['pad_pt']));center=xy(pp.GetPosition());side=ff.GetLayer()
   for radius in [.6,.9,1.2,1.6,2,2.5,3,4,5]:
    for angle in range(0,360,30):
     pt=(center[0]+radius*math.cos(math.radians(angle)),center[1]+radius*math.sin(math.radians(angle)))
     for ll,poly,ids in destinations:
      if not any(poly.Contains(v(*pt),i) for i in ids) or not legal_via(pt,nn,side,ll,.3,.15):continue
      for width in ([.5,.3] if nn.startswith('/P12_') else [.5,.3] if nn=='/TBT_5V0' else [.2,.1]):
       try:path=localroute(center,pt,nn,width,side)
       except RuntimeError:continue
       via(pt,nn,side,ll,.3,.15)
       for x,z in zip(path,path[1:]):track(x,z,nn,side,width)
       rec=dict(net=nn,layer=side,width=width,points=path,plane_layer=b.GetLayerName(ll),method='short surface fanout into main power plane',thermal_and_current_qualified=False)
       (pd['ground_island_surface_routes'] if nn=='/GND' else pd['control_routes']).append(rec);done.append(rec);union(root,main);success=True;break
      if success:break
     if success:break
    if success:break
   if success:break
  if success:
   print('Surface power repair',nn,'connected',flush=True);continue
  print('Locate short plane cut',nn,flush=True)
  rc=[t for t in vv if member(t,nn)==find(root)];mc=[t for t in vv if member(t,nn)==find(main)];pairs=sorted(((math.dist(xy(t.GetPosition()),xy(u.GetPosition())),t,u) for t in rc for u in mc),key=lambda q:q[0]);candidates=[]
  for zi,z in enumerate(b.Zones()):
   if z.GetNetname()!=nn:continue
   ll=z.GetLayer();poly=z.GetFilledPolysList(ll)
   def region(pt):
    for i in range(poly.OutlineCount()):
     if poly.Contains(v(*pt),i):return find(('zone',zi,i))
    return None
   for dist0,t,u in pairs[:2]:
    if not t.IsOnLayer(ll) or not u.IsOnLayer(ll):continue
    ss=[];mm=[];x=xy(t.GetPosition());y=xy(u.GetPosition());steps=max(2,math.ceil(dist0/.4))
    for j in range(steps+1):
     pt=tuple(x[k]+(y[k]-x[k])*j/steps for k in range(2));rt=region(pt)
     if rt==find(root):ss.append(pt)
     elif rt==find(main):mm.append(pt)
    near=sorted(((math.dist(pt,qt),pt,qt) for pt in ss for qt in mm),key=lambda q:q[0])[:24]
    candidates +=[(dd,ll,pt,qt) for dd,pt,qt in near if dd>.45]
  candidates.sort(key=lambda q:q[0]);success=False
  print('Plane cut candidates',nn,len(candidates),flush=True)
  width=.3 if nn.startswith('/P12_') else .5 if nn=='/TBT_5V0' else .2
  for dd,base,pt,qt in candidates[:180]:
   ls=sorted((ll for ll in cu[1:-1] if ll!=base and ll not in reserved),key=lambda ll:abs(order[ll]-order[base]))
   for ll in ls:
    if not legal_via(pt,nn,base,ll,.3,.15) or not legal_via(qt,nn,base,ll,.3,.15):continue
    if not clear(pt,qt,nn,ll,width/2):continue
    via(pt,nn,base,ll,.3,.15);via(qt,nn,base,ll,.3,.15);track(pt,qt,nn,ll,width);union(root,main);success=True
    rec=dict(net=nn,layer=ll,width=width,points=[pt,qt],plane_layer=b.GetLayerName(base),method='short buried-via crossover between adjacent copper islands',thermal_and_current_qualified=False);pd['control_routes'].append(rec);done.append(rec);break
   if success:break
  if not success:
   # Low-current auxiliary islands can use an existing deep via's escape.
   for _,t,u in pairs[:30]:
    common=[ll for ll in cu[1:-1] if ll not in reserved and t.IsOnLayer(ll) and u.IsOnLayer(ll)]
    for ll in common:
     for ww in ([.3,.2,.1] if nn=='/P3V3_AUX' else [.3,.2] if nn.startswith('/P12_') else [.3]):
      try:path=localroute(xy(t.GetPosition()),xy(u.GetPosition()),nn,ww,ll)
      except RuntimeError:continue
      for x,z in zip(path,path[1:]):track(x,z,nn,ll,ww)
      rec=dict(net=nn,layer=ll,width=ww,points=path,method='auxiliary island continuity; current / temperature not qualified');pd['control_routes'].append(rec);done.append(rec);union(root,main);success=True;break
     if success:break
    if success:break
  if not success:failed.append(dict(net=nn,pads=[q['ref']+'.'+q['pin'] for rt,items in gg.items() if find(rt)==find(root) for q in items]))
  print('Crossover',nn,'connected',success,flush=True)
pd['plane_crossover_bridges']=done;pd['failed_plane_crossovers']=failed;pd['via_records']+=added
print('Fill short plane crossovers...',flush=True);b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(bp),b);(W/'power_geometry.json').write_text(json.dumps(pd,indent=2),encoding='utf-8')
print('Crossovers completed',len(done),'unresolved',failed,flush=True)
