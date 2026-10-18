from pathlib import Path
import subprocess,sys
sys.stdout.reconfigure(encoding='utf-8')
H=Path(__file__).resolve().parent;R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');W=R/'work/revM';W.mkdir(parents=True,exist_ok=True)
K='C:/Program Files/KiCad/10.0/bin/python.exe'
stages={'cad':[('m_schematic.py',),('m_assembly.py',)],
        'export':[('m_exports.py','Main_10E1S','drc','net','erc','step','bottom','render'),('m_exports.py','Assembly_View','step','render')],
        'stepcheck':[('m_stepcheck.py',)]}
stages['finish']=stages['cad']+stages['export']+stages['stepcheck']
stages['assembly']=[('m_assembly.py',),('m_exports.py','Assembly_View','step','render'),('m_stepcheck.py',)]
for script,*args in stages[sys.argv[1]]:
    q=subprocess.run([K,str(H/script),*args],capture_output=True)
    (W/(script+'.log')).write_bytes(q.stdout+b'\n'+q.stderr)
    print(script,'exit',q.returncode,flush=True)
    if q.stdout:print(q.stdout.decode('utf-8',errors='replace')[-3000:],flush=True)
    if q.returncode:
        print(q.stderr.decode('utf-8',errors='replace')[-3000:],flush=True);raise SystemExit(q.returncode)
