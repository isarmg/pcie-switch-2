"""Move the buried power landing out of the PD BGA via field with an F-side stub."""
from pathlib import Path
import shutil
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');W=R/'work/revW';F=R/'outputs/PCIe_E1S_96x45_USB12mm_RevW/Main_12E1S';S=W/'finalpatch'
shutil.copy2(S/'Base.kicad_pcb',F/'Main_12E1S.kicad_pcb')
exec(compile(Path(__file__).with_name('w_geometry.py').read_text(encoding='utf-8'),__file__,'exec'),globals())
nn='/P12_SLOT08';ff=fs['J8'];pp=pad(ff,'B6');pts=stitch(ff,pp,nn,[p.In25_Cu]);assert pts,'No safe power escape'
d=json.loads((S/'route_tasks.json').read_text(encoding='utf-8'));q=next(q for q in d['tasks'] if q['task_id']=='/P12_SLOT08__FINALPATCH_1');q['b'].update(pt=pts[0],pad_pt=pts[0]);q.update(layer=p.In25_Cu,layer_name='In25.Cu',layer_index=25)
d['vias']=[dict(net=t.GetNetname(),pt=xy(t.GetPosition()),diameter=p.ToMM(t.GetWidth(t.TopLayer())),layers=[ll for ll in cu if t.IsOnLayer(ll)]) for t in b.GetTracks() if isinstance(t,p.PCB_VIA)]
for t in b.GetTracks():
 if not isinstance(t,p.PCB_VIA) and t.GetNetname()==nn and any(math.dist(xy(t.GetStart()),pt)<.000003 or math.dist(xy(t.GetEnd()),pt)<.000003 for pt in pts):d['segments'].append(dict(net=nn,a=xy(t.GetStart()),b=xy(t.GetEnd()),width=p.ToMM(t.GetWidth()),layer=t.GetLayer()))
pd=json.loads((W/'power_geometry.json').read_text(encoding='utf-8'));pd['pad_stitches']+=proof;pd['via_records']+=added
(W/'power_geometry.json').write_text(json.dumps(pd,indent=2),encoding='utf-8');(S/'route_tasks.json').write_text(json.dumps(d,indent=2),encoding='utf-8');p.SaveBoard(str(S/'Base.kicad_pcb'),b)
print('Escaped slot 8 power to',pts[0],flush=True)
