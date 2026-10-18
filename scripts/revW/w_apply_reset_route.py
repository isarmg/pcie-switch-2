"""Add reviewed MR through-hole branch. Requires native DRC after application.
No manufacturing or sequencing qualification is implied by geometric connectivity.
"""
raise SystemExit('REJECTED candidate: violates 0.4mm board-edge clearance. Retained only as a documented failed experiment; do not apply.')
import argparse,json,uuid
from pathlib import Path
import pcbnew as p
ap=argparse.ArgumentParser();ap.add_argument('board',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args()
assert a.board.resolve()!=a.output.resolve()
r=json.loads(Path(__file__).with_name('reset_through_route.json').read_text());b=p.LoadBoard(str(a.board))
net=next(n for n in b.GetNetInfo().NetsByNetcode().values() if n.GetNetname().replace('{slash}','/')=='/TBT_PCIE_PERST_3V3_N')
def uid(key):return str(uuid.uuid5(uuid.NAMESPACE_URL,'revW-reset-through:'+key))
assert uid('via') not in a.board.read_text(),'Already applied'
fs={f.GetReference():f for f in b.GetFootprints()};mr=next(q for q in fs['U605'].Pads() if q.GetNumber()=='3');assert mr.GetNetCode()==net.GetNetCode()
assert abs(p.ToMM(mr.GetPosition().x)-1.325)<1e-6
v=p.PCB_VIA(b);v.SetUuid(p.KIID(uid('via')));v.SetPosition(p.VECTOR2I(*(p.FromMM(x) for x in r['via']['position'])));v.SetWidth(p.FromMM(.45));v.SetDrill(p.FromMM(.25));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNetCode(net.GetNetCode());b.Add(v)
for label,layer in [('b_cu_points',p.B_Cu),('inner_points',p.In15_Cu)]:
 for i,(start,end) in enumerate(zip(r[label],r[label][1:])):
  t=p.PCB_TRACK(b);t.SetUuid(p.KIID(uid(label+str(i))));t.SetStart(p.VECTOR2I(*(p.FromMM(x) for x in start)));t.SetEnd(p.VECTOR2I(*(p.FromMM(x) for x in end)));t.SetWidth(p.FromMM(.1));t.SetLayer(layer);t.SetNetCode(net.GetNetCode());b.Add(t)
p.SaveBoard(str(a.output),b)
print('Added 1 through via and 6 MR segments; native DRC required')
