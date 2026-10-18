from i_common import *
name='Right_M2_Upstream';o=ROOT/name;file=R/'work/revI'/f'{name}.placed.kicad_pcb';b=p.LoadBoard(str(file));left=p.LoadBoard(str(R/'work/revI/Left_2M2_Vertical.placed.kicad_pcb'));cs=json.loads((o/'COMPONENTS.json').read_text());old=b.FindFootprintByReference('J4');remove(b,old);cs=[c for c in cs if c['ref']!='J4']
# Match the two left-board socket centers and orientation exactly.
f=b.FindFootprintByReference('J3');dx,dy=14-xy(f.GetPosition())[0],17-xy(f.GetPosition())[1]
for ref in ['J3']+[f'C{320+i}' for i in range(8)]+['R310','R311']:b.FindFootprintByReference(ref).Move(v(dx,dy))
for ref,template in [('U23','U21'),('L3','L1')]+[(f'C{301+i}',f'C{101+i}') for i in range(6)]+[('R301','R101'),('R302','R102')]:b.FindFootprintByReference(ref).SetPosition(left.FindFootprintByReference(template).GetPosition())
for i in range(18):b.FindFootprintByReference(f'J{101+i}').SetPosition(v(1.4,2+2.3*i))
for i in range(8):
    f=b.FindFootprintByReference(f'C{420+i}');f.SetPosition(v(32,25-2.2*i));f.SetOrientationDegrees(180)
for g in list(b.GetDrawings()):
    if g.GetLayer()==p.Edge_Cuts:remove(b,g)
    elif isinstance(g,p.PCB_TEXT):
        if g.GetText().startswith('M3 /'):g.SetPosition(v(14,3.5))
        elif g.GetText().startswith('UP x4'):g.SetText('UPLINK / HOST ONLY');g.SetPosition(v(38,32))
        elif g.GetText().startswith('VERTICAL M-KEY'):g.SetPosition(v(26,1.1))
        elif '12V IN' in g.GetText():g.SetPosition(v(26,43.5))
rect(b,0,0,52,45,p.Edge_Cuts)
a=object.__new__(Board);a.b=b;a.name=name;a.w=52;a.h=45;a.folder=o;a.lib=o/'Local.pretty';a.models=o/'models';a.cs=cs;a.newrefs=[];a.root=uid();a.nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()};a.pro=json.loads((o/(name+'.kicad_pro')).read_text());a.plugin=p.PCB_IO_MGR.FindPlugin(p.PCB_IO_MGR.KICAD_SEXP)
pins=json.loads((R/'scripts/m2_pins.json').read_text());pm={}
for pin,fn in pins.items():
    if fn.startswith('GND') or pin=='69':nn='/GND'
    elif fn.startswith(('PET','PER')):
        lane=re.search(r'(\d)',fn)[1];pol='P' if fn[3]=='p' else 'N';d='RX' if fn.startswith('PET') else 'TX';nn=f'/UP_{d}{lane}_{pol}'+('_AC' if d=='TX' else '')
    elif fn.startswith('REFCLK'):nn='/UP_CLK_'+('P' if fn.endswith('p') else 'N')
    elif pin=='50':nn='/UP_PERST'
    elif pin=='52':nn='/UP_CLKREQ'
    elif pin=='54':nn='/UP_WAKE'
    else:nn=nc('J4',pin)
    pm[pin]=nn
pm.update(MP1='/GND',MP2='/GND')
a.place('J4','UPLINK M-Key / HOST ONLY','M2_MKey_VERTICAL_5p3_DRAFT',38,17,pm,angle=90,height=5.3,url='https://klsele.com/products/connectors/Card-connectors/M-2-NGFF-connectors/10763.html',names=pins)
for c in cs:c['x'],c['y']=xy(b.FindFootprintByReference(c['ref']).GetPosition());c['rotation_deg']=b.FindFootprintByReference(c['ref']).GetOrientationDegrees()
a.save();info=json.loads((ROOT/'BUILD.json').read_text());info['right_mm']=[52,45];info['upstream_interface']='Vertical M-Key socket, host via straight-through M.2 cable/adapter; not an SSD port';(ROOT/'BUILD.json').write_text(json.dumps(info,indent=2));print('Replaced edge upstream with vertical M-Key, socket centers (14,17)/(38,17), 52x45 mm.')
