from i_common import *
import csv,copy
OLD=R/'outputs/PCIe_3board_RevI'
names=['Main_10E1S','Left_2M2_Vertical','Right_M2_Upstream']
def adopt(name):
    a=object.__new__(Board);a.name=name;a.w=80 if name.startswith('Main') else 52;a.h=45
    a.folder=ROOT/name;a.lib=a.folder/'Local.pretty';a.models=a.folder/'models'
    source=OLD/name/(name+'.kicad_pcb') if name.startswith('Main') else R/'work/revI'/f'{name}.placed.kicad_pcb'
    if not source.exists():source=R/'work/revI'/f'{name}.base.kicad_pcb'
    a.b=p.LoadBoard(str(source));assert a.b,source
    if name.startswith('Main'):
        for t in list(a.b.GetTracks()):
            if re.match(r'/(M[1-5]|UP)_',t.GetNetname()):remove(a.b,t)
    a.nets={n.GetNetname():n for n in a.b.GetNetInfo().NetsByNetcode().values()}
    a.cs=json.loads((OLD/name/'COMPONENTS.json').read_text());a.newrefs=[];a.root=uid()
    a.pro=json.loads((OLD/name/(name+'.kicad_pro')).read_text())
    a.plugin=p.PCB_IO_MGR.FindPlugin(p.PCB_IO_MGR.KICAD_SEXP)
    return a
def update_cs(a):
    byref={c['ref']:c for c in a.cs}
    for f in a.b.GetFootprints():
        c=byref.get(f.GetReference())
        if c is not None:
            c.update(value=f.GetValue(),x=xy(f.GetPosition())[0],y=xy(f.GetPosition())[1],rotation_deg=f.GetOrientationDegrees(),footprint=str(f.GetFPID().GetLibItemName()),pinmap={q.GetNumber():q.GetNetname() for q in f.Pads() if q.GetNumber()})
def replace_control(a,ref,x,y,ports):
    old=a.b.FindFootprintByReference(ref);remove(a.b,old);a.cs=[c for c in a.cs if c['ref']!=ref]
    a.custom('Control_12_Wire',[(str(i+1),(i-5.5)*.9,0,.5,1.2) for i in range(12)],11.4,1.2)
    nn=[f'/{po}_{sig}' for po in ports for sig in ['PERST','CLKREQ','WAKE']]+['/GND']*3
    a.place(ref,'Three x4 port control / 12-wire','Control_12_Wire',x,y,{str(i+1):s for i,s in enumerate(nn)},'B')
def clone_slot(a,template,k,x):
    refs=['J2','U22','L2']+[f'C{n}' for n in list(range(201,207))+list(range(220,228))]+['R201','R202','R210','R211']
    oldmeta={c['ref']:c for c in template.cs}
    for ref in refs:
        src=template.b.FindFootprintByReference(ref);f=p.Cast_to_FOOTPRINT(src.Duplicate(False))
        n=int(ref[1:]);nr=f'J{k}' if ref=='J2' else f'U{20+k}' if ref=='U22' else f'L{k}' if ref=='L2' else ref[0]+str(n+(k-2)*100)
        a.b.Add(f);f.Move(v(x-38,0));f.SetReference(nr)
        for q in f.Pads():q.SetNet(a.net(q.GetNetname().replace('/M2_',f'/M{k}_').replace('(J2-',f'(J{k}-')))
        c=copy.deepcopy(oldmeta[ref]);c['ref']=nr;a.cs.append(c)
        if ref=='J2':f.SetValue(f'M{k} M-Key 2280 VERTICAL / LAND DRAFT')
    a.text(f'M{k} / 2280 VERTICAL',x,3.5,size=.6)

def move_slot(a,k,dx):
    refs=[f'J{k}',f'U{20+k}',f'L{k}']+[f'C{k*100+n}' for n in list(range(1,7))+list(range(20,28))]+[f'R{k*100+n}' for n in [1,2,10,11]]
    for ref in refs:a.b.FindFootprintByReference(ref).Move(v(dx,0))
def shift_buck(a,k,dx):
    refs=[f'U{20+k}',f'L{k}']+[f'C{k*100+n}' for n in range(1,7)]+[f'R{k*100+n}' for n in [1,2]]
    for ref in refs:a.b.FindFootprintByReference(ref).Move(v(dx,0))
main,left,right=[adopt(n) for n in names]
template=adopt('Left_2M2_Vertical')
move_slot(left,1,-4);move_slot(left,2,-12);move_slot(right,3,-4)
clone_slot(left,template,4,42)
clone_slot(right,template,5,26)
for k in [1,2,4]:shift_buck(left,k,-2)
for k in [3,5]:shift_buck(right,k,2)
# Shift the upstream socket and its associated AC capacitors to the third position.
for ref in ['J4']+[f'C{420+i}' for i in range(8)]:right.b.FindFootprintByReference(ref).Move(v(4,0))
for a in [left,right]:
    for g in list(a.b.GetDrawings()):
        if g.GetLayer()==p.Edge_Cuts:remove(a.b,g)
        elif isinstance(g,p.PCB_TEXT):
            if 'UPLINK / HOST' in g.GetText():g.SetPosition(v(42,32))
            elif g.GetText().startswith('VERTICAL M-KEY'):g.SetPosition(v(26,1.1))
            elif '12V IN' in g.GetText():g.SetText('12V / 3.3V SSD / 3 x4 PORTS');g.SetPosition(v(26,43.5))
            elif g.GetText().startswith('M1 /'):g.SetPosition(v(10,3.5))
            elif g.GetText().startswith('M2 /'):g.SetPosition(v(26,3.5))
            elif g.GetText().startswith('M3 /'):g.SetPosition(v(10,3.5))
    rect(a.b,0,0,52,45,p.Edge_Cuts)
# Preserve all old pair assignments. Add a third x4 bundle on each side.
pairmap=list(csv.DictReader((OLD/'TWINAX_MAP.csv').open(encoding='utf-8-sig')))
for row in pairmap:row['index']=int(row['index'])
for side,port in [('L','M4'),('R','M5')]:
    for i,function in enumerate([f'{d}{lane}' for lane in range(4) for d in ['TX','RX']]+['CLK']):
        idx=18+i
        pairmap.append(dict(side=side,index=idx,port=port,function=function,netP=f'/{port}_{function}_P',netN=f'/{port}_{function}_N',direction='remote to switch' if function.startswith('RX') else 'switch to remote',main_ref=f'J{101+idx if side=="L" else 201+idx}',daughter_ref=f'J{101+idx}'))
for row in pairmap:
    side=row['side'];idx=row['index'];d=left if side=='L' else right
    if idx<18:
        continue
    y=13.5+(idx-18)*3.1
    for a,ref,x in [(main,row['main_ref'],3.75 if side=='L' else 76.25),(d,row['daughter_ref'],48.1 if side=='L' else 3.9)]:
        a.place(ref,f'{row["port"]} {row["function"]}','Twinax_85R_Solder_DRAFT',x,y,{'P':row['netP'],'N':row['netN'],'G':'/GND'},'B')
replace_control(main,'J303',10,43,['M1','M2','M4'])
replace_control(main,'J304',70,43,['M3','UP','M5'])
replace_control(left,'J51',23,4,['M1','M2','M4'])
replace_control(right,'J51',28,4,['M3','UP','M5'])
# Route the additional 42 signals through previously unused fictional BGA balls.
bg=main.b.FindFootprintByReference('U1');bg.SetValue('FICTIONAL_BGA400_64lane');bg.SetFPID(p.LIB_ID('Local','FICTIONAL_BGA400_64lane'))
extra=[nn for row in pairmap if row['index']>=18 for nn in [row['netP'],row['netN']]]+[f'/{port}_{s}' for port in ['M4','M5'] for s in ['PERST','CLKREQ','WAKE']]
spare=[q for q in bg.Pads() if q.GetNetname().startswith('unconnected-') and 34<=xy(q.GetPosition())[0]<=46 and 16<=xy(q.GetPosition())[1]<=29]
assert len(spare)>=len(extra),(len(spare),len(extra))
for q,nn in zip(spare,extra):q.SetNet(main.net(nn))
# 3334/R_ILM gives nominal limit. Left supports three 13.2 W SSD design loads;
# right supports two. 665 ohm ~5.0 A, 1.10 kohm ~3.0 A; thermal rating unverified.
main.b.FindFootprintByReference('R415').SetValue('665R 1% / ILIM 5.0A')
main.b.FindFootprintByReference('J301').SetValue('12V protected / GND / 5A design target')
left.b.FindFootprintByReference('J50').SetValue('12V protected / GND / 5A design target')
for g in main.b.GetDrawings():
    if isinstance(g,p.PCB_TEXT):
        s=g.GetText().replace('REV I / 56 LANES','REV J / 64 LANES').replace('L: 2x M.2 x4','L: 3x M.2 x4').replace('R: M.2 + UP x4','R: 2x M.2 + UP x4')
        g.SetText(s)
from j_narrow import narrow,main_launches
narrow(left,[1,2,4],True);narrow(right,[3,5,4],False);main_launches(main)
for a in [main,left,right]:update_cs(a);a.save()
pairmap.sort(key=lambda q:(q['side'],q['index']))
with (ROOT/'TWINAX_MAP.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(pairmap[0]));w.writeheader();w.writerows(pairmap)
build=json.loads((ROOT/'BUILD.json').read_text());build.update(revision='J',left_mm=[52,45],right_mm=[52,45],m2_center_pitch_mm=16,pcie_lanes=64,lanes_per_side=12,links_per_side='3 independent x4 links; not a bonded x12 link',data_pairs_per_cable=24,clock_pairs_per_cable=3,ssd_count=5,route_status='placement complete; routing pending',left_current_limit_target_A=5.0,right_current_limit_target_A=3.0)
build.update(left_mm=[19.5,45],right_mm=[19.5,45],daughter_layers=16,m2_center_pitch_mm=6.2,m2_connector='Amphenol MDT350M01001VT',m2_connector_limit='PCIe Gen4 / 16 GT/s; channel NOT qualified',m2_body_mm=[24.2,3.5,5.5],m2_land_geometry_source='CMDT350X0X001VT rev 2',m2_pin_numbering_verified=False)
(ROOT/'BUILD.json').write_text(json.dumps(build,indent=2))
print('Rev J: five SSD sockets + one M.2 upstream, 27 twinax pairs per side, 64 fictional switch lanes',flush=True)
