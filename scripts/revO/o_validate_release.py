from pathlib import Path
STAGE=Path(__file__).resolve().parents[2]
ns={'__file__':str(STAGE/'scripts/revN/n_validate_release.py')}
prefix=(STAGE/'scripts/revN/n_validate_release.py').read_text(encoding='utf-8').split('exec(compile(src,')[0]
exec(compile(prefix,'build inherited validation','exec'),ns)
src=ns['src'].replace('PCIe_AllM2_RevN','PCIe_AllM2_RevO').replace('Main_23M2','Main_27M2').replace("'revision':'N'","'revision':'O'")
src=src.replace('==709','==730').replace('==277','==274').replace('==23','==27')
src=src.replace("    assert len(row['pex_lanes'])==4",'''    if row.get('power_only'):
        assert row['pex_lanes']==[] and port in ['P01','P02','P03','P04']
        assert all(q.GetNetname() in ['/GND',f'/{port}_3V3'] or q.GetNetname().startswith('unconnected-') for q in f.Pads())
        assert sum(q.GetNetname()==f'/{port}_3V3' for q in f.Pads())==9
        assert not any(q.GetNetname().startswith(f'/{port}_TX') or q.GetNetname().startswith(f'/{port}_RX') or q.GetNetname().startswith(f'/{port}_CLK') for q in f.Pads())
        plan.append([port,ref,'POWER ONLY','','',f'U{7000+int(port[1:])}',3.3,4,*xy(f.GetPosition())])
        continue
    assert len(row['pex_lanes'])==4''')
src=src.replace("==303.6","==356.4").replace("==92 and power","==108 and power")
src=src.replace('m2_slots=23','m2_slots=27,power_only_slots=4,data_m2_slots=23').replace('retained_footprint_positions_crosschecked=277','retained_footprint_positions_crosschecked=274').replace('total_ssd_output_W=303.6','total_ssd_output_W=356.4')
point=src.index("step=json.loads((O/'STEP_VALIDATION.json')")
src=src[:point]+'''
power_proof=json.loads((O/'POWER_ONLY_ROUTING.json').read_text(encoding='utf-8'))
assert len(power_proof['ports'])==4 and power_proof['power_vias_added']>200
assert power_proof['all_protocol_pads_on_power_only_ports_NC']
for proof in power_proof['pad_connections']:
    pp=next(q for q in fs[proof['reference']].Pads() if q.GetNumber()==proof['pad'])
    assert pp.GetNetname()==proof['net']
    for xx,yy in proof['via_centers_mm']:
        assert any(isinstance(t,p.PCB_VIA) and t.GetNetname()==proof['net'] and math.dist(xy(t.GetPosition()),[xx,yy])<.000003 for t in b.GetTracks())
assert len(power_proof['feedback_routes'])>=8
out.update(new_power_only_copper_planes_drawn=True,new_power_only_pad_connections=len(power_proof['pad_connections']),
           new_power_only_vias=power_proof['power_vias_added'],total_ssd_output_A=108,
           all_m2_pitch_mm=4.35,power_plane_stackup_and_current_rating_qualified=False)
''' +src[point:]
src=src.replace("R/'scripts/revN'","R/'scripts/revO'").replace('README_RevN.md','README_RevO.md')
(STAGE/'work/revO').mkdir(parents=True,exist_ok=True)
(STAGE/'work/revO/validate_source.py').write_text(src,encoding='utf-8')
exec(compile(src,str(__file__),'exec'))
