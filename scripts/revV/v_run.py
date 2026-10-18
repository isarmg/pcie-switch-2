from pathlib import Path
import subprocess,sys
sys.stdout.reconfigure(encoding='utf-8')
stage=Path(__file__).resolve().parents[2];logs=stage/'work/revV';logs.mkdir(parents=True,exist_ok=True)
for mode in sys.argv[1:]:
    args=mode.split(':');name=args.pop(0)
    result=subprocess.run(['C:/Program Files/KiCad/10.0/bin/python.exe','-X','utf8',str(Path(__file__).with_name('v_'+name+'.py'))]+args,capture_output=True)
    (logs/(name+'.log')).write_bytes(result.stdout+b'\nSTDERR\n'+result.stderr)
    print('\n'.join(q for q in result.stdout.decode('utf-8',errors='replace').splitlines() if not q.startswith(('swig/python detected a memory leak','Adding duplicate'))),flush=True)
    if result.stderr:print(result.stderr.decode('utf-8',errors='replace')[-5000:],flush=True)
    if result.returncode:sys.exit(result.returncode)
