from i_common import *
import csv
a=Board('Assembly_View',236,45,2)
for d in list(a.b.GetDrawings()):remove(a.b,d)
sources=[]
for n,dx,prefix in [('Main_10E1S',0,'M'),('Left_2M2_Vertical',-82,'L'),('Right_M2_Upstream',110,'R')]:
    o=ROOT/n;source=(R/'work/revI'/f'{n}.placed.kicad_pcb') if not n.startswith('Main') else o/(n+'.kicad_pcb');b=p.LoadBoard(str(source));sources.append(b)
    for f in b.GetFootprints():
        cp=p.Cast_to_FOOTPRINT(f.Duplicate(False));a.b.Add(cp);cp.Move(v(dx,0));cp.SetReference(prefix+'_'+f.GetReference());mods=[]
        for old in cp.Models():
            m=p.FP_3DMODEL();m.m_Offset=old.m_Offset;m.m_Rotation=old.m_Rotation;m.m_Scale=old.m_Scale;fn=Path(old.m_Filename.replace('${KIPRJMOD}',str(o)));dest=prefix+'_'+fn.name
            if fn.exists():shutil.copy2(fn,a.models/dest);m.m_Filename='${KIPRJMOD}/models/'+dest;mods.append(m)
        cp.Models().clear()
        for m in mods:cp.Models().append(m)
        for q in cp.Pads():q.SetNetCode(0)
    for g in b.GetDrawings():
        if g.GetLayer()==p.Edge_Cuts:cp=g.Duplicate();a.b.Add(cp);cp.Move(v(dx,0))
def model_faces(name,faces,color):
    src=(R/'scripts/step_primitives_template.py').read_text(encoding='utf-8-sig');start=src.index('# SFF-TA-1006');end=src.index('directed=Counter');src=src[:start]+'faces='+repr(faces)+'\n'+src[end:];src=src[:src.index('geometry=')];src=src.replace("O=R/'outputs/E1S_12slot_10mm'",f'O=Path({str(a.folder)!r})');src=re.sub(r'assert abs\(volume-.*?<1e-6','assert abs(volume)>0.0001',src);src=src.replace('E1S_5p9_simplified.step',name+'.step').replace('E1S 5.9mm SSD simplified',name).replace('E1S SSD closed solid',name).replace('Assumed insertion depth; not manufacturer CAD','Mechanical envelope, schematic cable route only').replace('0.55,0.67,0.78',color);exec(compile(src,'faces','exec'),{'__file__':str(R/'scripts/step_primitives_template.py')})
def cable(name,start,end,ry,rz,zbase,color):
    rings=[]
    for j in range(9):
        t=j/8;x=start[0]+(end[0]-start[0])*t;y=start[1]+(end[1]-start[1])*t;z=zbase-1.5*math.sin(math.pi*t)
        rings.append([(x,y+ry*math.cos(2*math.pi*i/12),z+rz*math.sin(2*math.pi*i/12)) for i in range(12)])
    faces=[rings[0][::-1],rings[-1]]
    for r,s in zip(rings,rings[1:]):
        for i in range(12):j=(i+1)%12;faces.append([r[i],r[j],s[j],s[i]])
    if start[0]>end[0]:faces=[f[::-1] for f in faces]
    model_faces(name,faces,color);f=p.FOOTPRINT(a.b);f.SetReference(name);f.SetValue('Cable route envelope / NOT fabrication');f.SetAttributes(p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES);a.b.Add(f);m=p.FP_3DMODEL();m.m_Filename='${KIPRJMOD}/models/'+name+'.step';f.Models().append(m);f.Reference().SetVisible(False);f.Value().SetVisible(False)
for side in ['L','R']:
    for i in range(18):
        cable(f'Twinax_{side}_{i+1:02}',(1.25 if side=='L' else 78.75,-(2+2.3*i)),(-31.4 if side=='L' else 111.4,-(2+2.3*i)),.7,.45,-2.3,'0.38,0.42,0.48')
    # Independent 12 V / ground wires; no power travels in the signal twinax conductors.
    for i,col in [(0,'0.75,0.05,0.04'),(1,'0.08,0.08,0.09')]:cable(f'Power_{side}_{i}',(4+3*i if side=='L' else 73+3*i,-10),(-40.5+3*i if side=='L' else 116.5+3*i,-4),.8,.8,-5.8,col)
    cable(f'Control_{side}',(7 if side=='L' else 73,-42),(-51 if side=='L' else 130,-4),.9,.3,-4.6,'0.12,0.25,0.65')
# Three vertical 2280 envelopes. SSD planes are XZ, perpendicular to the XY carrier PCBs.
for k,x,y in [(1,-68,17),(2,-44,17),(3,124,17)]:
    f=p.FOOTPRINT(a.b);f.SetReference(f'SSD{k}');f.SetValue('M.2 2280 VERTICAL ENVELOPE');a.b.Add(f);f.SetPosition(v(x,y));f.Reference().SetVisible(False);f.Value().SetVisible(False)
    a.model(f,'M2_2280_vertical_board',22,.8,80,(0,0,1.5),'0.05,0.3,0.14')
    for j in range(4):a.model(f,'SSD_chip_envelope',14,1.2,12,(0,1.0,12+j*16),'0.12,0.13,0.15')
    f.SetOrientationDegrees(90)
    # Key gap and edge fingers are intentionally not asserted by this bounding model.
a.text('ASSEMBLY VIEW ONLY / THREE INDEPENDENT PCBs / VERTICAL 2280',36,49,p.Dwgs_User,1.2)
a.save();(a.folder/'ASSEMBLY_ONLY.txt').write_text('Visualization only. This compound PCB is not an electrical/manufacturing design. Use the three separate projects. SSD and cable STEP solids are mechanical envelopes, not exact production CAD.\n')
print('Assembly built with three vertical SSDs, 36 twinax-pair envelopes, four power wires and two control bundles.')
