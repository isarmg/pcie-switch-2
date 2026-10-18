import sys,json,hashlib,re
from pathlib import Path
import pcbnew as p
if '--python-package-dir' in sys.argv:
 i=sys.argv.index('--python-package-dir');sys.path.insert(0,sys.argv[i+1]);del sys.argv[i:i+2]
from shapely.geometry import Polygon,LineString,mapping
from shapely.ops import unary_union
from shapely import make_valid
old,new,out=map(Path,sys.argv[1:4])
def norm(x):return str(x).replace('{slash}','/')
def sha(x):return hashlib.sha256(x.read_bytes()).hexdigest()
def xy(v):return [p.ToMM(v.x),p.ToMM(v.y)]
def index(l):return 0 if l=='F.Cu' else 31 if l=='B.Cu' else int(l[2:-3])
def load(path):
 assert path.with_suffix('.kicad_pro').exists();b=p.LoadBoard(str(path));layers={};repairs=[]
 for z in b.Zones():
  if norm(z.GetNetname())!='/GND':continue
  for l in b.GetEnabledLayers().Seq():
   if not z.IsOnLayer(l):continue
   f=z.GetFilledPolysList(l);ls=layers.setdefault(b.GetLayerName(l),[])
   def points(c):return [xy(c.CPoint(i)) for i in range(c.PointCount())]
   for i in range(f.OutlineCount()):
    q=Polygon(points(f.COutline(i)),[points(f.CHole(i,h)) for h in range(f.HoleCount(i))]);area=q.area
    if not q.is_valid:q=make_valid(q);repairs.append({'zone':z.m_Uuid.AsString(),'layer':b.GetLayerName(l),'before_mm2':area,'after_mm2':q.area})
    ls.append(q)
 return b,{l:unary_union(v) for l,v in layers.items()},repairs
before={str(x):sha(x) for x in [old,new,old.with_suffix('.kicad_pro'),new.with_suffix('.kicad_pro')]};a,ag,ar=load(old);b,bg,br=load(new);delta={};hits=[];skipped=[];oldids={t.m_Uuid.AsString() for t in a.GetTracks()};allnames={norm(x.GetNetname()) for f in b.GetFootprints() for x in f.Pads()}
for l in sorted(set(ag)|set(bg)):
 lost=ag.get(l,Polygon()).difference(bg.get(l,Polygon()));gained=bg.get(l,Polygon()).difference(ag.get(l,Polygon()));delta[l]={'lost_area_mm2':lost.area,'gained_area_mm2':gained.area,'lost_bounds':list(lost.bounds) if not lost.is_empty else [],'gained_bounds':list(gained.bounds) if not gained.is_empty else [],'lost_geometry':mapping(lost),'gained_geometry':mapping(gained)}
 if lost.is_empty:continue
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA) or norm(t.GetNetname())=='/GND':continue
  sl=b.GetLayerName(t.GetLayer())
  if abs(index(sl)-index(l))!=1:continue
  if isinstance(t,p.PCB_ARC):skipped.append(t.m_Uuid.AsString());continue
  q=LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2,quad_segs=128);added=q.intersection(lost)
  if added.area<=1e-15:continue
  n=norm(t.GetNetname());paired=n.endswith(('_P','_N')) and n[:-2]+('_N' if n.endswith('_P') else '_P') in allnames
  hits.append({'net':n,'signal_layer':sl,'reference_layer':l,'track_uuid':t.m_Uuid.AsString(),'preexisting_uuid':t.m_Uuid.AsString() in oldids,'differential_named':paired,'added_missing_area_mm2':added.area,'bounds':list(added.bounds),'geometry':mapping(added),'sensitivity_added_area_mm2':{str(v):q.intersection(ag[l].difference(bg[l].buffer(v))).area for v in [.001,.005,.01]}})
after={str(x):sha(x) for x in [old,new,old.with_suffix('.kicad_pro'),new.with_suffix('.kicad_pro')]};r={'source_hashes_before':before,'source_hashes_after':after,'sources_unchanged':before==after,'scope':'Exact polygon lost/gained for all actual GND-filled layers; all candidate non-GND straight tracks on each immediately adjacent physical layer checked at actual halfwidth. Includes low-speed and power tracks, not just selected differential nets. Comparison isolates reference-plane changes using candidate signal geometry in both plane states. No SI qualification.','quad_segs':128,'native_outline_repairs_before':ar,'native_outline_repairs_after':br,'layers':delta,'affected_track_projections':hits,'skipped_arcs':skipped,'differential_added_area_sum_mm2':sum(v['added_missing_area_mm2'] for v in hits if v['differential_named']),'note':'Summed individual track intersections can double-count joined overlap. The zero/nonzero differential result does not rely on summing disjointness.'};out.write_text(json.dumps(r,indent=2));print(json.dumps({'layers':{l:{k:v for k,v in d.items() if not k.endswith('geometry')} for l,d in delta.items()},'affected':[ {k:v for k,v in h.items() if k!='geometry'} for h in hits],'differential_added_area_sum_mm2':r['differential_added_area_sum_mm2'],'sources_unchanged':r['sources_unchanged']},indent=2))
