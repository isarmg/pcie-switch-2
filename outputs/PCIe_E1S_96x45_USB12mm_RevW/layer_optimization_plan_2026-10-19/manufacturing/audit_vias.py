from pathlib import Path
import re,json,hashlib,csv,itertools,collections,argparse
parser=argparse.ArgumentParser(description='Read-only via audit; refuses source bytes that differ from the reviewed baseline unless an explicit new expected hash is supplied.')
parser.add_argument('--board', type=Path, default=Path('outputs/PCIe_E1S_96x45_USB12mm_RevW/Main_12E1S/Main_12E1S.kicad_pcb'))
parser.add_argument('--out-dir', type=Path, default=Path(__file__).resolve().parent)
parser.add_argument('--expected-sha256', default='e33bc9bf7cb41045c3171abd07677bc36ebe7c3960d61349e4ad5ba2437ecb3c')
a=parser.parse_args();p=a.board;out=a.out_dir
actual_hash=hashlib.sha256(p.read_bytes()).hexdigest()
if actual_hash != a.expected_sha256:raise SystemExit('Source hash mismatch: expected '+a.expected_sha256+' got '+actual_hash)
out.mkdir(parents=True,exist_ok=True)
s=p.read_text()
layers=['F.Cu']+[f'In{i}.Cu' for i in range(1,31)]+['B.Cu']; li={v:i+1 for i,v in enumerate(layers)}
vs=[]
for m in re.finditer(r'^\t\(via(?:\s+(blind|micro))?\n(.*?)^\t\)',s,re.M|re.S):
 b=m.group(2)
 def a(k):return re.search(r'\('+k+r'\s+([^\n\)]*)\)',b).group(1)
 l=re.findall(r'"([^"]+)"',a('layers'));x,y=map(float,a('at').split());sz=float(a('size'));dr=float(a('drill'))
 vs.append(dict(uuid=a('uuid').strip('"'),net=a('net').strip('"'),type=m.group(1)or'through',x=x,y=y,size_mm=sz,drill_mm=dr,annular_mm=(sz-dr)/2,layer_start=l[0],layer_end=l[1],start=li[l[0]],end=li[l[1]],span=li[l[1]]-li[l[0]],line=s.count('\n',0,m.start())+1))
assert len(vs)==len(re.findall(r'^\t\(via(?:\s|\n)',s,re.M))
with (out/'vias.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=vs[0]);w.writeheader();w.writerows(vs)
keys=['type','size_mm','drill_mm','layer_start','layer_end','start','end','span']
counts=collections.Counter(tuple(v[k] for k in keys) for v in vs)
rows=[dict(zip(keys,k),count=v) for k,v in sorted(counts.items(),key=lambda kv:(kv[0][5],kv[0][6],kv[0][0],kv[0][1]))]
with (out/'via_pairs.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
bypos=collections.defaultdict(list)
for v in vs:bypos[(round(v['x'],5),round(v['y'],5))].append(v)
chains=[]
for xy,g in bypos.items():
 if len(g)>1:
  g=sorted(g,key=lambda x:(x['start'],x['end']));
  chains.append(dict(x=xy[0],y=xy[1],n=len(g),same_net=len(set(v['net'] for v in g))==1,net=list(set(v['net'] for v in g)),spans=[(v['start'],v['end'],v['type']) for v in g],touch_count=sum(a['end']==b['start'] for a,b in itertools.combinations(g,2)),uuids=[v['uuid'] for v in g]))
# Crossing layer span categories are not automatically geometric shorts; they are manufacturing sublamination constraints.
spans=sorted(set((v['start'],v['end']) for v in vs if v['type']!='through'))
crosses=[(a,b) for a,b in itertools.combinations(spans,2) if a[0]<b[0]<a[1]<b[1]]
padblocks=re.findall(r'^\t\(footprint.*?^\t\)',s,re.M|re.S)
centred=[]
for b in padblocks:
 refm=re.search(r'\(property "Reference" "([^"]+)"',b);fm=re.search(r'^\t\t\(at ([^\)]+)\)',b,re.M);lm=re.search(r'^\t\t\(layer "([^"]+)"\)',b,re.M)
 if not(refm and fm and lm):continue
 ref=refm.group(1);ff=list(map(float,fm.group(1).split()));fx,fy=ff[:2];ang=ff[2] if len(ff)>2 else 0
 # local pad transformations are rotated; test centers only. Backside footprints also use their stored rotation; no additional mirroring.
 import math
 for pb in re.findall(r'^\t\t\(pad .*?^\t\t\)',b,re.M|re.S):
  if not re.match(r'\s*\(pad "[^"]*" smd',pb):continue
  pm=re.search(r'\(at ([^\)]+)\)',pb);nm=re.search(r'\(net "([^"]+)"',pb);nn=re.match(r'\s*\(pad "([^"]*)"',pb)
  if not(pm and nm):continue
  px,py=map(float,pm.group(1).split()[:2]);t=math.radians(-ang);x=fx+px*math.cos(t)-py*math.sin(t);y=fy+px*math.sin(t)+py*math.cos(t)
  for v in bypos.get((round(x,5),round(y,5)),[]):
   if v['net']==nm.group(1):centred.append(dict(reference=ref,pad=nn.group(1),layer=lm.group(1),via_uuid=v['uuid'],net=v['net'],via_type=v['type'],via_size=v['size_mm'],via_drill=v['drill_mm'],span=[v['start'],v['end']]))
summary=dict(source=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),copper_layer_count=len(layers),thickness_mm=float(re.search(r'\(general\s*\(thickness ([^\)]+)',s).group(1)),explicit_stackup='(stackup' in s,via_count=len(vs),type_counts=dict(collections.Counter(v['type'] for v in vs)),size_drill_counts=[dict(size_mm=k[0],drill_mm=k[1],count=v) for k,v in collections.Counter((v['size_mm'],v['drill_mm']) for v in vs).most_common()],nonthrough_span_counts=dict(sorted(collections.Counter(v['span'] for v in vs if v['type']!='through').items())),via_pairs=rows,same_xy_multiple_via_groups=chains,non_nested_crossing_layer_span_pairs=crosses,rounded_10nm_center_smd_vias=centred)
(out/'audit.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in summary.items() if k not in ['same_xy_multiple_via_groups','rounded_10nm_center_smd_vias','via_pairs','non_nested_crossing_layer_span_pairs']},ensure_ascii=False,indent=2))
print('ROWS',len(rows),'SPAN_CROSS_PAIRS',len(crosses),'SAME_XY_GROUPS',len(chains),'MAX_COLOCATED',max((c['n'] for c in chains),default=1),'ROUNDED_10NM_CENTER_SMD_VIAS',len(centred))
print('SAME_XY_COUNTS',collections.Counter(c['n'] for c in chains))
print('SPAN_CROSSES',crosses[:15]);print('TOP_SMD_REFS',collections.Counter(v['reference'] for v in centred).most_common(20))
print('LARGEST_CHAINS',json.dumps(sorted(chains,key=lambda c:-c['n'])[:8]))
print('VIA_LAYER_PAIRS')
for r in rows:print(r)
