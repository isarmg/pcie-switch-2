"""Native all-pad connectivity audit of Rev P, not capped by DRC's report list.
Run using KiCad 10 Python. Never edits the board or suppresses errors.
"""
from pathlib import Path
from collections import defaultdict, Counter
import argparse, hashlib, json
import pcbnew as p
ROOT=Path(__file__).resolve().parents[2]
DEFAULT=ROOT/'outputs/PCIe_AllM2_RevP/Main_20M2/Main_20M2.kicad_pcb'
def display(x):return x.replace('{slash}','/')
def audit(board_path):
    board=p.LoadBoard(str(board_path));conn=board.GetConnectivity()
    pads={q.m_Uuid.AsString():q for f in board.GetFootprints() for q in f.Pads() if q.GetNumber()}
    def name(q):return q.GetParentFootprint().GetReference()+'.'+q.GetNumber()
    visited=set();nets=defaultdict(list);nc=[];no_net=[]
    for uid,pad in pads.items():
        net=pad.GetNetname()
        if not net:no_net.append(name(pad));continue
        if net.startswith('unconnected-'):nc.append(name(pad));continue
        if uid in visited:continue
        group_ids={q.m_Uuid.AsString() for q in conn.GetConnectedItems(pad) if isinstance(q,p.PAD) and q.GetNetname()==net}|{uid}
        visited.update(group_ids);qs=[pads[u] for u in group_ids if u in pads]
        nets[net].append({'unique_ref_pin':sorted({name(q) for q in qs}),'physical_pad_shapes':len(qs),'dnp_ref_pin':sorted({name(q) for q in qs if q.GetParentFootprint().IsDNP()})})
    details=[{'net':n,'display_name':display(n),'connected_components':len(g),'unique_ref_pin_count':len({q for group in g for q in group['unique_ref_pin']}),'physical_pad_shapes':sum(group['physical_pad_shapes'] for group in g),'groups':g} for n,g in sorted(nets.items())]
    tracks=Counter(display(t.GetNetname()) for t in board.GetTracks())
    reset=[]
    for name_ in [f'M{i}' for i in range(1,5)]+[f'N{i:02}' for i in range(1,17)]:
        rows=[n for n in details if n['display_name']==f'/{name_}_PERST']
        reset.append({'port':name_,'copper_objects':tracks[f'/{name_}_PERST'],'net':rows})
    return {'kicad_version':p.Version(),'board_sha256':hashlib.sha256(board_path.read_bytes()).hexdigest(),
        'method':'Every numbered native pad; KiCad GetConnectedItems physical clusters with saved zone fills. NC pins listed separately, no DRC list cap.',
        'all_numbered_pad_shapes':len(pads),'all_unique_ref_pin_count':len({name(q) for q in pads.values()}),
        'connected_net_pad_shapes_audited':len(visited),'intentional_nc_ref_pins':sorted(set(nc)),'no_net_ref_pins':sorted(set(no_net)),
        'net_count':len(details),'disconnected_net_count':sum(n['connected_components']>1 for n in details),
        'all_nets_connected':all(n['connected_components']==1 for n in details),'reset_networks':reset,
        'production_ready':False,'si_and_impedance_qualified':False,'current_and_thermal_qualified':False,'nets':details}
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--board',type=Path,default=DEFAULT);a.add_argument('--output',type=Path,required=True);args=a.parse_args()
    result=audit(args.board);args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('nets','reset_networks','intentional_nc_ref_pins','no_net_ref_pins')},indent=2))
