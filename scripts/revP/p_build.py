"""Latest requested geometry: 120 x 45 mm, twenty M.2 at 6 mm pitch."""
from pathlib import Path
base=Path(__file__).resolve().parent.parent
src=(base/'revN/n_build.py').read_text(encoding='utf-8')
src=src.replace('PCIe_AllM2_RevN','PCIe_AllM2_RevP').replace('Main_23M2','Main_20M2').replace('work/revN','work/revP')
# Input datasheet is an existing verified reference, not a generated P file.
src=src.replace("STAGE/'work/revP/TI_TPSM53604_SNVSBC9C.pdf'","STAGE/'work/revN/TI_TPSM53604_SNVSBC9C.pdf'")
src=src.replace("baseline={f.GetReference():{'position_mm':xy(f.GetPosition()),'rotation_deg':f.GetOrientationDegrees(),'layer':f.GetLayer()} for f in b.GetFootprints()}","baseline={f.GetReference():{'position_mm':xy(f.GetPosition()),'rotation_deg':f.GetOrientationDegrees(),'layer':f.GetLayer()} for f in b.GetFootprints() if f.GetReference() not in ['J501','J502','J503','J504']}")
src=src.replace("foot='MKey_Vertical",'''for row in ports:
    xx={'M1':3,'M2':9,'M3':111,'M4':117}[row['port']]
    b.FindFootprintByReference(row['ref']).SetPosition(v(xx,23.3));row['position_mm']=[xx,23.3]
foot='MKey_Vertical''')
src=src.replace('list(range(60,96,4))','list(range(60,84,4))').replace('len(lane_starts)==19','len(lane_starts)==16')
src=src.replace('x=15.7+(k-1)*4.35','x=15+(k-1)*6')
src=src.replace("bpmap[str(pp)]=f'/N{k:02}_CLK_P';bpmap[str(pn)]=f'/N{k:02}_CLK_N'","bpmap[str(pp)]=f'/N{k:02}_CLK_P' if k<=16 else c.nc(clock_ref,str(pp));bpmap[str(pn)]=f'/N{k:02}_CLK_N' if k<=16 else c.nc(clock_ref,str(pn))")
src=src.replace('N12-N19 CLOCK','N12-N16 CLOCK')
src=src.replace("movable=set(new_modules+new_caps+new_small)",'''extra_small=[f'C{3050+10*k+i}' for k in range(4) for i in range(1,9)]+[f'R{3000+10*k+i}' for k in range(4) for i in [3,4]]
for ref in extra_small:baseline.pop(ref)
new_small.extend(extra_small)
movable=set(new_modules+new_caps+new_small)''')
src=src.replace("for f in b.GetFootprints():\n    e=meta[f.GetReference()]",'''for f in b.GetFootprints():
    if f.GetValue().startswith('TPSM53604') and not list(f.Models()):a.model(f,'TPSM53604_5x5p5x4p1_ENVELOPE',5,5.5,4.1)
    e=meta[f.GetReference()]''')
src=src.replace("'ssd_slots':23","'ssd_slots':20").replace("'total_ssd_output_W':303.6","'total_ssd_output_W':264").replace("'total_ssd_output_A':92","'total_ssd_output_A':80").replace('303.6/.85','264/.85').replace("TPSM53604RDAR x19","TPSM53604RDAR x16")
src=src.replace("'revision':'N'","'revision':'P'").replace("'m2_slots':23","'m2_slots':20").replace("'new_central_m2_pitch_mm':4.35","'all_m2_pitch_mm':6").replace("'downstream_x4_ports':23","'downstream_x4_ports':20,'allocated_main_data_lanes':84,'unallocated_main_data_lanes':list(range(84,96))")
src=src.replace("'retained_geometry_matches_RevM':True","'retained_platform_geometry_matches_RevM':True,'retained_platform_footprints':233,'power_only_slots':0")
src=src.replace('23 x4 slots, 19 new 4A power modules','20 x4 slots at 6 mm pitch, 16 new 4A power modules')
exec(compile(src,str(__file__),'exec'))
