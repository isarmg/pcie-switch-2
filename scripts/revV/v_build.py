"""Rev V: verifiable SSD / auxiliary power. CPU VR and fictional switch stay pending."""
from pathlib import Path
from collections import defaultdict
import sys,json,math,shutil,re
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');SRC=R/'outputs/PCIe_E1S_96x45_12slot_RevU';O=R/'outputs/PCIe_E1S_96x45_12VPower_RevV';F=O/'Main_12E1S';W=R/'work/revV';W.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
assert not O.exists(), 'Keep existing Rev V; do not overwrite work'
shutil.copytree(SRC,O,ignore=shutil.ignore_patterns('*.lck','*.kicad_prl','*-backups','*.zip','SHA256SUMS.txt','DRC.json','ERC.json','*.step','preview.png','bottom.png','CONNECTIVITY.net','VALIDATION.json','STEP_VALIDATION.json'))
# Restore portable component models (ignore above excluded STEP files recursively).
shutil.copytree(SRC/'Main_12E1S/models',F/'models',dirs_exist_ok=True)
b=p.LoadBoard(str(F/'Main_12E1S.kicad_pcb'));meta={q['ref']:q for q in json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'))}
a=object.__new__(Board);a.b=b;a.folder=F;a.lib=F/'Local.pretty';a.models=F/'models';a.plugin=p.PCB_IO_MGR.FindPlugin(p.PCB_IO_MGR.KICAD_SEXP);a.cs=[];a.newrefs=[];a.nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
fs={f.GetReference():f for f in b.GetFootprints()}
power=set();moved=[]
def pos(ref,x,y,ang=0):
    f=fs[ref];f.SetOrientationDegrees(ang);f.SetPosition(v(x,y));meta[ref].update(x=x,y=y);power.add(ref);moved.append(ref)
def value(ref,val):fs[ref].SetValue(val);meta[ref]['value']=val
def addcap(ref,nn,x,y,val='1uF 25V X7R'):
    f=a.place(ref,val,'C_0603_1608Metric',x,y,{'1':nn,'2':'/GND'},height=.9,url='https://www.ti.com/lit/ds/symlink/tps25947.pdf');fs[ref]=f;meta[ref]=a.cs[-1];power.add(ref)
for k in range(1,13):
    x=.25+8*((k-1)%6);y=.4+6.5*((k-1)//6);u=f'U{k+10}';rr=100+5*(k-1);cc=100+3*(k-1)
    pos(u,x+3.6,y+2.4)
    for j,yy in enumerate([.9,2.05,3.2,4.35],1):pos(f'R{rr+j}',x+.9,y+yy)
    pos(f'R{rr+5}',x+6.1,y+2.05);pos(f'C{cc+1}',x+6.1,y+3.2)
    pos(f'C{cc+3}',x+6.1,y+5.4);value(f'C{cc+3}','10uF 25V X7R / effective >=1uF')
    addcap(f'C{9100+k}',f'/VBANK_{"A" if k in [1,2,3,4,5,11] else "B"}',x+2.5,y+5.4)
# AUX eFuse now supports both real 3 A buck stages. 3334 / 750 = 4.445 A nominal.
x,y=49,.4
pos('U30',x+3.6,y+2.4)
for j,yy in enumerate([.9,2.05,3.2,4.35],301):pos(f'R{j}',x+.9,y+yy)
pos('R305',x+6.1,y+2.05);value('R305','750R 1% / AUX limit 4.45A nominal')
pos('C301',x+6.1,y+3.2);addcap('C9130','/VBANK_A',x+2.5,y+5.4);addcap('C9131','/AUX_12V_PROTECTED',x+6.1,y+5.4,'10uF 25V X7R')
for ref,x,y in [('J101',35,42),('J102',76,42),('F1',7.5,42),('F2',53,42),('D1',19.5,42),('D2',91.5,42)]:pos(ref,x,y)
for ref,bank in [('J101','A'),('J102','B')]:value(ref,f'12V INPUT {bank} / 20A budget / solder cable')
for ref in ['F1','F2']:value(ref,'0456025.ER / 25A / derate with temperature');meta[ref].update(height_mm=3.12,datasheet='https://www.littelfuse.com/assetdocs/fuse-456-datasheet?assetguid=d86b18f9-14fa-4764-87ff-8aec12e9a89d')
for ref,x,y,ang in [('U31',67,5,0),('L31',62,5,180),('C311',71.2,4.8,0),('C312',71.2,2.8,0),('C313',71.2,7.1,180),('C314',61,10.7,0),('C315',66.7,10.7,0),('R311',71.2,9,0),('U506',88,5,0),('L502',82.8,5,180),('C5161',92.2,4.8,0),('C5162',92.2,2.8,0),('C5163',81,9.5,0),('C5164',92.2,7.1,180),('R5194',92.2,9,0),('C5117',85,10,0)]:pos(ref,x,y,ang)
# Use the same documented, portable low-profile footprint for both inductors.
old=fs['L502'];new=p.FootprintLoad(str(a.lib),'L_Coilcraft_XAL4020-XXX');new.SetReference('L502');new.SetValue('2.2uH / Isat >=4.5A / DCR <=55mOhm / select exact part');new.SetFPID(p.LIB_ID('Local','L_Coilcraft_XAL4020-XXX'));new.SetPosition(old.GetPosition());new.SetOrientationDegrees(180);new.SetPath(old.GetPath());b.Add(new)
for pp in new.Pads():pp.SetNet(a.net(meta['L502']['pinmap'][pp.GetNumber()]))
new.Reference().SetVisible(False);new.Value().SetVisible(False);remove(b,old);fs['L502']=new;meta['L502'].update(footprint='L_Coilcraft_XAL4020-XXX',value=new.GetValue(),height_mm=2.1)
value('L31','2.2uH / Isat >=4.5A / DCR <=55mOhm / select exact part')
# Pack only unmapped front-side auxiliaries around the fixed connector and IC layout.
signal=json.loads((SRC/'SIGNAL_ROUTES.json').read_text(encoding='utf-8'))['routes'];endrefs={q[e]['ref'] for q in signal for e in ['a','b']}
fixed=power|endrefs|{f'J{k}' for k in range(1,13)}|{ref for ref,f in fs.items() if f.GetLayer()==p.B_Cu}|{'C5119','C5120'}
def box(f):
    z=f.GetBoundingBox(False,False);return [p.ToMM(t) for t in [z.GetX(),z.GetY(),z.GetRight(),z.GetBottom()]]
def overlap(z,o,g=.035):return z[0]<o[2]+g and z[2]>o[0]-g and z[1]<o[3]+g and z[3]>o[1]-g
occupied=[(r,box(fs[r])) for r in fixed if fs[r].GetLayer()==p.F_Cu]
mov=[r for r,f in fs.items() if r not in fixed]
mov.sort(key=lambda r:-(lambda q:(q[2]-q[0])*(q[3]-q[1]))(box(fs[r])))
for ref in mov:
    f=fs[ref];old=xy(f.GetPosition());found=False
    for ang in [f.GetOrientationDegrees(),90,0]:
        f.SetOrientationDegrees(ang);z=box(f);off=[z[0]-old[0],z[1]-old[1],z[2]-old[0],z[3]-old[1]]
        candidates=[old]+[(xx/4,yy/4) for yy in range(3,178) for xx in range(3,381)]
        for x,y in candidates:
            zz=[x+off[0],y+off[1],x+off[2],y+off[3]]
            if zz[0]<.4 or zz[1]<.4 or zz[2]>95.6 or zz[3]>44.6:continue
            if all(not overlap(zz,o) for _,o in occupied):
                f.SetPosition(v(x,y));meta[ref].update(x=x,y=y);occupied.append((ref,box(f)));found=True;break
        if found:break
    assert found,('front packing',ref)
for ref in fs:
    f=fs[ref];meta[ref].update(x=xy(f.GetPosition())[0],y=xy(f.GetPosition())[1],rotation_deg=f.GetOrientationDegrees())
# J401 custom power contacts retain their isolated net: no unqualified 300 W USB connection.
value('J401','CUSTOM POWER USB-C / ISOLATED / INPUT RATING UNVERIFIED')
for t in b.GetDrawings():
    if isinstance(t,p.PCB_TEXT) and 'REV U' in t.GetText():t.SetText(t.GetText().replace('REV U','REV V'))
(F/'COMPONENTS.json').write_text(json.dumps(list(meta.values()),indent=2),encoding='utf-8')
(W/'power_refs.json').write_text(json.dumps(sorted(power),indent=2),encoding='utf-8')
p.SaveBoard(str(F/'Main_12E1S.kicad_pcb'),b)
print('Rev V created:',len(meta),'parts;',len(power),'power parts grouped; signal endpoints unchanged',flush=True)
