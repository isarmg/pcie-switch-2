from pathlib import Path
import concurrent.futures, subprocess, json, sys
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_3board_RevK';W=R/'work/revK'
CLI='C:/Program Files/KiCad/10.0/bin/kicad-cli.exe'
def run(job):
    name,kind=job;f=O/name;b=f/(name+'.kicad_pcb')
    cmds={
      'drc':['pcb','drc','--severity-all','--format','json','-o',str(f/'DRC.json'),str(b)],
      'step':['pcb','export','step','--force','-o',str(f/(name+'.step')),str(b)],
      'bottom':['pcb','render','--side','bottom','--width','1800','--height','900','--quality','high','--background','opaque','--zoom','1.45','-o',str(f/'bottom.png'),str(b)],
      'render':['pcb','render','--width','1800','--height','1000','--quality','high','--background','opaque','--rotate','320,0,20','--zoom',('0.67' if name=='Assembly_View' else '1.1'),'-o',str(f/'preview.png'),str(b)],
      'net':['sch','export','netlist','--format','kicadxml','-o',str(f/'CONNECTIVITY.net'),str(f/(name+'.kicad_sch'))],
      'erc':['sch','erc','--severity-all','--format','json','-o',str(f/'ERC.json'),str(f/(name+'.kicad_sch'))]
    }
    r=subprocess.run([CLI]+cmds[kind],capture_output=True)
    (W/(name+'_'+kind+'.log')).write_bytes(r.stdout+b'\n'+r.stderr)
    result={'board':name,'job':kind,'exit':r.returncode}
    if kind=='drc' and (f/'DRC.json').exists():
        d=json.loads((f/'DRC.json').read_text(encoding='utf8'));result.update(violations=len(d['violations']),unconnected=len(d['unconnected_items']))
    print(json.dumps(result),flush=True)
    if kind!='drc':assert r.returncode==0,result
if __name__=='__main__':
    name=sys.argv[1] if len(sys.argv)>1 else 'Main_10E1S'
    jobs=sys.argv[2:] or ['drc','step','bottom','render']
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(run,[(name,j) for j in jobs]))
