from i_common import *
import xml.etree.ElementTree as ET,collections,csv,subprocess
summary={'revision':'I','production_ready':False,'gen5_qualified':False,'m2_land_pattern_verified':False,'power_thermal_qualified':False,'migration_executed':(ROOT/'MIGRATION.json').exists(),'boards':{},'notes':['Fictitious BGA400; no real switch supply/clock/reset implementation','Provisional vertical M.2 footprint','PCB connectivity checks do not establish 32 GT/s channel performance']}
allpins={}
for n in ['Main_10E1S','Left_2M2_Vertical','Right_M2_Upstream']:
    o=ROOT/n;b=p.LoadBoard(str(o/(n+'.kicad_pcb')));fs={f.GetReference():f for f in b.GetFootprints()};boardpins={(f.GetReference(),q.GetNumber()):q.GetNetname() for f in b.GetFootprints() for q in f.Pads() if q.GetNumber()};allpins[n]=boardpins
    sch=ET.parse(o/'CONNECTIVITY.net').getroot();schpins={(q.get('ref'),q.get('pin')):nn.get('name') for nn in sch.findall('nets/net') for q in nn.findall('node')}
    assert len(sch.findall('components/comp'))==len(fs),(n,'schematic component count')
    connected={k:v for k,v in boardpins.items() if v and not v.startswith('unconnected-')};mismatch=[(k,v,schpins.get(k)) for k,v in connected.items() if schpins.get(k)!=v];assert not mismatch,(n,mismatch[:10])
    assert not any(q.GetAttribute()==p.PAD_ATTRIB_NPTH for f in fs.values() for q in f.Pads()),n
    expected_dims=[80,45] if n.startswith('Main') else [52,45]
    bb=b.GetBoardEdgesBoundingBox();dims=[round(p.ToMM(bb.GetWidth())-.05,3),round(p.ToMM(bb.GetHeight())-.05,3)]
    # Some stock edge graphics use 0.1 mm widths; polygon extents are verified separately below.
    points=[]
    for g in list(b.GetDrawings())+[g for f in fs.values() for g in f.GraphicalItems()]:
        if g.GetLayer()==p.Edge_Cuts:points += [xy(g.GetStart()),xy(g.GetEnd())]
    dims=[round(max(q[i] for q in points)-min(q[i] for q in points),3) for i in range(2)];assert dims==expected_dims,(n,dims)
    if n.startswith('Main'):
        assert all(xy(fs[f'J{k}'].GetPosition())==(4+(k-1)*8,22.5) for k in range(1,11));assert len(list(fs['U1'].Pads()))==400
    else:
        for k in [1,2] if n.startswith('Left') else [3]:
            f=fs[f'J{k}'];assert abs(f.GetOrientationDegrees()-90)<.01
            for pin,sig in [('49','TX0_P_AC'),('47','TX0_N_AC'),('43','RX0_P'),('41','RX0_N'),('55','CLK_P'),('53','CLK_N'),('50','PERST'),('52','CLKREQ'),('54','WAKE')]:assert boardpins[(f'J{k}',pin)]==f'/M{k}_{sig}',(n,k,pin)
            assert all(boardpins[(f'J{k}',str(pin))]==f'/M{k}_3V3' for pin in [2,4,12,14,16,18,70,72,74])
    d=json.loads((o/'DRC.json').read_text(encoding='utf8'));e=json.loads((o/'ERC.json').read_text(encoding='utf8'));ev=[v for sh in e['sheets'] for v in sh['violations']];errors=[v for v in d['violations'] if v['severity']=='error'];assert not errors and not d['unconnected_items'],(n,'DRC',len(errors),len(d['unconnected_items']))
    assert not [v for v in ev if v['severity']=='error'],(n,'ERC errors')
    paths=[]
    for f in fs.values():
        for m in f.Models():
            path=Path(m.m_Filename.replace('${KIPRJMOD}',str(o)));assert path.exists(),path;assert '${KICAD' not in m.m_Filename;paths.append(path.name)
    step=o/(n+'.step');assert step.exists() and step.stat().st_size>10000
    data=step.read_text();occ=collections.Counter(re.findall(r"NEXT_ASSEMBLY_USAGE_OCCURRENCE\('[^']*','([^']*)'",data));expected=collections.Counter(f.GetReference() for f in fs.values() for m in f.Models());assert all(occ[ref]==count for ref,count in expected.items()),(n,'STEP model count')
    with (o/'PIN_MAP.csv').open('w',encoding='utf-8-sig',newline='') as file:
        w=csv.writer(file);w.writerow(['Reference','Pin','Net','X_mm','Y_mm','Side'])
        for f in fs.values():
            for q in f.Pads():
                if q.GetNumber():w.writerow([f.GetReference(),q.GetNumber(),q.GetNetname(),*xy(q.GetPosition()),'F' if q.IsOnLayer(p.F_Cu) else 'B'])
    cs=json.loads((o/'COMPONENTS.json').read_text());heights={side:max([c['height_mm'] for c in cs if c['side']==side] or [0]) for side in ['F','B']};assert heights['B']<=8 and heights['F']<=9
    summary['boards'][n]={'size_mm':dims,'layers':b.GetCopperLayerCount(),'components':len(fs),'connected_pins_crosschecked':len(connected),'schematic_matches_pcb':True,'mounting_holes':0,'drc_errors':len(errors),'drc_warnings':len(d['violations'])-len(errors),'unconnected_items':len(d['unconnected_items']),'erc_errors':0,'erc_warnings':len(ev),'model_instances':len(paths),'new_component_height_mm':heights,'step_bytes':step.stat().st_size}
for row in csv.DictReader((ROOT/'TWINAX_MAP.csv').open(encoding='utf-8-sig')):
    daughter='Left_2M2_Vertical' if row['side']=='L' else 'Right_M2_Upstream'
    for pol in ['P','N']:
        assert allpins['Main_10E1S'][(row['main_ref'],pol)]==allpins[daughter][(row['daughter_ref'],pol)]==row['net'+pol]
rp=allpins['Right_M2_Upstream'];assert rp[('J4','49')]=='/UP_RX0_P' and rp[('J4','47')]=='/UP_RX0_N'
assert rp[('J4','43')]=='/UP_TX0_P_AC' and rp[('J4','41')]=='/UP_TX0_N_AC'
assert rp[('J4','52')]=='/UP_CLKREQ' and rp[('J4','50')]=='/UP_PERST'
assert all(rp[('J4',str(n))].startswith('unconnected-') for n in [2,4,12,14,16,18,70,72,74])
summary.update(pcie_lanes_total=56,twinax_pairs_per_side=18,twinax_data_pairs_per_side=16,vertical_ssds_parallel_to_e1s=True,cable_pin_map_crosschecked=True)
(ROOT/'VALIDATION.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
