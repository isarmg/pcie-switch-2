from pathlib import Path
exec(compile(Path(__file__).with_name('w_geometry.py').read_text(encoding='utf-8'),__file__,'exec'),globals())
for ref,x,y in [('C9011',4.9,11.45),('C9012',13.95,11.45)]:fs[ref].SetPosition(v(x,y))
move=['C721','C931','C5118','C726','C5151']
def box(f):
 z=f.GetBoundingBox(False,False);return [p.ToMM(t) for t in [z.GetX(),z.GetY(),z.GetRight(),z.GetBottom()]]
def ov(z,o,g=.02):return z[0]<o[2]+g and z[2]>o[0]-g and z[1]<o[3]+g and z[3]>o[1]-g
for ref in move:
 f=fs[ref];target=xy(f.GetPosition());side=f.GetLayer();others=[box(q) for r,q in fs.items() if q.GetLayer()==side and r!=ref];done=False
 for ang in [f.GetOrientationDegrees(),90,0]:
  f.SetOrientationDegrees(ang);old=xy(f.GetPosition());z=box(f);off=[z[0]-old[0],z[1]-old[1],z[2]-old[0],z[3]-old[1]]
  for x,y in sorted(((xx/4,yy/4) for xx in range(3,381) for yy in range(3,178)),key=lambda pt:math.dist(pt,target)):
   zz=[x+off[0],y+off[1],x+off[2],y+off[3]]
   if zz[0]<.4 or zz[1]<.4 or zz[2]>95.6 or zz[3]>44.6:continue
   if all(not ov(zz,o) for o in others):f.SetPosition(v(x,y));done=True;break
  if done:break
 assert done,ref
m={q['ref']:q for q in json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'))}
for ref,f in fs.items():m[ref].update(x=xy(f.GetPosition())[0],y=xy(f.GetPosition())[1],rotation_deg=f.GetOrientationDegrees())
(F/'COMPONENTS.json').write_text(json.dumps(list(m.values()),indent=2),encoding='utf-8');p.SaveBoard(str(bp),b)
for ref in ['U901','L901','L902','C9011','C9012']:print(ref,xy(fs[ref].GetPosition()),box(fs[ref]),[(pp.GetNumber(),xy(pp.GetPosition())) for pp in fs[ref].Pads()][:14],flush=True)
