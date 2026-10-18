"""Reserve In5 exclusively for the 150 W bank A; move its 12 signal sections."""
from pathlib import Path
from collections import defaultdict
import sys,json,math
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_12VPower_RevV';F=O/'Main_12E1S';W=R/'work/revV';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
bp=F/'Main_12E1S.kicad_pcb';b=p.LoadBoard(str(bp));sd=json.loads((O/'SIGNAL_ROUTES.json').read_text(encoding='utf-8'));tasks=[q for q in sd['routes'] if q['layer']==p.In5_Cu]
assert len(tasks)==12
for t in list(b.GetTracks()):
    if not isinstance(t,p.PCB_VIA) and t.GetLayer()==p.In5_Cu and t.GetNetname()!='/VBANK_A':remove(b,t)
# The earlier temporary narrow bank-A island links are now replaced by the plane.
oldbridges=json.loads((O/'POWER_ISLAND_BRIDGES.json').read_text(encoding='utf-8'))
for rec in oldbridges['bridges']:
    if rec['net']!='/VBANK_A':continue
    for t in list(b.GetTracks()):
        if isinstance(t,p.PCB_VIA) or t.GetNetname()!='/VBANK_A' or b.GetLayerName(t.GetLayer())!=rec['layer']:continue
        if any(math.dist(xy(t.GetStart()),x)<.000005 and math.dist(xy(t.GetEnd()),z)<.000005 for x,z in zip(rec['points'],rec['points'][1:])):remove(b,t)
for t in b.GetDrawings():
    if isinstance(t,p.PCB_TEXT):t.SetText(t.GetText().replace('TB5 PORT','TB3 HOST').replace('1550 balls / REAL PINOUT','FAKE 1024 BALLS / DRAFT').replace('PEX88096','FAKE PEX90064'))
p.SaveBoard(str(bp),b)
helper=Path(__file__).with_name('v_repair.py').read_text(encoding='utf-8');helper=helper[helper.index("src=Path(__file__).with_name('v_power.py')"):helper.index('bridged=[]')]
exec(compile(helper,'collision geometry','exec'),globals())
original_local=src[src.index('def localroute('):src.index('controlfailed=[]')].replace('def localroute(start,end,nn,width):','def localroute(start,end,nn,width,side=p.F_Cu):').replace('    side=p.F_Cu;rad=width/2','    rad=width/2')
moved=[]
for rec in tasks:
    nn=rec['net'];start,end=rec['a']['pt'],rec['b']['pt'];available=set(cu)-{p.In5_Cu,p.F_Cu,p.B_Cu}
    for pt in [start,end]:
        vs=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and t.GetNetname()==nn and math.dist(xy(t.GetPosition()),pt)<.000005];assert vs,(nn,pt)
        available&={ll for t in vs for ll in cu if t.IsOnLayer(ll)}
    layerorder=sorted(available,key=lambda ll:(sum(1 for t in b.GetTracks() if not isinstance(t,p.PCB_VIA) and t.GetLayer()==ll),ll))
    solved=None
    for ll in layerorder:
        for path in [rec['points'],[start,end]]:
            if all(clear(x,z,nn,ll,rec['width']/2) for x,z in zip(path,path[1:])):solved=(ll,path);break
        if solved:break
    if not solved:
        for grid in [.1,.05]:
            exec(compile(original_local.replace('grid=.05;',f'grid={grid};').replace('len(seen)>70000','len(seen)>40000'),'bounded signal route','exec'),globals())
            for ll in layerorder:
                try:path=localroute(start,end,nn,rec['width'],ll);solved=(ll,path);break
                except RuntimeError:pass
            if solved:break
    assert solved,('cannot move reserved-layer signal',nn)
    ll,path=solved
    for x,z in zip(path,path[1:]):track(x,z,nn,ll,rec['width'])
    rec.update(layer=ll,layer_name=b.GetLayerName(ll),layer_index=ll//2-1,points=path,length_mm=sum(math.dist(x,z) for x,z in zip(path,path[1:]))+sum(rec[e].get('fanout_mm',0) for e in ['a','b']),routing_method='moved from dedicated power plane; individual signal connectivity only')
    moved.append(dict(net=nn,from_layer='In5.Cu',to_layer=rec['layer_name']));print('Moved',nn,'to',rec['layer_name'],flush=True)
print('Fill continuous power plane...',flush=True);b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(bp),b)
(O/'SIGNAL_ROUTES.json').write_text(json.dumps(sd,indent=2),encoding='utf-8');oldbridges['replaced_by_exclusive_bank_A_plane']=[q for q in oldbridges['bridges'] if q['net']=='/VBANK_A'];oldbridges['bridges']=[q for q in oldbridges['bridges'] if q['net']!='/VBANK_A'];(O/'POWER_ISLAND_BRIDGES.json').write_text(json.dumps(oldbridges,indent=2),encoding='utf-8')
(O/'POWER_LAYER_RESERVATION.json').write_text(json.dumps(dict(exclusive_layer='In5.Cu',net='/VBANK_A',moved_signal_sections=moved,current_rating_qualified=False),indent=2),encoding='utf-8');print('Reserved In5.Cu, moved',len(moved),'signals',flush=True)
