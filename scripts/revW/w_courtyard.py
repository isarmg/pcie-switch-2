"""Resolve the remaining small capacitor courtyard overlap with short copper stubs."""
from pathlib import Path
exec(compile(Path(__file__).with_name('w_geometry.py').read_text(encoding='utf-8'),__file__,'exec'),globals())
pd=json.loads((W/'power_geometry.json').read_text(encoding='utf-8'));meta=json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'))

def box(f):
 boxes=[g.GetBoundingBox() for g in f.GraphicalItems() if g.GetLayer()==p.F_CrtYd]
 if not boxes:return None
 return min(p.ToMM(q.GetX()) for q in boxes),min(p.ToMM(q.GetY()) for q in boxes),max(p.ToMM(q.GetRight()) for q in boxes),max(p.ToMM(q.GetBottom()) for q in boxes)

moves=[]
for ref in ['C721','C931']:
 f=fs[ref];oldpos=xy(f.GetPosition());oldpads={pp.GetNumber():xy(pp.GetPosition()) for pp in f.Pads()};f.SetPosition(v(oldpos[0]+.4,oldpos[1]));chosen=xy(f.GetPosition());bb=box(f)
 for g in fs.values():
  if g==f or g.GetLayer()!=p.F_Cu:continue
  c=box(g)
  if c:assert not(max(bb[0],c[0])<min(bb[2],c[2]) and max(bb[1],c[1])<min(bb[3],c[3])),(ref,g.GetReference())
 newpads={pp.GetNumber():(pp.GetNetname(),xy(pp.GetPosition())) for pp in f.Pads()};moves.append((ref,oldpos,chosen,oldpads,newpads))
for z in b.Zones():
 if z.GetLayer()==p.In23_Cu:z.SetMinThickness(p.FromMM(.3))
p.SaveBoard(str(bp),b)
exec(compile(Path(__file__).with_name('w_geometry.py').read_text(encoding='utf-8'),__file__,'exec'),globals())
for ref,oldpos,chosen,oldpads,newpads in moves:
 for pn,(nn,pt) in newpads.items():
  path=localroute(oldpads[pn],pt,nn,.1,p.F_Cu)
  for aa,zz in zip(path,path[1:]):track(aa,zz,nn,p.F_Cu,.1)
  key='ground_island_surface_routes' if nn=='/GND' else 'control_routes';pd.setdefault(key,[]).append(dict(net=nn,layer=p.F_Cu,width=.1,points=path))
 for q in pd['pad_stitches']:
  if q['ref']==ref:q['pad_pt']=newpads[q['pin']][1]
 next(q for q in meta if q['ref']==ref).update(x=chosen[0],y=chosen[1])
 print(ref,'moved from',oldpos,'to',chosen,flush=True)
(F/'COMPONENTS.json').write_text(json.dumps(meta,indent=2),encoding='utf-8');(W/'power_geometry.json').write_text(json.dumps(pd,indent=2),encoding='utf-8')
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(bp),b)
