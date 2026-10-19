"""KiCad10 Python: replay_full.py EXACT_SOURCE_REVW_DIR NEW_REVW_DIR.
Reproduce the PCB, schematic, BOM, placement and measured status as one guarded batch.
"""
from pathlib import Path
import sys,subprocess,shutil,json,hashlib,base64
src,dst=map(Path,sys.argv[1:]);here=Path(__file__).resolve().parent
assert src.is_dir() and not dst.exists()
patches=json.loads((here/'METADATA_DELTA.json').read_text())
for patch in patches:assert hashlib.sha256((src/patch['path']).read_bytes()).hexdigest()==patch['before_sha256']
shutil.copytree(src,dst,ignore=lambda path,names:['Main_12E1S'] if Path(path)==src else [])
subprocess.run([sys.executable,str(here/'replay3.py'),str(src/'Main_12E1S'),str(dst/'Main_12E1S')],check=True)
for patch in patches:
 f=dst/patch['path'];assert hashlib.sha256(f.read_bytes()).hexdigest()==patch['before_sha256'];b=base64.b64decode(patch['base64']);assert hashlib.sha256(b).hexdigest()==patch['after_sha256'];f.write_bytes(b)
print('Full guarded LDO placement batch reproduced, including BOM, placement and measured status.')
