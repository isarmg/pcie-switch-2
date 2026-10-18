from pathlib import Path
import sys,json
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2')
sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
O=R/'outputs/PCIe_3board_RevL';W=R/'work/revL';folder=O/'Main_10E1S'
b=p.LoadBoard(str(W/'Main.cpu_vias.kicad_pcb'));a=object.__new__(Board);a.b=b;a.nets={q.GetNetname():q for q in b.GetNetInfo().NetsByNetcode().values()}
d=json.loads((W/'cpu_routes.json').read_text())
for r in d['routes']:
    for x,y in zip(r['points'],r['points'][1:]):a.track(x,y,r['net'],r['layer'],r['width'])
for i in range(12,31,2):a.zone('/GND',getattr(p,f'In{i}_Cu'),[(.4,.4),(109.6,.4),(109.6,44.6),(.4,44.6)])
p.ZONE_FILLER(b).Fill(b.Zones())
p.SaveBoard(str(folder/'Main_10E1S.kicad_pcb'),b)
(O/'CPU_LINK_LENGTHS.json').write_text(json.dumps(d['pairs'],indent=2))
(folder/'ROUTING_STATUS.json').write_text(json.dumps({'cpu_x4_and_refclock_copper_connections':len(d['routes']),'cpu_data_pairs':8,'cpu_refclock_pairs':1,'coupled_sections':d.get('coupled_sections',[]),'whole_board_state':'partially routed; most power/support/downstream nets remain unrouted','length_tuning_complete':False,'impedance_validated':False,'blind_via_stackup_validated':False,'production_ready':False},indent=2))
print('Applied CPU x4 and reference-clock copper geometry.',flush=True)
