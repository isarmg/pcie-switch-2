from i_common import *
import sys
def run(n):
    o=ROOT/n;bp=o/(n+'.kicad_pcb');pp=o/(n+'.kicad_pro');pro=json.loads(pp.read_text());rules=pro['board']['design_settings']['rules'];rules.update(min_track_width=.125,min_via_diameter=.4);pp.write_text(json.dumps(pro,indent=2));b=p.LoadBoard(str(bp));a=object.__new__(Board);a.b=b;a.nets={nn.GetNetname():nn for nn in b.GetNetInfo().NetsByNetcode().values()};dedup=0
    for t in list(b.GetTracks()):
        if not isinstance(t,p.PCB_VIA) and t.GetLength()<p.FromMM(.002):remove(b,t)
    seen=[]
    for t in list(b.GetTracks()):
        if not isinstance(t,p.PCB_VIA):continue
        pt=xy(t.GetPosition());found=None
        for old in seen:
            op=xy(old.GetPosition())
            if old.GetNetCode()==t.GetNetCode() and old.TopLayer()==t.TopLayer() and old.BottomLayer()==t.BottomLayer() and math.hypot(pt[0]-op[0],pt[1]-op[1])<.45:found=old;break
        if found:
            oldpt=xy(found.GetPosition());lo=t.TopLayer();hi=t.BottomLayer()
            # Join all trace endpoints touched by the removed same-net via on their own layers.
            if math.hypot(pt[0]-oldpt[0],pt[1]-oldpt[1])>.002:
                for fp in b.GetFootprints():
                    for ppd in fp.Pads():
                        if ppd.GetNetCode()!=t.GetNetCode():continue
                        qp=xy(ppd.GetPosition())
                        if math.hypot(qp[0]-pt[0],qp[1]-pt[1])<.05:
                            for layer in [p.F_Cu,p.B_Cu]:
                                if ppd.IsOnLayer(layer):a.track(qp,oldpt,t.GetNetname(),layer,.125)
                for tr in list(b.GetTracks()):
                    if isinstance(tr,p.PCB_VIA) or tr.GetNetCode()!=t.GetNetCode():continue
                    if any(math.hypot(xy(vv)[0]-pt[0],xy(vv)[1]-pt[1])<.201 for vv in [tr.GetStart(),tr.GetEnd()]):a.track(pt,oldpt,t.GetNetname(),tr.GetLayer(),.15)
            remove(b,t);dedup+=1
        else:seen.append(t)
    for z in b.Zones():z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
    for t in b.GetDrawings():
        if isinstance(t,p.PCB_TEXT) and p.ToMM(t.GetTextSize().y)<.6:t.SetTextSize(v(.6,.6))
    plugin=p.PCB_IO_MGR.FindPlugin(p.PCB_IO_MGR.KICAD_SEXP);done=set()
    for f in b.GetFootprints():
        name=str(f.GetFPID().GetLibItemName());f.SetFPID(p.LIB_ID('Local',name))
        if name in done:continue
        done.add(name);copy=p.Cast_to_FOOTPRINT(f.Duplicate(False));copy.SetPosition(v(0,0))
        if copy.GetLayer()==p.B_Cu:copy.Flip(v(0,0),p.FLIP_DIRECTION_LEFT_RIGHT)
        copy.SetOrientationDegrees(0);copy.SetReference('REF**');copy.SetValue(name);copy.Reference().SetVisible(False);copy.Value().SetVisible(False)
        plugin.FootprintSave(str(o/'Local.pretty'),copy)
    p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(bp),b);pp.write_text(json.dumps(pro,indent=2));print(n,'merged',dedup,'duplicate/adjacent same-net vias',flush=True)
for n in sys.argv[1:] or ['Main_10E1S','Left_2M2_Vertical','Right_M2_Upstream']:run(n)
