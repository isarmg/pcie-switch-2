from i_common import *
import sys
for name in sys.argv[1:] or ['Main_10E1S','Left_2M2_Vertical','Right_M2_Upstream']:
    o=ROOT/name;bp=o/(name+'.kicad_pcb');pro=(o/(name+'.kicad_pro')).read_bytes();b=p.LoadBoard(str(bp));d=json.loads((o/'DRC.json').read_text(encoding='utf8'));a=object.__new__(Board);a.b=b;a.nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()};byid={t.m_Uuid.AsString():t for t in b.GetTracks()}
    if name.startswith('Left'):
        for z in b.Zones():
            if z.GetLayer()==p.In10_Cu:
                old=z.GetNetname();remove(b,z);x0,x1=(.4,25.6) if old=='/M1_3V3' else (26.4,51.6);a.zone(old,p.In10_Cu,[(x0,.4),(x1,.4),(x1,44.6),(x0,44.6)])
    if name.startswith('Right') and d['unconnected_items']:
        for ref in ['J102','J113']:
            q=pad(b.FindFootprintByReference(ref),'N');pt=xy(q.GetPosition());t=min((z for z in b.GetTracks() if isinstance(z,p.PCB_VIA) and z.GetNetCode()==q.GetNetCode()),key=lambda z:math.hypot(xy(z.GetPosition())[0]-pt[0],xy(z.GetPosition())[1]-pt[1]));a.track(pt,xy(t.GetPosition()),q.GetNetname(),p.B_Cu,.125)
    removed=set()
    for violation in d['violations']:
        if violation['type']=='track_dangling' or (not d['unconnected_items'] and violation['type']=='via_dangling'):
            for item in violation['items']:
                iid=item['uuid']
                if iid in byid and iid not in removed:remove(b,byid[iid]);removed.add(iid)
    p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(bp),b);(o/(name+'.kicad_pro')).write_bytes(pro);print(name,'removed redundant stubs',len(removed),flush=True)
