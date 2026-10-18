from pathlib import Path
import sys,json,csv,hashlib,zipfile,collections,xml.etree.ElementTree as ET,shutil,math
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_3board_RevL';K=R/'outputs/PCIe_3board_RevK'
sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import p,xy
STAGE=Path(__file__).resolve().parents[2]
out={'revision':'L','production_ready':False,'electrical_design_complete':False,
     'main_routing_complete':False,'cpu_pmic_implemented':False,'firmware_boot_qualified':False,
     'pcie_gen4_qualified':False,'thunderbolt5_qualified':False,'custom_power_full_load_qualified':False,
     'cpu_land_pattern_manufacturer_approved':False,'hdi_process_validated':False,'boards':{}}
pins={};bom=[];boards={}
for n in ['Main_10E1S','Left_2M2_Vertical','Right_M2_Upstream']:
    f=O/n;bp=f/(n+'.kicad_pcb');b=p.LoadBoard(str(bp));boards[n]=b
    fs={q.GetReference():q for q in b.GetFootprints()}
    points=[xy(pt) for g in b.GetDrawings() if g.GetLayer()==p.Edge_Cuts for pt in [g.GetStart(),g.GetEnd()]]
    dims=[round(max(q[i] for q in points)-min(q[i] for q in points),3) for i in [0,1]]
    assert dims==([110,45] if n.startswith('Main') else [19.5,45]),(n,dims)
    if not n.startswith('Main'):assert bp.read_bytes()==(K/n/(n+'.kicad_pcb')).read_bytes()
    bpins={(ff.GetReference(),q.GetNumber()):q.GetNetname() for ff in fs.values() for q in ff.Pads() if q.GetNumber()};pins[n]=bpins
    sp={(q.get('ref'),q.get('pin')):nn.get('name') for nn in ET.parse(f/'CONNECTIVITY.net').getroot().findall('nets/net') for q in nn.findall('node')}
    connected={k:v for k,v in bpins.items() if v and not v.startswith('unconnected-')}
    bad=[(k,v,sp.get(k)) for k,v in connected.items() if sp.get(k)!=v]
    assert not bad,(n,bad[:10],len(bad))
    d=json.loads((f/'DRC.json').read_text(encoding='utf8'));e=json.loads((f/'ERC.json').read_text(encoding='utf8'))
    ee=[x for s in e['sheets'] for x in s['violations']]
    assert not d['violations'],(n,[(x['type'],x['description']) for x in d['violations'][:6]])
    if n.startswith('Main'):assert (f/'DRC.json').stat().st_mtime>=bp.stat().st_mtime
    else:assert not d['unconnected_items']
    meta={a['ref']:a for a in json.loads((f/'COMPONENTS.json').read_text(encoding='utf8'))}
    for ff in fs.values():
        for m in ff.Models():assert Path(m.m_Filename.replace('${KIPRJMOD}',str(f))).exists(),m.m_Filename
        c=meta.get(ff.GetReference(),{});side='F' if ff.GetLayer()==p.F_Cu else 'B'
        bom.append([n,ff.GetReference(),ff.GetValue(),str(ff.GetFPID().GetLibItemName()),side,*xy(ff.GetPosition()),ff.GetOrientationDegrees(),c.get('height_mm',''),ff.IsDNP(),c.get('mechanical_only',False)])
        if n.startswith('Main') and c.get('height_mm'):
            limit=8 if side=='B' else 9
            if ff.GetReference() not in [f'J{k}' for k in range(1,11)]:assert c['height_mm']<=limit,(ff.GetReference(),c['height_mm'])
    with (f/'PIN_MAP.csv').open('w',encoding='utf-8-sig',newline='') as fh:
        w=csv.writer(fh);w.writerow(['Reference','Value','Pad','Signal_name','Net','X_mm','Y_mm','Side','Pad_type'])
        for ref,ff in sorted(fs.items()):
            for q in ff.Pads():
                if q.GetNumber():w.writerow([ref,ff.GetValue(),q.GetNumber(),meta.get(ref,{}).get('pin_names',{}).get(q.GetNumber(),''),q.GetNetname(),*xy(q.GetPosition()),'B' if ff.GetLayer()==p.B_Cu else 'F',str(q.GetAttribute())])
    if n.startswith('Main'):
        assert b.GetCopperLayerCount()==32
        assert all(xy(fs[f'J{k}'].GetPosition())==(19+(k-1)*8,22.5) for k in range(1,11))
        assert all(q.GetAttribute()!=p.PAD_ATTRIB_NPTH for k in range(1,11) for q in fs[f'J{k}'].Pads())
        assert all(ff.GetReference() in ['J401','J402'] for ff in fs.values() for q in ff.Pads() if q.GetAttribute()==p.PAD_ATTRIB_NPTH)
        xx=[110-xy(fs[r].GetPosition())[0] for r in ['J401','J402','U502','U1']];assert xx==sorted(xx)
        for ref in ['J401','J402']:
            ff=fs[ref];assert ff.GetLayer()==p.B_Cu and abs(ff.GetOrientationDegrees()-90)<.001
            assert 'SMT_Shell' in str(ff.GetFPID().GetLibItemName())
            assert len([q for q in ff.Pads() if q.GetNumber() not in ['','SH']])==24
            sh=[q for q in ff.Pads() if q.GetNumber()=='SH'];assert len(sh)==4
            assert all(q.GetAttribute()==p.PAD_ATTRIB_SMD and q.GetDrillSize().x==0 and q.GetDrillSize().y==0 and q.IsOnLayer(p.B_Cu) and not q.IsOnLayer(p.F_Cu) for q in sh)
            assert len([q for q in ff.Pads() if q.GetAttribute()==p.PAD_ATTRIB_NPTH])==2
            assert len(list(ff.Models()))==10
        counts=collections.Counter(q.GetNetname() for q in fs['J401'].Pads() if q.GetNumber() not in ['','SH'])
        assert counts=={'/GND':12,'/CUSTOM_12V_RAW':10,'/CUSTOM_DET_A':1,'/CUSTOM_DET_B':1}
        for ref,pinfile,key,xform in [
            ('U502','INTEL_268V_PINOUT.json','pins',lambda q:(64.5-q['y_um']/1000,22.5+q['x_um']/1000)),
            ('U1','PEX88096_PINOUT.json','ball_records',lambda q:(22.5+q['x_mm'],22.5-q['y_mm']))]:
            data=json.loads((O/pinfile).read_text(encoding='utf-8'))[key];padmap={q.GetNumber():q for q in fs[ref].Pads()}
            assert len(padmap)==len(data)==(2833 if ref=='U502' else 1550)
            for record in data:
                q=padmap[record['ball']];assert math.dist(xy(q.GetPosition()),xform(record))<.000003,(ref,record['ball'],xy(q.GetPosition()),xform(record))
                assert meta[ref]['pin_names'][record['ball']]==record['signal']
                assert q.GetNetname()==meta[ref]['pinmap'][record['ball']]
            out[ref+'_ball_coordinates_crosschecked']=len(data)
        cpu=fs['U502'];cp={q.GetNumber():q for q in cpu.Pads()}
        assert pins[n][('U502','Y27')]==pins[n][('U502','AB27')]=='/CPU_EPD_ON_LOOP_1V25'
        assert all(abs(p.ToMM(q.GetSize().x)-.25)<1e-6 for q in cpu.Pads())
        out['cpu_pin_types']=dict(collections.Counter(meta['U502']['pin_types'].values()))
    out['boards'][n]={'size_mm':dims,'copper_layers':b.GetCopperLayerCount(),'footprints':len(fs),
       'schematic_pin_nets_crosschecked':len(connected),'netlist_matches':True,
       'drc_violations_by_type':dict(collections.Counter(x['type'] for x in d['violations'])),
       'reported_unconnected_items':len(d['unconnected_items']),
       'unconnected_report_may_be_capped':n.startswith('Main'),
       'erc_errors':sum(x['severity']=='error' for x in ee),'erc_warnings':sum(x['severity']=='warning' for x in ee),
       'state':'partial CPU x4/clock routing; most nets unrouted' if n.startswith('Main') else 'unchanged Rev K/Rev J CAD'}

# Check native copper endpoint connectivity independently of the capped DRC
# unconnected list. No inference about impedance, delay matching or SI is made.
b=boards['Main_10E1S'];fs={q.GetReference():q for q in b.GetFootprints()}
routes=json.loads((R/'work/revL/cpu_routes.json').read_text(encoding='utf-8'))['routes']
assert len(routes)==34
checked=[]
for r in routes:
    nn=r['net'];ts=[q for q in b.GetTracks() if q.GetNetname()==nn and not isinstance(q,p.PCB_VIA)]
    vias=[q for q in b.GetTracks() if q.GetNetname()==nn and isinstance(q,p.PCB_VIA)]
    assert ts and len(vias)==2,(nn,len(ts),len(vias))
    adj=collections.defaultdict(set)
    for t in ts:
        assert t.GetLayer()==r['layer']
        a,z=xy(t.GetStart()),xy(t.GetEnd());adj[a].add(z);adj[z].add(a)
    ends=[]
    for key in ['a','b']:
        endpoint=r[key];q=next(q for q in fs[endpoint['ref']].Pads() if q.GetNumber()==endpoint['pin'])
        pt=xy(q.GetPosition())
        assert q.GetNetname()==nn and math.dist(pt,endpoint['pt'])<.000003
        assert any(math.dist(xy(t.GetPosition()),pt)<.000003 and t.IsOnLayer(r['layer']) and t.IsOnLayer(p.B_Cu) for t in vias),(nn,pt,'missing in-pad via')
        nearest=min(adj,key=lambda z:math.dist(z,pt));assert math.dist(nearest,pt)<.000003,(nn,pt,nearest)
        ends.append(nearest)
    seen={ends[0]};todo=[ends[0]]
    while todo:
        for pt in adj[todo.pop()]:
            if pt not in seen:seen.add(pt);todo.append(pt)
    assert ends[1] in seen,(nn,'open copper path')
    checked.append(nn)
out['cpu_link_copper_connections_crosschecked']=len(checked)
out['cpu_link_data_pairs']=8;out['cpu_link_refclock_pairs']=1
out['length_tuning_complete']=False
lengths=json.loads((O/'CPU_LINK_LENGTHS.json').read_text(encoding='utf-8'))
out['cpu_link_pair_lengths']=lengths
rows=list(csv.DictReader((O/'TWINAX_MAP.csv').open(encoding='utf-8-sig')));assert len(rows)==54
for row in rows:
    dn='Left_2M2_Vertical' if row['side']=='L' else 'Right_M2_Upstream'
    for pol in 'PN':assert pins['Main_10E1S'][(row['main_ref'],pol)]==pins[dn][(row['daughter_ref'],pol)]==row['net'+pol]
out.update(all_usb_vertical=True,usb_pcb_rotation_deg=90,usb_shell_mounting='4 SMT pads each; 0 metal-stake holes',
    plastic_locator_holes_per_usb=2,usb_actual_part_qualified=False,usb_envelope_height_mm=7.46,
    custom_power_main_bus_connected=False,lanes_per_side=12,links_per_side='3 independent x4',cable_pair_count=54,cable_map_crosschecked=True)
step=json.loads((O/'STEP_VALIDATION.json').read_text(encoding='utf-8'))
assert all(step[n]['native_reimport_reexport'] for n in ['Main_10E1S','Assembly_View','Left_2M2_Vertical','Right_M2_Upstream'])
out['step_roundtrip_passed']=True
(O/'VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
with (O/'BOM.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['Board','Reference','Value','Footprint','Side','X_mm','Y_mm','Rotation_deg','Height_envelope_mm','DNP','Mechanical_only']);w.writerows(bom)
print(json.dumps({k:v for k,v in out.items() if k not in ['cpu_link_pair_lengths']},ensure_ascii=False,indent=2),flush=True)
if '--check-only' in sys.argv:raise SystemExit(0)

shutil.copy2(Path(__file__).parent/'README_RevL.md',O/'README.md')
dest_scripts=R/'scripts/revL';dest_scripts.mkdir(parents=True,exist_ok=True)
for src in Path(__file__).parent.iterdir():
    if src.suffix in ['.py','.md'] and src.resolve()!=(dest_scripts/src.name).resolve():shutil.copy2(src,dest_scripts/src.name)
for relative in ['work/intel_datasheets','work/revL']:
    srcdir=STAGE/relative;destdir=R/relative;destdir.mkdir(parents=True,exist_ok=True)
    if srcdir.resolve()!=destdir.resolve():
        for src in srcdir.iterdir():
            if src.name.endswith('.xlsx') or src.name in ['Intel_Core_Ultra_200V_829568-004.pdf','INTEL_268V_PINOUT.json','intel_tables.json']:
                shutil.copy2(src,destdir/src.name)
sources=json.loads((O/'references/SOURCES.json').read_text(encoding='utf-8'))
sources=[q for q in sources if not q.get('file','').startswith('Intel_268V/')]
for src in sorted((O/'references/Intel_268V').iterdir()):
    if src.is_file():sources.append({'file':'Intel_268V/'+src.name,'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'role':'Intel official 829568-004 datasheet or its embedded table','url':'https://cdrdv2-public.intel.com/829568/829568-004.pdf'})
(O/'references/SOURCES.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
build=json.loads((O/'BUILD.json').read_text(encoding='utf-8'))
build.update(usb_shell_mounting='SMT custom mechanical draft; original USB4160 part not compatible',
             cpu_pinmap_verified=True,cpu_link_copper_connections=34,main_routing_complete=False,
             electrical_design_complete=False,production_ready=False)
(O/'BUILD.json').write_text(json.dumps(build,ensure_ascii=False,indent=2),encoding='utf-8')
ignore=R/'.gitignore';text=ignore.read_text(encoding='utf-8')
rule='/outputs/PCIe_3board_RevL/*.zip'
if rule not in text:ignore.write_text(text.rstrip()+'\n'+rule+'\n',encoding='utf-8')
files=[f for f in O.rglob('*') if f.is_file() and f.suffix not in ['.zip','.lck','.kicad_prl'] and '-backups' not in str(f) and f.name!='SHA256SUMS.txt']
(O/'SHA256SUMS.txt').write_text('\n'.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.relative_to(O).as_posix() for f in sorted(files))+'\n',encoding='utf8')
dest=R/'outputs/PCIe_3board_RevL.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
    for f in O.rglob('*'):
        if f.is_file() and f.suffix not in ['.zip','.lck','.kicad_prl'] and '-backups' not in str(f):z.write(f,Path(O.name)/f.relative_to(O))
with zipfile.ZipFile(dest) as z:
    assert z.testzip() is None
    for line in z.read(O.name+'/SHA256SUMS.txt').decode('utf8').splitlines():
        digest,name=line.split('  ',1);assert hashlib.sha256(z.read(O.name+'/'+name)).hexdigest()==digest,name
print('Release archive verified:',dest,'bytes',dest.stat().st_size)
