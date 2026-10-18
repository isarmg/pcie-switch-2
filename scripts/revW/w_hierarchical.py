"""Fine BGA escapes to the open board region, then a conservative coarse route."""
from collections import deque,Counter
import heapq
def hierarchy(task):
 obs=ns['obstacles'](task);rad=task['width']/2;start=task['a']['pt'];end=task['b']['pt']
 if fast_clear(start,end,obs,rad):return [start,end]
 arr=fast_raster(obs,rad);G=ns['G'];height,width=arr.shape;stride=max(1,round(.1/G));radius=math.ceil(stride/2)+1
 inflated=ndimage.maximum_filter(arr,size=radius*2+1,mode='constant',cval=1)
 coarse=inflated[::stride,::stride];labels,nlabels=ndimage.label(~coarse)
 sizes=np.bincount(labels.ravel());sizes[0]=0
 if len(sizes)<2:raise RuntimeError('no coarse free region')
 main=int(sizes.argmax());ch,cw=coarse.shape
 moves=[(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
 def escape(point,wanted=None):
  sx,sy=(round(z/G) for z in point);origin=(sx,sy);prev={origin:None};queue=deque([origin]);found=None
  while queue:
   x,y=queue.popleft()
   if x%stride==0 and y%stride==0 and labels[y//stride,x//stride] and (wanted is None or labels[y//stride,x//stride]==wanted):found=(x,y);break
   if len(prev)>120000:raise RuntimeError('bounded fine escape')
   for dx,dy in moves:
    xx=x+dx;yy=y+dy;z=(xx,yy)
    if z in prev or xx<1 or yy<1 or xx>=width-1 or yy>=height-1 or arr[yy,xx]:continue
    if dx and dy and (arr[y,xx] or arr[yy,x]):continue
    prev[z]=(x,y);queue.append(z)
  if found is None:raise RuntimeError('no fine escape to main region')
  pts=[found]
  while prev[pts[-1]] is not None:pts.append(prev[pts[-1]])
  pts.reverse();out=[(x*G,y*G) for x,y in pts];out[0]=tuple(point);return found,out
 aa,prefix=escape(start);bb,suffix=escape(end)
 la=int(labels[aa[1]//stride,aa[0]//stride]);lb=int(labels[bb[1]//stride,bb[0]//stride])
 if la!=lb:
  try:
   if sizes[la]>=sizes[lb]:bb,suffix=escape(end,la)
   else:aa,prefix=escape(start,lb)
  except RuntimeError:aa,prefix=escape(start,main);bb,suffix=escape(end,main)
 s=(aa[0]//stride,aa[1]//stride);target=(bb[0]//stride,bb[1]//stride)
 def heuristic(q):
  dx=abs(q[0]-target[0]);dy=abs(q[1]-target[1]);return max(dx,dy)+.41421356237*min(dx,dy)
 heap=[(heuristic(s),0,s)];best={s:0};prev={};seen=set()
 while heap:
  _,cost,cur=heapq.heappop(heap)
  if cur in seen:continue
  if cur==target:break
  seen.add(cur)
  if len(seen)>180000:raise RuntimeError('bounded coarse route')
  x,y=cur
  for dx,dy in moves:
   xx=x+dx;yy=y+dy;z=(xx,yy)
   if xx<1 or yy<1 or xx>=cw-1 or yy>=ch-1 or coarse[yy,xx]:continue
   if dx and dy and (coarse[y,xx] or coarse[yy,x]):continue
   nc=cost+math.hypot(dx,dy)
   if nc<best.get(z,1e99):best[z]=nc;prev[z]=cur;heapq.heappush(heap,(nc+3*heuristic(z),nc,z))
 else:raise RuntimeError('no coarse path')
 mid=[target]
 while mid[-1]!=s:mid.append(prev[mid[-1]])
 mid=[(x*stride*G,y*stride*G) for x,y in mid[::-1]]
 pts=prefix+mid[1:]+suffix[-2::-1];simple=[]
 for pt in pts:
  if simple and math.dist(simple[-1],pt)<1e-8:continue
  while len(simple)>1 and abs(ns['orient'](simple[-2],simple[-1],pt))<1e-9:simple.pop()
  simple.append(pt)
 if not all(fast_clear(x,z,obs,rad-.000001) for x,z in zip(simple,simple[1:])):raise RuntimeError('hierarchy exact geometry failed')
 # Greedy visibility shortcuts only after exact conservative path construction.
 out=[simple[0]];i=0
 while i<len(simple)-1:
  found=i+1
  for j in range(len(simple)-1,i+1,-1):
   if fast_clear(simple[i],simple[j],obs,rad):found=j;break
  out.append(simple[found]);i=found
 return out
ns['route']=hierarchy
