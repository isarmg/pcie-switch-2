signalnets={q['net'] for q in routes['routes']};seg=defaultdict(list)
def segment_distance(q,x,z):
 dx,dy=z[0]-x[0],z[1]-x[1];den=dx*dx+dy*dy;t=max(0,min(1,((q[0]-x[0])*dx+(q[1]-x[1])*dy)/den)) if den else 0
 return math.dist(q,(x[0]+t*dx,x[1]+t*dy))
for t in b.GetTracks():
 if not isinstance(t,p.PCB_VIA) and t.GetNetname() in signalnets:seg[(t.GetNetname(),t.GetLayer())].append((xy(t.GetStart()),xy(t.GetEnd()),p.ToMM(t.GetWidth())/2))
for t in b.GetTracks():
 nn=t.GetNetname()
 if not isinstance(t,p.PCB_VIA) or nn not in signalnets:continue
 pp=xy(t.GetPosition());rr=p.ToMM(t.GetWidth(t.TopLayer()))/2
 for ll in cu:
  if not t.IsOnLayer(ll):continue
  for x,z,rad in seg[(nn,ll)]:
   if segment_distance(pp,x,z)<=rr+rad+.000001:link(nn,(pt(pp),ll),(pt(x),ll))
