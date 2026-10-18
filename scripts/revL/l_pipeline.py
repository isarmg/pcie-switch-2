from pathlib import Path
import subprocess,sys
sys.stdout.reconfigure(encoding='utf-8')
HERE=Path(__file__).resolve().parent
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');W=R/'work/revL';W.mkdir(parents=True,exist_ok=True)
K='C:/Program Files/KiCad/10.0/bin/python.exe'
PY='C:/Users/micro/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
stages={'refine':[(K,'l_electrical.py'),(K,'l_refine.py')],
        'route':[(K,'l_route_prepare.py'),(PY,'l_route_paired.py'),(K,'l_route_apply.py')],
        'route_fast':[(PY,'l_route_paired.py'),(K,'l_route_apply.py')],
        'cad':[(K,'l_schematic.py'),(K,'l_assembly.py')],
        'netcheck':[(K,'l_schematic.py'),(K,'l_exports.py','Main_10E1S','net','erc','drc')],
        'export':[(K,'l_exports.py','Main_10E1S','drc','net','erc','step','bottom','render'),(K,'l_exports.py','Assembly_View','step','render')],
        'stepcheck':[(K,'l_step_roundtrip.py')]}
for executable,script,*args in stages[sys.argv[1]]:
    result=subprocess.run([executable,str(HERE/script),*args],capture_output=True)
    (W/(script+'.log')).write_bytes(result.stdout+b'\n'+result.stderr)
    print(script,'exit',result.returncode,flush=True)
    if result.stdout:print(result.stdout.decode('utf-8',errors='replace')[-3000:],flush=True)
    if result.returncode:
        print(result.stderr.decode('utf-8',errors='replace')[-3000:],flush=True)
        raise SystemExit(result.returncode)
