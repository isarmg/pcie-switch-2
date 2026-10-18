from pathlib import Path
STAGE=Path(__file__).resolve().parents[2]
ns={'__file__':str(STAGE/'scripts/revN/n_validate_release.py')}
prefix=(STAGE/'scripts/revN/n_validate_release.py').read_text(encoding='utf-8').split('exec(compile(src,')[0]
exec(compile(prefix,'inherited validation builder','exec'),ns)
src=ns['src'].replace('PCIe_AllM2_RevN','PCIe_AllM2_RevP').replace('Main_23M2','Main_20M2').replace("'revision':'N'","'revision':'P'")
src=src.replace('==709','==643').replace('==277','==233').replace('len(ports)==23','len(ports)==20')
src=src.replace('assert used==set(range(96)),sorted(set(range(96))-used)', '''assert used==set(range(84)),sorted(set(range(84))-used)
for lane in range(84,96):
    for direction in ['TX','RX']:
        for pol in 'PN':assert pins['Main_20M2'][('U1',by_signal[f'{direction}{pol}[{lane}]'])].startswith('unconnected-')
positions=sorted(row['position_mm'][0] for row in ports)
assert positions==list(range(3,118,6)),positions
assert all(abs(row['position_mm'][1]-23.3)<.000003 for row in ports)
assert all(not row.get('power_only',False) for row in ports)
''')
src=src.replace('==303.6','==264').replace('==92 and power','==80 and power')
src=src.replace('m2_slots=23','m2_slots=20').replace('main_data_lanes_allocated=96','main_data_lanes_allocated=84,unused_main_data_lanes=12')
src=src.replace('downstream_x4_ports=23','downstream_x4_ports=20').replace('retained_footprint_positions_crosschecked=277','retained_footprint_positions_crosschecked=233').replace('total_ssd_output_W=303.6','total_ssd_output_W=264,total_ssd_output_A=80,m2_pitch_mm=6,power_only_slots=0')
src=src.replace("R/'scripts/revN'","R/'scripts/revP'").replace('README_RevN.md','README_RevP.md')
point=src.index("sources=json.loads((O/'references/SOURCES.json')")
src=src[:point]+'''sources=json.loads((O/'references/SOURCES.json').read_text(encoding='utf-8'))
if not any(q.get('file')=='TI_TPSM53604_SNVSBC9C.pdf' for q in sources):
    sources.append({'file':'TI_TPSM53604_SNVSBC9C.pdf','sha256':hashlib.sha256((O/'references/TI_TPSM53604_SNVSBC9C.pdf').read_bytes()).hexdigest(),'url':'https://www.ti.com/lit/ds/symlink/tpsm53604.pdf','role':'Official 4A power module pinout/package and application requirements'})
(O/'references/SOURCES.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
''' +src[point:]
(STAGE/'work/revP').mkdir(parents=True,exist_ok=True)
(STAGE/'work/revP/validate_source.py').write_text(src,encoding='utf-8')
exec(compile(src,str(__file__),'exec'))
