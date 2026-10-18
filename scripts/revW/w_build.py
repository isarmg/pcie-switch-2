"""Rev W: preserve real CPU balls, move ports, add reference switch supplies."""
from pathlib import Path
from collections import defaultdict
import sys,json,math,shutil,copy
sys.stdout.reconfigure(encoding='utf-8')
ST=Path(__file__).resolve().parents[2];R=Path('C:/Users/micro/Desktop/方案/pcie switch 2')
S=R/'outputs/PCIe_E1S_96x45_12VPower_RevV';O=R/'outputs/PCIe_E1S_96x45_USB12mm_RevW';F=O/'Main_12E1S';W=R/'work/revW'
sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
if O.exists():
 import hashlib
 assert hashlib.sha256((F/'Main_12E1S.kicad_pcb').read_bytes()).digest()==hashlib.sha256((S/'Main_12E1S/Main_12E1S.kicad_pcb').read_bytes()).digest(),'Do not reset saved work'
else:shutil.copytree(S,O,ignore=shutil.ignore_patterns('*.lck','*.kicad_prl','*-backups','*.zip','SHA256SUMS.txt','DRC.json','ERC.json','Main_12E1S.step','preview.png','bottom.png','CONNECTIVITY.net','VALIDATION.json','STEP_VALIDATION.json','POWER_CONNECTIVITY.json'))
W.mkdir(parents=True,exist_ok=True)
b=p.LoadBoard(str(F/'Main_12E1S.kicad_pcb'));m={q['ref']:q for q in json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'))}
a=object.__new__(Board);a.b=b;a.folder=F;a.lib=F/'Local.pretty';a.models=F/'models';a.plugin=p.PCB_IO_MGR.FindPlugin(p.PCB_IO_MGR.KICAD_SEXP);a.cs=[];a.newrefs=[];a.nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
fs={f.GetReference():f for f in b.GetFootprints()};oldpos={r:xy(f.GetPosition()) for r,f in fs.items()};oldside={r:f.GetLayer() for r,f in fs.items()}
for t in list(b.GetTracks()):remove(b,t)
for z in list(b.Zones()):remove(b,z)
def pos(ref,x,y,ang=None,side=None):
 f=fs[ref]
 if side and (f.GetLayer()==p.B_Cu)!=(side=='B'):f.Flip(f.GetPosition(),p.FLIP_DIRECTION_LEFT_RIGHT)
 if ang is not None:f.SetOrientationDegrees(ang)
 f.SetPosition(v(x,y));m[ref].update(x=x,y=y,side='B' if f.GetLayer()==p.B_Cu else 'F',rotation_deg=f.GetOrientationDegrees())
for r,f in fs.items():
 if f.GetLayer()==p.B_Cu and r not in ['C1','C102','C726','U603']:pos(r,oldpos[r][0]-15,oldpos[r][1])
pos('J401',84,22.5,90);pos('J402',72,22.5,90)
pos('U603',6,42,0,'B');pos('U604',12,42,0,'B')
pos('C1',75.75,8.25,0,'F');pos('C102',75.6,11.2,0,'F');pos('C726',79.4,40.2,0,'B')
def replace(ref,foot,x,y,ang=0,side='B'):
 old=fs[ref];ff=p.FootprintLoad(str(a.lib),foot);assert ff,foot
 ff.SetFPID(p.LIB_ID('Local',foot));ff.SetReference(ref);ff.SetValue(old.GetValue());ff.SetPath(old.GetPath());ff.Reference().SetVisible(False);ff.Value().SetVisible(False);b.Add(ff)
 if side=='B':ff.Flip(v(0,0),p.FLIP_DIRECTION_LEFT_RIGHT)
 ff.SetOrientationDegrees(ang);ff.SetPosition(v(x,y))
 for pp in ff.Pads():
  if pp.GetNumber():pp.SetNet(a.net(m[ref]['pinmap'][pp.GetNumber()]))
 remove(b,old);fs[ref]=ff;m[ref].update(footprint=foot,x=x,y=y,side=side,rotation_deg=ang)
smallr=next(q['footprint'] for q in m.values() if q['footprint'].startswith('R_0201_Dense'))
smallc=a.custom('C_0201_DenseCourtyard_1p0x0p4',[('1',-.24,0,.3,.3),('2',.24,0,.3,.3)],.6,.3,.33)
# Free a 24x13.5 mm front power area; all six original eFuses keep pinmaps.
relocated=[]
for ii,k in enumerate([1,2,3,7,8,9]):
 x=81.15+7.2*(ii%2);y=.5+5.4*(ii//2);rr=100+5*(k-1);cc=100+3*(k-1)
 pos(f'U{k+10}',x+3.6,y+1.95,0,'B');relocated.append(f'U{k+10}')
 for j,dy in enumerate([.55,1.45,2.35,3.25],1):replace(f'R{rr+j}',smallr,x+6.15,y+dy);relocated.append(f'R{rr+j}')
 replace(f'R{rr+5}',smallr,x+1.05,y+1.8);replace(f'C{cc+1}',smallc,x+1.05,y+3)
 pos(f'C{cc+3}',x+1.35,y+4.5,0,'B');pos(f'C{9100+k}',x+4.45,y+4.5,0,'B')
 relocated +=[f'R{rr+5}',f'C{cc+1}',f'C{cc+3}',f'C{9100+k}']
def add(ref,val,foot,x,y,pm,side='F',ang=0,h=.5,url=''):
 f=a.place(ref,val,foot,x,y,pm,side=side,angle=ang,height=h,url=url);fs[ref]=f;m[ref]=a.cs[-1];m[ref]['rotation_deg']=ang;return f
for lib,foot in [('Inductor_SMD','L_Coilcraft_XAL7070-XXX'),('Inductor_SMD','L_Coilcraft_XAL4020-XXX'),('Capacitor_Tantalum_SMD','CP_EIA-7343-31_Kemet-D'),('Capacitor_SMD','C_0805_2012Metric'),('Capacitor_SMD','C_1206_3216Metric')]:a.std(lib,foot)
# RVF0040A top view, TI recommended land pattern: body X5/Y7, EP 3.3x5.3.
pads=[]
for i in range(12):pads.append((i+1,-2.4,-2.75+.5*i,.6,.25))
for i in range(8):pads.append((13+i,-1.75+.5*i,3.4,.25,.6))
for i in range(12):pads.append((21+i,2.4,2.75-.5*i,.6,.25))
for i in range(8):pads.append((33+i,1.75-.5*i,-3.4,.25,.6))
pads.append((41,0,0,3.3,5.3));fp=a.custom('TI_RVF0040A_TPS548D22',pads,5,7,1.52)
g='/GND';n='/PEX_0V9';sw='/PEX09_SW'
pm={str(i):nc('U901',i) for i in range(1,42)}
for i in range(6,13):pm[str(i)]=sw
for i in list(range(13,21))+[29,30,41]:pm[str(i)]=g
for i in list(range(21,27))+[28]:pm[str(i)]='/VBANK_B'
pm.update({'4':'/PEX09_EN','5':'/PEX09_BOOT','31':'/PEX09_BP','32':'/PEX09_FSEL','33':'/PEX09_VSEL','34':'/PEX09_MODE','35':'/PEX09_PG','36':'/PEX09_ILIM','38':'/PEX09_SENSE_N','39':'/PEX09_SENSE_P','40':n})
add('U901','TPS548D22RVFR / 0.9004V 40A reference',fp,5.3,4.7,pm,ang=180,h=1.52,url='https://www.ti.com/lit/ds/symlink/tps548d22.pdf')
add('L901','XAL7070-161MEC / 0.16uH / thermal validation required','L_Coilcraft_XAL7070-XXX',13.4,4.7,{'1':sw,'2':n},ang=180,h=7,url='https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xal/xal7070/')
for r,x in [('C9011',4.9),('C9012',13.5)]:add(r,'T520D477M2R5ATE009 / 470uF 2.5V / ESR9mOhm','CP_EIA-7343-31_Kemet-D',x,11.25,{'1':n,'2':g},h=3.1,url='https://content.kemet.com/datasheets/KEM_T2005_T520.pdf')
# Low DCR filtered analog rail: the original PEX88096 VDDA filter is mandatory.
filterfp=a.custom('L_XEL4020_Land_4p5x4p1',[('1',-1.65,0,1.1,3.3),('2',1.65,0,1.1,3.3)],4.4,4.2,2.1)
add('L902','XEL4020-101MEC / 0.1uH / DCRmax2.5mOhm',filterfp,21,3.25,{'1':n,'2':'/PEX_0V9A'},ang=90,h=2.1,url='https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xel/xel4020/')
# RDF0022A land pattern. Large VIN/VOUT copper is represented conservatively
# by rectangles inside the manufacturer's notched recommended lands.
pads=[]
for i in range(9):
 y=-2.925+.65*i
 if i in [0,8]:pads.append((i+1,-2.75,y,1.4,.9))
 else:pads.append((i+1,-2.85,y,1.2,.25))
for i in range(9):
 y=2.925-.65*i
 if i in [0,8]:pads.append((10+i,2.75,y,1.4,.9))
 else:pads.append((10+i,2.85,y,1.2,.25))
for i,y in enumerate([-2.25,-.75,.75,2.25],19):pads.append((i,0,y,3.3,1.075))
fp=a.custom('TI_RDF0022A_TPSM63610_ConservativeLand',pads,7.5,6.5,4.05)
pm={'1':'/VBANK_B','18':'/VBANK_B','2':'/PEX18_RBOOT','3':'/PEX18_CBOOT','4':nc('U902','4'),'5':'/PEX_1V8','6':'/PEX18_VCC','7':g,'8':'/PEX18_FB','9':'/PEX_1V8','10':'/PEX_1V8','11':g,'12':'/PEX18_VCC','13':'/PEX18_PG','14':g,'15':'/PEX18_VCC','16':nc('U902','16'),'17':'/VBANK_B','19':g,'20':g,'21':g,'22':g}
add('U902','TPSM63610RDFR / 1.8V 8A',fp,87,33.6,pm,side='B',h=4.05,url='https://www.ti.com/lit/ds/symlink/tpsm63610.pdf')
add('L903','XEL4020-101MEC / 0.1uH / DCRmax2.5mOhm',filterfp,92.5,41.4,{'1':'/PEX_1V8','2':'/PEX_1V8A'},side='B',h=2.1,url='https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xel/xel4020/')
newpass=[]
def cap(ref,nn,val,foot='C_0402_1005Metric',side='F',target=(5,5)):
 f=add(ref,val,foot,*target,{'1':nn,'2':g},side=side,h=.9);newpass.append((ref,target));return f
def resistor(ref,nn1,nn2,val,side='F',target=(6,6)):
 f=add(ref,val,smallr,*target,{'1':nn1,'2':nn2},side=side,h=.33);newpass.append((ref,target));return f
for r,y in [('C9001',2.2),('C9002',5.6)]:cap(r,'/VBANK_B','22uF 25V X7R','C_0805_2012Metric',target=(1.15,y));fs[r].SetOrientationDegrees(90)
cap('C9003','/VBANK_B','100nF 25V',target=(3,1))
cap('C9004','/PEX09_BP','2.2uF 10V',target=(7.8,8.2))
cap('C9005','/VBANK_B','1uF 25V',target=(2.8,8.4))
f=add('C9006','100nF 25V BOOT','C_0402_1005Metric',8.2,6.8,{'1':'/PEX09_BOOT','2':sw},h=.5);newpass.append(('C9006',(8.2,6.8)))
for rr,nn,vv in [('R9001','/PEX09_FSEL','22.1k 1% / 650kHz FCCM'),('R9002','/PEX09_VSEL','33.2k 1% / 0.9004V'),('R9003','/PEX09_MODE','47.5k 1% / 2ms SS'),('R9004','/PEX09_ILIM','137k 1% / 43.2A valley')]:resistor(rr,nn,g,vv,target=(8,1))
resistor('R9005','/VBANK_B','/PEX09_EN','100k 1%',target=(2,8));resistor('R9006','/PEX09_EN',g,'18.2k 1% / UVLO nominal10.39V',target=(2,8));resistor('R9007','/PEX09_PG','/P3V3_AUX','100k',target=(8,8))
for rr,nn in [('R9011','/PEX09_FSEL'),('R9012','/PEX09_VSEL'),('R9013','/PEX09_MODE')]:resistor(rr,'/PEX09_BP',nn,'100k 1% / mandatory upper strap',target=(8,1))
resistor('R9008','/PEX09_SENSE_P',n,'0R / remote sense at switch',side='B',target=(37.9,40.4));resistor('R9009','/PEX09_SENSE_N',g,'0R / remote return at switch',side='B',target=(37.9,41.3))
for rr,nn in [('C9013',n),('C9014',n),('C9015','/PEX_0V9A'),('C9016','/PEX_0V9A')]:cap(rr,nn,'22uF 6.3V X5R / verify effective C','C_0603_1608Metric',target=(21,10))
for rr in ['C9021','C9022']:cap(rr,'/VBANK_B','22uF 25V X7R','C_0805_2012Metric',side='B',target=(92,29))
for rr in ['C9023','C9024','C9025']:cap(rr,'/PEX_1V8','47uF 6.3V X7R','C_1206_3216Metric',side='B',target=(85,40))
for rr in ['C9026','C9027']:cap(rr,'/PEX_1V8A','22uF 6.3V X7R','C_0805_2012Metric',side='B',target=(92,38))
cap('C9028','/PEX_1V8','100nF / VLDOIN bypass',side='B',target=(82,34))
resistor('R9021','/PEX18_RBOOT','/PEX18_CBOOT','100R',side='B',target=(92,31))
resistor('R9022','/PEX_1V8','/PEX18_FB','100k 0.1%',side='B',target=(92,35));resistor('R9023','/PEX18_FB',g,'125k 0.1%',side='B',target=(92,35));resistor('R9024','/PEX18_PG','/P3V3_AUX','100k',side='B',target=(82,34))
# Pack new passives close to their functional blocks, leaving existing endpoints.
def box(f):
 z=f.GetBoundingBox(False,False);return [p.ToMM(t) for t in [z.GetX(),z.GetY(),z.GetRight(),z.GetBottom()]]
def ov(z,o,g=.025):return z[0]<o[2]+g and z[2]>o[0]-g and z[1]<o[3]+g and z[3]>o[1]-g
np={r for r,_ in newpass};occupied=defaultdict(list)
for r,f in fs.items():
 if r not in np:occupied[f.GetLayer()].append((r,box(f)))
for ref,target in sorted(newpass,key=lambda t:-(lambda z:(z[2]-z[0])*(z[3]-z[1]))(box(fs[t[0]]))):
 f=fs[ref];side=f.GetLayer();found=False
 bounds=(.35,.35,24.25,13.7) if side==p.F_Cu else (80.8,28,95.6,44.5) if ref not in ['R9008','R9009'] else (37.2,39.4,40.5,44.4)
 for ang in [f.GetOrientationDegrees(),90,0]:
  f.SetOrientationDegrees(ang);old=xy(f.GetPosition());z=box(f);off=[z[0]-old[0],z[1]-old[1],z[2]-old[0],z[3]-old[1]]
  cand=sorted(((xx/10,yy/10) for xx in range(round(bounds[0]*10),round(bounds[2]*10)+1) for yy in range(round(bounds[1]*10),round(bounds[3]*10)+1)),key=lambda pt:math.dist(pt,target))
  for x,y in cand:
   zz=[x+off[0],y+off[1],x+off[2],y+off[3]]
   if zz[0]<bounds[0] or zz[1]<bounds[1] or zz[2]>bounds[2] or zz[3]>bounds[3]:continue
   if all(not ov(zz,o) for _,o in occupied[side]):f.SetPosition(v(x,y));occupied[side].append((ref,box(f)));found=True;break
  if found:break
 assert found,('power passive packing',ref)
# All active semiconductor pads retain exact original net definitions.
for ref,f in fs.items():m[ref].update(x=xy(f.GetPosition())[0],y=xy(f.GetPosition())[1],rotation_deg=f.GetOrientationDegrees(),side='B' if f.GetLayer()==p.B_Cu else 'F')
for d in b.GetDrawings():
 if isinstance(d,p.PCB_TEXT):d.SetText(d.GetText().replace('REV V','REV W'))
(F/'COMPONENTS.json').write_text(json.dumps(list(m.values()),indent=2),encoding='utf-8')
(W/'placement_changes.json').write_text(json.dumps(dict(old_positions=oldpos,old_sides=oldside,relocated_efuses=relocated,new_refs=a.newrefs),indent=2),encoding='utf-8')
for fn in ['TPS548D22.pdf','TPSM63610.pdf']:
 dest=O/'references/Power_RevW';dest.mkdir(parents=True,exist_ok=True);shutil.copy2(ST/'work/revW'/fn,dest/fn)
p.SaveBoard(str(F/'Main_12E1S.kicad_pcb'),b)
print('Rev W placed',len(fs),'parts; USB face distances 12/24 mm; centers X84/72 Y22.5',flush=True)
print('New parts',len(a.newrefs),'moved eFuse parts',len(relocated),flush=True)
