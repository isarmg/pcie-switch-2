"""Review drawing from measured source geometry and exact candidate polylines."""
from pathlib import Path
import json,os
D=Path(__file__).parent;os.environ.setdefault('MPLCONFIGDIR',str(D/'mplconfig'))
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
from matplotlib.collections import PatchCollection
from matplotlib.gridspec import GridSpec
s=json.loads((D/'NATIVE_GEOMETRY.json').read_text());e=json.loads((D/'extra_geometry.json').read_text());t=json.loads((D/'TRIAL_RESULT.json').read_text());r=json.loads((D/'RX0_SEPARATE_RESULT.json').read_text());v=json.loads((D/'VALIDATION_SUMMARY.json').read_text())
fig=plt.figure(figsize=(16,14),constrained_layout=True);gs=GridSpec(3,3,figure=fig,height_ratios=[3,3,2]);axes=[fig.add_subplot(gs[0,:]),fig.add_subplot(gs[1,:])];zaxes=[fig.add_subplot(gs[2,k]) for k in range(3)]
colors=['#bd2634','#145dc0']
def base(ax,lims=(0,96,0,45),zoom=False):
 ax.add_patch(Rectangle((0,0),96,45,fill=False,edgecolor='black',lw=1.2))
 pads=[Rectangle((p['bbox'][0],p['bbox'][1]),p['bbox'][2]-p['bbox'][0],p['bbox'][3]-p['bbox'][1]) for p in e['pads']]
 ax.add_collection(PatchCollection(pads,facecolor='#dddeda',edgecolor='none',alpha=.7))
 ax.add_collection(PatchCollection([Circle(x['xy'],x['diameter']/2) for x in s['vias']],facecolor='#888b8e',edgecolor='none',alpha=.55))
 ax.set_xlim(lims[:2]);ax.set_ylim(lims[3],lims[2]);ax.set_aspect('equal');ax.set_xlabel('x (mm)');ax.set_ylabel('y (mm)');ax.grid(alpha=.12)
 if not zoom:
  for f in s['fps']:
   if f['ref'] in ['J'+str(i) for i in range(1,13)]:ax.text(f['xy'][0],44,f['ref'],fontsize=8,ha='center')
def traces(ax,obj,zoom=False):
 for k,tr in enumerate(obj['traces']):
  xy=tr['points'];ax.plot([p[0] for p in xy],[p[1] for p in xy],c=colors[k],lw=1.1 if not zoom else 2.2,label='P' if k==0 else 'N')
  for p in [xy[0],xy[-1]]:ax.plot(*p,'o',color=colors[k],ms=2 if not zoom else 4)
base(axes[0]);traces(axes[0],t);axes[0].set_title('TX0: new coupled geometry on proposed L7 (adjacent GND L8 required). Long P/N = 74.532 / 74.679 mm',loc='left',fontsize=12);axes[0].legend(loc='lower right')
base(axes[1]);traces(axes[1],r);axes[1].set_title('RX0: separate proposed L18 (adjacent GND L17 required). Long P/N = 62.184 / 62.056 mm',loc='left',fontsize=12)
for ax,lim,title,obj in [(zaxes[0],(5.6,8.2,33.4,35.6),'TX0: U1 AH3 / AJ3 fanout',t),(zaxes[1],(61.9,65.15,23.7,25.5),'TX0: real C4041 / C4042 + J6',t),(zaxes[2],(56.4,58.5,23.7,25.5),'RX0: J6 A18 / A17 fanout',r)]:
 base(ax,lim,True);traces(ax,obj,True);ax.set_title(title,fontsize=10)
for k,ac in enumerate(v['AC_after_checks']):
 p=ac['points'];zaxes[1].plot([z[0] for z in p],[z[1] for z in p],c=colors[k],lw=2.2,ls='--')
zaxes[1].text(62.25,25.32,'Dashed: retained F.Cu AC-output traces',fontsize=7)
fig.suptitle('S06 lane 0 geometry prototype | 96 x 45 mm board | all 3,837 source vias preserved as projected obstacles\nOne x1 lane = TX + RX; AC sections are not extra lanes. Other internal copper is not modeled. No 24-layer PCB / SI / fabrication signoff.',fontsize=13)
fig.savefig(D/'PAIRED_GEOMETRY.png',dpi=180);fig.savefig(D/'PAIRED_GEOMETRY.svg');print('wrote review figure')
