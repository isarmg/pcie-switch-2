"""replay.py EXACT_SOURCE_REVW_DIR NEW_REVW_DIR. No geometry refilling or normalization."""
from pathlib import Path
import json,sys,hashlib,base64,shutil
r=Path(__file__).resolve().parent;src,dst=map(Path,sys.argv[1:]);d=json.loads((r/'DELTA.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest();assert not dst.exists()
for f in d['files']:assert sha((src/f['path']).read_bytes())==f['before_sha256'],f['path']
shutil.copytree(src,dst)
for f in d['files']:
 p=dst/f['path'];b=p.read_bytes()
 for e in reversed(f['patches']):assert b[e['start']:e['end']]==base64.b64decode(e['before_base64']);b=b[:e['start']]+base64.b64decode(e['after_base64'])+b[e['end']:]
 assert sha(b)==f['after_sha256'],f['path'];p.write_bytes(b)
print('Exact guarded metadata selection reproduced; no copper geometry changed.')
