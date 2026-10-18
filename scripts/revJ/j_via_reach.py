from i_common import *
for name in ['Left_2M2_Vertical','Right_M2_Upstream']:
    o=ROOT/name;bp=o/(name+'.kicad_pcb');b=p.LoadBoard(str(bp));a=object.__new__(Board);a.b=b;a.nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()};count=0
    if name.startswith('Left'):
        for t in list(b.GetTracks()):
            if isinstance(t,p.PCB_VIA) and t.GetNetname()=='/GND' and math.dist(xy(t.GetPosition()),(15.75,35.5))<.01:remove(b,t)
    else:
        q=pad(b.FindFootprintByReference('R301'),'2');pt=xy(q.GetPosition())
        if not any(isinstance(t,p.PCB_VIA) and t.GetNetname()==q.GetNetname() and math.dist(xy(t.GetPosition()),pt)<.01 for t in b.GetTracks()):a.via(*pt,q.GetNetname(),p.In14_Cu,p.B_Cu,.3,.1)
    tracks=[t for t in b.GetTracks() if not isinstance(t,p.PCB_VIA)]
    for via in b.GetTracks():
        if not isinstance(via,p.PCB_VIA):continue
        pt=xy(via.GetPosition());need=set()
        for tr in tracks:
            if tr.GetNetname()==via.GetNetname() and tr.GetLayer() in [p.F_Cu,p.B_Cu] and any(math.dist(xy(q),pt)<.025 for q in [tr.GetStart(),tr.GetEnd()]):need.add(tr.GetLayer())
        if any(not via.IsOnLayer(l) for l in need):
            lo=p.F_Cu if p.F_Cu in need else via.TopLayer();hi=p.B_Cu if p.B_Cu in need else via.BottomLayer();via.SetLayerPair(lo,hi);via.SetViaType(p.VIATYPE_THROUGH if lo==p.F_Cu and hi==p.B_Cu else p.VIATYPE_BLIND);count+=1
    p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(bp),b);print(name,'via layer ranges corrected',count,flush=True)
