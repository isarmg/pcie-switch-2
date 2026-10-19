"""Run with KiCad10 Python: replay.py EXACT_SOURCE_PROJECT_DIR NEW_PROJECT_DIR."""
import pathlib,sys,json,hashlib,shutil
import pcbnew as p
r=pathlib.Path(__file__).resolve().parent;d=json.loads((r/'DELTA.json').read_text());src,dst=map(pathlib.Path,sys.argv[1:]);name='Main_12E1S';board=src/(name+'.kicad_pcb');pro=src/(name+'.kicad_pro');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(board)==d['baseline_sha256'];assert sha(pro)==d['project_sha256'];assert not dst.exists();shutil.copytree(src,dst);out=dst/board.name;s=out.read_text()
for a in d['replaced']:
 assert s.count(a['before'])==1
 s=s.replace(a['before'],a['after'],1)
for a in d['added']:assert a['uuid'] not in s
s=s.rstrip();assert s.endswith(')');s=s[:-1]+'\n'+'\n'.join(a['block'] for a in d['added'])+'\n)\n';out.write_text(s)
b=p.LoadBoard(str(out));b.BuildConnectivity();assert p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(out),b)

import re
rx=re.compile(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+')
def blocks(s):
 depth=0;start=None;out=[]
 for m in rx.finditer(s):
  t=m.group()
  if t=='(':
   depth+=1
   if depth==2:start=m.start()
  elif t==')':
   if depth==2:out.append(s[start:m.end()])
   depth-=1
 assert depth==0
 return out
def kind(b):return rx.findall(b)[1]
def inventory(p):
 out={}
 for b in blocks(p.read_text()):
  if kind(b) in ['footprint','segment','via','arc','zone']:
   u=re.search(r'\(uuid "([^"]+)"\)',b).group(1);out[u]=b
 return out
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

actual={u:hashlib.sha256(json.dumps(rx.findall(v)).encode()).hexdigest() for u,v in inventory(out).items()}
assert actual==d['expected_native_block_token_sha256']
print('All native footprint/copper/zone blocks reproduced:',len(actual),'file SHA:',sha(out))
