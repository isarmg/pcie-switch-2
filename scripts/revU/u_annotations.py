from pathlib import Path
import sys,json
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_12slot_RevU';W=R/'work/revU';F=O/'Main_12E1S';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import p
b=p.LoadBoard(str(W/'Main.prepared.kicad_pcb'));tb=b.GetTitleBlock();tb.SetTitle('96 x 45 mm / 12 E1.S / 7.25 mm nominal SSD side clearance');tb.SetRevision('U');tb.SetComment(0,'FICTIONAL SWITCH / SIGNAL CONNECTIVITY DRAFT / NOT FOR FABRICATION')
for t in b.GetDrawings():
    if not isinstance(t,p.PCB_TEXT):continue
    s=t.GetText()
    for old,new in [('82x45','96x45'),('82 x 45','96 x 45'),('82 × 45','96 × 45'),('10 E1.S','12 E1.S'),('10E1S','12E1S'),('REV T','REV U')]:s=s.replace(old,new)
    t.SetText(s)
p.SaveBoard(str(W/'Main.prepared.kicad_pcb'),b)
pro=F/'Main_12E1S.kicad_pro';d=json.loads(pro.read_text());d['meta']['filename']='Main_12E1S.kicad_pro';pro.write_text(json.dumps(d,indent=2),encoding='utf-8')
meta=json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'));sw=next(q for q in meta if q['ref']=='U1');fake=json.loads((O/'PEX90064_FAKE_PINOUT.json').read_text());outs=[q for q in fake['ball_records'] if q['signal'].startswith('FAKE_3V3_PERST_OUT')]
for q in outs:sw.setdefault('pin_types',{})[q['ball']]='output'
fake['fake_3v3_io_outputs']=[dict(ball=q['ball'],signal=q['signal'],net=q['net']) for q in outs]
(O/'PEX90064_FAKE_PINOUT.json').write_text(json.dumps(fake,indent=2),encoding='utf-8');(F/'COMPONENTS.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
print('Updated U title and all twelve fictional reset output definitions.',flush=True)
