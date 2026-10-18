"""Refresh native BOM/pin coordinates after ECO; does not qualify component choices."""
import csv,json
import pcbnew as p
from w_power_models import DESIGN
F=DESIGN;b=p.LoadBoard(str(F/'Main_12E1S.kicad_pcb'));meta={x['ref']:x for x in json.loads((F/'COMPONENTS.json').read_text())}
with (F.parent/'BOM.csv').open('w',encoding='utf-8-sig',newline='') as bf,(F/'PIN_MAP.csv').open('w',encoding='utf-8-sig',newline='') as pf:
 bw=csv.writer(bf);pw=csv.writer(pf);bw.writerow(['Ref','Value','Footprint','Side','X_mm','Y_mm','Rotation_deg','Height_mm']);pw.writerow(['Ref','Pin','Signal','Net','X_mm','Y_mm'])
 for f in sorted(b.GetFootprints(),key=lambda f:f.GetReference()):
  r=f.GetReference();m=meta[r];bw.writerow([r,f.GetValue(),str(f.GetFPID().GetLibItemName()),'B' if f.IsFlipped() else 'F',p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y),f.GetOrientationDegrees(),m.get('height_mm','')])
  for q in sorted(f.Pads(),key=lambda q:q.GetNumber()):
   pw.writerow([r,q.GetNumber(),m.get('pin_names',{}).get(q.GetNumber(),''),q.GetNetname().replace('{slash}','/'),p.ToMM(q.GetPosition().x),p.ToMM(q.GetPosition().y)])
print('Refreshed BOM and native pad coordinates:',len(meta),'components')

plan={f.GetReference():dict(position_mm=[p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y)],side="B" if f.IsFlipped() else "F",rotation_deg=f.GetOrientationDegrees()) for f in b.GetFootprints()}
(F.parent/"PLACEMENT_PLAN.json").write_text(json.dumps(plan,indent=2)+"\n")
