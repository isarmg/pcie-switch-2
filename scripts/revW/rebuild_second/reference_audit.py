import sys,json,hashlib,math
from pathlib import Path
import pcbnew as p
package_dir=None
if '--python-package-dir' in sys.argv:
 i=sys.argv.index('--python-package-dir');package_dir=Path(sys.argv[i+1]);del sys.argv[i:i+2]
if package_dir is not None:sys.path.insert(0,str(package_dir))
from shapely.geometry import Polygon,LineString,Point,mapping,shape
from shapely.ops import unary_union
from shapely import make_valid
selected=set(json.load(open(Path(__file__).parent/'reference_config.json'))['nets']);src,dst=map(Path,sys.argv[1:3]);assert src.with_suffix('.kicad_pro').exists();b=p.LoadBoard(str(src));nets={};ground={};repairs=[]
def xy(v):return [p.ToMM(v.x),p.ToMM(v.y)]
def norm(n):return str(n).replace('{slash}','/')
def points(c):return [xy(c.CPoint(i)) for i in range(c.PointCount())]
for z in b.Zones():
 if norm(z.GetNetname())!='/GND':continue
 for l in b.GetEnabledLayers().Seq():
  if not z.IsOnLayer(l):continue
  f=z.GetFilledPolysList(l);ls=ground.setdefault(b.GetLayerName(l),[])
  for i in range(f.OutlineCount()):
   poly=Polygon(points(f.COutline(i)),[points(f.CHole(i,h)) for h in range(f.HoleCount(i))]);area=poly.area
   if not poly.is_valid:poly=make_valid(poly);repairs.append({'zone':z.m_Uuid.AsString(),'layer':b.GetLayerName(l),'before_area':area,'after_area':poly.area})
   ls.append(poly)
ground={l:unary_union(v) for l,v in ground.items()}
for t in b.GetTracks():
 if norm(t.GetNetname()) not in selected or isinstance(t,p.PCB_VIA):continue
 net=norm(t.GetNetname());layer=b.GetLayerName(t.GetLayer());n=nets.setdefault(net,{});n.setdefault(layer,[]).append(LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2,quad_segs=128))
result={};unmapped=[]
for n,ls in nets.items():
 vias=[t for t in b.GetTracks() if isinstance(t,p.PCB_VIA) and norm(t.GetNetname())==n];near=unary_union([Point(xy(v.GetPosition())).buffer(.35,quad_segs=128) for v in vias]);result[n]={}
 for l,geoms in ls.items():
  idx=0 if l=='F.Cu' else 31 if l=='B.Cu' else int(l[2:-3]);refs=['F.Cu' if i==0 else 'B.Cu' if i==31 else f'In{i}.Cu' for i in (idx-1,idx+1) if 0<=i<=31];signal=unary_union(geoms)
  for ref in refs:
   if ref not in ground:unmapped.append({'net':n,'signal_layer':l,'adjacent_layer':ref});continue
   miss=signal.difference(ground[ref]);outside=miss.difference(near);result[n][ref]={'signal_layer':l,'signal_area_mm2':signal.area,'missing_area_mm2':miss.area,'outside_same_net_via_035mm_area_mm2':outside.area,'missing_geometry':mapping(miss),'outside_geometry':mapping(outside),'sensitivity_missing_mm2':{str(t):signal.difference(ground[ref].buffer(t)).area for t in [.001,.005,.01]}}
r={'board_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'project_sha256':hashlib.sha256(src.with_suffix('.kicad_pro').read_bytes()).hexdigest(),'config_sha256':hashlib.sha256((Path(__file__).parent/'reference_config.json').read_bytes()).hexdigest(),'ground_layers':list(ground),'coverage_scope':'Explicit selected signal traces; both immediately adjacent physical copper layers where actual GND zones exist. Unmapped is not zero coverage.','buffer_quadrant_segments':128,'native_outline_make_valid':repairs,'near_via_radius_mm':.35,'near_via_note':'Geometric classification only; does not waive electrical return-path validation. Full raw missing polygons retained.','unmapped':unmapped,'nets':result,'si_qualified':False}
if len(sys.argv)>3:
 base=json.load(open(sys.argv[3]));delta={}
 for n,rs in result.items():
  delta[n]={}
  for l,v in rs.items():
   old=shape(base['nets'].get(n,{}).get(l,{'missing_geometry':mapping(Polygon())})['missing_geometry']);new=shape(v['missing_geometry']);delta[n][l]={'new_reference_mapping':l not in base['nets'].get(n,{}),'added_missing_area_mm2':new.difference(old).area,'resolved_missing_area_mm2':old.difference(new).area}
 r['baseline_report_sha256']=hashlib.sha256(Path(sys.argv[3]).read_bytes()).hexdigest();r['delta']=delta
Path(dst).write_text(json.dumps(r,indent=2));print(json.dumps({'nets':len(result),'unmapped':unmapped,'midrun_missing':[(n,l,v['outside_same_net_via_035mm_area_mm2']) for n,rs in result.items() for l,v in rs.items() if v['outside_same_net_via_035mm_area_mm2']>1e-9]},indent=2))
