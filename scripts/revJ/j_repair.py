from i_common import *
import subprocess,sys

for name in sys.argv[1:] or ['Main_10E1S','Left_2M2_Vertical','Right_M2_Upstream']:
    o=ROOT/name;bp=o/(name+'.kicad_pcb');b=p.LoadBoard(str(bp));main=name.startswith('Main');status=json.loads((o/'ROUTING_STATUS.json').read_text());ts=status['failed']
    if not ts:continue
    a=object.__new__(Board);a.b=b;a.nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
    ll=json.loads((R/'work/revJ'/f'{name}.layers.json').read_text());allmask=(1<<len(ll))-1;sh=[]
    retry_layer=12 if name.startswith('Left') else 9
    if not main and '--extend' in sys.argv:
        for t in ts:
            for pt in [(t['x'],t['y']),(t['tx'],t['ty'])]:
                found=False
                for vv in b.GetTracks():
                    if not isinstance(vv,p.PCB_VIA) or vv.GetNetname()!=t['net'] or math.dist(xy(vv.GetPosition()),pt)>.03:continue
                    found=True
                    if not vv.IsOnLayer(ll[retry_layer]):
                        if vv.TopLayer()==p.F_Cu:vv.SetLayerPair(p.F_Cu,ll[retry_layer])
                        elif vv.BottomLayer()==p.B_Cu:vv.SetLayerPair(ll[retry_layer],p.B_Cu)
                if not found:
                    match=next((q for f in b.GetFootprints() for q in f.Pads() if q.GetNetname()==t['net'] and math.dist(xy(q.GetPosition()),pt)<.03),None)
                    if match:a.via(*pt,t['net'],p.F_Cu if match.IsOnLayer(p.F_Cu) else ll[retry_layer],ll[retry_layer] if match.IsOnLayer(p.F_Cu) else p.B_Cu,.3,.1)
    def mask(t):return sum(1<<i for i,l in enumerate(ll) if t.IsOnLayer(l))
    for f in b.GetFootprints():
        for q in f.Pads():
            if q.GetAttribute()==p.PAD_ATTRIB_NPTH:pt=xy(q.GetPosition());sh.append((1,allmask,-1,*pt,*pt,p.ToMM(q.GetDrillSize().x)/2+.125));continue
            if not q.IsOnCopperLayer():continue
            bb=q.GetBoundingBox();sh.append((0,mask(q),q.GetNetCode() or -1,*xy(bb.GetOrigin()),*xy(bb.GetEnd()),0))
    for t in b.GetTracks():
        if isinstance(t,p.PCB_VIA):pt=xy(t.GetPosition());sh.append((1,mask(t),t.GetNetCode(),*pt,*pt,p.ToMM(t.GetWidth(p.B_Cu))/2))
        else:sh.append((1,mask(t),t.GetNetCode(),*xy(t.GetStart()),*xy(t.GetEnd()),p.ToMM(t.GetWidth())/2))
    for idx,t in enumerate(ts):
        t['id']=idx
        t['code']=a.nets[t['net']].GetNetCode()
        if main and not t['mode']:t['layer']=t['tl']=4
        elif not main and not t['mode']:
            sets=[]
            for pt in [(t['x'],t['y']),(t['tx'],t['ty'])]:
                sets.append({i for i,l in enumerate(ll) if i>=2 and any(isinstance(vv,p.PCB_VIA) and vv.GetNetname()==t['net'] and math.dist(xy(vv.GetPosition()),pt)<.03 and vv.IsOnLayer(l) for vv in b.GetTracks())})
            common=sets[0]&sets[1];tried=t.setdefault('tried_layers',[t['layer']] if t['layer']==t['tl'] else [])
            candidates=sorted(common-set(tried))
            if candidates:t['layer']=t['tl']=candidates[0];tried.append(candidates[0])
    lines=[f'{round((80 if main else 19.5)/.05)+1} 901 {len(ll)}',str(len(sh))]+[' '.join(map(str,q)) for q in sh]+[str(len(ts))]
    for t in ts:lines.append(f"{t['id']} {t['mode']} {t['code']} {t['layer']} {t['x']} {t['y']} {t['tl']} {t['tx']} {t['ty']} {t['w']}")
    pre=R/'work/revJ'/f'{name}.repair';inp=Path(str(pre)+'.input');out=Path(str(pre)+'.routes');inp.write_text('\n'.join(lines))
    subprocess.run([str(R/'work/revJ'/('router.exe' if main else 'router_inner.exe')),inp.name,out.name],cwd=pre.parent)
    success=[]
    for row in out.read_text().splitlines():
        z=list(map(int,row.split()));idx,count=z[:2];t=ts[idx];pts=[(z[2+j*3],z[3+j*3]*.05,z[4+j*3]*.05) for j in range(count)];nn=t['net'];success.append(idx)
        a.track((t['x'],t['y']),pts[0][1:],nn,ll[pts[0][0]],t['w'])
        for aa,zz in zip(pts,pts[1:]):
            if aa[0]==zz[0]:a.track(aa[1:],zz[1:],nn,ll[aa[0]],t['w'])
            else:a.via(*aa[1:],nn,p.In19_Cu if main else p.F_Cu if 0 in [aa[0],zz[0]] else p.In2_Cu,p.B_Cu if main or 1 in [aa[0],zz[0]] else p.In24_Cu)
        a.track(pts[-1][1:],(t['tx'],t['ty']),nn,ll[pts[-1][0]],t['w'])
    p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(bp),b);status['routed']+=len(success);status['failed']=[t for t in ts if t['id'] not in success];(o/'ROUTING_STATUS.json').write_text(json.dumps(status,indent=2));print(name,'repaired',len(success),'remaining',len(status['failed']),flush=True)
