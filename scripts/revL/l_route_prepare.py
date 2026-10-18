from pathlib import Path
import sys,json,re
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2')
sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
O=R/'outputs/PCIe_3board_RevL';W=R/'work/revL';W.mkdir(parents=True,exist_ok=True)
bp=O/'Main_10E1S/Main_10E1S.kicad_pcb';b=p.LoadBoard(str(bp))
for t in list(b.GetTracks()):remove(b,t)
for z in list(b.Zones()):remove(b,z)
p.SaveBoard(str(W/'Main.pre_route.kicad_pcb'),b)
a=object.__new__(Board);a.b=b;a.nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
tasks=[];by_net={};groups={}
for f in b.GetFootprints():
    for pp in f.Pads():
        nn=pp.GetNetname();m=re.fullmatch(r'/CPU_(G5|PEX)_(TX|RX)([0-3])_([PN])',nn)
        clk=re.fullmatch(r'/CPU_REFCLK_([PN])',nn)
        if not(m or clk):continue
        if clk:group='CLK';idx=8
        else:
            bank,direction,lane,pol=m.groups();idx=int(lane)+(0 if (bank,direction) in [('G5','TX'),('PEX','RX')] else 4)
            group=f'{"CPU_TX" if idx<4 else "PEX_TX"}{int(lane)}'
        layer=getattr(p,f'In{29-2*idx}_Cu')
        by_net.setdefault(nn,[]).append({'ref':f.GetReference(),'pin':pp.GetNumber(),'pt':xy(pp.GetPosition())})
        groups[nn]={'group':group,'layer':layer,'layer_name':b.GetLayerName(layer)}
        # Filled/capped in-pad blind via geometry. Span/process remains subject
        # to a fabricator-approved HDI stackup, explicitly recorded in README.
        a.via(*xy(pp.GetPosition()),nn,layer,p.B_Cu,.25,.10)
for nn,points in sorted(by_net.items()):
    assert len(points)==2,(nn,points)
    tasks.append({'net':nn,**groups[nn],'a':points[0],'b':points[1],'width':.10})
# Local ground returns use actual VSS balls, with adjacent internal reference
# planes. Only these selected ground balls are stitched in this partial layout.
used=set()
for ref in ['U502','U1']:
    ff=b.FindFootprintByReference(ref);ground=[pp for pp in ff.Pads() if pp.GetNetname()=='/GND']
    source=[q for t in tasks for q in [t['a'],t['b']] if q['ref']==ref]
    targets=[]
    for bank in ['CLK','CPU_TX0','CPU_TX1','CPU_TX2','CPU_TX3']:
        pts=[q['pt'] for t in tasks if t['group']==bank for q in [t['a'],t['b']] if q['ref']==ref]
        if pts:targets.append(tuple(sum(q[k] for q in pts)/len(pts) for k in [0,1]))
    for target in targets:
        choices=[pp for pp in ground if (ref,pp.GetNumber()) not in used and all(math.dist(xy(pp.GetPosition()),q['pt'])>.70 for q in source)]
        pp=min(choices,key=lambda z:math.dist(xy(z.GetPosition()),target));used.add((ref,pp.GetNumber()))
        a.via(*xy(pp.GetPosition()),'/GND',p.In12_Cu,p.B_Cu,.25,.10)
vias=[]
for via in b.GetTracks():
    assert isinstance(via,p.PCB_VIA),'route_prepare expects unrouted Rev L base'
    vias.append({'net':via.GetNetname(),'pt':xy(via.GetPosition()),'diameter':.25,'layers':[l for l in sorted({t['layer'] for t in tasks}) if via.IsOnLayer(l)]})
(W/'cpu_route_tasks.json').write_text(json.dumps({'tasks':tasks,'vias':vias,'grid_mm':.05,'clearance_mm':.10,'selected_ground_balls':[list(z) for z in sorted(used)]},indent=2))
p.SaveBoard(str(W/'Main.cpu_vias.kicad_pcb'),b)
print('CPU link route tasks:',len(tasks),'blind vias:',len(vias),flush=True)
