from pathlib import Path
exec(compile(Path(__file__).with_name('w_geometry.py').read_text(encoding='utf-8'),__file__,'exec'),globals())
pd=json.loads((W/'power_geometry.json').read_text(encoding='utf-8'));done=[]
assert 'ground_reference_through_bridges' not in pd,'Already bridged; preserve existing work'
# Join the front and back reference planes with legal full-stack return vias.
# These are electrical vias; the four mechanical mounting holes remain removed.
for target in [(x,y) for y in [42.5,40.5,2,4] for x in [20,26,32,40,48,56,64,72,80,88]]:
 if len(done)>=24:break
 found=None
 candidates=sorted(((target[0]+dx/4,target[1]+dy/4) for dx in range(-5,6) for dy in range(-5,6)),key=lambda pt:math.dist(pt,target))
 for pt in candidates:
  if legal_via(pt,'/GND',p.F_Cu,p.B_Cu,.45,.25):via(pt,'/GND',p.F_Cu,p.B_Cu,.45,.25);found=pt;break
 if found:done.append(found)
assert len(done)>=8,('ground plane bridge locations',len(done))
for z in b.Zones():
 z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
 if z.GetNetname()=='/GND':z.SetLocalClearance(p.FromMM(.1));z.SetMinThickness(p.FromMM(.12))
print('Refill all ground references...',len(done),'through vias',flush=True);b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(bp),b)
pd['via_records']+=added;pd['ground_reference_through_bridges']=done;(W/'power_geometry.json').write_text(json.dumps(pd,indent=2),encoding='utf-8')
print('Ground references joined',flush=True)
