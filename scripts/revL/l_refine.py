from pathlib import Path
import sys,json,math,re
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2')
sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
O=R/'outputs/PCIe_3board_RevL';folder=O/'Main_10E1S';bp=folder/'Main_10E1S.kicad_pcb'
b=p.LoadBoard(str(bp));pro=(folder/'Main_10E1S.kicad_pro').read_bytes()
meta={q['ref']:q for q in json.loads((folder/'COMPONENTS.json').read_text(encoding='utf-8'))}
nets={q.GetNetname():q for q in b.GetNetInfo().NetsByNetcode().values()}
def net(s):
    if s not in nets:nets[s]=p.NETINFO_ITEM(b,s);b.Add(nets[s])
    return nets[s]
fixed={'U1','U502','U501','J401','J402','U601','U602'}|{f'C{i}' for i in list(range(801,809))+list(range(811,819))}
b.FindFootprintByReference('U1').SetOrientationDegrees(0)
b.FindFootprintByReference('U502').SetOrientationDegrees(270)
for i in range(8):
    b.FindFootprintByReference(f'C{801+i}').SetOrientationDegrees(180)
    b.FindFootprintByReference(f'C{811+i}').SetOrientationDegrees(0)
anchors={'U701':(82.5,30.5),'Y701':(73.6,38.25),'Y702':(77.8,38.25),'U702':(83.0,39.8),
         'C703':(71.0,40.5),'C704':(75.0,40.5),'C705':(77.1,40.5),'C706':(79.3,40.5)}
for ref,pt in anchors.items():
    ff=b.FindFootprintByReference(ref);ff.SetOrientationDegrees(0);ff.SetPosition(v(*pt));fixed.add(ref)
for lane in range(4):
    for j in range(2):b.FindFootprintByReference(f'C{811+lane*2+j}').SetPosition(v(43.1,18-lane*2.4+(j-.5)*1.2))
for ff in b.GetFootprints():
    if ff.GetReference() in ['U601','U602']:
        for pp in ff.Pads():
            m=re.fullmatch(r'/(S\d\d)_REFCLK_([PN])',pp.GetNetname())
            if m:pp.SetNet(net('/'+m[1]+'_REFCLK0_'+m[2]))
    if ff.GetReference()=='U702':meta['U702']['pin_types']={'1':'power_in','2':'power_in','3':'input','4':'no_connect','5':'power_out'}

# Put the original input/buck power stages in the two free front-side wings.
# This also separates their switching loops from the CPU's clock components.
front_refs={'F1','F2','D1','D2','C1','C2','U30','U31','U41','U42','L31'}
front_refs|={f'{letter}{i}' for letter,lo,hi in [('R',301,305),('C',301,301),('R',311,311),('C',311,315),('R',411,415),('R',421,425),('C',411,412),('C',421,422)] for i in range(lo,hi+1)}
for ff in b.GetFootprints():
    if ff.GetReference() in front_refs and ff.GetLayer()==p.B_Cu:ff.Flip(ff.GetPosition(),p.FLIP_DIRECTION_LEFT_RIGHT)

# Conservative rectangle occupancy accelerates repacking the small components.
def bounds(ff):
    bb=ff.GetBoundingBox(False,False);return tuple(p.ToMM(z) for z in [bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom()])
step=.1;occ={'B':[0]*451,'F':[0]*451}
def raster(bb):
    x0,y0,x1,y1=bb
    return max(0,math.floor((x0-.05)/step)),max(0,math.floor((y0-.05)/step)),min(1100,math.ceil((x1+.05)/step)),min(450,math.ceil((y1+.05)/step))
def reserve(bb,side):
    x0,y0,x1,y1=raster(bb);mask=((1<<(x1-x0+1))-1)<<x0
    for y in range(y0,y1+1):occ[side][y]|=mask
def free(bb,side):
    x0,y0,x1,y1=raster(bb);mask=((1<<(x1-x0+1))-1)<<x0
    return not any(occ[side][y]&mask for y in range(y0,y1+1))
movable=[f for f in b.GetFootprints() if (f.GetLayer()==p.B_Cu or f.GetReference() in front_refs) and f.GetReference() not in fixed and not re.fullmatch(r'J[12]\d\d',f.GetReference())]
mrefs={f.GetReference() for f in movable}
for ff in b.GetFootprints():
    if ff.GetReference() not in mrefs:
        side='B' if ff.GetLayer()==p.B_Cu else 'F';reserve(bounds(ff),side)
        if any(pp.GetAttribute() in [p.PAD_ATTRIB_PTH,p.PAD_ATTRIB_NPTH] for pp in ff.Pads()):reserve(bounds(ff),'F' if side=='B' else 'B')
regions={'B':[(51.3,37.0,78,44.2),(51.3,.8,78,8.0),(79.0,.8,89,44.2),(89,30.2,107.2,44.2),(42.0,9.0,50.7,35.5),(88.0,11.3,107.2,16.0)],'F':[(2.6,.8,13.5,44.2),(97.0,.8,107.2,44.2)]}
movable.sort(key=lambda f:-(bounds(f)[2]-bounds(f)[0])*(bounds(f)[3]-bounds(f)[1]))
for ff in movable:
    ff.SetPosition(v(0,0));found=None;side='B' if ff.GetLayer()==p.B_Cu else 'F'
    for rot in [0,90]:
        if rot:ff.SetOrientationDegrees(ff.GetOrientationDegrees()+90)
        bb=bounds(ff);ww=bb[2]-bb[0];hh=bb[3]-bb[1]
        for x0,y0,x1,y1 in regions[side]:
            for iy in range(math.ceil(y0/step),math.floor((y1-hh)/step)+1,2):
                yy=iy*step
                for ix in range(math.ceil(x0/step),math.floor((x1-ww)/step)+1,2):
                    xx=ix*step;trial=(xx,yy,xx+ww,yy+hh)
                    if free(trial,side):found=(xx-bb[0],yy-bb[1],trial);break
                if found:break
            if found:break
        if found:break
    assert found,('cannot pack',ff.GetReference(),ww,hh)
    ff.SetPosition(v(*found[:2]));reserve(found[2],side)
for ff in b.GetFootprints():
    e=meta[ff.GetReference()];e.update(x=xy(ff.GetPosition())[0],y=xy(ff.GetPosition())[1],side='B' if ff.GetLayer()==p.B_Cu else 'F',rotation_deg=ff.GetOrientationDegrees(),pinmap={q.GetNumber():q.GetNetname() for q in ff.Pads() if q.GetNumber()})
(folder/'COMPONENTS.json').write_text(json.dumps(list(meta.values()),ensure_ascii=False,indent=2),encoding='utf-8')
p.SaveBoard(str(bp),b);(folder/'Main_10E1S.kicad_pro').write_bytes(pro)
print('Refined crystal/flash positions and E1.S REFCLK0 clock connections.',flush=True)
