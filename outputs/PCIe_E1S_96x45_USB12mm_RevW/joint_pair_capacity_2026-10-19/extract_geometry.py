"""Read-only extraction using KiCad's native PCB parser. Never SaveBoard()."""
import pcbnew,json,hashlib,argparse,os
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=os.environ.get('E1S_SOURCE'),required=not bool(os.environ.get('E1S_SOURCE')));ap.add_argument('--out',type=Path,default=Path(__file__).parent);args=ap.parse_args();p=args.source
before=hashlib.sha256(p.read_bytes()).hexdigest();assert before=='e33bc9bf7cb41045c3171abd07677bc36ebe7c3960d61349e4ad5ba2437ecb3c','Input source changed; re-scope and revalidate endpoints before replay';b=pcbnew.LoadBoard(str(p));mm=pcbnew.ToMM;pt=lambda p:[mm(p.x),mm(p.y)]
r={'sha256':before,'version':pcbnew.Version(),'copper_layers':b.GetCopperLayerCount(),'nets':{},'tracks':[],'vias':[],'pads':[],'fps':[],'front_copper_zones':[]};ex={'sha256':before,'kicad':pcbnew.Version(),'pads':[],'drawings':[],'rule_areas':[]}
for k,v in b.GetNetsByNetcode().items():r['nets'][str(k)]=v.GetNetname()
for t in b.GetTracks():
 if isinstance(t,pcbnew.PCB_VIA):r['vias'].append({'net':t.GetNetname(),'xy':pt(t.GetPosition()),'top':b.GetLayerName(t.TopLayer()),'bottom':b.GetLayerName(t.BottomLayer()),'diameter':mm(t.GetWidth(t.TopLayer())),'drill':mm(t.GetDrillValue()),'type':int(t.GetViaType())});continue
 r['tracks'].append({'net':t.GetNetname(),'layer':b.GetLayerName(t.GetLayer()),'start':pt(t.GetStart()),'end':pt(t.GetEnd()),'width':mm(t.GetWidth()),'length':mm(t.GetLength())})
for fp in b.GetFootprints():
 r['fps'].append({'ref':fp.GetReference(),'value':fp.GetValue(),'xy':pt(fp.GetPosition()),'footprint':str(fp.GetFPID().GetLibItemName()),'side':b.GetLayerName(fp.GetLayer())})
 for pad in fp.Pads():
  common={'ref':fp.GetReference(),'pin':pad.GetNumber(),'net':pad.GetNetname(),'xy':pt(pad.GetPosition()),'layers':[b.GetLayerName(l) for l in pad.GetLayerSet().Seq() if pcbnew.IsCopperLayer(l)],'size':pt(pad.GetSize())};r['pads'].append(common)
  bb=pad.GetBoundingBox();ex['pads'].append({**common,'bbox':[mm(bb.GetX()),mm(bb.GetY()),mm(bb.GetRight()),mm(bb.GetBottom())],'angle':pad.GetOrientationDegrees(),'shape':int(pad.GetShape()),'drill':pt(pad.GetDrillSize())})
for x in b.GetDrawings():
 if x.GetLayer()==pcbnew.Edge_Cuts:ex['drawings'].append({'shape':str(x.GetShape()),'start':pt(x.GetStart()),'end':pt(x.GetEnd())})
for z in b.Zones():
 if z.GetLayerSet().Contains(pcbnew.F_Cu) and not z.GetIsRuleArea():
  f=z.GetFilledPolysList(pcbnew.F_Cu);polys=[]
  for i in range(f.OutlineCount()):
   outline=f.COutline(i);shell=[pt(outline.CPoint(j)) for j in range(outline.PointCount())];holes=[]
   for j in range(f.HoleCount(i)):
    h=f.CHole(i,j);holes.append([pt(h.CPoint(k)) for k in range(h.PointCount())])
   polys.append({'shell':shell,'holes':holes})
  r['front_copper_zones'].append({'net':z.GetNetname(),'polygons':polys})
 if z.GetIsRuleArea():ex['rule_areas'].append({'name':z.GetZoneName(),'net':z.GetNetname(),'layers':[b.GetLayerName(l) for l in z.GetLayerSet().Seq()]})
assert before==hashlib.sha256(p.read_bytes()).hexdigest();args.out.mkdir(exist_ok=True)
(args.out/'NATIVE_GEOMETRY.json').write_text(json.dumps(r));(args.out/'extra_geometry.json').write_text(json.dumps(ex))
print('Native extraction:',r['version'],r['copper_layers'],'copper layers',len(r['tracks']),'tracks',len(r['vias']),'vias',len(r['pads']),'pads; source unchanged',before)
