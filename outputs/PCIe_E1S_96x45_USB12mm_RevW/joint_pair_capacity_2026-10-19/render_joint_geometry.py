from pathlib import Path
import os,json
D=Path(__file__).parent;os.environ.setdefault('MPLCONFIGDIR',str(D/'mplconfig'))
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Rectangle
from matplotlib.collections import PatchCollection
s=json.loads((D/'NATIVE_GEOMETRY.json').read_text());e=json.loads((D/'extra_geometry.json').read_text());v=json.loads((D/'JOINT_VALIDATION_SUMMARY.json').read_text());x1=json.loads((D/'SCENARIO_01.json').read_text());best=json.loads((D/v['x2_best_candidate']['scenario_file']).read_text())
fig,axes=plt.subplots(2,1,figsize=(16,15),constrained_layout=True);palette={'S06_SW_RX0':'#126b55','S06_SW_TX0':'#164fbe','S06_SW_RX1':'#be6b12','S06_SW_TX1':'#992e74'}
for ax,routes,title in [(axes[0],[x1['first'],x1['second']],'Complete x1: RX0 first, then jointly rerouted TX0 | minimum channel-to-channel copper gap 0.3234 mm'),(axes[1],best['attempts'],'Bounded x2 attempt: best accepted prefix '+str(best['successfully_routed_channels'])+'/4 channels | not a complete x2 solution')]:
 ax.add_patch(Rectangle((0,0),96,45,fill=False,edgecolor='black',lw=1))
 ax.add_collection(PatchCollection([Rectangle((p['bbox'][0],p['bbox'][1]),p['bbox'][2]-p['bbox'][0],p['bbox'][3]-p['bbox'][1]) for p in e['pads']],facecolor='#dddeda',edgecolor='none',alpha=.65))
 ax.add_collection(PatchCollection([Circle(x['xy'],x['diameter']/2) for x in s['vias']],facecolor='#8c8f93',edgecolor='none',alpha=.55))
 for r in routes:
  if r['geometry_pass']:
   for i,t in enumerate(r['traces']):
    pts=t['points'];ax.plot([p[0] for p in pts],[p[1] for p in pts],color=palette[r['pair']],lw=1.25,ls='-' if i==0 else '--',label=r['pair'].replace('S06_SW_','')+(' P' if i==0 else ' N'))
  else:
   for hit in r.get('search',{}).get('endpoint_obstacles',[]):
    p=hit['grid_xy_mm'];ax.plot(*p,'rx',ms=9,mew=2);ax.annotate(r['pair'].replace('S06_SW_','')+' blocked trial entry',p,xytext=(p[0]+3,p[1]-3),arrowprops={'arrowstyle':'->','color':'#a00'},color='#a00',fontsize=9)
 ax.set_xlim(0,96);ax.set_ylim(45,0);ax.set_aspect('equal');ax.grid(alpha=.1);ax.set_xlabel('x (mm)');ax.set_ylabel('y (mm)');ax.set_title(title,loc='left',fontsize=13);ax.legend(loc='lower right',ncol=2,fontsize=9)
fig.suptitle('Same-plane paired routing on proposed L7 | 96 x 45 mm | all 3,837 source vias preserved\n0.10 mm width / pair gap / other-net clearance assumptions. Existing other internal copper omitted.\nNo 24-layer implementation, full-board native DRC, continuous-reference, SI or fabrication approval.',fontsize=13)
fig.savefig(D/'JOINT_GEOMETRY.png',dpi=170);print('Saved JOINT_GEOMETRY.png')
