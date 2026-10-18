"""Audit every native PCB pad using KiCad 10 connectivity, without work/ inputs.

Run with KiCad 10's Python (pcbnew). Never treats a selected stitch list as a
complete net. Does not edit the board, refill zones, or suppress violations.
"""
from pathlib import Path
from collections import defaultdict, Counter
import argparse
import hashlib
import json
import pcbnew as p

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT/'outputs/PCIe_E1S_96x45_USB12mm_RevW'

def display_name(name):
    return name.replace('{slash}', '/')

def audit(output=DEFAULT):
    board_path = output/'Main_12E1S/Main_12E1S.kicad_pcb'
    board = p.LoadBoard(str(board_path))
    conn = board.GetConnectivity()
    pads = {q.m_Uuid.AsString(): q for f in board.GetFootprints() for q in f.Pads() if q.GetNumber()}
    visited = set()
    nets = defaultdict(list)
    def name(q):
        return q.GetParentFootprint().GetReference()+'.'+q.GetNumber()
    no_net = []
    intentional_nc = []
    for uid, pad in pads.items():
        net = pad.GetNetname()
        if not net:
            no_net.append(name(pad))
            continue
        if net.startswith('unconnected-'):
            intentional_nc.append(name(pad))
            continue
        if uid in visited:
            continue
        # KiCad 10 returns the complete physically connected cluster, including
        # pad/track/via and filled-zone connectivity, not just direct neighbors.
        items = conn.GetConnectedItems(pad)
        group_ids = {q.m_Uuid.AsString() for q in items if isinstance(q, p.PAD) and q.GetNetname()==net}
        group_ids.add(uid)
        visited.update(group_ids)
        group_pads = [pads[x] for x in group_ids if x in pads]
        nets[net].append({
            'unique_ref_pin': sorted({name(q) for q in group_pads}),
            'physical_pad_shapes': len(group_pads),
            'dnp_ref_pin': sorted({name(q) for q in group_pads if q.GetParentFootprint().IsDNP()}),
        })
    details = [{ 'net': net, 'connected_components': len(groups),
                 'unique_ref_pin_count':len({v for g in groups for v in g['unique_ref_pin']}),
                 'physical_pad_shapes':sum(g['physical_pad_shapes'] for g in groups),
                 'groups':groups} for net, groups in sorted(nets.items())]
    legacy_path = output/'POWER_CONNECTIVITY.json'
    legacy = json.loads(legacy_path.read_text()) if legacy_path.exists() else {}
    legacy_rows = [pin for n in legacy.get('nets',[]) for g in n['groups'] for pin in g]
    legacy_by_net = {n['net']: {pin for g in n['groups'] for pin in g} for n in legacy.get('nets',[])}
    missing = {n['net']:sorted({pin for g in n['groups'] for pin in g['unique_ref_pin']}-legacy_by_net[display_name(n['net'])])
               for n in details if display_name(n['net']) in legacy_by_net}
    routes_path = output/'SIGNAL_ROUTES.json'
    routes = json.loads(routes_path.read_text()) if routes_path.exists() else {}
    route_list = routes.get('routes',[]) if isinstance(routes,dict) else routes
    pairs = defaultdict(list)
    for route in route_list:
        if route.get('paired'):
            pairs[route['group']].append(route)
    paired_layers=defaultdict(dict)
    for route in route_list:
        if route.get('paired') and route['net'].endswith(('_P','_N')):
            paired_layers[route['net'][:-2]][route['net'][-1]]=route['layer_name']
    different_layers=[{'section':key,**layers} for key,layers in sorted(paired_layers.items())
                      if len(set(layers.values()))>1]
    length_path=output/'SIGNAL_ROUTE_LENGTHS.json'
    lengths=json.loads(length_path.read_text()) if length_path.exists() else []
    result={
        'kicad_version':p.Version(),
        'board_sha256':hashlib.sha256(board_path.read_bytes()).hexdigest(),
        'method':'All numbered native pad shapes, KiCad 10 GetConnectedItems physical clusters; saved zone fills',
        'all_numbered_pad_shapes':len(pads),
        'all_unique_ref_pin_count':len({name(q) for q in pads.values()}),
        'connected_net_pad_shapes_audited':len(visited),
        'intentional_nc_ref_pins':sorted(set(intentional_nc)),
        'no_net_ref_pins':sorted(set(no_net)),
        'net_count':len(details),
        'disconnected_net_count':sum(n['connected_components']>1 for n in details),
        'all_nets_connected':all(n['connected_components']==1 for n in details),
        'legacy_power_report_rows':len(legacy_rows),
        'legacy_power_report_unique_ref_pin_count':len(set(legacy_rows)),
        'legacy_omitted_ref_pins_by_net':{n:ps for n,ps in missing.items() if ps},
        'differential_sections_with_P_N_on_different_layers':different_layers,
        'differential_sections_with_P_N_on_different_layers_count':len(different_layers),
        'largest_recorded_geometric_skews_mm':sorted(lengths,key=lambda x:x['geometric_skew_mm'],reverse=True)[:20],
        'length_source_note':'Historical routed-section records; excludes package/via electrical delays; not SI qualification',
        'current_and_thermal_qualified':False,'si_and_impedance_qualified':False,
        'production_ready':False,'nets':details,
    }
    target=output/'NATIVE_ALL_PAD_AUDIT.json'
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k in ['kicad_version','all_numbered_pad_shapes','all_unique_ref_pin_count','net_count','disconnected_net_count','legacy_power_report_rows','legacy_power_report_unique_ref_pin_count','differential_sections_with_P_N_on_different_layers_count']},indent=2))
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=DEFAULT)
    audit(parser.parse_args().output)
