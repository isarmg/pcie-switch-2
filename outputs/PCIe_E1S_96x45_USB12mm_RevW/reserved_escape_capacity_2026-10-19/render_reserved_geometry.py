"""Review picture from exact trial output; drawing is not a geometry checker."""
from pathlib import Path
import json
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Rectangle
D=Path(__file__).parent;d=json.loads((D/'NATIVE_GEOMETRY.json').read_text());pre=json.loads((D/'ENDPOINT_PREFLIGHT.json').read_text());ss=[(p,json.loads(p.read_text())) for p in sorted(D.glob('RESERVED_SCENARIO_*.json'))];p,s=max(ss,key=lambda q:q[1]['successfully_routed_channels']);sel=pre['selected_combinations'][s['combination_index']]['selected'];colors={'S06_SW_RX0':'#168b65','S06_SW_RX1':'#e58918','S06_SW_TX0':'#2382cf','S06_SW_TX1':'#9345bd'}
fig=plt.figure(figsize=(15,9));gs=fig.add_gridspec(2,2,width_ratios=[1.7,1]);axes=[fig.add_subplot(gs[:,0]),fig.add_subplot(gs[0,1]),fig.add_subplot(gs[1,1])]
for ax in axes:
 ax.set_facecolor('#fafafa')
 for v in d['vias']:ax.add_patch(Circle(v['xy'],v['diameter']/2,color='#555555',alpha=.45,lw=0))
 for r in s['attempts']:
  if not r['geometry_pass']:continue
  for j,t in enumerate(r['traces']):
   x,y=zip(*t['points']);ax.plot(x,y,color=colors[r['pair']],linewidth=1.0 if ax==axes[0] else 1.5,label=r['pair'].replace('S06_SW_','') if j==0 else None)
  x,y=zip(*(t['points'][0] for t in r['traces']));ax.scatter(x,y,s=18,color=colors[r['pair']])
 for pair,port in sel.items():
  for t in port['fragments']:
   x,y=zip(*t['points']);ax.plot(x,y,color=colors[pair],linewidth=1.0,linestyle='--',alpha=.7)
  x,y=port['end'];ax.scatter([x],[y],marker='s',s=22,facecolors='none',edgecolors=colors[pair])
 for r in s['attempts']:
  if not r['geometry_pass']:
   x,y=sel[r['pair']]['end'];ax.scatter([x],[y],s=70,marker='x',color='#c92338');ax.annotate(r['pair'].replace('S06_SW_','')+' unfinished',(x,y),xytext=(x-6,y-1),fontsize=9,color='#ad1830',arrowprops={'arrowstyle':'->','color':'#ad1830'})
 ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_xlabel('x / mm');ax.set_ylabel('y / mm')
axes[0].set_xlim(0,96);axes[0].set_ylim(45,0);axes[0].set_title('Best bounded prefix: RX0 + RX1 + TX1; TX0 still unrouted');axes[0].legend(loc='upper right',fontsize=9)
axes[1].set_xlim(55.8,65.0);axes[1].set_ylim(26.2,21.1);axes[1].set_title('Destination fanouts: selected alternatives reserved')
axes[2].set_xlim(5.7,10.5);axes[2].set_ylim(36,31.3);axes[2].set_title('Actual U1 pins and fixed source fanouts')
fig.suptitle('S06 same-plane x2: hard endpoint reservations remove the earlier entrance conflict',fontsize=14)
fig.text(.04,.025,'0.10 mm width / pair gap / other-net gap; 0.05 mm grid; all 3,837 source vias projected. Dashed = reserved fanout.\n12 bounded scenarios: best 3/4 directional channels, NOT complete x2; no native PCB DRC, SI, GND reference or manufacturing signoff.',fontsize=10)
fig.subplots_adjust(top=.91,bottom=.12,wspace=.22,hspace=.35);fig.savefig(D/'RESERVED_GEOMETRY.png',dpi=150);print('Saved',D/'RESERVED_GEOMETRY.png')
