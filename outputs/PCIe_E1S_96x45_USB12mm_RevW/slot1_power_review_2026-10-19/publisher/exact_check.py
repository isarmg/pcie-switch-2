import pathlib,re,json,hashlib
D=pathlib.Path('/workspace/scratch/08a6fde47383/e1s-slot1-recovery-20261019');d=json.loads((D/'DELTA.json').read_text())
def blocks(s):
 depth=0; quoted=False;escape=False;start=None;out=[]
 for i,c in enumerate(s):
  if quoted:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c=='"':quoted=False
  elif c=='"':quoted=True
  elif c=='(':
   depth+=1
   if depth==2:start=i
  elif c==')':
   if depth==2:out.append(s[start:i+1])
   depth-=1
 assert depth==0
 return out
norm=lambda s:re.sub(r'\s+',' ',s).strip()
def objects(p):
 r={}
 for b in blocks(p.read_text()):
  kind=b.split()[0][1:]
  if kind not in ('segment','via','arc','footprint','zone'):continue
  u=re.search(r'\(uuid "([^\"]+)"\)',b).group(1)
  # Footprint first nested UUID may identify an attribute; map stable full blocks nonetheless.
  r[u]=(kind,norm(b))
 return r
base=objects(D/'Base/Main_12E1S.kicad_pcb');after=objects(D/'Candidate/Main_12E1S.kicad_pcb')
removed={a['uuid'] for a in d['removed']};added={a['uuid'] for a in d['added']}
assert base.keys()-after.keys()==removed
assert after.keys()-base.keys()==added
for u in base.keys()&after.keys():
 if base[u][0]!='zone':assert base[u]==after[u],u
for a in d['added']:assert after[a['uuid']][1]==norm(a['block'])
for a in d['removed']:assert base[a['uuid']][1]==norm(a['block'])
result={'removed_exact':len(removed),'added_exact':len(added),'retained_nonzone_objects_unchanged':True,'base_objects':len(base),'final_objects':len(after)}
pathlib.Path('/workspace/scratch/08a6fde47383/e1s-slot1-publisher-audit/EXACT_OBJECTS.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
