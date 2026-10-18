from pathlib import Path
import json,sys,collections
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');F=R/'outputs/PCIe_E1S_96x45_12slot_RevU/Main_12E1S'
m=json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'))
for q in m:
    ref=q['ref'];pm=q['pinmap']
    if ref in ['U1','U502','U501','U503']:continue
    if ref in ['U31','U30','L31','U506','L502','U21','U22','J101','J102'] or (ref.startswith(('R','C','FB')) and (any(z in s for s in pm.values() for z in ['AUX','BUCK','PEX_0V','PEX_1V','P12_SLOT','S11_PWR','S12_PWR','S01_PWR']) or ref.startswith('C51'))):
        print(ref,q['value'],q['footprint'],q['side'],q['x'],q['y'],json.dumps(pm,separators=(',',':')))
import pcbnew as p
b=p.LoadBoard(str(F/'Main_12E1S.kicad_pcb'))
print('LAYERS',[(b.GetLayerName(l),sum(t.IsOnLayer(l) for t in b.GetTracks()),sum(z.IsOnLayer(l) for z in b.Zones())) for l in [p.F_Cu]+[getattr(p,f'In{i}_Cu') for i in range(1,31)]+[p.B_Cu]])
for ref in ['J101','F1','U11','U31','L31','U506']:
    f=b.FindFootprintByReference(ref)
    print('PADS',ref,[(q.GetNumber(),q.GetNetname(),[round(p.ToMM(z),6) for z in [q.GetPosition().x,q.GetPosition().y,q.GetSize().x,q.GetSize().y]]) for q in f.Pads()])
