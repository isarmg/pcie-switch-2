from pathlib import Path
import sys,json
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');F=R/'outputs/PCIe_E1S_96x45_USB12mm_RevW/Main_12E1S';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
b=p.LoadBoard(str(F/'Main_12E1S.kicad_pcb'));m={q['ref']:q for q in json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'))};fs={f.GetReference():f for f in b.GetFootprints()}
a=object.__new__(Board);a.b=b;a.folder=F;a.lib=F/'Local.pretty';a.models=F/'models';a.cs=[];a.newrefs=[];a.nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()};a.plugin=p.PCB_IO_MGR.FindPlugin(p.PCB_IO_MGR.KICAD_SEXP)
a.std('Capacitor_Tantalum_SMD','CP_EIA-3528-21_Kemet-B')
fs['L901'].SetOrientationDegrees(0)
for ref in ['C9023','C9024']:
 old=fs[ref];ff=p.FootprintLoad(str(a.lib),'CP_EIA-3528-21_Kemet-B');ff.SetReference(ref);ff.SetValue('T520B227M006ATE025 / 220uF 6.3V / ESR25mOhm');ff.SetFPID(p.LIB_ID('Local','CP_EIA-3528-21_Kemet-B'));ff.SetPath(old.GetPath());b.Add(ff);ff.Flip(v(0,0),p.FLIP_DIRECTION_LEFT_RIGHT);ff.SetPosition(old.GetPosition());ff.Reference().SetVisible(False);ff.Value().SetVisible(False)
 for pp in ff.Pads():pp.SetNet(a.net(m[ref]['pinmap'][pp.GetNumber()]))
 remove(b,old);fs[ref]=ff;m[ref].update(footprint='CP_EIA-3528-21_Kemet-B',height_mm=2.1,value=ff.GetValue())
smallc='C_0201_DenseCourtyard_1p0x0p4'
if 'C9029' not in fs:
 f=a.place('C9029','100pF C0G / FB feedforward',smallc,94,32,{'1':'/PEX_1V8','2':'/PEX18_FB'},side='B',height=.33);fs['C9029']=f;m['C9029']=a.cs[-1]
def box(f):
 z=f.GetBoundingBox(False,False);return [p.ToMM(t) for t in [z.GetX(),z.GetY(),z.GetRight(),z.GetBottom()]]
def ov(z,o,g=.01):return z[0]<o[2]+g and z[2]>o[0]-g and z[1]<o[3]+g and z[3]>o[1]-g
moving={'C9023','C9024','C9025','C9026','C9027','C9028','C9029','R9021','R9022','R9023','R9024','C9021','C9022'}
occ=[(r,box(f)) for r,f in fs.items() if f.GetLayer()==p.B_Cu and r not in moving]
for ref in sorted(moving,key=lambda r:-(lambda z:(z[2]-z[0])*(z[3]-z[1]))(box(fs[r]))):
 f=fs[ref];target=xy(f.GetPosition());found=False
 for ang in [0,90]:
  f.SetOrientationDegrees(ang);old=xy(f.GetPosition());z=box(f);off=[z[0]-old[0],z[1]-old[1],z[2]-old[0],z[3]-old[1]]
  for x,y in sorted(((xx/10,yy/10) for xx in range(808,957) for yy in range(280,446)),key=lambda pt:math.dist(pt,target)):
   zz=[x+off[0],y+off[1],x+off[2],y+off[3]]
   if zz[0]<80.8 or zz[1]<28 or zz[2]>95.6 or zz[3]>44.5:continue
   if all(not ov(zz,o) for _,o in occ):f.SetPosition(v(x,y));occ.append((ref,box(f)));found=True;break
  if found:break
 assert found,ref
for ref,f in fs.items():m[ref].update(value=f.GetValue(),x=xy(f.GetPosition())[0],y=xy(f.GetPosition())[1],rotation_deg=f.GetOrientationDegrees(),side='B' if f.GetLayer()==p.B_Cu else 'F')
(F/'COMPONENTS.json').write_text(json.dumps(list(m.values()),indent=2),encoding='utf-8');p.SaveBoard(str(F/'Main_12E1S.kicad_pcb'),b)
for i,(r,f) in enumerate(fs.items()):
 z=box(f)
 for s,g in list(fs.items())[i+1:]:
  if f.GetLayer()==g.GetLayer() and ov(z,box(g),-.02):print('BOX OVERLAP',r,s,z,box(g),flush=True)
print('Patched capacitor stability reserve and power coil polarity. Parts',len(fs),flush=True)
