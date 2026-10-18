from pathlib import Path
B=Path(__file__).resolve().parent.parent;S=B/'revS';T=B/'revT'
for name in ['route','apply_routes','schematic','stepcheck','run']:
    s=(S/f's_{name}.py').read_text(encoding='utf-8').replace('PCIe_E1S_82x45_FakePEX90064_RevS','PCIe_E1S_82x45_TB3Host_RevT').replace('work/revS','work/revT').replace('s_'+name+'.py','t_'+name+'.py')
    if name=='run':s=s.replace("'s_'+name+'.py'","'t_'+name+'.py'")
    if name=='route':
        s=s.replace('if dist>=5 and attempt<2:', 'if dist>=5 and attempt<2 and layer not in [60,62]:')
        s=s.replace("src=src.replace('1.04*h','1.18*h')", "src=src.replace('1.04*h','1.35*h').replace('.05+.25-CLEAR','.05+.10-CLEAR')")
        s=s.replace('G=.05;NX=1641;NY=901;CLEAR=.13','G=.05;NX=1641;NY=901;CLEAR=.08')
        s=s.replace("ns={'__file__':__file__};exec", "src=src.replace('[:4,:]','[:INSET,:]').replace('[-4:,:]','[-INSET:,:]').replace('[:,:4]','[:,:INSET]').replace('[:,-4:]','[:,-INSET:]').replace('xx<4','xx<INSET').replace('xx>=NX-4','xx>=NX-INSET').replace('yy<4','yy<INSET').replace('yy>=NY-4','yy>=NY-INSET')\n    ns={'__file__':__file__};exec")
        s=s.replace("for attempt in range(6):", "for attempt in range(6):\n        ns['G']=.025 if attempt>=4 else .05;ns['NX']=round(82/ns['G'])+1;ns['NY']=round(45/ns['G'])+1;ns['INSET']=round(.6/ns['G'])")
        s=s.replace("ns['G']=.025 if attempt>=4 else .05", "ns['G']=.025 if attempt>=4 or all(t['kind'].startswith('TB3_') for t in tasks) else .05")
        s=s.replace("choices=sorted({min(v,dist*.28) for v in [1.0,1.75,3.]})", "choices=[min(1.,dist*.28)] if pt['net'].startswith('/TBT_') else sorted({min(v,dist*.28) for v in [1.,1.75,3.]})")
        s=s.replace("exec(compile(paired,'paired route geometry','exec'),ns)","paired=paired.replace('bulks=[offset(center,.125*sign),offset(center,-.125*sign)]',\"half=(ptask['width']+.15)/2;bulks=[offset(center,half*sign),offset(center,-half*sign)]\")\n    exec(compile(paired,'paired route geometry','exec'),ns)")
        s=s.replace("==310",">=386").replace("==len(data['tasks'])>=386","==len(data['tasks'])")
        s=s.replace('base signal classification','base signal classification')
        s=s.replace("metrics=[];result=[]","metrics=[];result=[]")
        # Native KiCad's lengths include short surface clock fanouts.
        s=s.replace("for group in sorted({q['group']", "for r in results:r['length_mm']+=r['a'].get('fanout_mm',0)+r['b'].get('fanout_mm',0)\n    for group in sorted({q['group']")
        s=s.replace('300 allocated PCIe data/reference-clock sections and ten per-slot PERST reset networks.','Allocated E1.S/CPU PCIe and TB3 host data/clock plus control sections; power routing remains incomplete.')
    if name=='apply_routes':
        s=s.replace('p.ZONE_FILLER(b).Fill(b.Zones())','for z in b.Zones():z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)\np.ZONE_FILLER(b).Fill(b.Zones())')
        s=s.replace("==310",">=386").replace('Applied 310 signal connections','Applied allocated PCIe / TB3 signal connections')
        s=s.replace("whole_board_routing_complete=False", "tb3_host_data_clock_routed=True,whole_board_routing_complete=False")
        s=s.replace("allocated_signal_sections_copper_routed=310", "allocated_signal_sections_copper_routed=len(d['routes'])")
    if name=='schematic':
        s=s.replace('(rev "S")','(rev "T")').replace('REV S: FICTIONAL 64-LANE PEX90064 / 33x33mm / 82x45mm CARRIER','REV T: 288V 32GB / FICTIONAL PEX90064 / THUNDERBOLT 3 HOST')
        s=s.replace('CPU288V 32GB MoP; PMIC/boot work remains open.','TB3 host: Alpine Ridge DP + TPS65982. CPU PMIC / BIOS / NVM / SI qualification pending.')
    (T/f't_{name}.py').write_text(s,encoding='utf-8')
print('Rev T orchestration/export scripts prepared.')
