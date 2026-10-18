"""Read-only regression checks for the Rev W reset-domain ECO and net classes."""
from pathlib import Path
from collections import Counter
import fnmatch,hashlib,json
import pcbnew as p
from w_power_models import DESIGN
F=DESIGN
b=p.LoadBoard(str(F/'Main_12E1S.kicad_pcb'));conn=b.GetConnectivity()
fs={f.GetReference():f for f in b.GetFootprints()}
def display(x):return x.replace('{slash}','/')
def pad(ref,pin):return next(q for q in fs[ref].Pads() if q.GetNumber()==pin)
def group(q):return {t.GetParentFootprint().GetReference()+'.'+t.GetNumber() for t in conn.GetConnectedItems(q) if isinstance(t,p.PAD)}
expected={'1':'/PEX_SYS_RESET_N','2':'/GND','3':'/TBT_PCIE_PERST_3V3_N','4':'/PEX_RESET_CT','5':'/PEX_0V9','6':'/P3V3_AUX'}
for pin,net in expected.items():assert display(pad('U605',pin).GetNetname())==net,(pin,net)
assert 'C9040.1' in group(pad('U605','6'))
assert 'R9040.1' in group(pad('U605','3'))
# MR long branch remains unrouted: report actual physical connectivity, never hide it.
assert display(pad('R9040','2').GetNetname())=='/GND'
ground_group=group(pad('U605','2'))
assert 'C9040.2' in ground_group
added_ground_pins=['C5120.2','C931.2','C5119.2','C738.2','C901.2','C965.2','U701.4','Y501.2']
assert set(added_ground_pins)<=ground_group, sorted(set(added_ground_pins)-ground_group)
assert any(k.startswith('J101.') for k in ground_group), 'Local ground has not reached input ground'
classes=Counter();class_errors=[]
for net in b.GetNetInfo().NetsByNetcode().values():
    name=display(net.GetNetname())
    want='PCIe_DATA_DRAFT' if fnmatch.fnmatchcase(name,'/S*_SW_*') else 'REFCLK_DRAFT' if fnmatch.fnmatchcase(name,'/S*_REFCLK*') else 'Default'
    # KiCad 10 composite classes include Default as a fallback for properties.
    actual=set(net.GetNetClassName().split(','))-{'Default'}
    expected_classes=set() if want=='Default' else {want}
    if actual!=expected_classes:class_errors.append({'net':name,'expected':want,'actual':net.GetNetClassName()})
    classes[want]+=1
assert not class_errors,class_errors
result={'board_sha256':hashlib.sha256((F/'Main_12E1S.kicad_pcb').read_bytes()).hexdigest(),
        'reset_supply_domain_and_pin_mapping_passed':True,
        'local_bypass_to_U605_supply_copper_connected':True,
        'U605_and_bypass_ground_connected_to_input_ground':True,
        'U605_supply_cluster':sorted(group(pad('U605','6'))),
        'U605_MR_connected_to_U511_output': 'U511.4' in group(pad('U605','3')),
        'U605_MR_cluster':sorted(group(pad('U605','3'))),
        'R9040_ground_connected_to_input_ground':'R9040.2' in ground_group,
        'eight_added_ground_pads_in_input_ground_cluster':added_ground_pins,
        'netclass_assignment_checked_per_net':True,'netclass_counts':dict(classes),
        'cpu_supply_implemented':False,'brownout_transition_and_load_leakage_qualified':False,
        'reset_sequence_qualified':False,'production_ready':False}
(F.parent/'ECO_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
