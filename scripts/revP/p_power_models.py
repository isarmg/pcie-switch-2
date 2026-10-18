"""Truthful Rev P ERC types from TI pin tables, preserving every net and UUID.
U31 TPS62132: TI SLVSAG7F table 6-1 (fixed 3.3-V variant).
U605 TPS3808: TI SBVS050 pin functions; MR voltage-domain issue remains open.
U3001..U3004 TPS565201: TI SLVSE71 pin table. VBST is an analog floating
bootstrap supply, not an independent output or a ready external power rail.
No PWR_FLAG, no NC marker, no ERC exclusion is added by this script.
"""
from pathlib import Path
import argparse,json,re
ROOT=Path(__file__).resolve().parents[2]
DEFAULT=ROOT/'outputs/PCIe_AllM2_RevP/Main_20M2'
def models():
    buck={str(n):(name,kind) for n,name,kind in [
        (1,'SW','power_out'),(2,'SW','passive'),(3,'SW','passive'),
        (4,'PG','open_collector'),(5,'FB','input'),(6,'AGND','power_in'),
        (7,'FSW','input'),(8,'DEF','input'),(9,'SS_TR','passive'),
        (10,'AVIN','power_in'),(11,'PVIN','power_in'),(12,'PVIN','power_in'),
        (13,'EN','input'),(14,'VOS','input'),(15,'PGND','power_in'),(16,'PGND','power_in'),(17,'EP_GND','power_in')]}
    reset={'1':('RESET','open_collector'),'2':('GND','power_in'),'3':('MR','input'),'4':('CT','passive'),'5':('SENSE','input'),'6':('VDD','power_in')}
    end={'1':('GND','power_in'),'2':('SW','power_out'),'3':('VIN','power_in'),'4':('VFB','input'),'5':('EN','input'),'6':('VBST','passive')}
    return {'U31':buck,'U605':reset,**{f'U{3000+i}':end for i in range(1,5)}}
def apply(folder):
    path=folder/'COMPONENTS.json';data=json.loads(path.read_text());cs={q['ref']:q for q in data};model=models()
    before={r:dict(c['pinmap']) for r,c in cs.items()}
    for ref,pins in model.items():
        c=cs[ref];assert set(c['pinmap'])==set(pins),(ref,'pin map differs')
        assert c['value'].startswith('TPS62132' if ref=='U31' else 'TPS3808' if ref=='U605' else 'TPS565201')
        c['pin_names']={pin:name for pin,(name,kind) in pins.items()};c['pin_types']={pin:kind for pin,(name,kind) in pins.items()}
        c['datasheet']='https://www.ti.com/lit/ds/symlink/'+('tps62132' if ref=='U31' else 'tps3808' if ref=='U605' else 'tps565201')+'.pdf'
        c['erc_model_note']='Manufacturer pin functions; paralleled SW terminals represented by one driver; analog timing/bootstrap pins passive. No power-domain, startup or copper guarantee.'
    assert before=={r:c['pinmap'] for r,c in cs.items()}
    changed=[];seen=set()
    for file in [folder/'Local.kicad_sym',*folder.glob('*.kicad_sch')]:
        text=file.read_bytes().decode();lines=[];current=None
        for line in text.splitlines(keepends=True):
            m=re.search(r'\(symbol "(?:Local:)?PART_([^"_]+)(?:_\d+_\d+)?"',line)
            if m:current=m[1]
            if current in model and line.startswith('(pin '):
                pin=re.search(r'\(number "([^"]+)"',line)[1];name,kind=model[current][pin]
                line=re.sub(r'^\(pin \S+ line',f'(pin {kind} line',line)
                line=re.sub(r'\(name "[^"]*"',f'(name "{name}"',line,count=1);seen.add((current,pin))
            lines.append(line)
        new=''.join(lines)
        if new!=text:file.write_bytes(new.encode());changed.append(file.name)
    expected={(r,pin) for r,pins in model.items() for pin in pins};assert seen==expected,(expected-seen,seen-expected)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'updated_files':changed,'modeled_pins':len(seen),'nets_changed':False,'U605_MR_domain_fixed':False},indent=2))
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--folder',type=Path,default=DEFAULT);apply(a.parse_args().folder)
