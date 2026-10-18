"""Read-only Rev P circuit audit, independent of KiCad and archived pass flags.

This checks net assignments, NOT physical copper continuity, timings or SI.
Run: python scripts/revP/p_electrical_audit.py [--output path]
"""
from pathlib import Path
import argparse, collections, hashlib, json, re, xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / 'outputs/PCIe_AllM2_RevP'
BOARD = DESIGN / 'Main_20M2'


def expressions(text):
    """Yield immediate child s-expressions, honoring quoted/escaped parentheses."""
    depth = 0; quoted = False; escaped = False; start = 0
    for i, ch in enumerate(text):
        if quoted:
            if escaped: escaped = False
            elif ch == '\\': escaped = True
            elif ch == '"': quoted = False
            continue
        if ch == '"': quoted = True
        elif ch == '(':
            if depth == 1: start = i
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth == 1: yield text[start:i+1]
            if depth < 0: raise ValueError('Unbalanced s-expression')
    if depth or quoted: raise ValueError('Unbalanced s-expression')


def run():
    components = json.loads((BOARD/'COMPONENTS.json').read_text())
    cs = {c['ref']: c for c in components}
    ports = json.loads((DESIGN/'M2_PORTS.json').read_text())
    issues = []; checks = collections.Counter()
    def check(ok, category, detail):
        checks[category] += 1
        if not ok: issues.append({'category': category, 'detail': detail})
    pads = {}; track_nets = collections.Counter()
    for block in expressions((BOARD/'Main_20M2.kicad_pcb').read_text()):
        if block.startswith('(footprint '):
            ref = re.search(r'\(property "Reference" "([^"]+)"', block)[1]
            for pad in expressions(block):
                if not pad.startswith('(pad '): continue
                number = re.match(r'\(pad "([^"]*)"', pad)[1]
                if not number: continue
                net = re.search(r'\(net(?: \d+)? "([^"]*)"\)', pad)
                pads[ref, number] = net[1].replace('{slash}', '/') if net else ''
        elif re.match(r'\((segment|via)\s',block):
            net = re.search(r'\(net(?: \d+)? "([^"]*)"\)', block)
            if net: track_nets[net[1].replace('{slash}', '/')] += 1
    for c in components:
        for pin, net in c.get('pinmap', {}).items():
            actual = pads.get((c['ref'], pin))
            check(actual == net or (net.startswith('unconnected-') and bool(actual) and actual.startswith('unconnected-')), 'pcb_metadata', f'{c["ref"]}.{pin}: expected {net}; PCB {pads.get((c["ref"], pin))}')
    netlist = ET.parse(BOARD/'CONNECTIVITY.net').getroot()
    exported = {(n.get('ref'), n.get('pin')): net.get('name').replace('{slash}', '/') for net in netlist.findall('./nets/net') for n in net.findall('node')}
    for key, net in pads.items():
        if net and not net.startswith('unconnected-'):
            check(exported.get(key) == net, 'exported_netlist', f'{key}: PCB {net}; export {exported.get(key)}')
    nodes = collections.defaultdict(list)
    for (ref,pin),net in pads.items(): nodes[net].append((ref,pin))
    signal_to_pin = {name: pin for pin,name in cs['U1']['pin_names'].items()}
    allocated = [0,1,2,3]; reset = []; output_rails = []; clocks=[]
    rx_pins = [(43,41),(31,29),(19,17),(7,5)]
    tx_pins = [(49,47),(37,35),(25,23),(13,11)]
    powerpins = ['2','4','12','14','16','18','70','72','74']
    for port in ports:
        name,ref = port['port'],port['ref']; pm=cs[ref]['pinmap']
        allocated += port['pex_lanes']
        for local,lane in enumerate(port['pex_lanes']):
            for direction,pin_pairs in [('RX',rx_pins),('TX',tx_pins)]:
                for pol,connectorpin in zip('PN',pin_pairs[local]):
                    net=f'/{name}_{direction}{local}_{pol}'
                    check(pads['U1',signal_to_pin[f'{direction}{pol}[{lane}]']]==net,'lane_endpoint',net)
                    end=net+'_AC' if direction=='TX' else net
                    check(pm[str(connectorpin)]==end,'connector_endpoint',f'{ref}.{connectorpin}: {end}')
                    if direction=='TX':
                        caps=[c['ref'] for c in components if c['ref'].startswith('C') and set(c.get('pinmap',{}).values())=={net,end}]
                        check(len(caps)==1,'tx_ac_coupling',f'{net}: {caps}')
        for pin in powerpins: check(pm[pin]==f'/{name}_3V3','slot_power',f'{ref}.{pin}')
        resetnet=f'/{name}_PERST'; rn=nodes[resetnet]
        down=[r for r,p in rn if r.startswith('R') and '/GND' in cs[r]['pinmap'].values()]
        drivers=[(r,p) for r,p in rn if cs[r].get('pin_types',{}).get(p) in ('output','open_collector')]
        reset.append({'port':name,'nodes':rn,'pulldowns':down,'verified_release_drivers':drivers,'copper_objects_on_net':track_nets[resetnet]})
        for pol,pin in [('P','55'),('N','53')]:
            net=f'/{name}_CLK_{pol}'
            sources=[(r,p) for r,p in nodes[net] if r in ('U601','U602','U6501')]
            check(len(sources)==1 and pm[pin]==net,'clock_assignment',f'{name} {pol}: {sources}')
            clocks.append({'net':net,'buffer_pin':sources,'copper_objects':track_nets[net]})
        output_rails.append({'rail':f'/{name}_3V3','nodes':len(nodes[f'/{name}_3V3']),'copper_objects':track_nets[f'/{name}_3V3']})
    check(len(allocated)==len(set(allocated)) and set(allocated)==set(range(84)), 'lane_budget','CPU x4 + 20 downstream x4 must allocate exactly 0..83')
    for c in components:
        if c['value'].startswith('TPSM53604'):
            for pin in ('4','5'):
                net=pads[c['ref'],pin]
                check(net.startswith('unconnected-') and len(nodes[net])==1,'module_dnc',f'{c["ref"]}.{pin}')
            check(c['pinmap']['7']==c['pinmap']['8'],'module_vout',c['ref'])
    result={'scope':'Static assignments only. Does not establish copper connectivity or hardware operation.',
            'production_ready':False,'checks':dict(checks),'contract_failures':issues,
            'reset_networks':reset,'clock_assignments':clocks,'slot_rails':output_rails,
            'blocking_findings':[
                'No verified PERST release driver on any of the 20 slots.',
                'CPU PMIC, reset sequencing, clock enable firmware and switch port configuration remain incomplete.',
                'Custom power USB connector is not connected to the main bus.',
                'Mechanical-only JHL9580 has no electrical implementation.',
                'No impedance, skew, copper current, thermal or connector qualification is established.'],
            'inputs_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [BOARD/'Main_20M2.kicad_pcb',BOARD/'COMPONENTS.json',BOARD/'CONNECTIVITY.net',DESIGN/'M2_PORTS.json']}}
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args()
    report=run();text=json.dumps(report,indent=2,ensure_ascii=False)+'\n'
    if args.output: args.output.write_text(text)
    else: print(text)
    raise SystemExit(bool(report['contract_failures']))
