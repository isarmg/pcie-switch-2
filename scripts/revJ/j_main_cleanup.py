from i_common import *
n='Main_10E1S';o=ROOT/n;bp=o/(n+'.kicad_pcb');b=p.LoadBoard(str(bp));d=json.loads((o/'DRC.json').read_text());a=object.__new__(Board);a.b=b;a.nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
ids={i['uuid'] for v in d['violations'] if v['type']=='via_dangling' for i in v['items']}
for t in list(b.GetTracks()):
    if t.m_Uuid.AsString() in ids and t.GetNetname()!='/M3_RX0_P':remove(b,t)
def distseg(q,s,z):
    dx,dy=z[0]-s[0],z[1]-s[1];dd=dx*dx+dy*dy;t=max(0,min(1,((q[0]-s[0])*dx+(q[1]-s[1])*dy)/dd)) if dd else 0
    return math.hypot(q[0]-s[0]-t*dx,q[1]-s[1]-t*dy)
def clear(q):
    for f in b.GetFootprints():
        for pd in f.Pads():
            if pd.GetNetname()=='/GND':continue
            bb=pd.GetBoundingBox();aa=xy(bb.GetOrigin());zz=xy(bb.GetEnd())
            if math.hypot(max(aa[0]-q[0],0,q[0]-zz[0]),max(aa[1]-q[1],0,q[1]-zz[1]))<.4:return False
    for t in b.GetTracks():
        if isinstance(t,p.PCB_VIA):
            if math.dist(q,xy(t.GetPosition()))<.55:return False
        elif t.GetNetname()!='/GND' and distseg(q,xy(t.GetStart()),xy(t.GetEnd()))<p.ToMM(t.GetWidth())/2+.4:return False
    return True
stitches=[]
for xbase in [19,60]:
    done=False
    for yy in [41.8,42.4,43,43.6]:
        for dx in [0,.6,1.2,-.6]:
            q=(xbase+dx,yy)
            if clear(q):a.via(*q,'/GND');stitches.append(q);done=True;break
        if done:break
b.FindFootprintByReference('R425').SetValue('953R 1% / ILIM 3.5A')
for z in b.Zones():z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(bp),b);print('Full-stack GND stitches',stitches,flush=True)
