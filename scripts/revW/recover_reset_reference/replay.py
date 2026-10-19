"""Reconstruct the published reset correction. Requires KiCad 10 pcbnew.
Never modifies the input project. Formal project copied before load/refill.
"""
from pathlib import Path
import hashlib,json,re,shutil,sys
import pcbnew as p
src,dst=map(Path,sys.argv[1:3]);delta=json.loads(Path(__file__).with_name('DELTA.json').read_text())
assert src.is_dir() and not dst.exists()
board=src/'Main_12E1S.kicad_pcb';pro=src/'Main_12E1S.kicad_pro'
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
assert sha(board)==delta['baseline_pcb_sha256']
assert sha(pro)=='9086611e035a0210cfc1bdfb30769d78d36880dd96954c8f5b869291103f8f30'
s=board.read_text()
for q in delta['removed']:
 assert s.count(q['before'])==1,q['uuid'];s=s.replace(q['before'],'',1)
for q in delta['replaced']:
 assert s.count(q['before'])==1,q['uuid'];s=s.replace(q['before'],q['after'],1)
assert hashlib.sha256(s.encode()).hexdigest()==delta['prefill_sha256']
shutil.copytree(src,dst);out=dst/board.name;out.write_text(s)
shutil.copyfile(out,dst.parent/'CORRECTION_PREFILL.kicad_pcb')
b=p.LoadBoard(str(out));b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(out),b)
assert sha(dst/pro.name)==sha(pro)
assert sha(out)==delta['expected_refilled_pcb_sha256'], "Refill differs from independently fixed candidate"
print(json.dumps({'pcb_sha256':sha(out),'pro_sha256':sha(pro),'scope':'19 deleted copper; 2 GND geometric replacements; no footprint/schematic changes'}))
