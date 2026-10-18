"""Correct U504/U505 SS (208 mil) MPN to SN (150 mil), preserving copper.
Official Winbond W25Q80DV Rev N 2026-04-24, pp6/61/62/66/67.
Only explicit part-number tokens are changed; no pin/net/geometry/model changes.
"""
from pathlib import Path
import argparse,json,hashlib
OLD=b'W25Q80DVSSIG';NEW=b'W25Q80DVSNJG'
SOURCE='https://www.winbond.com/resource-files/W25Q80DV_revN_04242026%20Plus.pdf'
a=argparse.ArgumentParser();a.add_argument('--design',type=Path,required=True);a.add_argument('--proof',type=Path,required=True);args=a.parse_args();d=args.design
meta=json.loads((d/'COMPONENTS.json').read_text());targets=[x for x in meta if OLD.decode() in x['value']]
assert {x['ref'] for x in targets}=={'U504','U505'}
assert all(x['footprint']=='SOIC-8_3.9x4.9mm_P1.27mm' for x in targets)
paths=[d/'COMPONENTS.json',d/'Main_12E1S.kicad_pcb',d/'Local.kicad_sym',d/'CONNECTIVITY.net',d.parent/'BOM.csv',*d.glob('*.kicad_sch')]
updates=[]
for p in paths:
 b=p.read_bytes()
 if OLD not in b:continue
 z=b.replace(OLD,NEW)
 updates.append((p,b,z))
assert len(updates)>=5
assert not args.proof.exists()
proof={'official_source':SOURCE,'revision':'Preliminary N, 2026-04-24','pages':{'pinmap':6,'SN_dimensions':61,'SS_dimensions':62,'ordering':66,'valid_part_numbers':67},'correction':{'refs':['U504','U505'],'old':OLD.decode(),'new':NEW.decode(),'actual_footprint':'SOIC-8_3.9x4.9mm_P1.27mm','package':'SN 150mil, nominal 3.9x4.9mm, 1.27mm pitch, max height1.75mm','temperature':'J: -40 to105C; endurance qualification is at85C per manufacturer note','pin_network_geometry_change':False},'files':[{'path':str(p),'replacements':b.count(OLD),'before_sha256':hashlib.sha256(b).hexdigest(),'after_sha256':hashlib.sha256(z).hexdigest()}for p,b,z in updates],'limitations':['NVM image, host SPI mode, sequencing and rail implementation remain unqualified.','MPN selection is not procurement availability or manufacturing approval.']}
for p,b,z in updates:assert p.read_bytes()==b;p.write_bytes(z)
args.proof.parent.mkdir(parents=True,exist_ok=True);args.proof.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'files':len(updates),'refs':['U504','U505']}))
