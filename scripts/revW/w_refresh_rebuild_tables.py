"""Refresh BOM, placement and pad coordinates from a specified native ECO design."""
import sys,json,csv,io
from pathlib import Path
import pcbnew as p
D=Path(sys.argv[1]);b=p.LoadBoard(str(D/'Main_12E1S.kicad_pcb'));meta={c['ref']:c for c in json.loads((D/'COMPONENTS.json').read_text())}
for filename,fields,rows in [('BOM.csv',['Ref','Value','Footprint','Side','X_mm','Y_mm','Rotation_deg','Height_mm','DNP'],[[f.GetReference(),f.GetValue(),str(f.GetFPID().GetLibItemName()),'B' if f.IsFlipped() else 'F',p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y),f.GetOrientationDegrees(),meta[f.GetReference()].get('height_mm',''),'yes' if f.IsDNP() else 'no'] for f in sorted(b.GetFootprints(),key=lambda f:f.GetReference())]),('PIN_MAP.csv',['Ref','Pin','Signal','Net','X_mm','Y_mm'],[[f.GetReference(),q.GetNumber(),meta[f.GetReference()].get('pin_names',{}).get(q.GetNumber(),''),q.GetNetname().replace('{slash}','/'),p.ToMM(q.GetPosition().x),p.ToMM(q.GetPosition().y)] for f in sorted(b.GetFootprints(),key=lambda f:f.GetReference()) for q in sorted(f.Pads(),key=lambda q:q.GetNumber())])]:
 dest=(D.parent if filename=='BOM.csv' else D)/filename
 with dest.open('w',encoding='utf-8-sig',newline='') as out:
  w=csv.writer(out);w.writerow(fields);w.writerows(rows)
plan={f.GetReference():dict(position_mm=[p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y)],side='B' if f.IsFlipped() else 'F',rotation_deg=f.GetOrientationDegrees()) for f in b.GetFootprints()}
(D.parent/'PLACEMENT_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
