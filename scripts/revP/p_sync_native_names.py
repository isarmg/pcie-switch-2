"""Synchronize PCB internal names from a fresh official kicadsexpr netlist.
Usage: KiCad-python p_sync_native_names.py board.pcb fresh.net output.pcb

Checks every ref.pin in both directions and forbids splitting an existing PCB
net. No geometry, copper netcode assignment, or pin mapping is changed.
Schematic global labels and JSON metadata remain display names (e.g. /GND);
KiCad internal names use escaped literals (e.g. {slash}GND).
"""
import sys,re,json,collections,pcbnew as p
board,netlist,out=sys.argv[1:]
stack=[];root=None
for t in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',open(netlist).read()):
 if t=='(': x=[]; stack[-1].append(x) if stack else None; stack.append(x)
 elif t==')': root=stack.pop()
 else: stack[-1].append(json.loads(t) if t.startswith('"') else t)
def child(x,k):return next((i for i in x[1:] if isinstance(i,list) and i and i[0]==k),None)
def val(x,k):return child(x,k)[1]
want={}
for net in child(root,'nets')[1:]:
 name=val(net,'name')
 for node in net[1:]:
  if isinstance(node,list) and node[0]=='node':
   key=(val(node,'ref'),val(node,'pin'));assert key not in want or want[key]==name;want[key]=name
b=p.LoadBoard(board);mapped=collections.defaultdict(set);missing=[];seen=set()
for f in b.GetFootprints():
 for pad in f.Pads():
  if not pad.GetNumber():continue
  key=(f.GetReference(),pad.GetNumber()); seen.add(key)
  if key in want: mapped[pad.GetNetCode()].add(want[key])
  elif pad.GetNetname():missing.append((key,pad.GetNetname()))
assert not missing,('PCB pads absent from schematic',missing[:20])
assert not set(want)-seen,('schematic nodes missing PCB',list(set(want)-seen)[:20])
assert all(len(v)==1 for v in mapped.values()),('inconsistent mapping',[(k,list(v)) for k,v in mapped.items() if len(v)>1][:10])
# Also prohibit merging distinct old nets merely by assigning the same name.
reverse=collections.defaultdict(set)
for code,names in mapped.items():
 for name in names:reverse[name].add(code)
assert all(len(codes)==1 for codes in reverse.values()), ('merge would change connectivity',dict(reverse))
nets=b.GetNetsByNetcode();changes=[]
for code,names in mapped.items():
 new=next(iter(names));old=nets[code].GetNetname()
 if old!=new:changes.append((code,old,new));nets[code].SetNetname(new)
p.SaveBoard(out,b)
print(json.dumps({'nodes':len(want),'physical_changes_to_copper':False,'renamed_nets':len(changes),'changes':changes},indent=2))
