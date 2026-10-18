from pathlib import Path
import sys,json,collections
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
O=R/'outputs/PCIe_E1S_82x45_TB3Host_RevT';W=R/'work/revT';folder=O/'Main_10E1S'
b=p.LoadBoard(str(W/'Main.signal_vias.kicad_pcb'));current=p.LoadBoard(str(folder/'Main_10E1S.kicad_pcb'))
paths={f.GetReference():f.GetPath() for f in current.GetFootprints()}
for f in b.GetFootprints():f.SetPath(paths[f.GetReference()])
a=object.__new__(Board);a.b=b;a.nets={q.GetNetname():q for q in b.GetNetInfo().NetsByNetcode().values()}
d=json.loads((W/'signal_routes.json').read_text(encoding='utf-8'));assert len(d['routes'])>=386
for r in d['routes']:
    for x,y in zip(r['points'],r['points'][1:]):a.track(x,y,r['net'],r['layer'],r['width'])
for i in range(1,29,3):a.zone('/GND',getattr(p,f'In{i}_Cu'),[(.4,.4),(81.6,.4),(81.6,44.6),(.4,44.6)])
for z in b.Zones():z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(folder/'Main_10E1S.kicad_pcb'),b)
(O/'SIGNAL_ROUTE_LENGTHS.json').write_text(json.dumps(d['pairs'],indent=2),encoding='utf-8')
(O/'SIGNAL_ROUTES.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
(folder/'ROUTING_STATUS.json').write_text(json.dumps(dict(allocated_pcie_data_and_clock_sections=300,slot_reset_connections=10,allocated_signal_sections_copper_routed=len(d['routes']),e1s_downstream_lanes=40,cpu_host_lanes=4,active_data_differential_pairs=88,reference_clock_differential_pairs=14,reserved_switch_lanes=20,e1s_tx_source_coupling_caps=80,all_allocated_pcie_data_clock_reset_routed=True,switch_pinout_is_fictional=True,fictional_reset_io_voltage=3.3,tb3_host_data_clock_routed=True,whole_board_routing_complete=False,cpu_and_switch_power_design_complete=False,length_tuning_complete=False,impedance_validated=False,blind_via_stackup_validated=False,production_ready=False),indent=2),encoding='utf-8')
build=json.loads((O/'BUILD.json').read_text(encoding='utf-8'));build.update(allocated_pcie_data_clock_reset_copper_sections=310,main_routing_complete=False,all_allocated_pcie_signal_routes_complete=True)
(O/'BUILD.json').write_text(json.dumps(build,ensure_ascii=False,indent=2),encoding='utf-8')
print('Applied',len(d['routes']),'signal/control sections; floating ground islands removed.',flush=True)
