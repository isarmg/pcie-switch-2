from directed_port_trial import *
checks=[]
def reject(points,label):
 try:directed_offset(points,.1)
 except ValueError:checks.append(label);return
 raise AssertionError(label)
reject([[0,0],[1,0],[0,0],[2,0]],'180 degree reversal rejected')
reject([[0,0],[0,1],[1,1]],'wrong source side rejected')
reject([[0,0],[1,0],[1,1]],'wrong destination side rejected')
# Explicit independent miter geometry: every turn retained; each generated
# corner sits at the declared signed offset from both infinite incident lines.
points=[[0,0],[1,0],[2,1],[3,1],[3,2],[4,2]]
for offset in [-.1,.1]:
 out=directed_offset(points,offset);assert len(out)==len(points)
 for i,(x,y) in enumerate(out[1:-1],1):
  for a,b in [(points[i-1],points[i]),(points[i],points[i+1])]:
   ux,uy=(b[0]-a[0],b[1]-a[1]);le=math.hypot(ux,uy)
   assert abs((ux*(y-a[1])-uy*(x-a[0]))/le-offset)<1e-9
 assert math.dist(out[0],[0,offset])<1e-9 and math.dist(out[-1],[4,2+offset])<1e-9
checks.append('all miter vertices retained, exact signed offset and east endpoint polarity')
q=compact_collinear([[0,0],[.5,0],[1,0],[1,1],[1,1],[2,1]])
assert q==[[0,0],[1,0],[1,1],[2,1]]
assert compact_collinear([[0,0],[1,0],[.5,0]])==[[0,0],[1,0],[.5,0]]
checks.append('compression preserves turns and reversals, removes only duplicate or forward collinear points')
old=json.loads((D/'REGRESSION_OLD_RX1_THEN_RX0.json').read_text());bad=old['attempts'][1]
p,n=[LineString(t['points']) for t in bad['traces']];assert not p.is_simple and p.distance(n)-.1<0
partner=[]
for t in bad['traces']:
 line=LineString(t['points']);partner.append(min(line.distance(Point(v['xy']))-.05-v['diameter']/2 for v in d['vias'] if v['net']!=t['net']))
assert min(partner)<0
checks.append('old self-intersection, PN crossing and opposite-net via overlap independently reproduced')
# Self-crossing polygon with east-facing ends cannot become a silently
# shortened successful offset: reject or retain all corners for full checking.
cross=[[0,0],[2,0],[2,2],[0,2],[0,1],[3,1]]
try:
 out=directed_offset(cross,.1);assert len(out)==len(cross)
 assert not LineString(out).is_simple
except ValueError:pass
checks.append('crossing centerline cannot silently be repaired or clipped')
(D/'INDEPENDENT_OFFSET_TESTS.json').write_text(json.dumps({'pass':True,'source_sha256':d['sha256'],'checks':checks},indent=2)+'\n');print('independent offset tests',len(checks))
