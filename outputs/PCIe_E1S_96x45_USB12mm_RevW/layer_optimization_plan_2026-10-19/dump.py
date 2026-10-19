import pcbnew,json,hashlib,argparse
from pathlib import Path
ap=argparse.ArgumentParser(description='Read-only KiCad 10 native geometry extraction; does not save or refill the board.');ap.add_argument('--board',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();p=args.board
if p.resolve()==args.out.resolve():raise SystemExit('Output must not overwrite source board')
args.out.parent.mkdir(parents=True,exist_ok=True)
b=pcbnew.LoadBoard(str(p));mm=pcbnew.ToMM
pt=lambda p:[mm(p.x),mm(p.y)]
r={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'version':pcbnew.Version(),'nets':{},'tracks':[],'vias':[],'zones':[],'pads':[],'fps':[]}
for k,v in b.GetNetsByNetcode().items():r['nets'][str(k)]=v.GetNetname()
for t in b.GetTracks():
 if isinstance(t,pcbnew.PCB_VIA):r['vias'].append({'net':t.GetNetname(),'xy':pt(t.GetPosition()),'top':b.GetLayerName(t.TopLayer()),'bottom':b.GetLayerName(t.BottomLayer()),'diameter':mm(t.GetWidth(t.TopLayer())),'drill':mm(t.GetDrillValue()),'type':int(t.GetViaType())});continue
 r['tracks'].append({'net':t.GetNetname(),'layer':b.GetLayerName(t.GetLayer()),'start':pt(t.GetStart()),'end':pt(t.GetEnd()),'width':mm(t.GetWidth()),'length':mm(t.GetLength())})
for z in b.Zones():
 for l in z.GetLayerSet().Seq():
  if not b.IsLayerEnabled(l) or not pcbnew.IsCopperLayer(l):continue
  f=z.GetFilledPolysList(l);polys=[]
  for i in range(f.OutlineCount()):
   outline=f.COutline(i);shell=[pt(outline.CPoint(j)) for j in range(outline.PointCount())]; holes=[]
   for j in range(f.HoleCount(i)):
    h=f.CHole(i,j); holes.append([pt(h.CPoint(k)) for k in range(h.PointCount())])
   polys.append({'shell':shell,'holes':holes})
  r['zones'].append({'net':z.GetNetname(),'layer':b.GetLayerName(l),'polygons':polys})
for fp in b.GetFootprints():
 r['fps'].append({'ref':fp.GetReference(),'value':fp.GetValue(),'xy':pt(fp.GetPosition()),'footprint':str(fp.GetFPID().GetLibItemName()),'side':b.GetLayerName(fp.GetLayer())})
 for pad in fp.Pads():r['pads'].append({'ref':fp.GetReference(),'pin':pad.GetNumber(),'net':pad.GetNetname(),'xy':pt(pad.GetPosition()),'layers':[b.GetLayerName(l) for l in pad.GetLayerSet().Seq() if pcbnew.IsCopperLayer(l)],'size':pt(pad.GetSize())})
out=args.out;out.write_text(json.dumps(r));print('wrote',out,len(r['tracks']),len(r['vias']),len(r['nets']),len(r['zones']))

print('ZONE NETS',[(x['layer'],x['net'],len(x['polygons'])) for x in r['zones']])
