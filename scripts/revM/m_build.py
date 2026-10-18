"""One 110x45 carrier: 10 E1.S plus four upright M-Key draft sockets."""
from pathlib import Path
import sys,json,shutil,re,copy,math
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2')
sys.path.insert(0,str(R/'scripts/revJ'))
import i_common as c
from i_common import *
S=R/'outputs/PCIe_3board_RevL';O=R/'outputs/PCIe_Main_RevM';c.ROOT=O
O.mkdir(parents=True,exist_ok=True);folder=O/'Main_10E1S'
shutil.copytree(S/'Main_10E1S',folder,dirs_exist_ok=True)
shutil.copytree(S/'references',O/'references',dirs_exist_ok=True)
for fn in ['INTEL_268V_PINOUT.json','PEX88096_PINOUT.json','PEX88096_BALLS.csv','CPU_LINK_LENGTHS.json','CPU_PEX_LINK.json','CPU_POWER_DOMAINS.csv','CUSTOM_POWER_PINOUT.csv','USB_MOUNTING_STATUS.json']:
    shutil.copy2(S/fn,O/fn)
for fn in ['DRC.json','ERC.json','CONNECTIVITY.net','Main_10E1S.step','preview.png','bottom.png','PIN_MAP.csv']:
    f=folder/fn
    if f.exists():f.unlink()
bp=folder/'Main_10E1S.kicad_pcb';b=p.LoadBoard(str(bp));pro=(folder/'Main_10E1S.kicad_pro').read_bytes()
a=object.__new__(Board);a.name='Main_10E1S';a.w=110;a.h=45;a.b=b;a.folder=folder;a.lib=folder/'Local.pretty';a.models=folder/'models';a.plugin=p.PCB_IO_MGR.FindPlugin(p.PCB_IO_MGR.KICAD_SEXP)
a.nets={q.GetNetname():q for q in b.GetNetInfo().NetsByNetcode().values()};a.cs=[];a.newrefs=[]
meta={q['ref']:q for q in json.loads((folder/'COMPONENTS.json').read_text(encoding='utf-8'))}
removed=[]
for f in list(b.GetFootprints()):
    ref=f.GetReference()
    if 'Twinax_' in str(f.GetFPID().GetLibItemName()) or ref in ['J301','J302','J303','J304']:
        remove(b,f);meta.pop(ref,None);removed.append(ref)
assert len(removed)==58,len(removed)
for f in b.GetFootprints():
    for q in f.Pads():
        nn=q.GetNetname()
        if nn.startswith('/M5_') or nn.startswith('/UP_'):q.SetNet(a.net(c.nc(f.GetReference(),q.GetNumber())))
        elif nn=='/CABLE12_L':q.SetNet(a.net('/M2_12V_L'))
        elif nn=='/CABLE12_R':q.SetNet(a.net('/M2_12V_R'))
for g in list(b.GetDrawings()):
    if isinstance(g,p.PCB_TEXT):
        text=g.GetText()
        if any(s in text.upper() for s in ['TWINAX','THREE INDEPENDENT','CABLE','REV K','REV L']):remove(b,g)

# A no-peg concept is necessary over the switch's backside BGA. This is not
# represented as an orderable unmodified MDT350 connector land pattern.
srcdir=S/'Left_2M2_Vertical';source=p.LoadBoard(str(srcdir/'Left_2M2_Vertical.kicad_pcb'))
srcmeta={q['ref']:q for q in json.loads((srcdir/'COMPONENTS.json').read_text(encoding='utf-8'))}
oldname='Amphenol_MDT350M01001VT_MKey_Vertical_Gen4'
name='MKey_Vertical_Gen4_24p2x3p5_NoLocatingPegs_DRAFT'
uf=p.FootprintLoad(str(srcdir/'Local.pretty'),oldname);assert uf
for q in list(uf.Pads()):
    if q.GetAttribute()==p.PAD_ATTRIB_NPTH:remove(uf,q)
uf.SetFPID(p.LIB_ID('Local',name));uf.SetLibDescription('Custom no-locating-peg concept based on Amphenol CMDT350X0X001VT rev2. Four sockets share carrier with PEX BGA on reverse. Stock MDT350 locating pegs cannot be fitted here. Use a verified no-peg variant or a reviewed depopulated-peg part. Physical contact numbering / Gen4 channel remain unqualified.')
for m in uf.Models():
    path=Path(m.m_Filename.replace('${KIPRJMOD}',str(srcdir)));shutil.copy2(path,a.models/path.name)
a.savefoot(uf)
placements=[(1,3.6,23.3,'left outer'),(2,9.8,23.3,'left inner'),(3,100.2,23.3,'right inner'),(4,106.4,23.3,'right outer')]
ports=[];powergroups={};new_fixed=set()
for k,x,y,location in placements:
    port=f'M{k}';ref=f'J{500+k}'
    def rename(nn,oldref,newref):
        return nn.replace('/M1_',f'/{port}_').replace('/CABLE12','/M2_12V_L' if k<=2 else '/M2_12V_R').replace(f'({oldref}-',f'({newref}-')
    pm={pin:rename(nn,'J1',ref) for pin,nn in srcmeta['J1']['pinmap'].items()}
    a.place(ref,f'{port} SSD / VERTICAL M-Key 2280 / NO-PEG DRAFT',name,x,y,pm,'F',90,5.5)
    new_fixed.add(ref)
    lane_base={1:44,2:48,3:56,4:52}[k]
    ports.append({'port':port,'ref':ref,'location':location,'position_mm':[x,y],'rotation_deg':90,'side':'F','role':'NVMe SSD downstream x4','pex_lanes':list(range(lane_base,lane_base+4)),'rail':f'/{port}_3V3','design_output_budget_A':4,'no_locating_pegs_required':True,'physical_pin_numbering_verified':False,'pcie_gen4_channel_qualified':False})
    # Reuse known support topology but assign unique references on the carrier.
    refs={'U21':f'U{3000+k}','L1':f'L{3000+k}',**{f'C{101+i}':f'C{3000+(k-1)*10+i+1}' for i in range(6)},'R101':f'R{3000+(k-1)*10+1}','R102':f'R{3000+(k-1)*10+2}','R110':f'R{3000+(k-1)*10+3}','R111':f'R{3000+(k-1)*10+4}',**{f'C{120+i}':f'C{3050+(k-1)*10+i+1}' for i in range(8)}}
    powergroups[k]=[]
    for oldref,newref in refs.items():
        src=source.FindFootprintByReference(oldref);foot=str(src.GetFPID().GetLibItemName())
        for m in src.Models():
            path=Path(m.m_Filename.replace('${KIPRJMOD}',str(srcdir)))
            if path.exists():shutil.copy2(path,a.models/path.name)
        local=srcdir/'Local.pretty'/(foot+'.kicad_mod')
        if local.exists():shutil.copy2(local,a.lib/local.name)
        pm={pin:rename(nn,oldref,newref) for pin,nn in srcmeta[oldref]['pinmap'].items()}
        val=srcmeta[oldref]['value'];height=srcmeta[oldref].get('height_mm',.55)
        if oldref in ['C104','C105']:
            foot='C_0805_2012Metric';val='22uF 10V X5R / DC-bias review pending';height=1.45
        f=a.place(newref,val,foot,0,0,pm,'F',0,height)
        if oldref=='U21':
            a.cs[-1]['pin_names']={'1':'GND','2':'SW','3':'VIN','4':'VFB','5':'EN','6':'VBST'}
            a.cs[-1]['pin_types']={'1':'power_in','2':'output','3':'power_in','4':'input','5':'input','6':'output'}
            a.cs[-1]['datasheet']='https://www.ti.com/lit/ds/symlink/tps565201.pdf'
            a.cs[-1]['status']='12V to 3.3V 4A design budget, 5A IC; power-loop routing and thermal validation pending'
        if oldref.startswith('C12'):
            # AC capacitors in the narrow strips adjacent to the upright sockets.
            i=int(oldref[1:])-120;cx={1:6.7,2:12.9,3:97.1,4:103.3}[k]
            f.SetPosition(v(cx,13.5+i*2.2));f.SetOrientationDegrees(90);new_fixed.add(newref)
        elif oldref in ['R110','R111']:
            cx={1:6.7,2:12.9,3:97.1,4:103.3}[k];f.SetPosition(v(cx,31.5+(oldref=='R111')*2.2));f.SetOrientationDegrees(90);new_fixed.add(newref)
        else:powergroups[k].append(newref)
assert len({f.GetReference() for f in b.GetFootprints()})==len(list(b.GetFootprints())),'duplicate references'
for q in a.cs:meta[q['ref']]=q
for ref in ['J501','J502','J503','J504']:
    meta[ref].update(actual_orderable_part_verified=False,locating_pegs_removed_in_draft=True,physical_pin_numbering_verified=False)

# Pack each new converter together, then place the old input protection/buck
# components in remaining top-strip and end-wing space. Backside CPU geometry
# and its existing copper routes do not move.
old_front={'F1','F2','D1','D2','C1','C2','U30','U31','U41','U42','L31'}
old_front|={f'{letter}{i}' for letter,lo,hi in [('R',301,305),('C',301,301),('R',311,311),('C',311,315),('R',411,415),('R',421,425),('C',411,412),('C',421,422)] for i in range(lo,hi+1)}
for ref,x in [('F1',57.0),('F2',70.0)]:
    f=b.FindFootprintByReference(ref)
    if f.GetLayer()==p.F_Cu:f.Flip(f.GetPosition(),p.FLIP_DIRECTION_LEFT_RIGHT)
    f.SetOrientationDegrees(0);f.SetPosition(v(x,4));old_front.remove(ref)
movable=old_front|{r for refs in powergroups.values() for r in refs}
def bounds(f):
    bb=f.GetBoundingBox(False,False);return tuple(p.ToMM(z) for z in [bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom()])
step=.1;occ=[0]*451
def raster(bb):
    x0,y0,x1,y1=bb
    return max(0,math.floor((x0-.06)/step)),max(0,math.floor((y0-.06)/step)),min(1100,math.ceil((x1+.06)/step)),min(450,math.ceil((y1+.06)/step))
def reserve(bb):
    x0,y0,x1,y1=raster(bb);mask=((1<<(x1-x0+1))-1)<<x0
    for y in range(y0,y1+1):occ[y]|=mask
def free(bb):
    x0,y0,x1,y1=raster(bb);mask=((1<<(x1-x0+1))-1)<<x0
    return not any(occ[y]&mask for y in range(y0,y1+1))
for f in b.GetFootprints():
    if f.GetLayer()==p.F_Cu and f.GetReference() not in movable:reserve(bounds(f))
    if f.GetLayer()==p.B_Cu:
        for q in f.Pads():
            if q.GetAttribute() in [p.PAD_ATTRIB_NPTH,p.PAD_ATTRIB_PTH]:
                xx,yy=xy(q.GetPosition());rr=max(p.ToMM(q.GetDrillSize().x),p.ToMM(q.GetDrillSize().y))/2+.35;reserve((xx-rr,yy-rr,xx+rr,yy+rr))
def pack(refs,regions):
    fs=[b.FindFootprintByReference(r) for r in refs]
    fs.sort(key=lambda f:-(bounds(f)[2]-bounds(f)[0])*(bounds(f)[3]-bounds(f)[1]))
    for f in fs:
        f.SetPosition(v(0,0));found=None
        for rot in [0,90]:
            f.SetOrientationDegrees(rot);bb=bounds(f);ww=bb[2]-bb[0];hh=bb[3]-bb[1]
            for x0,y0,x1,y1 in regions:
                for iy in range(math.ceil(y0/step),math.floor((y1-hh)/step)+1,2):
                    yy=iy*step
                    for ix in range(math.ceil(x0/step),math.floor((x1-ww)/step)+1,2):
                        xx=ix*step;trial=(xx,yy,xx+ww,yy+hh)
                        if free(trial):found=(xx-bb[0],yy-bb[1],trial);break
                    if found:break
                if found:break
            if found:break
        assert found,('cannot pack',f.GetReference(),ww,hh)
        f.SetPosition(v(*found[:2]));reserve(found[2])
for k in range(1,5):
    x0,x1=(.8,15.6) if k<=2 else (94.4,109.2)
    if k==1:x1=28.4
    if k==3:x0=81.6
    y0,y1=(.8,9.4) if k in [1,3] else (35.8,44.2)
    pack(powergroups[k],[(x0,y0,x1,y1)])
pack(old_front,[(.8,.8,109.2,9.4),(.8,10,14.8,44.2),(95.2,10,109.2,44.2),(15,35.8,95,44.2)])
# Repack only unrouted backside support parts around the two moved fuses.
# The BGA packages, all routed CPU-link capacitor endpoints and clocks stay put.
occ=[0]*451
fixed_b={'U1','U502','U501','J401','J402','U601','U602','F1','F2','U701','Y701','Y702','U702','C703','C704','C705','C706'}|{f'C{i}' for i in list(range(801,809))+list(range(811,819))}
back_moving=[]
for f in b.GetFootprints():
    if f.GetLayer()==p.B_Cu:
        if f.GetReference() in fixed_b:reserve(bounds(f))
        else:back_moving.append(f.GetReference())
pack(back_moving,[(50.5,37.0,78.5,44.2),(50.5,.8,78.5,8.4),(78.8,.8,93,44.2),(41.8,8.6,50.5,36.3),(89,30.2,109.2,44.2),(93,11.5,109.2,16.0),(.5,.8,3.3,44.2),(107,.8,109.4,44.2)])
for f in b.GetFootprints():
    e=meta[f.GetReference()];e.update(x=xy(f.GetPosition())[0],y=xy(f.GetPosition())[1],side='B' if f.GetLayer()==p.B_Cu else 'F',rotation_deg=f.GetOrientationDegrees(),pinmap={q.GetNumber():q.GetNetname() for q in f.Pads() if q.GetNumber()},value=f.GetValue(),footprint=str(f.GetFPID().GetLibItemName()))
(folder/'COMPONENTS.json').write_text(json.dumps(list(meta.values()),ensure_ascii=False,indent=2),encoding='utf-8')
p.SaveBoard(str(bp),b);(folder/'Main_10E1S.kicad_pro').write_bytes(pro)
(O/'M2_PORTS.json').write_text(json.dumps(ports,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'BUILD.json').write_text(json.dumps({'revision':'M','main_mm':[110,45],'daughter_boards':0,'cable_connections':0,'e1s_slots':10,'e1s_pitch_mm':8,'m2_slots':4,'m2_each_side':2,'m2_pitch_mm':6.2,'m2_orientation':'vertical; all F side; parallel to E1.S','m2_power':'four independent TPS565201 12V to 3.3V stages; 4A design budget per socket','removed_cable_footprints':removed,'cpu_bga_balls':2833,'pex_bga_balls':1550,'cpu_pmic_implemented':False,'main_routing_complete':False,'production_ready':False},ensure_ascii=False,indent=2),encoding='utf-8')
(folder/'ROUTING_STATUS.json').write_text(json.dumps({'cpu_x4_and_refclock_copper_connections':34,'m2_net_assignments_complete':True,'m2_copper_routing_complete':False,'power_loop_routing_complete':False,'whole_board_state':'partial CPU link routing; most power/support/downstream nets remain unrouted','length_tuning_complete':False,'impedance_validated':False,'blind_via_stackup_validated':False,'production_ready':False},indent=2),encoding='utf-8')
print('One main board; 10 E1.S + 4 vertical no-peg M.2 concepts, four 3.3V regulators; all daughter cable pads removed.',flush=True)
