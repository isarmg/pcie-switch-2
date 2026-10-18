from i_common import *
import csv,collections,xml.etree.ElementTree as ET
out=dict(revision='J',production_ready=False,pcie_gen4_qualified=False,m2_geometry_source='Amphenol CMDT350X0X001VT rev 2',m2_pin_numbering_verified=False,power_thermal_qualified=False,fictional_switch=True,boards={})
pins={}
for name in ['Main_10E1S','Left_2M2_Vertical','Right_M2_Upstream']:
    o=ROOT/name;b=p.LoadBoard(str(o/(name+'.kicad_pcb')));fs={f.GetReference():f for f in b.GetFootprints()};points=[xy(pt) for g in b.GetDrawings() if g.GetLayer()==p.Edge_Cuts for pt in [g.GetStart(),g.GetEnd()]]
    dims=[round(max(pt[i] for pt in points)-min(pt[i] for pt in points),3) for i in [0,1]];assert dims==([80,45] if name.startswith('Main') else [19.5,45]),(name,dims)
    bp={(f.GetReference(),q.GetNumber()):q.GetNetname() for f in fs.values() for q in f.Pads() if q.GetNumber()};pins[name]=bp
    sch=ET.parse(o/'CONNECTIVITY.net').getroot();sp={(q.get('ref'),q.get('pin')):nn.get('name') for nn in sch.findall('nets/net') for q in nn.findall('node')}
    assert len(sch.findall('components/comp'))==len(fs)
    connected={k:v for k,v in bp.items() if v and not v.startswith('unconnected-')};mismatches=[(k,v,sp.get(k)) for k,v in connected.items() if sp.get(k)!=v];assert not mismatches,(name,mismatches[:5])
    npth=sum(q.GetAttribute()==p.PAD_ATTRIB_NPTH for f in fs.values() for q in f.Pads());assert npth==(0 if name.startswith('Main') else 6)
    if name.startswith('Main'):
        assert all(xy(fs[f'J{k}'].GetPosition())==(4+(k-1)*8,22.5) for k in range(1,11));assert len(list(fs['U1'].Pads()))==400
    else:
        keys=[1,2,4] if name.startswith('Left') else [3,5,4]
        for i,k in enumerate(keys):
            f=fs[f'J{k}'];assert xy(f.GetPosition())==(3.55+6.2*i,17) or math.dist(xy(f.GetPosition()),(3.55+6.2*i,17))<.00001
            assert f.GetLayer()==p.F_Cu and abs(f.GetOrientationDegrees()-90)<.01 and 'MDT350' in str(f.GetFPID().GetLibItemName())
    d=json.loads((o/'DRC.json').read_text(encoding='utf8'));e=json.loads((o/'ERC.json').read_text(encoding='utf8'));errors=[z for z in d['violations'] if z['severity']=='error'];warnings=[z for z in d['violations'] if z['severity']=='warning'];erc=[z for sh in e['sheets'] for z in sh['violations']]
    models=[]
    for f in fs.values():
        for m in f.Models():
            path=Path(m.m_Filename.replace('${KIPRJMOD}',str(o)));assert path.exists(),path;models.append(path.name)
    step=o/(name+'.step');assert step.stat().st_size>10000
    cs=json.loads((o/'COMPONENTS.json').read_text());heights={side:max([c.get('height_mm',0) for c in cs if c['side']==side] or [0]) for side in ['F','B']};assert heights['B']<=8
    with (o/'PIN_MAP.csv').open('w',encoding='utf-8-sig',newline='') as file:
        w=csv.writer(file);w.writerow(['Reference','Pin','Net','X_mm','Y_mm','Side'])
        for f in fs.values():
            for q in f.Pads():
                if q.GetNumber():w.writerow([f.GetReference(),q.GetNumber(),q.GetNetname(),*xy(q.GetPosition()),'F' if q.IsOnLayer(p.F_Cu) else 'B'])
    out['boards'][name]=dict(size_mm=dims,layers=b.GetCopperLayerCount(),components=len(fs),connected_pins_crosschecked=len(connected),schematic_matches_pcb=True,corner_mounting_holes=0,connector_locating_holes=npth,drc_errors=len(errors),drc_warnings=len(warnings),unconnected_items=len(d['unconnected_items']),erc_errors=sum(x['severity']=='error' for x in erc),erc_warnings=sum(x['severity']=='warning' for x in erc),model_instances=len(models),new_component_height_mm=heights,step_bytes=step.stat().st_size)
    legacy=json.loads((BASE/'POWER_COMPONENTS.json').read_text()) if name.startswith('Main') else []
    combined={c['ref']:c for c in legacy+cs};back_height=max(c.get('height_mm',0) for c in combined.values() if c['side']=='B');assert back_height<=8
    out['boards'][name]['max_known_component_envelope_mm']={'B':back_height,'F':9.05 if name.startswith('Main') else heights['F'],'E1S_connector_exempt':name.startswith('Main')}
rows=list(csv.DictReader((ROOT/'TWINAX_MAP.csv').open(encoding='utf-8-sig')));assert len(rows)==54
for row in rows:
    dn='Left_2M2_Vertical' if row['side']=='L' else 'Right_M2_Upstream'
    for pol in ['P','N']:assert pins['Main_10E1S'][(row['main_ref'],pol)]==pins[dn][(row['daughter_ref'],pol)]==row['net'+pol]
rp=pins['Right_M2_Upstream'];assert rp[('J4','49')]=='/UP_RX0_P' and rp[('J4','43')]=='/UP_TX0_P_AC'
assert all(rp[('J4',str(i))].startswith('unconnected-') for i in [2,4,12,14,16,18,70,72,74])
out.update(pcie_lanes_total=64,lanes_per_side=12,links_per_side='3 independent x4',twinax_pairs_per_side=27,twinax_data_pairs_per_side=24,clock_pairs_per_side=3,ssd_count=5,m2_socket_count=6,all_m2_sockets_on_top=True,vertical_ssds_parallel_to_e1s=True,cable_map_crosschecked=True)
out['electrical_draft_checks_pass']=all(z['drc_errors']==0 and z['unconnected_items']==0 and z['erc_errors']==0 for z in out['boards'].values())
(ROOT/'VALIDATION.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
