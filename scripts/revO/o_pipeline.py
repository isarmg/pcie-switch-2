from pathlib import Path
import subprocess,sys
sys.stdout.reconfigure(encoding='utf-8')
H=Path(__file__).resolve().parent;R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');W=R/'work/revO';W.mkdir(parents=True,exist_ok=True)
K='C:/Program Files/KiCad/10.0/bin/python.exe'
stages={'cad':[('o_power.py',),('o_schematic.py','Main_27M2'),('o_assembly.py',)],
        'export':[('o_exports.py','Main_27M2','drc','step','bottom','render'),('o_exports.py','Main_27M2','net'),('o_exports.py','Main_27M2','erc'),('o_exports.py','Assembly_View','step','render')],
        'stepcheck':[('o_stepcheck.py',)],'checks':[('o_exports.py','Main_27M2','drc'),('o_exports.py','Main_27M2','net'),('o_exports.py','Main_27M2','erc')]}
stages['finish']=stages['cad']+stages['export']+stages['stepcheck']
for script,*args in stages[sys.argv[1]]:
    q=subprocess.run([K,str(H/script),*args],capture_output=True)
    (W/(script+'_'+('_'.join(args))+'.log')).write_bytes(q.stdout+b'\n'+q.stderr)
    print(script,args,'exit',q.returncode,flush=True)
    if q.stdout:print(q.stdout.decode('utf-8',errors='replace')[-2200:],flush=True)
    if q.returncode:print(q.stderr.decode('utf-8',errors='replace')[-2200:],flush=True);raise SystemExit(q.returncode)
