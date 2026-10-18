from pathlib import Path
import shutil
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');W=R/'work/revW';F=R/'outputs/PCIe_E1S_96x45_USB12mm_RevW/Main_12E1S'
shutil.copy2(W/'bridge/Base.kicad_pcb',F/'Main_12E1S.kicad_pcb')
exec(compile(Path(__file__).with_name('w_geometry.py').read_text(encoding='utf-8'),__file__,'exec'),globals())
d=json.loads((W/'bridge/route_tasks.json').read_text(encoding='utf-8'));cp=W/'bridge/progress.json';complete={q['task_id'] for q in json.loads(cp.read_text(encoding='utf-8'))['routes']} if cp.exists() else set();extensions=json.loads((W/'bridge/extensions.json').read_text(encoding='utf-8'))
def extendable(t,ll):
 old={l for l in cu if t.IsOnLayer(l)};lo,hi=sorted([t.TopLayer(),t.BottomLayer(),ll],key=lambda l:order[l])[::2];pt=xy(t.GetPosition());nn=t.GetNetname();rad=p.ToMM(t.GetWidth(t.TopLayer()))/2;dr=p.ToMM(t.GetDrillValue())
 for l in set(span(lo,hi))-old:
  if not clear(pt,pt,nn,l,rad,dr):return False
  if any(kind=='via' and math.dist(pt,x)<(dr+hole)/2+.251 for x,z,rr,net,layer,kind,hole in nearby(l,pt,pt)):return False
 return True
for q in d['tasks']:
 if q['task_id'] in complete:continue
 for end in ['a','b']:
  e=q[end];nn=q['net'];oldpt=e['pt'];vs=sorted([t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()==nn and math.dist(xy(t.GetPosition()),oldpt)<3],key=lambda t:math.dist(xy(t.GetPosition()),oldpt));chosen=None
  for ll in [p.In27_Cu,p.In25_Cu,p.In24_Cu,p.In23_Cu,p.In21_Cu,p.In18_Cu]:
   for t in vs:
    if extendable(t,ll):chosen=(t,ll);break
   if chosen:break
  assert chosen,(q['net'],end,'no broader via access')
  t,ll=chosen;old={l for l in cu if t.IsOnLayer(l)};lo,hi=sorted([t.TopLayer(),t.BottomLayer(),ll],key=lambda l:order[l])[::2];t.SetLayerPair(lo,hi);pt=xy(t.GetPosition());rad=p.ToMM(t.GetWidth(t.TopLayer()))/2;dr=p.ToMM(t.GetDrillValue())
  for l in set(span(lo,hi))-old:insert((pt,pt,rad,nn,l,'via',dr))
  e.update(pt=pt,pad_pt=pt);extensions.append(dict(net=nn,pt=pt,target=b.GetLayerName(ll)));print('Broaden',nn,end,pt,b.GetLayerName(ll),flush=True)
d['vias']=[dict(net=t.GetNetname(),pt=xy(t.GetPosition()),diameter=p.ToMM(t.GetWidth(t.TopLayer())),layers=[ll for ll in cu if t.IsOnLayer(ll)]) for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
(W/'bridge/route_tasks.json').write_text(json.dumps(d,indent=2),encoding='utf-8');(W/'bridge/extensions.json').write_text(json.dumps(extensions,indent=2),encoding='utf-8');p.SaveBoard(str(W/'bridge/Base.kicad_pcb'),b)
print('Power via access broadened.',flush=True)
