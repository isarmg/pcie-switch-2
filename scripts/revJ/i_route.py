from i_common import *
import sys,collections,subprocess
names=['Main_10E1S','Left_2M2_Vertical','Right_M2_Upstream']
def run(name):
    folder=ROOT/name;bp=folder/(name+'.kicad_pcb');pro=(folder/(name+'.kicad_pro')).read_bytes();placement=R/'work/revJ'/f'{name}.placed.kicad_pcb'
    if not placement.exists():shutil.copy2(bp,placement)
    b=p.LoadBoard(str(placement));main=name.startswith('Main');w=80 if main else 19.5;h=45
    if not main:b.SetCopperLayerCount(32)
    cs=json.loads((folder/'COMPONENTS.json').read_text());refs={c['ref'] for c in cs};ll=([p.B_Cu]+[getattr(p,f'In{i}_Cu') for i in [19,21,23,25,27,29]]) if main else [p.F_Cu,p.B_Cu]+[getattr(p,f'In{i}_Cu') for i in range(2,25,2)]
    port_order=['M1','M2','M4'] if name.startswith('Left') else ['M3','M5','UP']
    def signal_layer(nn):
        m=re.match(r'/(M[1-5]|UP)_(TX[0-3]|RX[0-3]|CLK(?:_[PN])?|PERST|CLKREQ|WAKE)',nn)
        if not m:return None
        lane=int(m[2][-1]) if m[2].startswith(('TX','RX')) else 3
        return 2+4*port_order.index(m[1])+lane
    allmask=(1<<len(ll))-1;shapes=[];pads=[];a=object.__new__(Board);a.b=b;a.nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
    def add(kind,mask,net,start,end,r):
        if mask:shapes.append((kind,mask,net,*start,*end,r))
    def mask(obj):return sum(1<<i for i,l in enumerate(ll) if obj.IsOnLayer(l))
    def connectable(q):return q.GetNumber() and q.GetNetname() and not q.GetNetname().startswith('unconnected-')
    # Existing ground returns connect new reference layers. Add ground pours on daughter surfaces.
    if not main:
        for z in list(b.Zones()):remove(b,z)
        for i in range(1,30,2):a.zone('/GND',getattr(p,f'In{i}_Cu'),[(.4,.4),(w-.4,.4),(w-.4,44.6),(.4,44.6)])
        for l in [p.F_Cu,p.B_Cu]:a.zone('/GND',l,[(.4,.4),(w-.4,.4),(w-.4,44.6),(.4,44.6)])
        powerplanes={k:getattr(p,f'In{26+idx*2}_Cu') for idx,k in enumerate([1,2,4] if name.startswith('Left') else [3,5])}
        for k,l in powerplanes.items():a.zone(f'/M{k}_3V3',l,[(.4,.4),(w-.4,.4),(w-.4,44.6),(.4,44.6)])
    # Escape the 0.5 mm M.2 rows before global routing. Alternate via distances
    # maintain via-to-via clearance, while keeping every signal's pad identity.
    m2escape={};esc_layer={}
    if not main:
        for f in b.GetFootprints():
            if 'MDT350' not in str(f.GetFPID().GetLibItemName()):continue
            for q in f.Pads():
                if not connectable(q) or not q.GetNumber().isdigit():continue
                x,y=xy(q.GetPosition());nn=q.GetNetname();idx=signal_layer(nn) or 2;hi=powerplanes[int(nn[2])] if re.fullmatch(r'/M[1-5]_3V3',nn) else p.In2_Cu if nn=='/GND' else ll[idx]
                a.via(x,y,nn,p.F_Cu,hi,.3,.1);m2escape[(f.GetReference(),q.GetNumber())]=(x,y);esc_layer[(f.GetReference(),q.GetNumber())]=idx
    for f in b.GetFootprints():
        for q in f.Pads():
            if q.GetAttribute()==p.PAD_ATTRIB_NPTH:
                pt=xy(q.GetPosition());add(1,allmask,-1,pt,pt,p.ToMM(q.GetDrillSize().x)/2+.125);continue
            if not q.IsOnCopperLayer():continue
            nn=q.GetNetname();code=q.GetNetCode() or -1;bb=q.GetBoundingBox();add(0,allmask if q.GetAttribute()==p.PAD_ATTRIB_NPTH else mask(q),code,xy(bb.GetOrigin()),xy(bb.GetEnd()),0)
            wanted=(not main or bool(re.match(r'/(M[1-5]|UP)_',nn)) or (f.GetReference() in [f'J{i}' for i in list(range(119,128))+list(range(219,228))]+['J303','J304'] and nn=='/GND'))
            if wanted and connectable(q):
                pt=xy(q.GetPosition());layer=0 if main or q.IsOnLayer(p.F_Cu) else 1
                # Filled/capped blind via-in-pad for new BGA and main cable signal launch pads.
                if main and (f.GetReference()=='U1' or (f.GetReference().startswith('J') and q.GetNumber() in ['P','N'])):
                    a.via(*pt,nn,p.In19_Cu,p.B_Cu);layer=1
                elif not main and (f.GetReference(),q.GetNumber()) not in m2escape and (nn=='/GND' or nn.endswith('_3V3') or signal_layer(nn) is not None):
                    front=q.IsOnLayer(p.F_Cu)
                    target=powerplanes[int(nn[2])] if re.fullmatch(r'/M[1-5]_3V3',nn) else p.In2_Cu if front and nn=='/GND' else p.In28_Cu if nn=='/GND' else ll[signal_layer(nn)]
                    a.via(*pt,nn,p.F_Cu if front else target,target if front else p.B_Cu,.3,.1);layer=signal_layer(nn) or 2
                if (f.GetReference(),q.GetNumber()) in m2escape:
                    if nn=='/GND' or nn.endswith('_3V3'):continue
                    pt=m2escape[(f.GetReference(),q.GetNumber())];layer=esc_layer[(f.GetReference(),q.GetNumber())]
                if not main and (nn=='/GND' or re.fullmatch(r'/M[1-5]_3V3',nn)):continue
                pads.append(dict(ref=f.GetReference(),pin=q.GetNumber(),net=nn,code=code,x=pt[0],y=pt[1],layer=layer,width=p.ToMM(min(q.GetSize().x,q.GetSize().y))))
    for t in b.GetTracks():
        if isinstance(t,p.PCB_VIA):add(1,mask(t),t.GetNetCode(),xy(t.GetPosition()),xy(t.GetPosition()),p.ToMM(t.GetWidth(p.B_Cu))/2)
        else:add(1,mask(t),t.GetNetCode(),xy(t.GetStart()),xy(t.GetEnd()),p.ToMM(t.GetWidth())/2)
    unique={}
    for q in pads:
        key=(q['ref'],q['pin'])
        if key not in unique or q['width']>unique[key]['width']:unique[key]=q
    pads=list(unique.values());groups=collections.defaultdict(list)
    for q in pads:groups[q['net']].append(q)
    tasks=[]
    def task(q,z=None,width=.125,mode=0):
        tasks.append(dict(q,tl=z['layer'] if z else q['layer'],tx=z['x'] if z else q['x'],ty=z['y'] if z else q['y'],w=width,mode=mode,target_ref=z['ref'] if z else '',target_pin=z['pin'] if z else ''))
    for nn,qs in groups.items():
        if nn=='/GND':
            # Surface pours join ground; one stitch per connector / IC / large capacitor also ties internal references.
            seen=set()
            for q in qs:
                if q['ref'] in seen or q['ref'].startswith('R'):continue
                seen.add(q['ref']);task(q,width=min(.2,q['width']-.08),mode=1)
            continue
        if not main and re.fullmatch(r'/M[1-5]_3V3',nn):
            for q in qs:task(q,width=min(.3,max(.15,q['width']-.1)),mode=1)
            continue
        if main and nn in ['/VIN_A','/VIN_B']:
            f=b.FindFootprintByReference('F1' if nn.endswith('A') else 'F2');p1=pad(f,1);x,y=xy(p1.GetPosition());qs.append(dict(ref=f.GetReference(),pin='1',net=nn,code=p1.GetNetCode(),x=x,y=y,layer=0,width=1))
        if len(qs)<2:continue
        done=[qs[0]];pending=qs[1:]
        while pending:
            z,q=min(((d,t) for d in done for t in pending),key=lambda pair:math.hypot(pair[0]['x']-pair[1]['x'],pair[0]['y']-pair[1]['y']))
            width=.125
            if nn.startswith(('/CABLE12','/VIN_')) or nn.endswith('_SW'):width=min(.45,max(.15,min(q['width'],z['width'])-.1))
            task(q,z,width);done.append(q);pending.remove(q)
    # High-current local connections first, then short control, data and finally plane stitching.
    tasks.sort(key=lambda t:(t['mode'],0 if t['net'].endswith('_SW') else 1 if t['net'].startswith('/CABLE12') else 2,math.hypot(t['x']-t['tx'],t['y']-t['ty'])))
    lines=[f'{round(w/.05)+1} {round(h/.05)+1} {len(ll)}',str(len(shapes))]+[' '.join(map(str,s)) for s in shapes]+[str(len(tasks))]
    for i,t in enumerate(tasks):
        t['id']=i;lines.append(f"{i} {t['mode']} {t['code']} {t['layer']} {t['x']} {t['y']} {t['tl']} {t['tx']} {t['ty']} {t['w']}")
    pre=R/'work/revJ'/name;pre.with_suffix('.input').write_text('\n'.join(lines));pre.with_suffix('.tasks.json').write_text(json.dumps(tasks,indent=2));pre.with_suffix('.layers.json').write_text(json.dumps(ll));p.SaveBoard(str(pre.with_suffix('.base.kicad_pcb')),b)
    with pre.with_suffix('.route.log').open('w') as log:r=subprocess.run([str(R/('work/revJ/router.exe' if main else 'work/revJ/router_inner.exe')),pre.with_suffix('.input').name,pre.with_suffix('.routes').name],cwd=pre.parent,stdout=log,stderr=log)
    succeeded=[]
    for row in pre.with_suffix('.routes').read_text().splitlines():
        z=list(map(int,row.split()));idx,count=z[:2];t=tasks[idx];pts=[(z[2+j*3],z[3+j*3]*.05,z[4+j*3]*.05) for j in range(count)];nn=t['net'];succeeded.append(idx)
        start=pts[0];end=pts[-1];a.track((t['x'],t['y']),start[1:],nn,ll[start[0]],t['w'])
        for aa,zz in zip(pts,pts[1:]):
            if aa[0]==zz[0]:a.track(aa[1:],zz[1:],nn,ll[aa[0]],t['w'])
            else:a.via(*aa[1:],nn,p.In19_Cu if main else p.F_Cu if 0 in [aa[0],zz[0]] else p.In2_Cu,p.B_Cu if main or 1 in [aa[0],zz[0]] else p.In24_Cu)
        if t['mode']:a.via(*end[1:],nn,p.In19_Cu if main else p.F_Cu,p.B_Cu)
        else:a.track(end[1:],(t['tx'],t['ty']),nn,ll[end[0]],t['w'])
    p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(bp),b);(folder/(name+'.kicad_pro')).write_bytes(pro)
    result=dict(tasks=len(tasks),routed=len(succeeded),failed=[t for t in tasks if t['id'] not in succeeded]);(folder/'ROUTING_STATUS.json').write_text(json.dumps(result,indent=2));print(name, len(succeeded),'/',len(tasks),flush=True)
for name in sys.argv[1:] or names:run(name)
