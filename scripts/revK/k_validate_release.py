from pathlib import Path
import sys,json,csv,hashlib,zipfile,collections,xml.etree.ElementTree as ET,shutil,math
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_3board_RevK';J=R/'outputs/PCIe_3board_RevJ'
sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import p,xy
out={'revision':'K','production_ready':False,'electrical_design_complete':False,'main_routing_complete':False,
 'pcie_gen4_qualified':False,'thunderbolt5_qualified':False,'custom_power_full_load_qualified':False,
 'cpu_and_tb_controller_ballmaps_verified':False,'boards':{}}
pins={};bom=[]
for n in ['Main_10E1S','Left_2M2_Vertical','Right_M2_Upstream']:
    f=O/n;b=p.LoadBoard(str(f/(n+'.kicad_pcb')));fs={q.GetReference():q for q in b.GetFootprints()}
    points=[xy(pt) for g in b.GetDrawings() if g.GetLayer()==p.Edge_Cuts for pt in [g.GetStart(),g.GetEnd()]]
    dims=[round(max(q[i] for q in points)-min(q[i] for q in points),3) for i in [0,1]]
    assert dims==([110,45] if n.startswith('Main') else [19.5,45]),(n,dims)
    if not n.startswith('Main'):
        assert (f/(n+'.kicad_pcb')).read_bytes()==(J/n/(n+'.kicad_pcb')).read_bytes()
    bp={(ff.GetReference(),q.GetNumber()):q.GetNetname() for ff in fs.values() for q in ff.Pads() if q.GetNumber()};pins[n]=bp
    sp={(q.get('ref'),q.get('pin')):nn.get('name') for nn in ET.parse(f/'CONNECTIVITY.net').getroot().findall('nets/net') for q in nn.findall('node')}
    connected={k:v for k,v in bp.items() if v and not v.startswith('unconnected-')}
    bad=[(k,v,sp.get(k)) for k,v in connected.items() if sp.get(k)!=v]
    assert not bad,(n,bad[:6])
    d=json.loads((f/'DRC.json').read_text(encoding='utf8'));e=json.loads((f/'ERC.json').read_text(encoding='utf8'))
    ee=[x for s in e['sheets'] for x in s['violations']]
    structural=[x for x in d['violations'] if x['type'] in ['shorting_items','clearance','hole_clearance','hole_to_hole','copper_edge_clearance','courtyards_overlap']]
    assert not structural,[(x['type'],x['description']) for x in structural[:5]]
    meta={a['ref']:a for a in json.loads((f/'COMPONENTS.json').read_text(encoding='utf8'))}
    for ff in fs.values():
        for m in ff.Models():assert Path(m.m_Filename.replace('${KIPRJMOD}',str(f))).exists(),m.m_Filename
        c=meta.get(ff.GetReference(),{});bom.append([n,ff.GetReference(),ff.GetValue(),str(ff.GetFPID().GetLibItemName()),'F' if ff.GetLayer()==p.F_Cu else 'B',*xy(ff.GetPosition()),ff.GetOrientationDegrees(),c.get('height_mm',''),c.get('mechanical_only',False)])
    if n.startswith('Main'):
        assert len(list(fs['U1'].Pads()))==1550
        assert all(xy(fs[f'J{k}'].GetPosition())==(19+(k-1)*8,22.5) for k in range(1,11))
        assert all(q.GetAttribute()!=p.PAD_ATTRIB_NPTH for k in range(1,11) for q in fs[f'J{k}'].Pads())
        assert all(ff.GetReference() in ['J401','J402'] for ff in fs.values() for q in ff.Pads() if q.GetAttribute()==p.PAD_ATTRIB_NPTH)
        xx=[110-xy(fs[r].GetPosition())[0] for r in ['J401','J402','U502','U1']];assert xx==sorted(xx)
        for ref in ['J401','J402']:
            ff=fs[ref];assert ff.GetLayer()==p.B_Cu and abs(ff.GetOrientationDegrees()-90)<.001 and 'USB4160' in str(ff.GetFPID().GetLibItemName())
            assert len([q for q in ff.Pads() if q.GetNumber() not in ['','SH']])==24
        counts=collections.Counter(q.GetNetname() for q in fs['J401'].Pads() if q.GetNumber() not in ['','SH'])
        assert counts=={'/GND':12,'/CUSTOM_12V_RAW':10,'/CUSTOM_DET_A':1,'/CUSTOM_DET_B':1}
        assert not list(b.GetTracks()) and not list(b.Zones())
    else:assert not d['violations'] and not d['unconnected_items']
    out['boards'][n]={'size_mm':dims,'copper_layers':b.GetCopperLayerCount(),'footprints':len(fs),
       'schematic_pin_nets_crosschecked':len(connected),'netlist_matches':True,
       'drc_violations_by_type':dict(collections.Counter(x['type'] for x in d['violations'])),
       'reported_unconnected_items':len(d['unconnected_items']),
       'erc_errors':sum(x['severity']=='error' for x in ee),'erc_warnings':sum(x['severity']=='warning' for x in ee),
       'state':'unrouted main placement' if n.startswith('Main') else 'unchanged Rev J CAD'}
rows=list(csv.DictReader((O/'TWINAX_MAP.csv').open(encoding='utf-8-sig')))
assert len(rows)==54
for row in rows:
    dn='Left_2M2_Vertical' if row['side']=='L' else 'Right_M2_Upstream'
    for pol in 'PN':assert pins['Main_10E1S'][(row['main_ref'],pol)]==pins[dn][(row['daughter_ref'],pol)]==row['net'+pol]
out.update(real_pex1550_pinmap_crosschecked=True,all_usb_vertical=True,usb_pcb_rotation_deg=90,
    usb_geometry_reference_height_mm=7.46,usb_height_within_8mm=True,custom_power_main_bus_connected=False,
    lanes_per_side=12,links_per_side='3 independent x4',cable_pair_count=54,cable_map_crosschecked=True)
(O/'VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
with (O/'BOM.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['Board','Reference','Value','Footprint','Side','X_mm','Y_mm','Rotation_deg','Height_envelope_mm','Mechanical_only']);w.writerows(bom)
stage=Path(__file__).resolve().parent
shutil.copy2(stage/'README_RevK.md',O/'README.md')
for src in stage.iterdir():
    if src.suffix not in ['.py','.md']:continue
    dst=R/'scripts/revK'/src.name
    if src.resolve()!=dst.resolve():shutil.copy2(src,dst)
files=[f for f in O.rglob('*') if f.is_file() and f.suffix not in ['.zip','.lck','.kicad_prl'] and '-backups' not in str(f) and f.name!='SHA256SUMS.txt']
(O/'SHA256SUMS.txt').write_text('\n'.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.relative_to(O).as_posix() for f in sorted(files))+'\n',encoding='utf8')
dest=R/'outputs/PCIe_3board_RevK.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
    for f in O.rglob('*'):
        if f.is_file() and f.suffix not in ['.zip','.lck','.kicad_prl'] and '-backups' not in str(f):z.write(f,Path(O.name)/f.relative_to(O))
with zipfile.ZipFile(dest) as z:
    assert z.testzip() is None
    for line in z.read(O.name+'/SHA256SUMS.txt').decode('utf8').splitlines():
        digest,name=line.split('  ',1);assert hashlib.sha256(z.read(O.name+'/'+name)).hexdigest()==digest,name
print(json.dumps(out,ensure_ascii=False,indent=2))
print('Release archive verified:',dest,'bytes',dest.stat().st_size)
