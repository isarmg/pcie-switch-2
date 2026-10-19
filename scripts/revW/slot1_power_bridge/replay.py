"""Run with KiCad10 Python: replay.py EXACT_SOURCE_PROJECT_DIR NEW_PROJECT_DIR."""
import pathlib,sys,json,hashlib,shutil
import pcbnew as p
r=pathlib.Path(__file__).resolve().parent;d=json.loads((r/'DELTA.json').read_text());src,dst=map(pathlib.Path,sys.argv[1:]);name='Main_12E1S';board=src/(name+'.kicad_pcb');pro=src/(name+'.kicad_pro');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(board)==d['baseline_sha256'];assert sha(pro)==d['project_sha256'];assert not dst.exists();shutil.copytree(src,dst);out=dst/board.name;s=out.read_text()
for a in d['removed']:assert s.count(a['block'])==1,a['uuid']
for a in d['removed']:s=s.replace(a['block'],'',1)
for a in d['added']:assert a['uuid'] not in s
s=s.rstrip();assert s.endswith(')');s=s[:-1]+'\n'+'\n'.join(a['block'] for a in d['added'])+'\n)\n';out.write_text(s)
b=p.LoadBoard(str(out));b.BuildConnectivity();assert p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(out),b);assert sha(out)==d['candidate_sha256'];print('Exact guarded candidate reproduced:',sha(out))
