from pathlib import Path
import subprocess,sys
sys.stdout.reconfigure(encoding='utf-8')
stage=Path(__file__).resolve().parents[2];logs=stage/'work/revU';logs.mkdir(parents=True,exist_ok=True)
python='C:/Program Files/KiCad/10.0/bin/python.exe'
for mode in sys.argv[1:]:
    args=mode.split(':');name=args.pop(0)
    result=subprocess.run([python,'-X','utf8',str(Path(__file__).with_name('u_'+name+'.py'))]+args,capture_output=True)
    (logs/(name+'.log')).write_bytes(result.stdout+b'\nSTDERR\n'+result.stderr)
    out=result.stdout.decode('utf-8',errors='replace');err=result.stderr.decode('utf-8',errors='replace')
    print('\n'.join(q for q in out.splitlines() if not q.startswith('swig/python detected a memory leak')),flush=True)
    if err:print(err[-6000:],flush=True)
    if result.returncode:sys.exit(result.returncode)
