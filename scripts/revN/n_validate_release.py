from pathlib import Path
src=(Path(__file__).resolve().parent.parent/'revL/l_validate_release.py').read_text(encoding='utf-8')
src=src.replace("['Main_10E1S','Assembly_View','Left_2M2_Vertical','Right_M2_Upstream']","['Main_10E1S','Assembly_View']")
src=src.replace("['Main_10E1S','Left_2M2_Vertical','Right_M2_Upstream']","['Main_10E1S']")
src=src.replace('PCIe_3board_RevL','PCIe_AllM2_RevN').replace('Main_10E1S','Main_23M2').replace("'revision':'L'","'revision':'N'")
src=src.replace('[110,45]','[120,45]').replace('xx=[110-','xx=[120-')
start=src.index("        assert all(xy(fs[f'J{k}']")
end=src.index('        assert all(ff.GetReference()',start)
src=src[:start]+src[end:]
start=src.index("rows=list(csv.DictReader((O/'TWINAX_MAP.csv')")
end=src.index("step=json.loads((O/'STEP_VALIDATION.json')",start)
src=src[:start]+'''
b=boards['Main_23M2'];fs={q.GetReference():q for q in b.GetFootprints()}
assert len(fs)==len(list(b.GetFootprints()))==709,len(fs)
assert not any('Samtec_HSEC' in str(f.GetFPID().GetLibItemName()) or 'Twinax_' in str(f.GetFPID().GetLibItemName()) for f in fs.values())
base=json.loads((O/'CORE_PLACEMENT_BASELINE.json').read_text(encoding='utf-8'));assert len(base)==277
for ref,q in base.items():
    f=fs[ref];assert math.dist(xy(f.GetPosition()),q['position_mm'])<.000003 and f.GetLayer()==q['layer'] and f.GetOrientationDegrees()==q['rotation_deg'],ref
ports=json.loads((O/'M2_PORTS.json').read_text(encoding='utf-8'));assert len(ports)==23
source=json.loads((O/'PEX88096_PINOUT.json').read_text(encoding='utf-8'))['ball_records'];by_signal={q['signal']:q['ball'] for q in source}
used=set(range(4));net_count=0;plan=[]
for row in ports:
    port=row['port'];ref=row['ref'];f=fs[ref];assert f.GetLayer()==p.F_Cu and f.GetOrientationDegrees()==90
    assert math.dist(xy(f.GetPosition()),row['position_mm'])<.000003
    assert len(list(f.Pads()))==69 and all(q.GetAttribute()==p.PAD_ATTRIB_SMD for q in f.Pads())
    assert len([q for q in f.Pads() if q.GetNumber().startswith('MP')])==2
    assert not any('12V' in q.GetNetname() or '/P12_' in q.GetNetname() for q in f.Pads())
    assert len(row['pex_lanes'])==4 and not used.intersection(row['pex_lanes'])
    used.update(row['pex_lanes'])
    for lane,actual in enumerate(row['pex_lanes']):
        for pol in 'PN':
            for direction in ['TX','RX']:
                ball=by_signal[f'{direction}{pol}[{actual}]'];nn=f'/{port}_{direction}{lane}_{pol}'
                assert pins['Main_23M2'][('U1',ball)]==nn,(port,actual,direction,ball)
            for tail in [f'TX{lane}_{pol}',f'TX{lane}_{pol}_AC',f'RX{lane}_{pol}']:
                nn=f'/{port}_'+tail;matches=[(ff.GetReference(),q.GetNumber()) for ff in fs.values() for q in ff.Pads() if q.GetNetname()==nn]
                assert len(matches)==2,(nn,matches);net_count+=1
    for pol in 'PN':
        nn=f'/{port}_CLK_{pol}';matches=[ff.GetReference() for ff in fs.values() for q in ff.Pads() if q.GetNetname()==nn]
        assert len(matches)==2 and ref in matches,(nn,matches)
    if port.startswith('N'):
        k=int(port[1:]);reg=fs[f'U{5000+k}'];pm={q.GetNumber():q.GetNetname() for q in reg.Pads()}
        assert pm['1']==pm['2']==pm['14']==('/VBANK_A' if k<=10 else '/VBANK_B')
        assert pm['7']==pm['8']==f'/{port}_3V3' and pm['15']==pm['12']=='/GND'
        assert all(pm[pin].startswith('unconnected-') for pin in ['4','5','6','13'])
        for n in [1,2]:assert fs[f'R{5000+k*10+n}'].GetValue()==('10k 1%' if n==1 else '4.32k 1%')
        clock='U601' if k<=7 else 'U602' if k<=11 else 'U6501';power=reg.GetReference()
    else:clock='U602';power='U'+str(3000+int(port[1:]))
    plan.append([port,ref,'x4',' '.join(map(str,row['pex_lanes'])),clock,power,3.3,4,*xy(f.GetPosition())])
assert used==set(range(96)),sorted(set(range(96))-used)
cpu_names=json.loads((O/'INTEL_268V_PINOUT.json').read_text(encoding='utf-8'))['pins'];cmap={q['signal']:q['ball'] for q in cpu_names}
for pol in 'PN':assert pins['Main_23M2'][('U502',cmap[f'CLKOUT_{pol}3'])]==f'/CPU_CLKBUF3_IN_{pol}'
with (O/'PORT_PLAN.csv').open('w',encoding='utf-8-sig',newline='') as fh:
    w=csv.writer(fh);w.writerow(['Port','Reference','Link','PEX_lanes','Clock_buffer','Regulator','Nominal_V','Design_budget_A','X_mm','Y_mm']);w.writerows(plan)
power=json.loads((O/'POWER_BUDGET.json').read_text(encoding='utf-8'))
assert power['total_ssd_output_W']==303.6 and power['total_ssd_output_A']==92 and power['input_design_target_A']==50
out.update(daughter_boards=0,e1s_slots=0,m2_slots=23,slot_data_nets_crosschecked=net_count,main_data_lanes_allocated=96,
    host_link_lanes=4,downstream_x4_ports=23,switch_port_firmware_configured=False,
    retained_footprint_positions_crosschecked=277,m2_no_peg_concepts=True,m2_actual_part_and_pin_direction_qualified=False,
    clock_buffers=3,per_slot_design_A=4,total_ssd_output_W=303.6,input_design_target_A=50,
    power_copper_and_thermal_qualified=False,slot_copper_routing_complete=False,
    all_usb_vertical=True,usb_pcb_rotation_deg=90,usb_shell_mounting='four SMD pads each',usb_metal_stake_holes=0,
    usb_plastic_locator_holes_per_port=2,usb_actual_part_qualified=False,custom_power_main_bus_connected=False)
''' +src[end:]
src=src.replace("R/'scripts/revL'","R/'scripts/revN'").replace('README_RevL.md','README_RevN.md')
debug=Path(__file__).resolve().parents[2]/'work/revN';debug.mkdir(parents=True,exist_ok=True)
(debug/'validate_source.py').write_text(src,encoding='utf-8')
exec(compile(src,str(__file__),'exec'))
