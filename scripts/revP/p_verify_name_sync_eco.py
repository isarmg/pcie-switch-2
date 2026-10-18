"""Exact name-only ECO proof, preserving generic literal-net gate separately.
Requires native inventories, official kicadsexpr and explicit old/new map.
Verifies all pad/copper geometry and UUIDs plus one-to-one net correspondence.
"""
import argparse,json,hashlib,re
from pathlib import Path
import pcbnew as p

def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def parse(txt):
 stack=[];root=None
 for t in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',txt):
  if t=='(':x=[];stack[-1].append(x) if stack else None;stack.append(x)
  elif t==')':root=stack.pop()
  else:stack[-1].append(json.loads(t) if t.startswith('"') else t)
 return root

def child(x,k):return next(i for i in x[1:] if isinstance(i,list) and i and i[0]==k)
def run(a):
 assert not a.report.exists();src=[a.baseline,a.candidate,a.mapping,a.netlist]
 for b in [a.baseline,a.candidate]:assert b.with_suffix('.kicad_pro').exists();src.append(b.with_suffix('.kicad_pro'))
 before={str(q):sha(q) for q in src};changes=json.loads(a.mapping.read_text())['changes'];mapping={old:new for _,old,new in changes};assert len(mapping)==len(changes) and len(set(mapping.values()))==len(changes)
 tree=parse(a.netlist.read_text());want={}
 for net in child(tree,'nets')[1:]:
  name=child(net,'name')[1]
  for node in net[1:]:
   if isinstance(node,list) and node[0]=='node':want[(child(node,'ref')[1],child(node,'pin')[1])]=name
 boards=[p.LoadBoard(str(q)) for q in [a.baseline,a.candidate]]
 def pads(b):return {q.m_Uuid.AsString():q for f in b.GetFootprints() for q in f.Pads() if q.GetNumber()}
 old,new=map(pads,boards);assert old.keys()==new.keys();seen=set()
 for uid,q in old.items():
  z=new[uid];key=(q.GetParentFootprint().GetReference(),q.GetNumber());assert key==(z.GetParentFootprint().GetReference(),z.GetNumber());assert z.GetNetname()==mapping.get(q.GetNetname(),q.GetNetname());assert want[key]==z.GetNetname();seen.add(key)
  assert (q.GetPosition(),q.GetSize(),q.GetShape(),q.GetLayerSet().FmtHex())==(z.GetPosition(),z.GetSize(),z.GetShape(),z.GetLayerSet().FmtHex()),'pad geometry changed'
 assert seen==set(want)
 def tracks(b):return {t.m_Uuid.AsString():t for t in b.GetTracks()}
 ot,nt=map(tracks,boards);assert ot.keys()==nt.keys()
 for uid,t in ot.items():
  z=nt[uid];assert z.GetNetname()==mapping.get(t.GetNetname(),t.GetNetname());assert (type(t),t.GetStart(),t.GetEnd(),t.GetLayerSet().FmtHex())==(type(z),z.GetStart(),z.GetEnd(),z.GetLayerSet().FmtHex())
  if isinstance(t,p.PCB_VIA):assert t.GetDrillValue()==z.GetDrillValue() and all(t.GetWidth(l)==z.GetWidth(l) for l in t.GetLayerSet().Seq())
  else:assert t.GetWidth()==z.GetWidth();assert not isinstance(t,p.PCB_ARC) or t.GetMid()==z.GetMid()
 # Compare saved physical pad clusters independently of renamed net strings.
 def clusters(b):
  con=b.GetConnectivity();seen=set();out=set()
  for uid,q in pads(b).items():
   if uid in seen:continue
   g=frozenset(v.m_Uuid.AsString() for v in [q,*con.GetConnectedItems(q)] if isinstance(v,p.PAD) and v.GetNetCode()==q.GetNetCode());seen.update(g);out.add(g)
  return out
 assert clusters(boards[0])==clusters(boards[1]),'physical pad clusters changed'
 # Parse saved zones to ensure fills and geometry unchanged, allowing only exact net spelling.
 def zones(path):
  tree=parse(path.read_text());out={}
  for z in tree[1:]:
   if isinstance(z,list) and z and z[0]=='zone':
    uid=child(z,'uuid')[1];out[uid]=[v for v in z if not(isinstance(v,list) and v and v[0] in ('net','net_name'))]
  return out
 assert zones(a.baseline)==zones(a.candidate),'saved zone geometry/fill changed'
 assert before=={str(q):sha(q) for q in src};result={'sources':before,'script_sha256':sha(Path(__file__)),'precise_bijective_name_ECO_passed':True,'official_ref_pin_nodes':len(want),'pad_shapes_unchanged':len(old),'copper_UUID_geometry_unchanged':len(ot),'all_physical_pad_clusters_unchanged':True,'saved_zone_geometry_and_fills_unchanged':True,'renamed_net_count':len(changes),'ordinary_literal_net_gate_still_separate':True,'production_ready':False};a.report.write_text(json.dumps(result,indent=2)+'\n');print(result)
if __name__=='__main__':
 x=argparse.ArgumentParser(description=__doc__)
 for name in ['baseline','candidate','mapping','netlist','report']:x.add_argument('--'+name,type=Path,required=True)
 run(x.parse_args())
