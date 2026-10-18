"""Explicitly leave unused mux unpopulated and model the TPS3808 supervisor.
Does not implement an SMBus topology or suppress any native diagnostic.
Requires KiCad10 Python; --design points to a standalone project directory.
"""
from pathlib import Path
import argparse,json,re,hashlib,csv,io,pcbnew as p

def end(s,start):
 depth=0;quote=False;escape=False
 for i in range(start,len(s)):
  c=s[i]
  if quote:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c=='"':quote=False
  elif c=='"':quote=True
  elif c=='(':depth+=1
  elif c==')':
   depth-=1
   if depth==0:return i+1
 raise ValueError('Unbalanced S-expression')
a=argparse.ArgumentParser();a.add_argument('--design',type=Path,required=True);a.add_argument('--proof',type=Path,required=True);x=a.parse_args();d=x.design
assert not x.proof.exists()
mp=d/'COMPONENTS.json';meta=json.loads(mp.read_text());by={q['ref']:q for q in meta};assert by['U510']['value'].startswith('TPS3808G33DBVR');assert by['U607']['value']=='TCA9548ARGER / SUPPORT NETWORK PENDING';assert not by['U607'].get('dnp')
pins={'1':'open_collector','2':'power_in','3':'input','4':'passive','5':'input','6':'power_in'};sources={'U510':'https://www.ti.com/lit/ds/symlink/tps3808.pdf','U607':'https://www.ti.com/lit/ds/symlink/tca9548a.pdf'}
changes=[];counts=[]
for f in [d/'Local.kicad_sym',*d.glob('*.kicad_sch')]:
 old=f.read_bytes();s=old.decode();m=re.search(r'\(symbol "(?:Local:)?PART_U510"',s)
 if m:
  j=end(s,m.start());block=s[m.start():j];seen=[]
  def pinfix(q):
   t=q.group(0);num=re.search(r'\(number "([^"]+)"',t).group(1);seen.append(num);return re.sub(r'^\(pin \S+ line',f'(pin {pins[num]} line',t)
  # Each source pin definition is one line; names/net labels remain unchanged.
  block=re.sub(r'^\(pin [^\r\n]+',pinfix,block,flags=re.M);assert set(seen)==set(pins);counts.append({'file':f.name,'pins':seen});s=s[:m.start()]+block+s[j:]
 if f.name=='Connectivity_54.kicad_sch':
  start=s.index('(symbol (lib_id "Local:PART_U607")');j=end(s,start);blk=s[start:j];assert '(dnp no)' in blk;blk=blk.replace('(dnp no)','(dnp yes)',1);s=s[:start]+blk+s[j:]
 if s.encode()!=old:f.write_bytes(s.encode());changes.append(f.name)
assert len(counts)==2
boardpath=d/'Main_12E1S.kicad_pcb';b=p.LoadBoard(str(boardpath));f=next(q for q in b.GetFootprints() if q.GetReference()=='U607');assert not f.IsDNP();f.SetDNP(True);p.SaveBoard(str(boardpath),b)
by['U607']['dnp']=True;by['U607']['assembly_note']='Unimplemented reference mux: all22 signal pins singleton. Keep DNP until master, channels, address and reset bias are defined.';by['U510']['pin_types']=pins;by['U510']['erc_model_source']=sources['U510'];by['U510']['erc_model_note']='SBVS050N Table5-1 p4; CT analog timing pin passive, RESET open collector.'
raw=mp.read_bytes();mp.write_bytes((json.dumps(meta,ensure_ascii=False,indent=2)+'\n').replace('\n','\r\n' if b'\r\n'in raw else '\n').encode())
bom=d.parent/'BOM.csv'
with bom.open(encoding='utf-8-sig',newline='') as h:
 reader=csv.DictReader(h);rows=list(reader);fields=list(reader.fieldnames)
assert sum(row['Ref']=='U607' for row in rows)==1
if 'DNP' not in fields:fields.append('DNP')
for row in rows:row['DNP']='yes' if by[row['Ref']].get('dnp',False) else 'no'
with bom.open('w',encoding='utf-8-sig',newline='') as h:
 writer=csv.DictWriter(h,fieldnames=fields);writer.writeheader();writer.writerows(rows)
x.proof.parent.mkdir(parents=True,exist_ok=True);x.proof.write_text(json.dumps({'sources':sources,'pin_model_files':counts,'changed_schematic_files':changes,'mux_unpopulated':True,'nets_or_geometry_changed':False,'limitations':['Management bus remains unimplemented; DNP does not satisfy system management requirements.','Supervisor supply/reset sequencing remain unqualified.']},indent=2)+'\n')
