"""KiCad10 Python: test_courtyard_layers.py BOARD OUTPUT_JSON.
Regression: use native layer enums, never display names, for geometry membership.
"""
import pcbnew as p,json,sys,pathlib
b=p.LoadBoard(sys.argv[1]);fs={f.GetReference():f for f in b.GetFootprints()};rows=[]
for ref,layer in [('TP706',p.F_CrtYd),('TP710',p.F_CrtYd),('TP707',p.F_CrtYd),('TP709',p.F_CrtYd),('TP702',p.F_CrtYd),('TP705',p.F_CrtYd),('C5114',p.B_CrtYd),('C5112',p.B_CrtYd),('C5113',p.B_CrtYd)]:
 f=fs[ref];graphics=list(f.GraphicalItems());count=sum(g.GetLayer()==layer for g in graphics);assert count==(4 if ref.startswith('TP') else 1),(ref,count)
 name=b.GetLayerName(layer);assert name in ('F.Courtyard','B.Courtyard','F.CrtYd','B.CrtYd'),name
 assert all(b.GetLayerID(b.GetLayerName(g.GetLayer()))==g.GetLayer() for g in graphics)
 rows.append({'ref':ref,'native_enum':layer,'display_name':name,'native_courtyard_graphics':count,'legacy_abbreviated_name_count':sum(b.GetLayerName(g.GetLayer())==('F.CrtYd' if layer==p.F_CrtYd else 'B.CrtYd')for g in graphics)})
pathlib.Path(sys.argv[2]).write_text(json.dumps({'kicad_version':p.GetBuildVersion(),'passed':True,'checks':rows,'scope':'Native enum membership and display-name roundtrip; prior geometry collision scripts already compared native enums.'},indent=2)+'\n')
print('Courtyard enum regression passed for',len(rows),'footprints')
