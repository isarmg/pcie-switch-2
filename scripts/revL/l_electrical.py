"""Mandatory external biases and Intel's required EPD loop from pp116-121."""
from pathlib import Path
import sys,json
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2')
sys.path.insert(0,str(R/'scripts/revJ'))
import i_common as c
from i_common import *
O=R/'outputs/PCIe_3board_RevL';folder=O/'Main_10E1S';bp=folder/'Main_10E1S.kicad_pcb';b=p.LoadBoard(str(bp))
a=object.__new__(Board);a.b=b;a.folder=folder;a.lib=folder/'Local.pretty';a.models=folder/'models';a.cs=[];a.newrefs=[];a.nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
meta={x['ref']:x for x in json.loads((folder/'COMPONENTS.json').read_text(encoding='utf-8'))}
renames={'/CPU_EPD_ON_IN':'/CPU_EPD_ON_LOOP_1V25','/CPU_EPD_ON_OUT':'/CPU_EPD_ON_LOOP_1V25','/CPU_PLT_PWROK_1V8':'/CPU_PLT_PWROK','/CPU_RSMRST_1V8_N':'/CPU_RSMRST_N'}
for ff in b.GetFootprints():
    for pp in ff.Pads():
        if pp.GetNetname() in renames:pp.SetNet(a.net(renames[pp.GetNetname()]))
cpu=b.FindFootprintByReference('U502')
gpio={'GPP_V00':'/CPU_BATLOW_N','GPP_V01':'/CPU_ACPRESENT','GPP_E21':'/CPU_PMCALERT_N','GPP_V12':'/CPU_WAKE_N'}
for pp in cpu.Pads():
    primary=meta['U502']['pin_names'][pp.GetNumber()].split('/')[0]
    if primary in gpio:pp.SetNet(a.net(gpio[primary]))
for i,(nn,pull) in enumerate([('/CPU_BATLOW_N','/CPU_VCCPRIM_1P8'),('/CPU_ACPRESENT','/CPU_VCCPRIM_1P8'),('/CPU_PMCALERT_N','/CPU_VCCPRIM_1P8'),('/CPU_WAKE_N','/CPU_VCCPRIM_1P8'),('/CPU_RSMRST_N','/GND'),('/CPU_PLT_PWROK','/GND'),('/CPU_SYS_PWROK_1V8','/GND')]):
    ref=f'R{740+i}'
    if not b.FindFootprintByReference(ref):a.place(ref,'10k / Intel required external bias','R_0402_1005Metric',0,0,{'1':nn,'2':pull},'B',0,.4)
for e in a.cs:meta[e['ref']]=e
# KiCad uses the open_collector enum for both open-collector and open-drain
# pins. "open_drain" is not a valid symbol-file token and prevents the CPU
# cached symbol, and neighbouring cached symbols, from loading.
meta['U502']['pin_types']={k:('open_collector' if v=='open_drain' else v) for k,v in meta['U502']['pin_types'].items()}
for ff in b.GetFootprints():
    e=meta[ff.GetReference()];e.update(pinmap={pp.GetNumber():pp.GetNetname() for pp in ff.Pads() if pp.GetNumber()})
    for old,new in renames.items():
        if old in ff.GetValue():ff.SetValue(ff.GetValue().replace(old,new));e['value']=ff.GetValue()
(folder/'COMPONENTS.json').write_text(json.dumps(list(meta.values()),ensure_ascii=False,indent=2),encoding='utf-8')
p.SaveBoard(str(bp),b)
print('Added required external biases and joined EPD_ON_IN/OUT; unverified control voltages left unnamed.',flush=True)
