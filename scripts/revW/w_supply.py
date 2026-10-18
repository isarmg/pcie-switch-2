from pathlib import Path
exec(compile(Path(__file__).with_name('w_geometry.py').read_text(encoding='utf-8'),__file__,'exec'),globals())
planes.update({'/PEX_0V9':[p.In19_Cu],'/PEX_0V9A':[p.In22_Cu],'/PEX_1V8':[p.In4_Cu],'/PEX_1V8A':[p.In7_Cu]})
oldpower=set(json.loads((R/'work/revV/power_refs.json').read_text(encoding='utf-8')))
meta={q['ref']:q for q in json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'))}
power=oldpower|{r for r in fs if r[1:].isdigit() and int(r[1:])>=9000}|{'U901','U902','L901','L902','L903'}
# New refs use four-digit C/R and three-digit U/L. Retain native power ball names.
groundrefs=power|{'U1','U502','U501','U503','U601','U602','U510','U511','U512','U702','U607','J401','J402'}|{f'J{k}' for k in range(1,13)}
selected=[]
for f in fs.values():
 seen=set()
 for pp in f.Pads():
  nn=pp.GetNetname();key=(pp.GetNumber(),xy(pp.GetPosition()))
  if not pp.GetNumber() or key in seen:continue
  seen.add(key)
  if nn in planes:selected.append((f,pp,nn,planes[nn]))
  elif nn=='/GND' and (f.GetReference() in groundrefs or (f.GetReference().startswith('C') and any(q.GetNetname() in planes for q in f.Pads()))):selected.append((f,pp,nn,[p.In1_Cu] if f.GetLayer()==p.F_Cu else [p.In28_Cu]))
selected.sort(key=lambda z:(min(p.ToMM(z[1].GetSize().x),p.ToMM(z[1].GetSize().y))<2.5,z[2],z[0].GetReference()))
for i,(f,pp,nn,targets) in enumerate(selected):
 stitch(f,pp,nn,targets)
 if i%100==0:print('Power fanout',i,'/',len(selected),'failed',len(failed),flush=True)
bridges=[]
for ref in ['L31','C314','C315']:
 pp=next(q for q in fs[ref].Pads() if q.GetNetname()=='/P3V3_AUX');cx,cy=xy(pp.GetPosition())
 for dx in [0,-.3,.3]:
  for dy in [0,-.5,.5,-1,1]:
   pt=(cx+dx,cy+dy)
   if pp.HitTest(v(*pt)) and legal_via(pt,'/P3V3_AUX',p.F_Cu,p.In30_Cu,.2,.1):via(pt,'/P3V3_AUX',p.F_Cu,p.In30_Cu);bridges.append(pt)
by=defaultdict(list)
for ref in power:
 if ref not in fs:continue
 for pp in fs[ref].Pads():
  nn=pp.GetNetname()
  if nn in planes or nn=='/GND' or not nn or nn.startswith('unconnected-') or nn=='/PEX09_SW':continue
  if any(s in nn for s in ['_PWR_','/AUX_','/BUCK_','/TBT_5V_','/PEX09_','/PEX18_']):
   entry=dict(ref=ref,pin=pp.GetNumber(),pt=xy(pp.GetPosition()),side=fs[ref].GetLayer())
   if not any(z['side']==entry['side'] and math.dist(z['pt'],entry['pt'])<.000002 for z in by[nn]):by[nn].append(entry)
controlfailed=[];ctrlinner=[]
for nn,es in sorted(by.items(),key=lambda kv:('SW' not in kv[0],kv[0])):
 sides={e['side'] for e in es};width=.35 if nn in ['/BUCK_SW','/TBT_5V_SW'] else .1
 connected=[es[0]]
 for e in es[1:]:
  start=min(connected,key=lambda z:math.dist(z['pt'],e['pt']));path=None
  if len(sides)==1:
   try:path=localroute(start['pt'],e['pt'],nn,width,e['side'])
   except RuntimeError:pass
  if path:
   for x,z in zip(path,path[1:]):track(x,z,nn,e['side'],width)
   controls.append(dict(net=nn,points=path,width=width,layer=e['side']))
  else:ctrlinner.append(dict(net=nn,a=start,b=e,width=width))
  connected.append(e)
 print('Local control',nn,'deferred inner sections',len(ctrlinner),flush=True)
# Dedicated short switch node copper on the component side, clear of BOOT.
a.zone('/PEX09_SW',p.F_Cu,[(7.35,1.6),(12.2,1.6),(12.2,5.15),(7.35,5.15)])
z=list(b.Zones())[-1];z.SetMinThickness(p.FromMM(.12));z.SetLocalClearance(p.FromMM(.1));z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
# Include BOOT capacitor's switch side using a short local branch, not an inner SW plane.
swpads=[pp for ref in ['U901','L901','C9006'] for pp in fs[ref].Pads() if pp.GetNetname()=='/PEX09_SW']
cp=next(pp for pp in fs['C9006'].Pads() if pp.GetNetname()=='/PEX09_SW');sp=min(swpads[:-1],key=lambda q:math.dist(xy(q.GetPosition()),xy(cp.GetPosition())))
try:
 path=localroute(xy(cp.GetPosition()),xy(sp.GetPosition()),'/PEX09_SW',.18)
 for x,z in zip(path,path[1:]):track(x,z,'/PEX09_SW',p.F_Cu,.18)
 controls.append(dict(net='/PEX09_SW',points=path,width=.18,layer=p.F_Cu))
except RuntimeError:controlfailed.append(dict(net='/PEX09_SW',ref='C9006',reason='short surface branch blocked'))
for pp in swpads:proof.append(dict(ref=pp.GetParentFootprint().GetReference(),pin=pp.GetNumber(),net='/PEX09_SW',pad_pt=xy(pp.GetPosition()),side=p.F_Cu,target_layer=p.F_Cu,via_centers_mm=[],desired_parallel_vias=0,parallel_via_target_met=True,direct_surface_pour=True))
for nn,ls in planes.items():
 for ll in ls:
  x0,x1=(.5,44.5) if nn=='/VIN_A' else (44.9,95.5) if nn=='/VIN_B' else (.5,95.5)
  a.zone(nn,ll,[(x0,.5),(x1,.5),(x1,44.5),(x0,44.5)])
  z=list(b.Zones())[-1];z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS);z.SetMinThickness(p.FromMM(.12));z.SetLocalClearance(p.FromMM(.1))
for idx in [1,10,13,16,25,28]:a.zone('/GND',getattr(p,f'In{idx}_Cu'),[(.5,.5),(95.5,.5),(95.5,44.5),(.5,44.5)])
p.SaveBoard(str(bp),b)
data=dict(planes={nn:[b.GetLayerName(ll) for ll in ls] for nn,ls in planes.items()},via_records=added,pad_stitches=proof,failed_pad_stitches=failed,control_routes=controls,failed_control_routes=controlfailed,deferred_inner_controls=ctrlinner,aux_3v3_plane_bridges=bridges,thermal_and_current_capacity_qualified=False,blind_via_stackup_qualified=False,cpu_dynamic_vr_implemented=False,fictional_switch_regulators_implemented=True)
(W/'power_geometry.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
print('Power built:',len(proof),'pad stitches;',len(failed),'failed;',len(controls),'local controls;',len(ctrlinner),'inner controls',flush=True)
