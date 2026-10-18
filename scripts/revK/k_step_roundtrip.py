from pathlib import Path
import sys,json,subprocess
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_3board_RevK';W=R/'work/revK'
sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import p,rect
old=json.loads((R/'outputs/PCIe_3board_RevJ/STEP_VALIDATION.json').read_text())
out={n:{**old[n],'retained_from_unchanged_revision':'J'} for n in ['Left_2M2_Vertical','Right_M2_Upstream']}
for n in ['Main_10E1S','Assembly_View']:
    src=O/n/(n+'.step');before=src.read_text().count('MANIFOLD_SOLID_BREP');assert before>0
    b=p.BOARD();f=p.FOOTPRINT(b);f.SetReference('STEP_VALIDATE');m=p.FP_3DMODEL();m.m_Filename=src.as_posix();f.Models().append(m);b.Add(f);rect(b,0,0,20,20,p.Edge_Cuts)
    temp=W/(n+'_step_readback.kicad_pcb');p.SaveBoard(str(temp),b);dst=temp.with_suffix('.step')
    r=subprocess.run(['C:/Program Files/KiCad/10.0/bin/kicad-cli.exe','pcb','export','step','--force','--no-board-body','-o',str(dst),str(temp)],capture_output=True)
    temp.with_suffix('.log').write_bytes(r.stdout+b'\n'+r.stderr);assert r.returncode==0
    after=dst.read_text().count('MANIFOLD_SOLID_BREP');assert before==after,(n,before,after)
    out[n]={'native_reimport_reexport':True,'unique_solid_definitions':before,'bytes':src.stat().st_size}
    print(n,before,'solid definitions; STEP round-trip passed',flush=True)
(O/'STEP_VALIDATION.json').write_text(json.dumps(out,indent=2))
