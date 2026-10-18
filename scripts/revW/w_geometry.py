"""Load native geometry, conservative pads, all-net drill spacing, safe track IU."""
from pathlib import Path
root=Path(__file__).resolve().parents[2]
src=(root/'scripts/revV/v_power.py').read_text(encoding='utf-8')
prefix=src.split('# Source and return rail pad stitches.')[0]
prefix=prefix.replace('PCIe_E1S_96x45_12VPower_RevV','PCIe_E1S_96x45_USB12mm_RevW').replace('work/revV','work/revW').replace("assert not (W/'power_geometry.json').exists(),'Do not duplicate routed power'",'').replace("power=set(json.loads((W/'power_refs.json').read_text(encoding='utf-8')))","power=set()")
prefix=prefix.replace("insert((x,z,rad,nn,ll,'pad',0))","insert((x,z,rad,nn,ll,'pad',0));insert(((p.ToMM(bb.GetX()),p.ToMM(bb.GetY())),(p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom())),0,nn,ll,'rect',0))")
prefix=prefix.replace('        limit=rad+rr+.079', '''        if kind=='rect':
            if (c[0]<=x[0]<=e[0] and c[1]<=x[1]<=e[1]) or (c[0]<=z[0]<=e[0] and c[1]<=z[1]<=e[1]):return False
            corners=[c,(e[0],c[1]),e,(c[0],e[1])]
            if any(dist(x,z,q,t)<rad+.079 for q,t in zip(corners,corners[1:]+corners[:1])):return False
            continue
        limit=rad+rr+.079''')
exec(compile(prefix,'native collision geometry','exec'),globals())
local=src[src.index('def localroute('):src.index('controlfailed=[]')].replace('def localroute(start,end,nn,width):','def localroute(start,end,nn,width,side=p.F_Cu):').replace('    side=p.F_Cu;rad=width/2','    rad=width/2')
exec(compile(local,'local router','exec'),globals())
def legal_via(pt,nn,side,target,dia,dr):
 for ll in span(side,target):
  if not clear(pt,pt,nn,ll,dia/2,dr):return False
  for x,z,rr,net,layer,kind,hole in nearby(ll,pt,pt):
   if kind=='via' and math.dist(pt,x)<(dr+hole)/2+.251:return False
 return True
