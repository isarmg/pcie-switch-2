"""Numpy broad-phase filters and cached via rasters; preserve exact clearance check."""
import numpy as np,math
import sys
sys.path.insert(0,str(STAGE/'tmp/route_deps'))
from scipy import ndimage
_raw_obstacles=ns['obstacles'];_raster_cache={}
class Obstacles(list):pass
def fast_obstacles(task):
 out=Obstacles(_raw_obstacles(task));out.layer=task['layer'];out.nn=task['net'];out.exempt=set(task.get('exempt_nets',[]))|{out.nn};out.start=task['a']['pt'];out.end=task['b']['pt']
 if out:
  ar=np.asarray([[min(a[0],b[0])-r,min(a[1],b[1])-r,max(a[0],b[0])+r,max(a[1],b[1])+r] for a,b,r in out]);out.bb=ar
 else:out.bb=np.empty((0,4))
 return out
def fast_clear(a,b,obs,radius):
 if not obs:return True
 pad=radius+ns['CLEAR']-.000001;bb=obs.bb
 mask=(bb[:,0]<=max(a[0],b[0])+pad)&(bb[:,2]>=min(a[0],b[0])-pad)&(bb[:,1]<=max(a[1],b[1])+pad)&(bb[:,3]>=min(a[1],b[1])-pad)
 for ix in np.flatnonzero(mask):
  c,e,rr=obs[ix]
  if ns['distance'](a,b,c,e)<radius+rr+ns['CLEAR']-.000001:return False
 return True
def stamp(arr,a,b,r,value,mode='count'):
 G=ns['G'];NY,NX=arr.shape
 x0=max(0,math.floor((min(a[0],b[0])-r)/G));x1=min(NX-1,math.ceil((max(a[0],b[0])+r)/G));y0=max(0,math.floor((min(a[1],b[1])-r)/G));y1=min(NY-1,math.ceil((max(a[1],b[1])+r)/G))
 if x0>x1 or y0>y1:return
 xs=np.arange(x0,x1+1)*G;ys=np.arange(y0,y1+1)[:,None]*G;vx=b[0]-a[0];vy=b[1]-a[1];den=vx*vx+vy*vy
 t=np.clip(((xs-a[0])*vx+(ys-a[1])*vy)/den,0,1) if den else 0;hit=(xs-(a[0]+t*vx))**2+(ys-(a[1]+t*vy))**2<=r*r
 if mode=='count':arr[y0:y1+1,x0:x1+1]+=hit.astype(np.int16)*value
 else:arr[y0:y1+1,x0:x1+1]|=hit
def fast_raster(obs,radius):
 G=ns['G'];CLEAR=ns['CLEAR'];NX=ns['NX'];NY=ns['NY'];key=(obs.layer,G,radius,NX,NY)
 if key not in _raster_cache:
  counts=np.zeros((NY,NX),dtype=np.int16)
  for vv in ns['vias']:
   if obs.layer in vv['layers']:
    rr=max(vv['diameter']/2,.05+.10-CLEAR);stamp(counts,vv['pt'],vv['pt'],rr+radius+CLEAR+.001,1)
  _raster_cache[key]=counts
 counts=_raster_cache[key].copy()
 for vv in ns['vias']:
  if vv['net'] in obs.exempt and obs.layer in vv['layers']:
   rr=max(vv['diameter']/2,.05+.10-CLEAR);stamp(counts,vv['pt'],vv['pt'],rr+radius+CLEAR+.001,-1)
 arr=counts>0;inset=ns['INSET'];arr[:inset,:]=1;arr[-inset:,:]=1;arr[:,:inset]=1;arr[:,-inset:]=1
 for s in ns['segments']:
  if s['net'] not in obs.exempt and s['layer']==obs.layer:stamp(arr,s['a'],s['b'],s['width']/2+radius+CLEAR+.001,1,'bool')
 sx,sy=(round(z/G) for z in obs.start);ex,ey=(round(z/G) for z in obs.end)
 if not getattr(obs,'skip_endpoint_check',False):
  if arr[sy,sx] or arr[ey,ex]:raise RuntimeError('blocked grid endpoint')
  labels,count=ndimage.label(~arr)
  if labels[sy,sx]!=labels[ey,ex]:raise RuntimeError('disconnected raster regions')
 return arr
ns['obstacles']=fast_obstacles;ns['clear_segment']=fast_clear;ns['raster']=fast_raster
import time
_raw_route=ns['route']
def timed_route(task):
 t0=time.perf_counter();error=''
 try:return _raw_route(task)
 except (RuntimeError,AssertionError) as e:error=str(e);raise
 finally:
  dt=time.perf_counter()-t0
  if dt>1:print('Search',task['net'],'layer',task['layer'],'grid',ns['G'],'seconds',round(dt,2),error,flush=True)
ns['route']=timed_route
exec(compile((STAGE/'scripts/revW/w_hierarchical.py').read_text(encoding='utf-8'),'hierarchical route','exec'),globals())
exec(compile((STAGE/'scripts/revW/w_power_hierarchy.py').read_text(encoding='utf-8'),'power neck escapes','exec'),globals())
