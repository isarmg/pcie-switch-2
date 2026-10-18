"""Synchronize the guarded BP 0603 ECO attributes; copper delta is applied separately."""
from pathlib import Path
import sys,json,csv,io,re
D=Path(sys.argv[1]);value='4.7uF 10V X7R / GRM188Z71A475KE15D';fp='C_0603_1608Metric_BP_Official'
p=D/'COMPONENTS.json';b=p.read_bytes();meta=json.loads(b)
for c in meta:
 if c['ref']=='C9004':
  assert c['value']=='2.2uF 10V';c.update(value=value,footprint=fp,x=1.25,y=6.35,rotation_deg=90.0,height_mm=.95,mpn='GRM188Z71A475KE15D',qualification_note='Nominal 4.7uF 10V X7R; DC-bias effective capacity, startup ripple, thermal and mechanical qualification pending.')
 if c['ref']=='R9007':c['y']=4.65
 if c['ref']=='R9011':c['y']=4.15
newline='\r\n' if b'\r\n' in b else '\n';p.write_bytes((json.dumps(meta,ensure_ascii=False,indent=2)+'\n').replace('\n',newline).encode())
for p in [D/'Local.kicad_sym',*D.glob('*.kicad_sch')]:
 b=p.read_bytes();lines=b.splitlines(keepends=True);count=0
 for i,line in enumerate(lines):
  if any(k in line for k in [b'(symbol "PART_C9004"',b'(symbol "Local:PART_C9004"',b'(lib_id "Local:PART_C9004")']):
   assert b'2.2uF 10V' in line;lines[i]=line.replace(b'2.2uF 10V',value.encode()).replace(b'Local:C_0402_1005Metric',('Local:'+fp).encode());count+=1
 if count:p.write_bytes(b''.join(lines))
p=D/'CONNECTIVITY.net';b=p.read_bytes();pattern=rb'<comp ref="C9004">.*?</comp>';m=re.search(pattern,b,re.S);assert m
z=m.group().replace(b'2.2uF 10V',value.encode()).replace(b'Local:C_0402_1005Metric',('Local:'+fp).encode());p.write_bytes(b[:m.start()]+z+b[m.end():])
p=D.parent/'BOM.csv';b=p.read_bytes();rows=list(csv.DictReader(io.StringIO(b.decode())));fields=list(rows[0])
for r in rows:
 if 'C9004' in r.values():
  for k,v in list(r.items()):
   if v=='2.2uF 10V':r[k]=value
   if v=='C_0402_1005Metric':r[k]=fp
   if v=='Local:C_0402_1005Metric':r[k]='Local:'+fp
out=io.StringIO();w=csv.DictWriter(out,fieldnames=fields,lineterminator='\r\n' if b'\r\n' in b else '\n');w.writeheader();w.writerows(rows);p.write_text(out.getvalue(),newline='')
