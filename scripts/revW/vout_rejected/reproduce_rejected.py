"""KiCad10 Python: reproduce_rejected.py EXACT_SOURCE_PROJECT NEW_SCRATCH_ROOT.
Produces a KNOWN INVALID board solely to reproduce rejected DRC geometry. Never merge.
"""
import pathlib,sys,hashlib,shutil
source,work=map(pathlib.Path,sys.argv[1:]);assert not work.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source/'Main_12E1S.kicad_pcb')=='a501903278d07b19a431bb5bfb35a8012abc06ce05154d7c82ad7a32a5abfe19'
assert sha(source/'Main_12E1S.kicad_pro')=='9086611e035a0210cfc1bdfb30769d78d36880dd96954c8f5b869291103f8f30'
work.mkdir();shutil.copytree(source,work/'Base');shutil.copytree(source,work/'Candidate3')
import pcbnew as p,json,shutil
from pathlib import Path
r=work;src=r/'Base/Main_12E1S.kicad_pcb';dst=r/'Candidate3/Main_12E1S.kicad_pcb';assert src.with_suffix('.kicad_pro').read_bytes()==dst.with_suffix('.kicad_pro').read_bytes();b=p.LoadBoard(str(src));fs={f.GetReference():f for f in b.GetFootprints()};xy=lambda t:p.VECTOR2I(p.FromMM(t[0]),p.FromMM(t[1]));new=[]
for ref,pos,angle in [('C5115',(71.8,34.35),180),('R5151',(70.25,33.45),180),('R5152',(70.05,34.75),180)]:fs[ref].SetPosition(xy(pos));fs[ref].SetOrientationDegrees(angle)
fs['TP711'].Flip(fs['TP711'].GetPosition(),False)
for ref,pin,width,pts in [('C5115','1',.075,[(72.28,34.35),(72.28,33.95),(73.75,33.95),(74,34.2)]),('C5115','2',.15,[(71.32,34.35),(71.55,34.0),(71.55,32.42),(72.15,32.42)]),('R5151','1',.1,[(70.76,33.45),(70.09,33.7)]),('R5152','1',.1,[(70.37,34.75),(70.28,34.75)])]:
 q=next(q for q in fs[ref].Pads()if q.GetNumber()==pin)
 for a,z in zip(pts,pts[1:]):
  t=p.PCB_TRACK(b);t.SetStart(xy(a));t.SetEnd(xy(z));t.SetWidth(p.FromMM(width));t.SetLayer(p.B_Cu);t.SetNetCode(q.GetNetCode());b.Add(t);new.append(dict(uuid=t.m_Uuid.AsString(),ref=ref+'.'+pin,net=t.GetNetname(),length=p.ToMM(t.GetLength())))
p.SaveBoard(str(dst),b)
text=dst.read_text()
for item,u in zip(new,['6d6e89ec-50e9-4ae0-9d42-411931a2e6ab', '2be43596-5dd8-4992-8492-f68e69a2670a', 'acb79bd1-05b6-4382-afd2-21368e9c19b8', 'aa318411-435f-4f74-aac7-439c7b800d7a', 'f99f9a76-8fdc-4c3e-954e-1622df870a13', '3aa94b73-d3db-4379-9c7e-66f02fc34432', '5dbf7d7f-386e-48de-8c28-477a819bb1de', '35e99243-e313-450a-a8ee-7b9fed6acc77']):
 text=text.replace(item['uuid'],u);item['uuid']=u
dst.write_text(text);b=p.LoadBoard(str(dst))
shutil.copy2(dst,r/'Prefill3.kicad_pcb');shutil.copy2(dst.with_suffix('.kicad_pro'),r/'Prefill3.kicad_pro');assert p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(dst),b);(r/'BUILD3.json').write_text(json.dumps(dict(added=[x['uuid']for x in new],routes=new,moved=[fs[x].m_Uuid.AsString()for x in ['C5115','R5151','R5152','TP711']]),indent=2))

assert sha(work/'Candidate3/Main_12E1S.kicad_pcb')=='4ee99eaea34f90c8768feba0a1ad95d6e22d2988646d4f56fc2745f3daaa801d'
print('Known-rejected candidate reproduced exactly; do not merge.')
