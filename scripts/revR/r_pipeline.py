from pathlib import Path
import subprocess,sys
sys.stdout.reconfigure(encoding='utf-8')
H=Path(__file__).resolve().parent;R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');W=R/'work/revR';W.mkdir(parents=True,exist_ok=True)
K='C:/Program Files/KiCad/10.0/bin/python.exe';PY='C:/Users/micro/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
stages={'cad':[('r_build.py',),('r_route_prepare.py',),('r_route.py',),('r_route_apply.py',),('r_schematic.py','Main_10E1S')],
        'export':[('r_exports.py','Main_10E1S','drc','step','render','bottom'),('r_exports.py','Main_10E1S','net'),('r_exports.py','Main_10E1S','erc')],
        'stepcheck':[('r_stepcheck.py',)]}
stages['finish']=stages['cad']+stages['export']+stages['stepcheck']
for script,*args in stages[sys.argv[1]]:
    q=subprocess.run([PY if script=='r_route.py' else K,str(H/script),*args],capture_output=True)
    (W/(script+'_'+('_'.join(args))+'.log')).write_bytes(q.stdout+b'\n'+q.stderr)
    print(script,args,'exit',q.returncode,flush=True)
    if q.stdout:print('\n'.join(z for z in q.stdout.decode('utf-8',errors='replace').splitlines() if 'swig/python detected' not in z)[-2200:],flush=True)
    if q.returncode:print(q.stderr.decode('utf-8',errors='replace')[-2200:],flush=True);raise SystemExit(q.returncode)
