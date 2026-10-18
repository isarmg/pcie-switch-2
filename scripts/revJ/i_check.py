from pathlib import Path
import subprocess,sys,concurrent.futures,json,collections
R=Path(__file__).resolve().parents[2];O=R/'outputs/PCIe_3board_RevJ';CLI='C:/Program Files/KiCad/10.0/bin/kicad-cli.exe'
BASIC='--basic' in sys.argv
if BASIC:sys.argv.remove('--basic')
def run(q):
    folder,job=q;n=folder.name;board=folder/(n+'.kicad_pcb')
    args={'drc':['pcb','drc','--format','json','--all-track-errors','--severity-all','-o',str(folder/'DRC.json'),str(board)],'step':['pcb','export','step','--force','-o',str(folder/(n+'.step')),str(board)],'render':['pcb','render','--width','1500','--height','1000','--background','opaque','--quality','high','--rotate','320,0,20','--zoom','1.1','-o',str(folder/'preview.png'),str(board)],'bottom':['pcb','render','--width','1500','--height','1000','--background','opaque','--quality','high','--side','bottom','--zoom','1.7','-o',str(folder/'bottom.png'),str(board)],'erc':['sch','erc','--format','json','--severity-all','-o',str(folder/'ERC.json'),str(folder/(n+'.kicad_sch'))],'net':['sch','export','netlist','--format','kicadxml','-o',str(folder/'CONNECTIVITY.net'),str(folder/(n+'.kicad_sch'))]}
    if BASIC and job in ['render','bottom']:args[job][args[job].index('--quality')+1]='basic'
    if n=='Assembly_View' and job=='render':args[job][args[job].index('--zoom')+1]='0.72'
    if job=='drc':args[job].remove('--all-track-errors')
    r=subprocess.run([CLI]+args[job],capture_output=True,text=True,encoding='utf8',errors='replace');(R/f'work/revJ/{n}_{job}.log').write_text(r.stdout+'\n'+r.stderr,encoding='utf8');msg={'board':n,'job':job,'exit':r.returncode}
    if job=='drc' and (folder/'DRC.json').exists():
        d=json.loads((folder/'DRC.json').read_text(encoding='utf8'));msg.update(violations=dict(collections.Counter(v['type'] for v in d['violations'])),unconnected=len(d['unconnected_items']))
    print(json.dumps(msg),flush=True)
selected=next((z.split('=',1)[1] for z in sys.argv if z.startswith('--board=')),None)
if selected:sys.argv.remove('--board='+selected)
folders=[O/n for n in ([selected] if selected else ['Assembly_View'] if '--assembly' in sys.argv else ['Main_10E1S','Left_2M2_Vertical','Right_M2_Upstream'])]
if '--assembly' in sys.argv:sys.argv.remove('--assembly')
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(run,[(f,j) for f in folders for j in sys.argv[1:] or ['drc']]))
