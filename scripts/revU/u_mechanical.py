"""Apply user's 7.25mm nominal side-edge clearance and local placement repairs."""
from pathlib import Path
from collections import defaultdict
import sys,json,math,re
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_12slot_RevU';W=R/'work/revU';F=O/'Main_12E1S';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
b=p.LoadBoard(str(W/'Main.prepared.kicad_pcb'));m={q['ref']:q for q in json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'))};d=json.loads((W/'route_tasks.json').read_text(encoding='utf-8'));dy=26.54-xy(b.FindFootprintByReference('J1').GetPosition())[1]
moved={r for r in m if re.fullmatch(r'J(?:[1-9]|1[012])',r) or (re.fullmatch(r'C40\d\d',r) and not 4073<=int(r[1:])<=4080)}
via_moves={}
for q in d['tasks']+d['retained']:
    for end in ['a','b']:
        if q[end]['ref'] not in moved:continue
        e=q[end];via_moves[(q['net'],tuple(e['pt']))]=(e['pt'][0],e['pt'][1]+dy)
        for k in ['pt','pad_pt']:e[k][1]+=dy
for vv in d['vias']:
    key=(vv['net'],tuple(vv['pt']))
    if key in via_moves:vv['pt']=list(via_moves[key])
grounds=[]
for r in moved:
    if not r.startswith('J'):continue
    f=b.FindFootprintByReference(r)
    for pp in f.Pads():
        if pp.GetNetname()=='/GND':grounds.append(pp)
for t in b.GetTracks():
    if not isinstance(t,p.PCB_VIA):continue
    key=(t.GetNetname(),xy(t.GetPosition()))
    if key in via_moves:t.SetPosition(v(*via_moves[key]))
    elif t.GetNetname()=='/GND' and t.IsOnLayer(p.F_Cu) and any(pp.HitTest(t.GetPosition()) for pp in grounds):t.Move(v(0,dy))
for r in moved:b.FindFootprintByReference(r).Move(v(0,dy))
def pos(r,x,y,ang=None):
    f=b.FindFootprintByReference(r);f.SetPosition(v(x,y))
    if ang is not None:f.SetOrientationDegrees(ang)
def box(f):
    z=f.GetBoundingBox(False,False);return [p.ToMM(x) for x in [z.GetX(),z.GetY(),z.GetRight(),z.GetBottom()]]
def overlap(a,z,g=.025):return a[0]<z[2]+g and a[2]>z[0]-g and a[1]<z[3]+g and a[3]>z[1]-g
for r in ['F1','F2']:pos(r,*[xy(b.FindFootprintByReference(r).GetPosition())[0],42.2])
pos('L501',93.5,3.05,90);pos('C5115',95.1,39,90)
signal_nets={q['net'] for q in d['tasks']+d['retained']};fixed={r for r in m if b.FindFootprintByReference(r).GetLayer()==p.B_Cu or r in ['F1','F2','J101','J102'] or r in moved or re.fullmatch(r'C40\d\d',r) or any(n in signal_nets for n in m[r]['pinmap'].values())}
occupied=defaultdict(list)
for r in fixed:occupied[b.FindFootprintByReference(r).GetLayer()].append(box(b.FindFootprintByReference(r)))
pending=[r for r in m if r not in fixed];pending.sort(key=lambda r:-(lambda z:(z[2]-z[0])*(z[3]-z[1]))(box(b.FindFootprintByReference(r))))
for ref in pending:
    f=b.FindFootprintByReference(ref);old=xy(f.GetPosition());z=box(f);bounds=[z[0]-old[0],z[1]-old[1],z[2]-old[0],z[3]-old[1]];ll=f.GetLayer()
    candidates=[old]+[(xx/4,yy/4) for yy in range(3,178) for xx in range(3,381)]
    for x,y in candidates:
        zz=[x+bounds[0],y+bounds[1],x+bounds[2],y+bounds[3]]
        if zz[0]<.5 or zz[1]<.5 or zz[2]>95.5 or zz[3]>44.5:continue
        if all(not overlap(zz,o) for o in occupied[ll]):pos(ref,x,y);occupied[ll].append(zz);break
    else:raise RuntimeError(('packing',ref))
for ref in m:
    f=b.FindFootprintByReference(ref);m[ref].update(x=xy(f.GetPosition())[0],y=xy(f.GetPosition())[1],rotation_deg=f.GetOrientationDegrees())
# Shrink CPU via copper to the already used provisional 0.20mm HDI size;
# 0.50mm CPU pitch then has room for 0.10mm fanout traces and 0.075mm space.
cpu=b.FindFootprintByReference('U502');cpu_pts={xy(pp.GetPosition()) for pp in cpu.Pads()}
for t in b.GetTracks():
    if isinstance(t,p.PCB_VIA) and xy(t.GetPosition()) in cpu_pts:t.SetWidth(p.FromMM(.20))
d['vias']=[]
cu=[p.F_Cu]+[getattr(p,f'In{i}_Cu') for i in range(1,31)]+[p.B_Cu]
for t in b.GetTracks():
    if isinstance(t,p.PCB_VIA):d['vias'].append(dict(net=t.GetNetname(),pt=xy(t.GetPosition()),diameter=p.ToMM(t.GetWidth(t.TopLayer())),layers=[ll for ll in cu if t.IsOnLayer(ll)]))
(F/'COMPONENTS.json').write_text(json.dumps(list(m.values()),indent=2),encoding='utf-8');(W/'route_tasks.json').write_text(json.dumps(d,indent=2),encoding='utf-8');p.SaveBoard(str(W/'Main.prepared.kicad_pcb'),b)
mech=json.loads((O/'MECHANICAL_CLEARANCE.json').read_text());mech.update(footprint_origin_y_mm=26.54,translation_y_mm=3.04,device_body_y_min_mm=6.25,device_body_y_max_mm=37.75,nominal_body_side_to_bottom_edge_mm=7.25,nominal_opposite_side_clearance_mm=6.25);(O/'MECHANICAL_CLEARANCE.json').write_text(json.dumps(mech,indent=2),encoding='utf-8')
ports=json.loads((O/'E1S_PORTS.json').read_text());
for q in ports:q['position_mm'][1]=26.54
(O/'E1S_PORTS.json').write_text(json.dumps(ports,indent=2),encoding='utf-8')
print('Twelve connector origins Y=26.54mm; SSD lower side Y=37.75mm; bottom edge 45mm; nominal gap=7.25mm',flush=True)
