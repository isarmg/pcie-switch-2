import pcbnew,json,hashlib,os
from pathlib import Path
D=Path(__file__).parent;p=Path(os.environ['E1S_SOURCE']).resolve();b=pcbnew.LoadBoard(str(p));cs=[l for l in b.GetEnabledLayers().Seq() if pcbnew.IsCopperLayer(l)];r=[];n=0
for t in b.GetTracks():
 if not isinstance(t,pcbnew.PCB_VIA):continue
 n+=1;ds={b.GetLayerName(l):pcbnew.ToMM(t.GetWidth(l)) for l in cs}
 if len(set(ds.values()))!=1:r.append({'net':t.GetNetname(),'xy':[pcbnew.ToMM(t.GetPosition().x),pcbnew.ToMM(t.GetPosition().y)],'diameters':ds})
x={'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'via_count':n,'layer_varying_diameter_vias':r,'top_diameter_conservative_for_all_layers':len(r)==0}
(D/'VIA_DIAMETER_CHECK.json').write_text(json.dumps(x,indent=2));print(x);assert not r
