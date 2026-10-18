from i_common import *
import subprocess,collections
out={}
for n in ['Main_10E1S','Left_2M2_Vertical','Right_M2_Upstream','Assembly_View']:
    path=ROOT/n/(n+'.step');source=path.read_text();b=p.BOARD();f=p.FOOTPRINT(b);f.SetReference('VALIDATE');m=p.FP_3DMODEL();m.m_Filename=path.as_posix();f.Models().append(m);b.Add(f);rect(b,0,0,20,20,p.Edge_Cuts)
    tmp=R/'work/revI'/f'{n}_roundtrip.kicad_pcb';p.SaveBoard(str(tmp),b);dest=tmp.with_suffix('.step');r=subprocess.run(['C:/Program Files/KiCad/10.0/bin/kicad-cli.exe','pcb','export','step',str(tmp),'--no-board-body','--force','-o',str(dest)],capture_output=True,text=True,encoding='utf8',errors='replace');log=r.stdout+'\n'+r.stderr;filtered='\n'.join(s for s in log.splitlines() if 'registry key' not in s);tmp.with_suffix('.log').write_text(log,encoding='utf8');assert r.returncode==0 and not any(s in filtered.lower() for s in ['cannot','failed','not found','error:']),filtered
    before=source.count('MANIFOLD_SOLID_BREP');after=dest.read_text().count('MANIFOLD_SOLID_BREP');assert before==after,(n,before,after);out[n]={'native_reimport_reexport':True,'unique_solid_definitions':before,'bytes':path.stat().st_size}
    print(n,before,'solid definitions; round-trip passed',flush=True)
(ROOT/'STEP_VALIDATION.json').write_text(json.dumps(out,indent=2))
