from pathlib import Path
import sys,json,subprocess,concurrent.futures
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_82x45_TB3Host_RevT';W=R/'work/revT';W.mkdir(parents=True,exist_ok=True)
CLI='C:/Program Files/KiCad/10.0/bin/kicad-cli.exe'
def run(kind):
    f=O/'Main_10E1S';pcb=f/'Main_10E1S.kicad_pcb';sch=f/'Main_10E1S.kicad_sch'
    jobs={
      'drc':['pcb','drc','--severity-all','--format','json','-o',str(f/'DRC.json'),str(pcb)],
      'net':['sch','export','netlist','--format','kicadxml','-o',str(f/'CONNECTIVITY.net'),str(sch)],
      'erc':['sch','erc','--severity-all','--format','json','-o',str(f/'ERC.json'),str(sch)],
      'step':['pcb','export','step','--force','-o',str(f/'Main_10E1S.step'),str(pcb)],
      'bottom':['pcb','render','--side','bottom','--width','1000','--height','650','--quality','basic','--background','opaque','--zoom','1.45','-o',str(f/'bottom.png'),str(pcb)],
      'render':['pcb','render','--width','1000','--height','650','--quality','basic','--background','opaque','--rotate','320,0,20','--zoom','1.1','-o',str(f/'preview.png'),str(pcb)]}
    cmd=[CLI]+jobs[kind]
    if kind in ['bottom','render']:
        prefs=json.loads(Path('C:/Users/micro/AppData/Roaming/kicad/10.0/3d_viewer.json').read_text(encoding='utf-8'))
        presets=[q for q in prefs.get('layer_presets',[]) if all(k in q.get('layers',[]) for k in ['th_models','smd_models','virtual_models'])]
        assert presets;cmd+=['--preset',presets[0]['name']]
    rr=subprocess.run(cmd,capture_output=True,timeout=90 if kind in ['bottom','render'] else 300)
    (W/('Main_10E1S_'+kind+'.log')).write_bytes(rr.stdout+b'\n'+rr.stderr)
    out=dict(job=kind,exit=rr.returncode)
    if kind=='drc':
        d=json.loads((f/'DRC.json').read_text(encoding='utf-8'));out.update(violations=len(d['violations']),reported_unconnected=len(d['unconnected_items']))
    print(json.dumps(out),flush=True);assert rr.returncode==0,out
if __name__=='__main__':
    args=sys.argv[1:]
    if args and args[0]=='Main_10E1S':args=args[1:]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:list(ex.map(run,args or ['drc','net','erc','step']))
