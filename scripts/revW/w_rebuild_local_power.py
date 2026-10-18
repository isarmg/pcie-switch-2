"""Rebuild verified local TPS62132/133 input and ground copper from R1 source.
Run with KiCad10 Python: SCRIPT SOURCE.kicad_pcb NEW_OUTPUT.kicad_pcb.
Official TPS62130 RevF Table6-1/11.1; this is not a full power-loop qualification.
"""
from pathlib import Path
import pcbnew as p,shutil,json,uuid,sys,hashlib
src,dst=map(Path,sys.argv[1:3]);root=dst.parent
assert src.resolve()!=dst.resolve(), 'Refuse in-place edit'
assert hashlib.sha256(src.read_bytes()).hexdigest()=='de635e94e064d38aac5c28133bc7f5e38eb8d7bfee041a3dba8ee77283be24b8', 'Unexpected source'
assert src.with_suffix('.kicad_pro').exists()
assert not dst.exists(), 'Refuse overwrite'
shutil.copyfile(src.with_suffix('.kicad_pro'),dst.with_suffix('.kicad_pro'))
b=p.LoadBoard(str(src));fs={f.GetReference():f for f in b.GetFootprints()};added=[]
ADDED_UUIDS=['d3f8fd25-b5ff-4146-8119-8115cb0c8c01', 'f01b9e14-2dea-4927-9c30-e6b16ae0f799', '4141d628-1ea2-438f-8ae6-bdcdc3bf8fc8', '2178db32-cc36-4781-94b1-a9153dcba8a1', 'ea9a438e-8cd2-4da6-906a-f3194b8540b6', 'aaace832-4d38-4022-b57c-e80a3797d846', '1db15030-c347-4d47-a3ba-11e8daa8177d', '8e2a5a0b-9088-4235-a7ee-542fe0d6d6ea']
def seg(a,z,net,w):
 t=p.PCB_TRACK(b);t.SetStart(a);t.SetEnd(z);t.SetLayer(p.F_Cu);t.SetWidth(p.FromMM(w));t.SetNet(net);b.Add(t);added.append(t.m_Uuid.AsString())
for ref in ['U31','U506']:
 pads={q.GetNumber():q for q in fs[ref].Pads()};ep=pads['17'].GetPosition()
 for pin in ['6','15','16']:
  q=pads[pin];v=q.GetPosition();end=p.VECTOR2I(v.x,ep.y+(p.FromMM(.7) if v.y>ep.y else -p.FromMM(.7)))
  seg(v,end,q.GetNet(),.3)
pads={q.GetNumber():q for q in fs['U31'].Pads()}
for pin in ['10','12']:seg(pads['11'].GetPosition(),pads[pin].GetPosition(),pads[pin].GetNet(),.3)
changed=[]
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):continue
 pts=[t.GetStart(),t.GetEnd()]
 if t.GetLayer()==p.F_Cu and t.GetNetname()=='{slash}AUX_12V_PROTECTED' and any((v-pads['11'].GetPosition()).EuclideanNorm()<10000 for v in pts) and t.GetLength()>p.FromMM(1):
  changed.append({'uuid':t.m_Uuid.AsString(),'old_width':p.ToMM(t.GetWidth())});t.SetWidth(p.FromMM(.5))
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(dst),b)
s=dst.read_text()
for old,new in zip(added,ADDED_UUIDS):s=s.replace(old,new)
dst.write_text(s);added=ADDED_UUIDS.copy()
(root/'local_power_changes.json').write_text(json.dumps({'added':added,'broadened':changed},indent=2));print(dst)
