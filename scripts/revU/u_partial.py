"""Independent native geometry audit of the copper accumulated so far."""
from pathlib import Path
from collections import Counter
import sys,json,shutil,subprocess
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');W=R/'work/revU';F=R/'outputs/PCIe_E1S_96x45_12slot_RevU/Main_12E1S';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
b=p.LoadBoard(str(W/'Main.prepared.kicad_pcb'));a=object.__new__(Board);a.b=b;a.nets={q.GetNetname():q for q in b.GetNetInfo().NetsByNetcode().values()};routes=json.loads((W/'progress.json').read_text(encoding='utf-8'))['routes']
for r in routes:
    for aa,bb in zip(r['points'],r['points'][1:]):a.track(aa,bb,r['net'],r['layer'],r['width'])
target=W/'Partial.kicad_pcb';p.SaveBoard(str(target),b);shutil.copy2(F/'Main_12E1S.kicad_pro',target.with_suffix('.kicad_pro'))
(W/'fp-lib-table').write_text('(fp_lib_table (lib (name "Local")(type "KiCad")(uri "'+(F/'Local.pretty').as_posix()+'")(options "")(descr "Actual project library for scratch DRC")))',encoding='utf-8')
rr=subprocess.run(['C:/Program Files/KiCad/10.0/bin/kicad-cli.exe','pcb','drc','--severity-all','--format','json','-o',str(W/'Partial.DRC.json'),str(target)],capture_output=True,timeout=300);assert rr.returncode==0
d=json.loads((W/'Partial.DRC.json').read_text(encoding='utf-8'));other=[q for q in d['violations'] if q['type']!='via_dangling'];print('Partial native copper check:',len(routes),'new sections;',Counter(q['type'] for q in d['violations']),'other than pending vias:',len(other),flush=True)
