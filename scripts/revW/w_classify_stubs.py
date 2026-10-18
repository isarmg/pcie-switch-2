"""Keep relocation stubs on unimplemented real CPU rails outside the completed-power audit scope."""
from pathlib import Path
import json
path=Path('C:/Users/micro/Desktop/方案/pcie switch 2/work/revW/power_geometry.json')
d=json.loads(path.read_text(encoding='utf-8'))
pending=[q for q in d['control_routes'] if q['net'].startswith('/CPU_')]
d['control_routes']=[q for q in d['control_routes'] if not q['net'].startswith('/CPU_')]
d.setdefault('pending_cpu_rail_relocation_stubs',[]).extend(pending)
d['pending_cpu_rail_note']='Local capacitor relocation stubs retain their old landings only; CPU VR, full CPU power rails and sequencing remain unimplemented by user choice.'
path.write_text(json.dumps(d,indent=2),encoding='utf-8')
print('Separated',len(pending),'CPU relocation stub from implemented-power scope.')
