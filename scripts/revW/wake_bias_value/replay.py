"""Apply only guarded R743 value substitutions into a new full RevW output directory.
Usage: python replay.py SOURCE_REVW_DIR NEW_REVW_DIR
"""
from pathlib import Path
import re, json, hashlib, shutil, sys
src, dst = map(Path, sys.argv[1:])
g = json.loads(Path(__file__).with_name('GUARD.json').read_text())
assert src.is_dir() and not dst.exists()
old, new = g['old_value'].encode(), g['new_value'].encode()
prepared = {}
for f in g['files']:
 rel = f['path']; b = (src / rel).read_bytes()
 assert hashlib.sha256(b).hexdigest() == f['before_sha256'], rel
 if rel.endswith('COMPONENTS.json'): pats = [rb'"ref": "R743".*?"value": "([^"]+)"']
 elif rel.endswith('.kicad_pcb'): pats = [rb'\(property "Reference" "R743".*?\(property "Value" "([^"]+)"']
 elif rel.endswith('.kicad_sch'): pats = [rb'\(symbol "Local:PART_R743".*?\(property "Value" "([^"]+)"', rb'\(lib_id "Local:PART_R743".*?\(property "Value" "([^"]+)"']
 elif rel.endswith('.kicad_sym'): pats = [rb'\(symbol "PART_R743".*?\(property "Value" "([^"]+)"']
 elif rel.endswith('.net'): pats = [rb'<comp ref="R743">.*?<value>(.*?)</value>', rb'<libpart lib="Local" part="PART_R743">.*?<field name="Value">(.*?)</field>']
 elif rel == 'BOM.csv': pats = [rb'R743,([^,]+),']
 else: raise AssertionError(rel)
 spans = []
 for pat in pats:
  matches = list(re.finditer(pat,b,re.S)); assert len(matches)==1, rel
  m = matches[0]; assert m[1] == old, rel; spans.append(m.span(1))
 assert len(spans) == f['substitutions']
 c = b
 for lo,hi in sorted(spans,reverse=True): c = c[:lo]+new+c[hi:]
 assert c.replace(new,old)==b
 assert hashlib.sha256(c).hexdigest()==f['after_sha256'], rel
 prepared[rel] = c
shutil.copytree(src,dst)
for rel,c in prepared.items(): (dst/rel).write_bytes(c)
print('Exact six-file, eight-substitution R743 correction reproduced.')
