from pathlib import Path
import pcbnew as p, json, re, shutil, uuid, math
R=Path(__file__).resolve().parents[1]
ROOT=R/'outputs/PCIe_3board_RevI'
BASE=R/'outputs/E1S_10slot_80x45_12V'
STOCK=Path('C:/Program Files/KiCad/10.0/share/kicad/footprints')
keep=[]
def uid():return str(uuid.uuid4())
def v(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def xy(a):return round(p.ToMM(a.x),6),round(p.ToMM(a.y),6)
def layers(*a):
    z=p.LSET()
    for l in a:z.AddLayer(l)
    return z
def remove(par,a):keep.append(a);par.Remove(a)
def line(par,a,z,l,w=.05):
    t=p.PCB_SHAPE(par);t.SetShape(p.SHAPE_T_SEGMENT);t.SetStart(v(*a));t.SetEnd(v(*z));t.SetLayer(l);t.SetWidth(p.FromMM(w));par.Add(t)
def rect(par,x0,y0,x1,y1,l,w=.05):
    pts=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
    for a,z in zip(pts,pts[1:]+pts[:1]):line(par,a,z,l,w)
def box_model(folder,name,sx,sy,h,color='0.2,0.22,0.24'):
    dest=folder/'models'/f'{name}.step';dest.parent.mkdir(exist_ok=True)
    if dest.exists():return
    src=(R/'scripts/step_primitives_template.py').read_text(encoding='utf-8-sig');a=src.index('# SFF-TA-1006');c=src.index('directed=Counter')
    src=src[:a]+f'top=ring({sx/2},{sy/2},{h});bottom=ring({sx/2},{sy/2},0)\nfaces=[top,bottom[::-1]]\nfor i in range(4):\n n=(i+1)%4;faces.append([bottom[i],bottom[n],top[n],top[i]])\n'+src[c:]
    src=src[:src.index('geometry=')].replace("O=R/'outputs/E1S_12slot_10mm'",f'O=Path({str(folder)!r})').replace('(31.5*5.9*105.49+18.48*1.57*6)',str(sx*sy*h)).replace('E1S_5p9_simplified.step',name+'.step').replace('E1S 5.9mm SSD simplified',name).replace('E1S SSD closed solid',name).replace('Assumed insertion depth; not manufacturer CAD','Simplified mechanical envelope; NOT manufacturer CAD').replace('0.55,0.67,0.78',color)
    exec(compile(src,'model','exec'),{'__file__':str(R/'work/box_source.py')})
class Board:
    def __init__(self,name,w,h,copper=12,base=False):
        self.name=name;self.w=w;self.h=h;self.folder=ROOT/name;self.folder.mkdir(parents=True,exist_ok=True);self.lib=self.folder/'Local.pretty';self.lib.mkdir(exist_ok=True);self.models=self.folder/'models';self.models.mkdir(exist_ok=True)
        self.b=p.LoadBoard(str(BASE/(BASE.name+'.kicad_pcb'))) if base else p.BOARD()
        self.b.SetCopperLayerCount(copper);self.b.GetDesignSettings().SetBoardThickness(p.FromMM(1.6))
        self.nets={n.GetNetname():n for n in self.b.GetNetInfo().NetsByNetcode().values()};self.cs=[];self.root=uid();self.newrefs=[]
        self.pro=json.loads((BASE/(BASE.name+'.kicad_pro')).read_text());self.pro['meta']['filename']=name+'.kicad_pro'
        self.plugin=p.PCB_IO_MGR.FindPlugin(p.PCB_IO_MGR.KICAD_SEXP)
        if base:
            shutil.copytree(BASE/'models',self.models,dirs_exist_ok=True)
            shutil.copytree(BASE/'E1S.pretty',self.lib,dirs_exist_ok=True)
        else:rect(self.b,0,0,w,h,p.Edge_Cuts)
    def net(self,s):
        if s not in self.nets:self.nets[s]=p.NETINFO_ITEM(self.b,s);self.b.Add(self.nets[s])
        return self.nets[s]
    def text(self,s,x,y,layer=p.F_SilkS,size=.65):
        t=p.PCB_TEXT(self.b);t.SetText(s);t.SetPosition(v(x,y));t.SetLayer(layer);t.SetTextSize(v(size,size));t.SetTextThickness(p.FromMM(.1));t.SetMirrored(layer==p.B_SilkS);self.b.Add(t)
    def model(self,f,name,sx,sy,h,offset=(0,0,0),color='0.2,0.22,0.24'):
        box_model(self.folder,name,sx,sy,h,color);m=p.FP_3DMODEL();m.m_Filename='${KIPRJMOD}/models/'+name+'.step';m.m_Offset=p.VECTOR3D(*offset);f.Models().append(m)
    def custom(self,name,pads,sx,sy,h=0):
        f=p.FOOTPRINT(self.b);f.SetFPID(p.LIB_ID('Local',name));f.SetAttributes(p.FP_SMD)
        for n,x,y,w,hh in pads:
            q=p.PAD(f);q.SetNumber(str(n));q.SetPosition(v(x,y));q.SetSize(v(w,hh));q.SetShape(p.PAD_SHAPE_RECT);q.SetAttribute(p.PAD_ATTRIB_SMD);q.SetLayerSet(layers(p.F_Cu,p.F_Mask,p.F_Paste));f.Add(q)
        rect(f,-sx/2,-sy/2,sx/2,sy/2,p.F_Fab,.1)
        xx=max([sx/2]+[abs(a[1])+a[3]/2 for a in pads]);yy=max([sy/2]+[abs(a[2])+a[4]/2 for a in pads]);rect(f,-xx-.15,-yy-.15,xx+.15,yy+.15,p.F_CrtYd)
        if h:self.model(f,name,sx,sy,h)
        self.savefoot(f);return name
    def savefoot(self,f):
        f.Reference().SetVisible(False);f.Value().SetVisible(False);self.plugin.FootprintSave(str(self.lib),f)
    def std(self,lib,name):
        f=p.FootprintLoad(str(STOCK/(lib+'.pretty')),name);assert f,name
        f.SetFPID(p.LIB_ID('Local',name));mods=[]
        for old in f.Models():
            m=p.FP_3DMODEL();m.m_Filename=old.m_Filename;m.m_Offset=old.m_Offset;m.m_Rotation=old.m_Rotation;m.m_Scale=old.m_Scale;path=Path(re.sub(r'\$\{KICAD\d+_3DMODEL_DIR\}','C:/Program Files/KiCad/10.0/share/kicad/3dmodels',m.m_Filename))
            if path.exists():shutil.copy2(path,self.models/path.name);m.m_Filename='${KIPRJMOD}/models/'+path.name;mods.append(m)
        f.Models().clear()
        for m in mods:f.Models().append(m)
        for g in list(f.GraphicalItems()):
            if g.GetLayer()==p.F_SilkS:remove(f,g)
        self.savefoot(f);return name
    def place(self,ref,value,foot,x,y,pinmap,side='F',angle=0,height=0,url='',names=None):
        f=p.FootprintLoad(str(self.lib),foot);assert f,foot
        f.SetFPID(p.LIB_ID('Local',foot));f.SetReference(ref);f.SetValue(value);f.Reference().SetVisible(False);f.Value().SetVisible(False);self.b.Add(f)
        if side=='B':f.Flip(v(0,0),p.FLIP_DIRECTION_LEFT_RIGHT)
        f.SetOrientationDegrees(angle);f.SetPosition(v(x,y))
        for q in f.Pads():
            if q.GetNumber():q.SetNet(self.net(pinmap[str(q.GetNumber())]))
        self.cs.append(dict(ref=ref,value=value,footprint=foot,pinmap=pinmap,x=x,y=y,side=side,height_mm=height,datasheet=url,pin_names=names or {}));self.newrefs.append(ref);return f
    def track(self,a,z,nn,layer,w=.125):
        if math.hypot(a[0]-z[0],a[1]-z[1])<.002:return
        t=p.PCB_TRACK(self.b);t.SetStart(v(*a));t.SetEnd(v(*z));t.SetNet(self.net(nn));t.SetLayer(layer);t.SetWidth(p.FromMM(w));self.b.Add(t)
    def via(self,x,y,nn,lo=p.F_Cu,hi=p.B_Cu,d=.4,dr=.2):
        t=p.PCB_VIA(self.b);t.SetPosition(v(x,y));t.SetWidth(p.FromMM(d));t.SetDrill(p.FromMM(dr));t.SetViaType(p.VIATYPE_THROUGH if lo==p.F_Cu and hi==p.B_Cu else p.VIATYPE_BLIND);t.SetLayerPair(lo,hi);t.SetNet(self.net(nn));self.b.Add(t)
    def zone(self,nn,layer,pts):
        z=p.ZONE(self.b);z.SetLayer(layer);z.SetNet(self.net(nn));z.SetLocalClearance(p.FromMM(.15));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetMinThickness(p.FromMM(.1));z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_NEVER);o=z.Outline();o.NewOutline()
        for x,y in pts:o.Append(p.FromMM(x),p.FromMM(y))
        self.b.Add(z)
    def save(self):
        p.SaveBoard(str(self.folder/(self.name+'.kicad_pcb')),self.b)
        (R/'work/revI').mkdir(parents=True,exist_ok=True);shutil.copy2(self.folder/(self.name+'.kicad_pcb'),R/'work/revI'/f'{self.name}.placed.kicad_pcb')
        (self.folder/(self.name+'.kicad_pro')).write_text(json.dumps(self.pro,indent=2))
        (self.folder/'COMPONENTS.json').write_text(json.dumps(self.cs,indent=2))
        (self.folder/'fp-lib-table').write_text('(fp_lib_table (lib (name "Local")(type "KiCad")(uri "${KIPRJMOD}/Local.pretty")(options "")(descr "Local portable library")))')
        (self.folder/'sym-lib-table').write_text('(sym_lib_table (lib (name "Local")(type "KiCad")(uri "${KIPRJMOD}/Local.kicad_sym")(options "")(descr "Project symbols")))')
def nc(ref,pin):return f'unconnected-({ref}-Pad{pin})'
def pad(f,n):return next(q for q in f.Pads() if q.GetNumber()==str(n))
