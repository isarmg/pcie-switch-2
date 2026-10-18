"""Refresh Rev P BOM and pad table from the current board, preserving CSV schema."""
from pathlib import Path
import csv,json
import pcbnew as p
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'outputs/PCIe_AllM2_RevP';F=D/'Main_20M2'
def display(x):return x.replace('{slash}','/')
def refresh():
    b=p.LoadBoard(str(F/'Main_20M2.kicad_pcb'));meta={q['ref']:q for q in json.loads((F/'COMPONENTS.json').read_text())}
    with (D/'BOM.csv').open('w',encoding='utf-8-sig',newline='') as bf,(F/'PIN_MAP.csv').open('w',encoding='utf-8-sig',newline='') as pf:
        bw=csv.writer(bf);pw=csv.writer(pf)
        bw.writerow(['Board','Reference','Value','Footprint','Side','X_mm','Y_mm','Rotation_deg','Height_envelope_mm','DNP','Mechanical_only'])
        pw.writerow(['Reference','Value','Pad','Signal_name','Net','X_mm','Y_mm','Side','Pad_type'])
        for f in sorted(b.GetFootprints(),key=lambda q:q.GetReference()):
            r=f.GetReference();m=meta[r];side='B' if f.IsFlipped() else 'F'
            bw.writerow(['Main_20M2',r,f.GetValue(),str(f.GetFPID().GetLibItemName()),side,p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y),f.GetOrientationDegrees(),m.get('height_mm',''),f.IsDNP(),m.get('mechanical_only',False)])
            for q in sorted(f.Pads(),key=lambda q:q.GetNumber()):
                if not q.GetNumber():continue
                pw.writerow([r,f.GetValue(),q.GetNumber(),m.get('pin_names',{}).get(q.GetNumber(),''),display(q.GetNetname()),p.ToMM(q.GetPosition().x),p.ToMM(q.GetPosition().y),side,q.GetAttribute()])
    print('Refreshed native BOM and pin table for',len(meta),'components')
if __name__=='__main__':refresh()
