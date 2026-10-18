"""82 x 45 mm E1.S-only carrier. Repack the retained platform components."""
from pathlib import Path
base=Path(__file__).resolve().parent.parent
src=(base/'revQ/q_build.py').read_text(encoding='utf-8').replace('PCIe_E1S_Only_RevQ','PCIe_E1S_82x45_RevR').replace("'revision':'Q'","'revision':'R'")
exec(compile(src,str(__file__)+' removal','exec'))
for t in list(b.GetTracks()):remove(b,t)
for z in list(b.Zones()):remove(b,z)
for g in list(b.GetDrawings()):
    if g.GetLayer()==p.Edge_Cuts:remove(b,g)
rect(b,0,0,82,45,p.Edge_Cuts)
# Retain the 220 nF / 16 V coupling values while using real 0201 lands in
# the narrow channel between the two BGA packages.
a.folder=folder;a.lib=folder/'Local.pretty';a.models=folder/'models';a.plugin=p.PCB_IO_MGR.FindPlugin(p.PCB_IO_MGR.KICAD_SEXP)
compact=a.std('Capacitor_SMD','C_0201_0603Metric')
for ref in [f'C{i}' for i in list(range(801,809))+list(range(811,819))]:
    old=b.FindFootprintByReference(ref);new=p.FootprintLoad(str(a.lib),compact);b.Add(new);new.SetFPID(p.LIB_ID('Local',compact));new.SetReference(ref);new.SetValue('220nF 16V / GRM033R61C224KE14D');new.Reference().SetVisible(False);new.Value().SetVisible(False)
    for q in new.Pads():
        if q.GetNumber():q.SetNet(a.net(meta[ref]['pinmap'][q.GetNumber()]))
    remove(b,old);meta[ref].update(footprint=compact,value=new.GetValue(),height_mm=.33,datasheet='https://www.murata.com/-/media/webrenewal/tool/library/common-pdf/dynamic-model/component-list-d-mlcc-2504.ashx?cvid=20250523010405000000&la=en')
fixed={}
def put(ref,x,y,angle=None,side=None):
    f=b.FindFootprintByReference(ref);assert f,ref
    if side is not None and (f.GetLayer()==p.B_Cu)!=(side=='B'):f.Flip(f.GetPosition(),p.FLIP_DIRECTION_LEFT_RIGHT)
    if angle is not None:f.SetOrientationDegrees(angle)
    f.SetPosition(v(x,y));fixed[ref]={'position_mm':[x,y],'rotation_deg':f.GetOrientationDegrees(),'layer':f.GetLayer()}
for k in range(1,11):put(f'J{k}',5+8*(k-1),23.5,90,'F')
for ref,x,y,ang in [('U1',20,22.5,0),('U502',54.5,22.5,270),('J401',78,6,90),('J402',73,6,90),('U501',75.1,23,180),('U601',44.4,4.6,0),('U602',53.1,4.6,0),('U701',62.4,4.6,0),('Y701',52.5,40.6,0),('Y702',58,40.6,0),('U702',65.1,40.6,0),('C703',49.1,43.4,0),('C704',53,43.4,0),('C705',58,43.4,0),('C706',65.1,43.4,0)]:put(ref,x,y,ang,'B')
for i in range(8):
    lane,j=divmod(i,2)
    put(f'C{801+i}',39.85,30.2-2.4*lane+(j-.5)*1.2,180,'B')
    put(f'C{811+i}',39.85,18-2.4*lane+(j-.5)*1.2,0,'B')
for ref,x,y in [('J11',20,4),('J12',61,4),('F1',20,40.4),('F2',61,40.4)]:put(ref,x,y,0,'F')

def bounds(f):
    bb=f.GetBoundingBox(False,False);return tuple(p.ToMM(z) for z in [bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom()])
step=.05;margin=.015;nx=1641;ny=901;occ={'F':[0]*ny,'B':[0]*ny};allbits=(1<<nx)-1
def raster(bb):
    x0,y0,x1,y1=bb
    return max(0,math.floor((x0-margin)/step)),max(0,math.floor((y0-margin)/step)),min(nx-1,math.ceil((x1+margin)/step)),min(ny-1,math.ceil((y1+margin)/step))
def reserve(bb,side):
    x0,y0,x1,y1=raster(bb);mask=((1<<(x1-x0+1))-1)<<x0
    for yy in range(y0,y1+1):occ[side][yy]|=mask
def free(bb,side):
    x0,y0,x1,y1=raster(bb);mask=((1<<(x1-x0+1))-1)<<x0
    return not any(occ[side][yy]&mask for yy in range(y0,y1+1))
for f in b.GetFootprints():
    if f.GetReference() not in fixed:continue
    side='B' if f.GetLayer()==p.B_Cu else 'F';reserve(bounds(f),side)
    for q in f.Pads():
        if q.GetAttribute() in [p.PAD_ATTRIB_NPTH,p.PAD_ATTRIB_PTH]:
            xx,yy=xy(q.GetPosition());rr=max(xy(q.GetDrillSize()))/2+.35;reserve((xx-rr,yy-rr,xx+rr,yy+rr),'F' if side=='B' else 'B')
regions={'F':[(.6,.6,81.4,10.7),(.6,36.2,81.4,44.4),(.6,.6,81.4,44.4)],'B':[(68.2,30.1,81.4,44.4),(68.2,11.3,81.4,15.8),(40,.6,69.9,8.2),(40,36.8,69.9,44.4),(.6,.6,81.4,44.4)]}
def pack(refs,sides):
    fs=[b.FindFootprintByReference(r) for r in refs];fs.sort(key=lambda f:-(bounds(f)[2]-bounds(f)[0])*(bounds(f)[3]-bounds(f)[1]))
    for f in fs:
        f.SetPosition(v(0,0));found=None
        for side in sides:
            if (f.GetLayer()==p.B_Cu)!=(side=='B'):f.Flip(v(0,0),p.FLIP_DIRECTION_LEFT_RIGHT)
            for rot in [0,90]:
                f.SetOrientationDegrees(rot);bb=bounds(f);ww=bb[2]-bb[0];hh=bb[3]-bb[1]
                for x0,y0,x1,y1 in regions[side]:
                    first=math.ceil(x0/step);last=math.floor((x1-ww)/step)
                    if last<first:continue
                    allowed=((1<<(last-first+1))-1)<<(first-1);width=math.ceil((ww+margin)/step)+2
                    for iy in range(math.ceil(y0/step),math.floor((y1-hh)/step)+1):
                        blocked=0
                        for row in occ[side][max(0,iy-1):min(ny-1,iy+math.ceil((hh+margin)/step))+1]:blocked|=row
                        starts=(~blocked)&allbits;span=1
                        while span*2<=width:starts&=starts>>span;span*=2
                        if width>span:starts&=starts>>(width-span)
                        candidates=starts&allowed
                        while candidates:
                            bit=candidates&-candidates;xx=bit.bit_length()*step;yy=iy*step;trial=(xx,yy,xx+ww,yy+hh)
                            if free(trial,side):found=(xx-bb[0],yy-bb[1],trial,side);break
                            candidates^=bit
                        if found:break
                    if found:break
                if found:break
            if found:break
        assert found,('cannot pack',f.GetReference(),ww,hh)
        f.SetPosition(v(*found[:2]));reserve(found[2],found[3])
    print('Repacked',len(refs),'components;',sides,flush=True)
front=[f.GetReference() for f in b.GetFootprints() if f.GetReference() not in fixed and f.GetLayer()==p.F_Cu]
back=[f.GetReference() for f in b.GetFootprints() if f.GetReference() not in fixed and f.GetLayer()==p.B_Cu]
pack(front,['F','B']);pack(back,['B','F'])
for f in b.GetFootprints():
    e=meta[f.GetReference()];e.update(x=xy(f.GetPosition())[0],y=xy(f.GetPosition())[1],side='B' if f.GetLayer()==p.B_Cu else 'F',rotation_deg=f.GetOrientationDegrees(),pinmap={q.GetNumber():q.GetNetname() for q in f.Pads() if q.GetNumber()})
    x0,y0,x1,y1=bounds(f);assert x0>=0 and y0>=0 and x1<=82 and y1<=45,(f.GetReference(),bounds(f))
title=b.GetTitleBlock();title.SetTitle('82 x 45 mm / 10 E1.S / no M.2 or daughterboards');title.SetRevision('R')
p.SaveBoard(str(bp),b)
(folder/'COMPONENTS.json').write_text(json.dumps(list(meta.values()),ensure_ascii=False,indent=2),encoding='utf-8')
(O/'SOURCE_110mm_PLACEMENTS.json').write_bytes((O/'GEOMETRY_BASELINE.json').read_bytes());(O/'GEOMETRY_BASELINE.json').unlink()
(O/'PLACEMENT_PLAN.json').write_text(json.dumps(fixed,indent=2),encoding='utf-8')
ports=json.loads((O/'E1S_PORTS.json').read_text(encoding='utf-8'))
for row in ports:row['position_mm']=[5+8*(int(row['ref'][1:])-1),23.5]
(O/'E1S_PORTS.json').write_text(json.dumps(ports,indent=2),encoding='utf-8')
build=json.loads((O/'BUILD.json').read_text(encoding='utf-8'));build.pop('retained_footprint_positions',None);build.update(revision='R',main_mm=[82,45],retained_footprints_count=277,geometry_repacked=True,cpu_link_rerouting_required=True)
(O/'BUILD.json').write_text(json.dumps(build,indent=2),encoding='utf-8')
print('82 x 45 mm: 10 E1.S at 8mm pitch, zero M.2, zero daughterboards; platform repacked.',flush=True)
