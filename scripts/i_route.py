from i_common import *
import sys,collections,subprocess
names=['Main_10E1S','Left_2M2_Vertical','Right_M2_Upstream']
def run(name):
    folder=ROOT/name;bp=folder/(name+'.kicad_pcb');pro=(folder/(name+'.kicad_pro')).read_bytes();placement=R/'work/revI'/f'{name}.placed.kicad_pcb'
    if not placement.exists():shutil.copy2(bp,placement)
    b=p.LoadBoard(str(placement));main=name.startswith('Main');w=80 if main else 52;h=45
    cs=json.loads((folder/'COMPONENTS.json').read_text());refs={c['ref'] for c in cs};ll=([p.B_Cu]+[getattr(p,f'In{i}_Cu') for i in [19,21,23,25,27,29]]) if main else [p.F_Cu,p.B_Cu]+[getattr(p,f'In{i}_Cu') for i in [2,4,6,8]]
    allmask=(1<<len(ll))-1;shapes=[];pads=[];a=object.__new__(Board);a.b=b;a.nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
    def add(kind,mask,net,start,end,r):
        if mask:shapes.append((kind,mask,net,*start,*end,r))
    def mask(obj):return sum(1<<i for i,l in enumerate(ll) if obj.IsOnLayer(l))
    def connectable(q):return q.GetNumber() and q.GetNetname() and not q.GetNetname().startswith('unconnected-')
    # Existing ground returns connect new reference layers. Add ground pours on daughter surfaces.
    if not main:
        for z in list(b.Zones()):remove(b,z)
        for i in [1,3,5,7,9]:a.zone('/GND',getattr(p,f'In{i}_Cu'),[(.4,.4),(w-.4,.4),(w-.4,44.6),(.4,44.6)])
        for l in [p.F_Cu,p.B_Cu]:a.zone('/GND',l,[(.4,.4),(w-.4,.4),(w-.4,44.6),(.4,44.6)])
        # Dedicated power plane, split only on the dual-slot board.
        for k,x0,x1 in ([(1,.4,25.6),(2,26.4,51.6)] if name.startswith('Left') else [(3,.4,51.6)]):a.zone(f'/M{k}_3V3',p.In10_Cu,[(x0,.4),(x1,.4),(x1,44.6),(x0,44.6)])
    # Escape the 0.5 mm M.2 rows before global routing. Alternate via distances
    # maintain via-to-via clearance, while keeping every signal's pad identity.
    m2escape={}
    if not main:
        for f in b.GetFootprints():
            if 'M2_MKey_VERTICAL' not in str(f.GetFPID().GetLibItemName()):continue
            for q in f.Pads():
                if not connectable(q) or not q.GetNumber().isdigit():continue
                n=int(q.GetNumber());x,y=xy(q.GetPosition());offset=(-1 if n%2 else 1)*(1.0 if (n//2)%2 else 1.7);z=(x+offset,y) if abs(f.GetOrientationDegrees()-90)<.01 else (x,y+offset);nn=q.GetNetname()
                a.track((x,y),z,nn,p.F_Cu,.2 if nn=='/GND' or nn.endswith('_3V3') else .125);a.via(*z,nn);m2escape[(f.GetReference(),q.GetNumber())]=z
    for f in b.GetFootprints():
        for q in f.Pads():
            if not q.IsOnCopperLayer():continue
            nn=q.GetNetname();code=q.GetNetCode() or -1;bb=q.GetBoundingBox();add(0,mask(q),code,xy(bb.GetOrigin()),xy(bb.GetEnd()),0)
            wanted=(not main or f.GetReference() in refs or (f.GetReference()=='U1' and nn.startswith(('/M','/UP'))))
            if wanted and connectable(q):
                pt=xy(q.GetPosition());layer=0 if main or q.IsOnLayer(p.F_Cu) else 1
                # Filled/capped blind via-in-pad for new BGA and main cable signal launch pads.
                if main and (f.GetReference()=='U1' or (f.GetReference().startswith('J') and q.GetNumber() in ['P','N'])):
                    a.via(*pt,nn,p.In19_Cu,p.B_Cu);layer=1
                elif not main and 'Twinax_' in str(f.GetFPID().GetLibItemName()) and q.GetNumber() in ['P','N']:
                    a.via(*pt,nn);layer=2
                if (f.GetReference(),q.GetNumber()) in m2escape:
                    if nn=='/GND' or nn.endswith('_3V3'):continue
                    pt=m2escape[(f.GetReference(),q.GetNumber())];layer=2
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
        if not main and re.fullmatch(r'/M[123]_3V3',nn):
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
    tasks.sort(key=lambda t:(t['mode'],0 if t['net'].endswith('_SW') else 1,math.hypot(t['x']-t['tx'],t['y']-t['ty'])))
    lines=[f'{round(w/.05)+1} {round(h/.05)+1} {len(ll)}',str(len(shapes))]+[' '.join(map(str,s)) for s in shapes]+[str(len(tasks))]
    for i,t in enumerate(tasks):
        t['id']=i;lines.append(f"{i} {t['mode']} {t['code']} {t['layer']} {t['x']} {t['y']} {t['tl']} {t['tx']} {t['ty']} {t['w']}")
    pre=R/'work/revI'/name;pre.with_suffix('.input').write_text('\n'.join(lines));pre.with_suffix('.tasks.json').write_text(json.dumps(tasks,indent=2));pre.with_suffix('.layers.json').write_text(json.dumps(ll));p.SaveBoard(str(pre.with_suffix('.base.kicad_pcb')),b)
    with pre.with_suffix('.route.log').open('w') as log:r=subprocess.run([str(R/'work/revI/router.exe'),str(pre.with_suffix('.input')),str(pre.with_suffix('.routes'))],stdout=log,stderr=log)
    succeeded=[]
    for row in pre.with_suffix('.routes').read_text().splitlines():
        z=list(map(int,row.split()));idx,count=z[:2];t=tasks[idx];pts=[(z[2+j*3],z[3+j*3]*.05,z[4+j*3]*.05) for j in range(count)];nn=t['net'];succeeded.append(idx)
        start=pts[0];end=pts[-1];a.track((t['x'],t['y']),start[1:],nn,ll[start[0]],t['w'])
        for aa,zz in zip(pts,pts[1:]):
            if aa[0]==zz[0]:a.track(aa[1:],zz[1:],nn,ll[aa[0]],t['w'])
            else:a.via(*aa[1:],nn,p.In19_Cu if main else p.F_Cu,p.B_Cu)
        if t['mode']:a.via(*end[1:],nn,p.In19_Cu if main else p.F_Cu,p.B_Cu)
        else:a.track(end[1:],(t['tx'],t['ty']),nn,ll[end[0]],t['w'])
    p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(bp),b);(folder/(name+'.kicad_pro')).write_bytes(pro)
    result=dict(tasks=len(tasks),routed=len(succeeded),failed=[t for t in tasks if t['id'] not in succeeded]);(folder/'ROUTING_STATUS.json').write_text(json.dumps(result,indent=2));print(name, len(succeeded),'/',len(tasks),flush=True)
for name in sys.argv[1:] or names:run(name)
