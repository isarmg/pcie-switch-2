"""Rebuild guarded reset relocation and PLTRST in a new project. KiCad10 Python required."""
from pathlib import Path
import re,json,hashlib,shutil,sys,runpy
import pcbnew as p
HERE=Path(__file__).resolve().parent;src,dst=map(Path,sys.argv[1:3]);assert src.name==dst.name=='Main_12E1S' and not dst.exists()
assert hashlib.sha256((src/'Main_12E1S.kicad_pcb').read_bytes()).hexdigest()=='0083dece575e4515719c6dc3248dbae3c60fdb5734550eb05b64d91e5e4ad6b1'
assert hashlib.sha256((src/'Main_12E1S.kicad_pro').read_bytes()).hexdigest()=='9086611e035a0210cfc1bdfb30769d78d36880dd96954c8f5b869291103f8f30'
shutil.copytree(src,dst);shutil.copyfile(src.parent/'BOM.csv',dst.parent/'BOM.csv');board=dst/'Main_12E1S.kicad_pcb';s=board.read_text();refs=[]
for name in ['reset','cpu_perst']:
 F=HERE/'rebuild_reset'/name;m=json.loads((F/'summary.json').read_text())
 for q in m['footprint_replacements']:
  old=next(z for z in re.findall(r'\t\(footprint\b.*?\n\t\)',s,re.S)if f'(uuid "{q["uuid"]}")'in z);assert hashlib.sha256(old.encode()).hexdigest()==q['before_sha256'];s=s.replace(old,(F/q['file']).read_text().rstrip());refs.append(q['ref'])
 if m['remove_uuids']:
  olditems={q['uuid']:q for q in json.loads((F/'removed-items.json').read_text())}
  for u in m['remove_uuids']:
   z=olditems[u]['block'];assert s.count(z)==1;s=s.replace(z,'',1)
 s=s.rstrip()[:-1]+'\n'+(F/'patch.sexpr').read_text()+')\n'
board.write_text(s);b=p.LoadBoard(str(board));p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(board),b)
fps={f.GetReference():f for f in b.GetFootprints()};mp=dst/'COMPONENTS.json';raw=mp.read_bytes();meta=json.loads(raw)
for c in meta:
 if c['ref'] in refs:
  f=fps[c['ref']];c.update(x=p.ToMM(f.GetPosition().x),y=p.ToMM(f.GetPosition().y),side='B' if f.IsFlipped() else 'F',rotation_deg=f.GetOrientationDegrees())
 if c['ref']=='R725':
  assert not c.get('dnp',False);assert fps['R725'].IsDNP();c['dnp']=True;c['assembly_note']='DNP: external 10k PU conflicts with Intel PLTRST power-sequence internal 20k +/-30% pulldown. CPU rail/PEX load/brownout behavior still unqualified.'
newline='\r\n' if b'\r\n' in raw else '\n';mp.write_bytes((json.dumps(meta,ensure_ascii=False,indent=2)+'\n').replace('\n',newline).encode())
q=dst/'Connectivity_40.kicad_sch';raw=q.read_bytes();lines=raw.splitlines(keepends=True);count=0
for i,line in enumerate(lines):
 if b'(lib_id "Local:PART_R725")' in line:
  assert b'(dnp no)' in line;lines[i]=line.replace(b'(dnp no)',b'(dnp yes)',1);count+=1
assert count==1;q.write_bytes(b''.join(lines))
sys.argv=[str(HERE/'w_refresh_rebuild_tables.py'),str(dst)];runpy.run_path(str(HERE/'w_refresh_rebuild_tables.py'),run_name='__main__')
print('Rebuilt reset candidate',hashlib.sha256(board.read_bytes()).hexdigest())
