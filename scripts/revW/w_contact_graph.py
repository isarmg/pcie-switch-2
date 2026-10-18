"""Join touching native copper shapes, including a via touching a track interior."""
CELL=2;contact_index=defaultdict(list);contact_objects=[]
def point_segment(q,x,z):
 dx,dy=z[0]-x[0],z[1]-x[1];den=dx*dx+dy*dy;t=max(0,min(1,((q[0]-x[0])*dx+(q[1]-x[1])*dy)/den)) if den else 0
 return math.dist(q,(x[0]+dx*t,x[1]+dy*t))
def ori(x,y,z):return (y[0]-x[0])*(z[1]-x[1])-(y[1]-x[1])*(z[0]-x[0])
def sep(x,z,c,e):
 if max(min(x[0],z[0]),min(c[0],e[0]))<=min(max(x[0],z[0]),max(c[0],e[0])) and max(min(x[1],z[1]),min(c[1],e[1]))<=min(max(x[1],z[1]),max(c[1],e[1])) and ori(x,z,c)*ori(x,z,e)<=0 and ori(c,e,x)*ori(c,e,z)<=0:return 0
 return min(point_segment(x,c,e),point_segment(z,c,e),point_segment(c,x,z),point_segment(e,x,z))
def add_contact(nn,ll,x,z,rad,nd):
 cells=[(nn,ll,xx,yy) for xx in range(math.floor((min(x[0],z[0])-rad)/CELL),math.floor((max(x[0],z[0])+rad)/CELL)+1) for yy in range(math.floor((min(x[1],z[1])-rad)/CELL),math.floor((max(x[1],z[1])+rad)/CELL)+1)]
 ids={i for cell in cells for i in contact_index[cell]}
 for ix in ids:
  c,e,rr,other=contact_objects[ix]
  if sep(x,z,c,e)<=rad+rr+.000001:union(nd,other)
 ix=len(contact_objects);contact_objects.append((x,z,rad,nd))
 for cell in cells:contact_index[cell].append(ix)
for t in b.GetTracks():
 nn=t.GetNetname()
 if nn not in nets:continue
 if isinstance(t,p.PCB_VIA):
  pt=xy(t.GetPosition());rad=p.ToMM(t.GetWidth(t.TopLayer()))/2
  for ll in cu:
   if t.IsOnLayer(ll):add_contact(nn,ll,pt,pt,rad,node(nn,pt,ll))
 else:
  ll=t.GetLayer();x,z=xy(t.GetStart()),xy(t.GetEnd());add_contact(nn,ll,x,z,p.ToMM(t.GetWidth())/2,node(nn,x,ll))
