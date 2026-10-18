"""Align the module to the manufacturer's asymmetric end-terminal pitch."""
from pathlib import Path
exec(compile(Path(__file__).with_name('w_geometry.py').read_text(encoding='utf-8'),__file__,'exec'),globals())
pd=json.loads((W/'power_geometry.json').read_text(encoding='utf-8'));d=json.loads((W/'route_tasks.json').read_text(encoding='utf-8'));m={q['ref']:q for q in json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'))}
old=fs['U902'];a.folder=F;a.lib=F/'Local.pretty';a.models=F/'models';a.plugin=p.PCB_IO_MGR.FindPlugin(p.PCB_IO_MGR.KICAD_SEXP)
pads=[]
for pn,y in [(1,-2.925),(9,2.925),(10,2.925),(18,-2.925)]:
 sign=-1 if pn<10 else 1
 pads +=[(pn,sign*2.60,y,1.1,.9),(pn,sign*3.3,y-.325,.3,.25),(pn,sign*3.3,y+.325,.3,.25)]
for pn in range(2,9):pads.append((pn,-2.85,(pn-5)*.65,1.2,.25))
for pn in range(11,18):pads.append((pn,2.85,(14-pn)*.65,1.2,.25))
for pn,y in enumerate([-2.25,-.75,.75,2.25],19):pads.append((pn,0,y,3.3,1.075))
fp=a.custom('TI_RDF0022A_TPSM63610_NotchedLand',pads,6.5,7.5,4.05)
new=p.FootprintLoad(str(a.lib),fp);new.SetFPID(p.LIB_ID('Local',fp));new.SetReference('U902');new.SetValue(old.GetValue());new.SetPath(old.GetPath());new.Reference().SetVisible(False);new.Value().SetVisible(False);b.Add(new);new.Flip(v(0,0),p.FLIP_DIRECTION_LEFT_RIGHT);new.SetPosition(old.GetPosition())
for pp in new.Pads():pp.SetNet(a.net(m['U902']['pinmap'][pp.GetNumber()]))
remove(b,old);m['U902']['footprint']=fp
# Remove only this IC's old power stitches and its local configuration traces.
removedproof=[q for q in pd['pad_stitches'] if q['ref']=='U902' or q['net'].startswith('/PEX18_')]
oldvias={(q['net'],tuple(round(z,5) for z in pt)) for q in removedproof for pt in q.get('via_centers_mm',[])}
for t in list(b.GetTracks()):
 if isinstance(t,p.PCB_VIA):
  if (t.GetNetname(),tuple(round(z,5) for z in xy(t.GetPosition()))) in oldvias:remove(b,t)
 elif t.GetNetname().startswith('/PEX18_'):remove(b,t)
 elif t.GetLayer()==p.B_Cu and any(q['ref']=='U902' and t.GetNetname()==q['net'] and (math.dist(xy(t.GetStart()),q['pad_pt'])<.000005 or math.dist(xy(t.GetEnd()),q['pad_pt'])<.000005) for q in removedproof):remove(b,t)
pd['pad_stitches']=[q for q in pd['pad_stitches'] if q not in removedproof]
pd['control_routes']=[q for q in pd['control_routes'] if not q['net'].startswith('/PEX18_')]
p.SaveBoard(str(bp),b)
exec(compile(Path(__file__).with_name('w_geometry.py').read_text(encoding='utf-8'),__file__,'exec'),globals())
planes.update({'/PEX_0V9':[p.In19_Cu],'/PEX_0V9A':[p.In22_Cu],'/PEX_1V8':[p.In4_Cu],'/PEX_1V8A':[p.In7_Cu]})
for pp in fs['U902'].Pads():
 nn=pp.GetNetname()
 if nn in planes:stitch(fs['U902'],pp,nn,planes[nn])
 elif nn=='/GND':stitch(fs['U902'],pp,nn,[p.In28_Cu])
ns=defaultdict(list)
for ref,f in fs.items():
 for pp in f.Pads():
  nn=pp.GetNetname()
  if nn.startswith('/PEX18_'):
   pt=xy(pp.GetPosition())
   if not any(math.dist(pt,z['pt'])<.000002 for z in ns[nn]):ns[nn].append(dict(ref=ref,pin=pp.GetNumber(),pt=pt,side=f.GetLayer()))
newtasks=[];proofstart=len(proof)
for nn,es in sorted(ns.items()):
 linked=[es[0]]
 for i,e in enumerate(es[1:]):
  start=min(linked,key=lambda z:math.dist(z['pt'],e['pt']))
  try:path=localroute(start['pt'],e['pt'],nn,.1,p.B_Cu)
  except RuntimeError:path=None
  if path:
   for x,z in zip(path,path[1:]):track(x,z,nn,p.B_Cu,.1)
   pd['control_routes'].append(dict(net=nn,points=path,width=.1,layer=p.B_Cu))
  else:
   ends={}
   for en,it in [('a',start),('b',e)]:
    pp=pad(fs[it['ref']],it['pin']);target=p.In1_Cu
    # Reuse an existing same-net pad via when a branched net has another task.
    existing=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()==nn and t.IsOnLayer(p.B_Cu) and pp.HitTest(t.GetPosition())]
    pts=[xy(existing[0].GetPosition())] if existing else stitch(fs[it['ref']],pp,nn,[target]);assert pts,(it,nn)
    ends[en]=dict(ref=it['ref'],pin=it['pin'],pad_pt=xy(pp.GetPosition()),pt=pts[0],fanout_mm=math.dist(xy(pp.GetPosition()),pts[0]))
   newtasks.append(dict(net=nn,task_id=nn+'__MODULE_'+str(i),group=nn,kind='POWER_CONTROL',paired=False,width=.1,layer=36,layer_name='In17.Cu',layer_index=17,**ends))
  linked.append(e)
pd['pad_stitches']+=proof;pd['via_records']+=added;assert not failed,failed
d['tasks']=[q for q in d['tasks'] if not q['net'].startswith('/PEX18_')]+newtasks
d['vias']=[];d['segments']=[]
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):d['vias'].append(dict(net=t.GetNetname(),pt=xy(t.GetPosition()),diameter=p.ToMM(t.GetWidth(t.TopLayer())),layers=[ll for ll in cu if t.IsOnLayer(ll)]))
 else:d['segments'].append(dict(net=t.GetNetname(),a=xy(t.GetStart()),b=xy(t.GetEnd()),width=p.ToMM(t.GetWidth()),layer=t.GetLayer()))
(F/'COMPONENTS.json').write_text(json.dumps(list(m.values()),indent=2),encoding='utf-8');(W/'power_geometry.json').write_text(json.dumps(pd,indent=2),encoding='utf-8');(W/'route_tasks.json').write_text(json.dumps(d,indent=2),encoding='utf-8');p.SaveBoard(str(bp),b);p.SaveBoard(str(W/'Main.prepared.kicad_pcb'),b)
print('Module corrected to TI notched lands and 6.5x7.5 body;',len(newtasks),'inner module controls;',len(proof),'replacement stitches',flush=True)
