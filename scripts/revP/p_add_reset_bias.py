"""Add and locally route four missing end-slot reset pull-downs in Rev P.
Requires KiCad 10 pcbnew. Does not implement reset release or sequencing.
Idempotent: existing R3005/R3015/R3025/R3035 prevent a second application.
"""
from pathlib import Path
import csv, copy, json, re, uuid
import pcbnew as p
ROOT=Path(__file__).resolve().parents[2]; D=ROOT/'outputs/PCIe_AllM2_RevP'; B=D/'Main_20M2'

def uid(): return str(uuid.uuid4())
def v(x,y): return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def fx(): return '(effects (font (size 1 1)))'
def prop(n,val,x,y): return f'(property "{n}" "{val}" (at {x} {y} 0) {fx()})'

def main():
    b=p.LoadBoard(str(B/'Main_20M2.kicad_pcb'))
    refs=['R3005','R3015','R3025','R3035']
    existing=[b.FindFootprintByReference(r) is not None for r in refs]
    if all(existing): print('Reset bias patch already applied.'); return
    if any(existing): raise RuntimeError('Partial patch; inspect manually before continuing')
    meta=json.loads((B/'COMPONENTS.json').read_text()); byref={q['ref']:q for q in meta}
    sheet=B/'Connectivity_62.kicad_sch'; sch=sheet.read_text()
    rootpath=re.search(r'\(path "(/[^"]+)" \(reference "Y701"',sch)[1]
    symdefs=[]; instances=[]; new=[]
    def track(a,z,net):
        t=p.PCB_TRACK(b);t.SetStart(a);t.SetEnd(z);t.SetLayer(p.In1_Cu);t.SetWidth(p.FromMM(.10));t.SetNet(net);b.Add(t)
    def via(pos,net):
        q=p.PCB_VIA(b);q.SetPosition(pos);q.SetViaType(p.VIATYPE_MICROVIA);q.SetLayerPair(p.F_Cu,p.In1_Cu);q.SetWidth(p.FromMM(.25));q.SetDrill(p.FromMM(.10));q.SetNet(net);b.Add(q)
    for i,(ref,x) in enumerate(zip(refs,[6,12,108,114]),1):
        port=f'M{i}'; con=b.FindFootprintByReference(f'J{500+i}')
        cp={pad.GetNumber():pad for pad in con.Pads()}; net=cp['50'].GetNet();gnd=cp['51'].GetNet()
        f=p.FootprintLoad(str(B/'Local.pretty'),'R_0402_1005Metric');f.SetReference(ref)
        f.SetValue('100k / RESET BIAS ONLY - RELEASE DRIVER PENDING');f.SetPosition(v(x,28));f.SetOrientationDegrees(270)
        f.SetFPID(p.LIB_ID('Local','R_0402_1005Metric'));f.Reference().SetVisible(False);f.Value().SetVisible(False)
        ps={q.GetNumber():q for q in f.Pads()};ps['1'].SetNet(net);ps['2'].SetNet(gnd)
        sid=uid();path=p.KIID_PATH()
        for s in (rootpath+'/'+sid).strip('/').split('/'):path.push_back(p.KIID(s))
        f.SetPath(path);b.Add(f)
        # Adjacent-layer microvias avoid drilling through the back-side BGA.
        # The stackup/filled-via process still requires fabrication approval.
        for pad in [cp['50'],cp['51'],ps['1'],ps['2']]:via(pad.GetPosition(),pad.GetNet())
        a=cp['50'].GetPosition();z=ps['1'].GetPosition()
        first=p.VECTOR2I(a.x,a.y-p.FromMM(.2));bend=p.VECTOR2I(z.x,first.y)
        track(a,first,net);track(first,bend,net);track(bend,z,net)
        a=cp['51'].GetPosition();z=ps['2'].GetPosition();bend=p.VECTOR2I(a.x,z.y)
        track(a,bend,gnd);track(bend,z,gnd)
        c=copy.deepcopy(byref['R5015']);c.update(ref=ref,value=f.GetValue(),x=x,y=28,side='F',rotation_deg=270,pinmap={'1':f'/{port}_PERST','2':'/GND'},status='Locally copper-connected passive reset bias; no reset-release driver; fabrication process not qualified')
        meta.append(c);new.append(c)
        key=f'PART_{ref}';sy=round((170+(i-1)*24)/1.27)*1.27;sx=74.93
        definition=f'''(symbol "Local:{key}" (pin_names (offset .5)) (in_bom yes) (on_board yes)
{prop('Reference','R',0,0)}{prop('Value',f.GetValue(),0,0)}
(symbol "{key}_1_1" (rectangle (start -1.27 1.27) (end 1.27 -1.27) (stroke (width .254) (type default)) (fill (type background)))
(pin passive line (at -3.81 0 0) (length 2.54) (name "1" {fx()}) (number "1" {fx()}))
(pin passive line (at 3.81 0 180) (length 2.54) (name "2" {fx()}) (number "2" {fx()}))))'''
        symdefs.append(definition)
        instances.append(f'''(symbol (lib_id "Local:{key}") (at {sx} {sy} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{sid}")
{prop('Reference',ref,sx,sy-4)}{prop('Value',f.GetValue(),sx,sy-7)}{prop('Footprint','Local:R_0402_1005Metric',sx,sy)}
(pin "1" (uuid "{uid()}"))(pin "2" (uuid "{uid()}"))
(instances (project "Main_20M2" (path "{rootpath}" (reference "{ref}") (unit 1)))))
(global_label "/{port}_PERST" (shape passive) (at {sx-3.81} {sy} 180) {fx()} (uuid "{uid()}"))
(global_label "/GND" (shape passive) (at {sx+3.81} {sy} 0) {fx()} (uuid "{uid()}"))''')
    # Insert definitions into existing lib_symbols without rewriting other pages.
    sch=sch.replace('(lib_symbols ', '(lib_symbols '+'\n'.join(symdefs)+'\n',1)
    sch=sch.rstrip()[:-1]+'\n'+'\n'.join(instances)+'\n)\n'
    sheet.write_text(sch)
    library=B/'Local.kicad_sym';lib=library.read_text().rstrip()
    library.write_text(lib[:-1]+'\n'+'\n'.join(s.replace('(symbol "Local:','(symbol "',1) for s in symdefs)+'\n)\n')
    p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(B/'Main_20M2.kicad_pcb'),b)
    (B/'COMPONENTS.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n')
    with (D/'BOM.csv').open(encoding='utf-8-sig',newline='') as h:reader=csv.DictReader(h);fields=reader.fieldnames;rows=list(reader)
    for c in new:rows.append(dict(zip(fields,['Main_20M2',c['ref'],c['value'],c['footprint'],'F',c['x'],c['y'],270,.4,False,False])))
    with (D/'BOM.csv').open('w',encoding='utf-8-sig',newline='') as h:w=csv.DictWriter(h,fields);w.writeheader();w.writerows(rows)
    # Rebuild pad inventory from the actual board rather than assumed rotations.
    with (B/'PIN_MAP.csv').open(encoding='utf-8-sig',newline='') as h:fields=csv.DictReader(h).fieldnames
    with (B/'PIN_MAP.csv').open('w',encoding='utf-8-sig',newline='') as h:
        w=csv.DictWriter(h,fields);w.writeheader()
        for f in sorted(b.GetFootprints(),key=lambda f:f.GetReference()):
            for q in f.Pads():
                if not q.GetNumber():continue
                names=next((c.get('pin_names',{}) for c in meta if c['ref']==f.GetReference()),{})
                w.writerow(dict(zip(fields,[f.GetReference(),f.GetValue(),q.GetNumber(),names.get(q.GetNumber(),''),q.GetNetname(),p.ToMM(q.GetPosition().x),p.ToMM(q.GetPosition().y),'B' if f.GetLayer()==p.B_Cu else 'F',q.GetAttribute()])))
    print('Added four reset bias resistors, 16 adjacent-layer microvias, 20 In1.Cu segments. Run ERC and DRC before accepting.')
if __name__=='__main__': main()
