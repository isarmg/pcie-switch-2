"""Reproduce the second reviewed rebuild group in a NEW project directory.
KiCad10 Python: SCRIPT SOURCE/Main_12E1S DEST/Main_12E1S.
No network access; existing outputs are never overwritten. Does not certify SI/PDN.
"""
from pathlib import Path
import sys,json,hashlib,shutil,runpy,re
import pcbnew as p
HERE=Path(__file__).resolve().parent;DATA=HERE/'rebuild_second';src,dst=map(Path,sys.argv[1:3])
assert src.name==dst.name=='Main_12E1S' and not dst.exists()
board=src/'Main_12E1S.kicad_pcb';project=board.with_suffix('.kicad_pro')
assert hashlib.sha256(board.read_bytes()).hexdigest()=='cfd3a2a3de7bbeedeb94c3c2c9f6a1422be7a8a71141d28c105f218bc0c4ac80'
assert hashlib.sha256(project.read_bytes()).hexdigest()=='9086611e035a0210cfc1bdfb30769d78d36880dd96954c8f5b869291103f8f30'
shutil.copytree(src,dst);shutil.copyfile(src.parent/'BOM.csv',dst.parent/'BOM.csv');board=dst/board.name
s=board.read_text()
for file in ['translators_delta.json','s12_delta.json']:
 d=json.loads((DATA/file).read_text())
 for x in d['removed_blocks']:
  block=x['block'] if isinstance(x,dict) else x
  assert s.count(block)==1;s=s.replace(block,'',1)
 for block in d['added_blocks']:
  uid=re.search(r'\(uuid "([^"]+)"\)',block).group(1);assert uid not in s
 s=s.rstrip();assert s[-1]==')';s=s[:-1]+'\n'+'\n'.join(d['added_blocks'])+'\n)\n'
board.write_text(s)
def run(name,args):
 sys.argv=[str(HERE/name),*map(str,args)];runpy.run_path(str(HERE/name),run_name='__main__')
run('w_correct_flash_package.py',['--design',dst,'--proof',dst.parent/'MPN_PROOF.json'])
run('w_rebuild_support_models.py',['--design',dst,'--proof',dst.parent/'SUPPORT_PROOF.json'])
s=board.read_text();d=json.loads((DATA/'BP_FINAL_delta.json').read_text())
for x in d['changed']:assert s.count(x['before'])==1;s=s.replace(x['before'],x['after'],1)
for x in d['removed']:assert s.count(x['block'])==1;s=s.replace(x['block'],'',1)
for x in d['added']:assert x['uuid'] not in s
s=s.rstrip();s=s[:-1]+'\n'+'\n'.join(x['block'] for x in d['added'])+'\n)\n';board.write_text(s)
shutil.copyfile(DATA/d['library_alias'],dst/'Local.pretty'/d['library_alias'])
run('w_sync_bp_rebuild.py',[dst])
b=p.LoadBoard(str(board));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(board),b)
run('w_refresh_rebuild_tables.py',[dst])
print('Rebuilt candidate:',board,hashlib.sha256(board.read_bytes()).hexdigest())
print('Run native DRC/parity/ERC/full-pad regression and reference audit before accepting.')
