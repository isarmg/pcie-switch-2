#!/usr/bin/env python3
"""Apply only reviewed RevW TBT_USB2_TOP tracks, retaining every other byte.
Usage: KiCad 10 AppRun python3.11 apply_usb2_pair.py INPUT OUTPUT
Only geometry improvement; SI, stackup, return path and manufacture remain open.
Requires original segment UUIDs AND geometry; fails closed after any route edit.
Understands KiCad 10 internal {slash} names after schematic synchronization.
"""
import sys,json,math,re,uuid
from pathlib import Path
import pcbnew as p
src,dst=map(Path,sys.argv[1:3]);assert src.resolve()!=dst.resolve(),'Use a separate candidate output'
r=json.loads(Path(__file__).with_name('usb2_pair_route.json').read_text());norm=lambda s:s.replace('{slash}','/')
b=p.LoadBoard(str(src));fs={f.GetReference():f for f in b.GetFootprints()}
expected={'/TBT_USB2_TOP_N':[('J402','A7',[73.43,22.25]),('U503','L6',[76,32.7])],'/TBT_USB2_TOP_P':[('J402','A6',[73.43,22.75]),('U503','K6',[76,33.2])]}
for net,ends in expected.items():
 for ref,pin,pt in ends:
  pads=[a for a in fs[ref].Pads() if a.GetNumber()==pin and norm(a.GetNetname())==net]
  assert len(pads)==1,(ref,pin,net)
  assert math.dist([p.ToMM(pads[0].GetPosition().x),p.ToMM(pads[0].GetPosition().y)],pt)<1e-6,'Endpoint moved: reroute required'
before={net:sum(p.ToMM(t.GetLength()) for t in b.GetTracks() if norm(t.GetNetname())==net and not isinstance(t,p.PCB_VIA)) for net in r['nets']}
s=src.read_text();seen=set();netnames={}
def remove(m):
 block=m.group(0);uid=re.search(r'\(uuid "([^"]+)"\)',block).group(1)
 if uid not in r['original_segments']:return block
 old=r['original_segments'][uid]
 assert norm(block)==old['block'],'Original segment changed: '+uid
 raw=re.search(r'\(net "([^"]+)"\)',block).group(1);netnames[old['net']]=raw;seen.add(uid);return ''
s=re.sub(r'\t\(segment\n.*?\n\t\)',remove,s,flags=re.S)
assert seen==set(r['original_segments']),'Some original segments missing; refuse partial replacement'
new=[]
for net,pts in r['nets'].items():
 for a,z in zip(pts,pts[1:]):
  new.append(f'\t(segment\n\t\t(start {a[0]:.6f} {a[1]:.6f})\n\t\t(end {z[0]:.6f} {z[1]:.6f})\n\t\t(width {r["width"]})\n\t\t(layer "In27.Cu")\n\t\t(net "{netnames[net]}")\n\t\t(uuid "{uuid.uuid4()}")\n\t)\n')
idx=s.rfind(')');s=s[:idx]+''.join(new)+s[idx:];dst.write_text(s)
after={net:sum(math.dist(a,z) for a,z in zip(pts,pts[1:])) for net,pts in r['nets'].items()}
print(json.dumps({'removed_segments':len(seen),'added_segments':len(new),'before_mm':before,'after_mm':after,'skew_before_mm':abs(before[list(before)[0]]-before[list(before)[1]]),'skew_after_mm':abs(after[list(after)[0]]-after[list(after)[1]])},indent=2))
