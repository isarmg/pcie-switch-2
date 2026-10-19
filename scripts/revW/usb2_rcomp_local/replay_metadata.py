"""Copy a RevW directory to a new destination and apply only guarded R708 metadata.
Usage: python replay_metadata.py SOURCE_REVW_DIR NEW_REVW_DIR
"""
from pathlib import Path
import sys,json,hashlib,shutil
src,dst=map(Path,sys.argv[1:]);d=json.loads(Path(__file__).with_name('METADATA_DELTA.json').read_text());assert not dst.exists();prepared={}
for f in d['files']:
 b=(src/f['path']).read_bytes();assert hashlib.sha256(b).hexdigest()==f['before_sha256'];old=f['before'].encode();new=f['after'].encode();assert b.count(old)==1;c=b.replace(old,new,1);assert hashlib.sha256(c).hexdigest()==f['after_sha256'];prepared[f['path']]=c
shutil.copytree(src,dst)
for rel,c in prepared.items():(dst/rel).write_bytes(c)
print('Exact R708-only metadata corrections reproduced.')
