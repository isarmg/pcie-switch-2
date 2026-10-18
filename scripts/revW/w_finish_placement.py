from pathlib import Path
exec(compile(Path(__file__).with_name('w_geometry.py').read_text(encoding='utf-8'),__file__,'exec'),globals())
meta={q['ref']:q for q in json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'))};pd=json.loads((W/'power_geometry.json').read_text(encoding='utf-8'))
for ref,dx,dy in [('C9001',.5,0),('C9002',.5,0),('C9023',0,.2),('C9024',0,.2)]:
 f=fs[ref];x,y=xy(f.GetPosition());f.SetPosition(v(x+dx,y+dy));meta[ref].update(x=x+dx,y=y+dy)
 for q in pd['pad_stitches']:
  if q['ref']!=ref:continue
  pp=pad(f,q['pin']);assert all(pp.HitTest(v(*pt)) for pt in q.get('via_centers_mm',[])),(ref,'via outside moved pad')
  q['pad_pt']=xy(pp.GetPosition())
if '--check' not in sys.argv:
 (F/'COMPONENTS.json').write_text(json.dumps(list(meta.values()),indent=2),encoding='utf-8');(W/'power_geometry.json').write_text(json.dumps(pd,indent=2),encoding='utf-8');p.SaveBoard(str(bp),b)
print('Four capacitors adjusted; existing vias remain inside their pads.',flush=True)
