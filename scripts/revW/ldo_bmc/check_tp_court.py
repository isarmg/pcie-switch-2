import pcbnew as p,json,math,sys
from pathlib import Path
r=Path(__file__).parent;b=p.LoadBoard(sys.argv[1]);fs={f.GetReference():f for f in b.GetFootprints()}
def box(items):
 bb=[i.GetBoundingBox()for i in items];return [min(q.GetLeft()for q in bb),min(q.GetTop()for q in bb),max(q.GetRight()for q in bb),max(q.GetBottom()for q in bb)]
def gap(a,z):return math.hypot(max(z[0]-a[2],a[0]-z[2],0),max(z[1]-a[3],a[1]-z[3],0))/1e6
out={}
for ref in ['TP702','TP705','TP709','TP707','TP706','TP710']:
 f=fs[ref];a=box(list(f.Pads())+[g for g in f.GraphicalItems()if g.GetLayer()==p.F_CrtYd]);near=[]
 for other in fs.values():
  if other.GetReference()==ref:continue
  items=[g for g in other.GraphicalItems()if g.GetLayer()==p.F_CrtYd]
  if items:
   z=box(items);near.append(dict(ref=other.GetReference(),bbox_mm=[v/1e6 for v in z],bbox_gap_mm=gap(a,z)))
 near.sort(key=lambda x:x['bbox_gap_mm']);out[ref]=dict(pad_and_courtyard_bbox_mm=[v/1e6 for v in a],nearest_F_courtyard_bboxes=near[:8],no_F_courtyard_bbox_overlap=all(x['bbox_gap_mm']>0 for x in near))
Path(sys.argv[2]).write_text(json.dumps(out,indent=2));print(out);assert all(x['no_F_courtyard_bbox_overlap']for x in out.values())
