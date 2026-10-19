import pcbnew,json,collections,argparse,hashlib
from pathlib import Path
parser=argparse.ArgumentParser(description='Native read-only KiCad via cross-check; run the text audit in out-dir first.')
parser.add_argument('--board',type=Path,default=None)
parser.add_argument('--out-dir',type=Path,default=Path(__file__).resolve().parent)
parser.add_argument('--expected-sha256',default='e33bc9bf7cb41045c3171abd07677bc36ebe7c3960d61349e4ad5ba2437ecb3c')
a=parser.parse_args();out=a.out_dir;src=json.loads((out/'audit.json').read_text())
board=a.board or Path(src['source'])
actual_hash=hashlib.sha256(board.read_bytes()).hexdigest()
if actual_hash!=a.expected_sha256 or actual_hash!=src['sha256']:raise SystemExit('Source hash mismatch; text and native audits must examine identical expected bytes.')
src['source']=str(board)
b=pcbnew.LoadBoard(src['source']); vias=[t for t in b.GetTracks() if isinstance(t,pcbnew.PCB_VIA)]
print('KiCad',pcbnew.Version(),'layers',b.GetCopperLayerCount(),'vias',len(vias),'thickness',pcbnew.ToMM(b.GetDesignSettings().GetBoardThickness()))
print('via enum',collections.Counter(v.GetViaType() for v in vias))
print('size drill',collections.Counter((pcbnew.ToMM(v.GetWidth(v.TopLayer())),pcbnew.ToMM(v.GetDrillValue())) for v in vias))
print('native explicit stackup',b.GetDesignSettings().m_HasStackup); print('stackup info',[x for x in dir(b.GetDesignSettings().GetStackupDescriptor()) if any(t in x.lower() for t in ['get','count','thick'])])
bpos=collections.defaultdict(list)
for v in vias:bpos[(v.GetPosition().x,v.GetPosition().y)].append(v)
exact=[]
for f in b.GetFootprints():
 for p in f.Pads():
  if p.GetAttribute()!=pcbnew.PAD_ATTRIB_SMD:continue
  for v in bpos.get((p.GetPosition().x,p.GetPosition().y),[]):
   if p.GetNetCode()==v.GetNetCode() and v.IsOnLayer(f.GetLayer()):exact.append(dict(reference=f.GetReference(),pad=p.GetNumber(),net=p.GetNetname(),uuid=str(v.m_Uuid.AsString())))
print('native exact center smd via count',len(exact),collections.Counter(e['reference'] for e in exact).most_common(10))
(out/'native.json').write_text(json.dumps(dict(kicad_version=pcbnew.Version(),layer_count=b.GetCopperLayerCount(),via_count=len(vias),has_explicit_stackup=b.GetDesignSettings().m_HasStackup,exact_center_smd_vias=exact),indent=2))
assert len(vias)==src['via_count']
assert {v.m_Uuid.AsString() for v in vias}=={r['uuid'] for r in __import__('csv').DictReader((out/'vias.csv').open())}

rows={r['uuid']:r for r in __import__('csv').DictReader((out/'vias.csv').open())}
for v in vias:
 r=rows[v.m_Uuid.AsString()]
 assert b.GetLayerName(v.TopLayer())==r['layer_start'] and b.GetLayerName(v.BottomLayer())==r['layer_end']
 assert abs(pcbnew.ToMM(v.GetWidth(v.TopLayer()))-float(r['size_mm']))<1e-8
 assert abs(pcbnew.ToMM(v.GetDrillValue())-float(r['drill_mm']))<1e-8
print('PASS independent native via identity/count/layer-pair/size/drill cross-check')
