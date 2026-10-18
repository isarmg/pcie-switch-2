from pathlib import Path
exec(compile(Path(__file__).with_name('w_geometry.py').read_text(encoding='utf-8'),__file__,'exec'),globals())
import copy
S=R/'outputs/PCIe_E1S_96x45_12VPower_RevV';old={q['ref']:q for q in json.loads((S/'Main_12E1S/COMPONENTS.json').read_text(encoding='utf-8'))}
routes=json.loads((S/'SIGNAL_ROUTES.json').read_text(encoding='utf-8'))['routes'];endpoints={}
assert not list(b.GetTracks()),'Prepared only once'
for r in routes:
 for end in ['a','b']:
  e=r[end];key=(e['ref'],e['pin']);ff=fs[e['ref']];pp=pad(ff,e['pin']);actual=xy(pp.GetPosition());delta=[actual[i]-e['pad_pt'][i] for i in range(2)]
  endpoints[key]=dict(old=e,net=r['net'],direct=r['layer']==0,side=ff.GetLayer(),pad=pp,center=actual,desired=[e['pt'][i]+delta[i] for i in range(2)])
made={};fanouts=[];adjust=[]
# Fixed BGA fanouts first. Reposition connector vias only when drill clearance needs it.
for key,e in sorted(endpoints.items(),key=lambda kv:(kv[0][0] not in ['U502','U501','U503','U1'],kv[1]['side']==p.F_Cu,kv[0])):
 ref,pn=key;nn=e['net'];ff=fs[ref];pp=e['pad'];center=e['center'];side=e['side']
 if e['direct']:made[key]=dict(ref=ref,pin=pn,pt=center,pad_pt=center,fanout_mm=0);continue
 target=p.In1_Cu if side==p.B_Cu else p.In30_Cu;desired=tuple(e['desired']);dia=.2;dr=.1
 candidates=[desired,center]
 # Retain old edge fanouts where possible. Then search pad and short surface escapes.
 for radius in [.05,.1,.15,.2,.25,.3,.4,.5,.65,.8,1,1.3,1.7,2.2]:
  for angle in range(0,360,30):candidates.append((center[0]+radius*math.cos(math.radians(angle)),center[1]+radius*math.sin(math.radians(angle))))
 good=None;path=None
 for pt in candidates:
  if not legal_via(pt,nn,side,target,dia,dr):continue
  if math.dist(pt,center)<.000002 or clear(center,pt,nn,side,.05):good=pt;path=[center,pt];break
 if good is None:
  for pt in candidates:
   if not legal_via(pt,nn,side,target,dia,dr):continue
   try:path=localroute(center,pt,nn,.1,side);good=pt;break
   except RuntimeError:pass
 assert good is not None,('signal fanout',key,nn,center)
 via(good,nn,side,target,dia,dr)
 for x,z in zip(path,path[1:]):track(x,z,nn,side,.1)
 if math.dist(good,desired)>.000005:adjust.append(dict(ref=ref,pin=pn,old=desired,new=good))
 made[key]=dict(ref=ref,pin=pn,pt=xy(v(*good)),pad_pt=center,fanout_mm=sum(math.dist(x,z) for x,z in zip(path,path[1:])))
 if math.dist(center,good)>.000002:fanouts.append(dict(net=nn,ref=ref,pin=pn,points=path,layer=side,width=.1))
 if len(made)%100==0:print('Prepared signal endpoints',len(made),'/',len(endpoints),flush=True)
tasks=[];retained=[];old_transformed=[]
for r in routes:
 q=copy.deepcopy(r)
 for end in ['a','b']:q[end]=made[(r[end]['ref'],r[end]['pin'])]
 aa,bb=q['a']['pt'],q['b']['pt'];pts=r['points'];ds=[math.dist(x,z) for x,z in zip(pts,pts[1:])];total=sum(ds);at=0;trans=[]
 for i,pt in enumerate(pts):
  if i:at+=ds[i-1]
  ratio=at/total if total else 0;trans.append([pt[j]+(aa[j]-pts[0][j])*(1-ratio)+(bb[j]-pts[-1][j])*ratio for j in range(2)])
 q['points']=trans;old_transformed.append(q)
 if q['layer']==0:
  assert clear(aa,bb,q['net'],p.F_Cu,q['width']/2),('old direct F route obstructed',q['net'])
  track(aa,bb,q['net'],p.F_Cu,q['width']);q['points']=[aa,bb];q['length_mm']=math.dist(aa,bb);retained.append(q)
 else:tasks.append({k:v for k,v in q.items() if k not in ['points','length_mm']})
(W/'old_transformed.json').write_text(json.dumps(old_transformed,indent=2),encoding='utf-8')
(W/'route_base.json').write_text(json.dumps(dict(tasks=tasks,retained=retained,fanouts=fanouts,adjusted_signal_vias=adjust),indent=2),encoding='utf-8')
p.SaveBoard(str(bp),b)
print('Prepared',len(made),'endpoints;',len(tasks),'inner sections;',len(retained),'direct sections;',len(adjust),'relocated signal vias',flush=True)
