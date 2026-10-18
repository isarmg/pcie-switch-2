from i_common import *
for name in ['Main_10E1S','Left_2M2_Vertical','Right_M2_Upstream']:
    o=ROOT/name;bp=o/(name+'.kicad_pcb');b=p.LoadBoard(str(bp));cs=json.loads((o/'COMPONENTS.json').read_text())
    for c in cs:
        f=b.FindFootprintByReference(c['ref'])
        c.update(value=f.GetValue(),x=xy(f.GetPosition())[0],y=xy(f.GetPosition())[1],side='F' if f.GetLayer()==p.F_Cu else 'B',rotation_deg=f.GetOrientationDegrees(),footprint=str(f.GetFPID().GetLibItemName()),pinmap={q.GetNumber():q.GetNetname() for q in f.Pads() if q.GetNumber()})
    (o/'COMPONENTS.json').write_text(json.dumps(cs,indent=2))
    if not name.startswith('Main'):
        a=object.__new__(Board);a.b=b;a.nets={nn.GetNetname():nn for nn in b.GetNetInfo().NetsByNetcode().values()}
        for pt in [(1.0,43.3),(18.5,43.3)]:a.via(*pt,'/GND')
        for z in b.Zones():z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
        p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(bp),b)
    print(name,'metadata synchronized',flush=True)
d=json.loads((ROOT/'BUILD.json').read_text());d.update(daughter_layers=32,right_current_limit_target_A=3.5,route_status='Draft routing; see DRC.json and VALIDATION.json for actual checks')
(ROOT/'BUILD.json').write_text(json.dumps(d,indent=2))
readme=ROOT/'README.md';s=readme.read_text(encoding='utf8').replace('| 24 |','| 32 |');s=s.replace('其他器件/走线规则不放宽','另对盲埋孔间的孔到铜设 0.20 mm HDI 目标，孔到孔仍为 0.25 mm；普通孔到铜仍为 0.25 mm');readme.write_text(s,encoding='utf8')
