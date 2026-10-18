from pathlib import Path
import subprocess,sys
sys.stdout.reconfigure(encoding='utf-8')
logs=Path(__file__).resolve().parents[2]/'work/revW';logs.mkdir(parents=True,exist_ok=True)
for mode in sys.argv[1:]:
 args=mode.split(':');name=args.pop(0)
 proc=subprocess.Popen(['C:/Program Files/KiCad/10.0/bin/python.exe','-X','utf8',str(Path(__file__).with_name('w_'+name+'.py'))]+args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 with (logs/(name+'.log')).open('wb') as log:
  for raw in proc.stdout:
   log.write(raw);log.flush();line=raw.decode('utf-8',errors='replace').rstrip()
   if not line.startswith(('swig/python detected a memory leak','Adding duplicate')):print(line,flush=True)
 code=proc.wait()
 if code:sys.exit(code)
