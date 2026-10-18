from pathlib import Path
exec(compile(Path(__file__).with_name('w_geometry.py').read_text(encoding='utf-8'),__file__,'exec'),globals())
pd=json.loads((W/'power_geometry.json').read_text(encoding='utf-8'));m={q['ref']:q for q in json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'))}
for t in list(b.GetTracks()):
 if not isinstance(t,p.PCB_VIA) and t.GetNetname()=='/PEX09_BOOT':remove(b,t)
f=fs['C9006'];f.SetOrientationDegrees(90);f.SetPosition(v(8.7,5.2));m['C9006'].update(x=8.7,y=5.2,rotation_deg=90)
moved=[]
for ref in ['C9013','C9014','C9015','C9016']:
 f=fs[ref];old={pp.GetNumber():xy(pp.GetPosition()) for pp in f.Pads()};x,y=xy(f.GetPosition());f.SetPosition(v(x+.55,y));m[ref].update(x=x+.55,y=y)
 for pp in f.Pads():moved.append((ref,pp.GetNumber(),pp.GetNetname(),old[pp.GetNumber()],xy(pp.GetPosition())))
for q in pd['pad_stitches']:
 if q['ref'] in ['C9006','C9013','C9014','C9015','C9016']:q['pad_pt']=xy(pad(fs[q['ref']],q['pin']).GetPosition())
p.SaveBoard(str(bp),b)
exec(compile(Path(__file__).with_name('w_geometry.py').read_text(encoding='utf-8'),__file__,'exec'),globals())
for ref,pn,nn,start,end in moved:
 path=localroute(start,end,nn,.15,p.F_Cu)
 for x,z in zip(path,path[1:]):track(x,z,nn,p.F_Cu,.15)
pd['control_routes']=[q for q in pd['control_routes'] if q['net']!='/PEX09_BOOT']
for nn,pn,upn in [('/PEX09_BOOT','1','5'),('/PEX09_SW','2','6')]:
 start=xy(pad(fs['C9006'],pn).GetPosition());end=xy(pad(fs['U901'],upn).GetPosition());path=localroute(start,end,nn,.15,p.F_Cu)
 for x,z in zip(path,path[1:]):track(x,z,nn,p.F_Cu,.15)
 pd['control_routes'].append(dict(net=nn,points=path,width=.15,layer=p.F_Cu))
pd['failed_control_routes']=[]
for z in b.Zones():
 if z.GetLayer()==p.In23_Cu:z.SetMinThickness(p.FromMM(.2))
(F/'COMPONENTS.json').write_text(json.dumps(list(m.values()),indent=2),encoding='utf-8');(W/'power_geometry.json').write_text(json.dumps(pd,indent=2),encoding='utf-8');p.SaveBoard(str(bp),b)
print('Local capacitor clearances and short BOOT/SW loop repaired.',flush=True)
