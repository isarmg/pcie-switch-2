from pathlib import Path
src=(Path(__file__).resolve().parent.parent/'revL/l_validate_release.py').read_text(encoding='utf-8')
src=src.replace("['Main_10E1S','Assembly_View','Left_2M2_Vertical','Right_M2_Upstream']","['Main_10E1S','Assembly_View']")
src=src.replace("['Main_10E1S','Left_2M2_Vertical','Right_M2_Upstream']","['Main_10E1S']")
src=src.replace('PCIe_3board_RevL','PCIe_Main_RevM').replace("'revision':'L'","'revision':'M'")
start=src.index("rows=list(csv.DictReader((O/'TWINAX_MAP.csv')")
end=src.index("step=json.loads((O/'STEP_VALIDATION.json')",start)
src=src[:start]+'''
b=boards['Main_10E1S'];fs={q.GetReference():q for q in b.GetFootprints()}
assert len(fs)==377,len(fs)
assert not any('Twinax_' in str(f.GetFPID().GetLibItemName()) or f.GetReference() in ['J301','J302','J303','J304'] for f in fs.values())
assert not any(q.GetNetname().startswith('/M5_') or q.GetNetname().startswith('/UP_') for f in fs.values() for q in f.Pads())
assert not (O/'Left_2M2_Vertical').exists() and not (O/'Right_M2_Upstream').exists()
for k,x in [(1,3.6),(2,9.8),(3,100.2),(4,106.4)]:
    f=fs[f'J{500+k}'];assert xy(f.GetPosition())==(x,23.3) and f.GetLayer()==p.F_Cu and f.GetOrientationDegrees()==90
    assert len(list(f.Pads()))==69
    assert all(q.GetAttribute()==p.PAD_ATTRIB_SMD for q in f.Pads())
    assert len([q for q in f.Pads() if q.GetNumber().startswith('MP')])==2
    base={1:44,2:48,3:56,4:52}[k]
    names=json.loads((O/'PEX88096_PINOUT.json').read_text(encoding='utf-8'))['ball_records']
    by_signal={q['signal']:q['ball'] for q in names}
    for lane in range(4):
        for pol in 'PN':
            for direction in ['TX','RX']:
                ball=by_signal[f'{direction}{pol}[{base+lane}]'];assert pins['Main_10E1S'][('U1',ball)]==f'/M{k}_{direction}{lane}_{pol}'
            for tail in [f'TX{lane}_{pol}',f'TX{lane}_{pol}_AC',f'RX{lane}_{pol}']:
                nn=f'/M{k}_'+tail;matches=[(ff.GetReference(),q.GetNumber()) for ff in fs.values() for q in ff.Pads() if q.GetNetname()==nn]
                assert len(matches)==2,(nn,matches)
    regulator=fs[f'U{3000+k}'];pm={q.GetNumber():q.GetNetname() for q in regulator.Pads()}
    assert pm['1']=='/GND' and pm['2']==f'/M{k}_SW' and pm['3']==('/M2_12V_L' if k<=2 else '/M2_12V_R') and pm['4']==f'/M{k}_FB' and pm['5']==pm['3'] and pm['6']==f'/M{k}_BST'
out.update(daughter_boards=0,inter_board_cable_pairs=0,m2_slots=4,m2_each_side=2,m2_same_side_pitch_mm=6.2,m2_no_peg_concepts=True,
    m2_net_assignments_crosschecked=True,m2_copper_routing_complete=False,
    all_usb_vertical=True,usb_pcb_rotation_deg=90,usb_shell_mounting='four SMD pads each',usb_metal_stake_holes=0,
    usb_plastic_locator_holes_per_port=2,usb_actual_part_qualified=False,custom_power_main_bus_connected=False)
''' +src[end:]
src=src.replace("R/'scripts/revL'","R/'scripts/revM'").replace('README_RevL.md','README_RevM.md')
src=src.replace("'cpu_link_copper_connections':34","'cpu_link_copper_connections':34")
debug=Path(__file__).resolve().parents[2]/'work/revM';debug.mkdir(parents=True,exist_ok=True)
(debug/'validate_source.py').write_text(src,encoding='utf-8')
exec(compile(src,str(__file__),'exec'))
