import json,re,math,collections,csv,itertools,argparse
from pathlib import Path
from shapely import Polygon,LineString,Point,box,unary_union,make_valid,STRtree
ap=argparse.ArgumentParser(description='Read-only projected geometry analysis; no routing or SI signoff.');ap.add_argument('--geometry',required=True,type=Path);ap.add_argument('--outdir',required=True,type=Path);args=ap.parse_args();D=args.outdir;D.mkdir(parents=True,exist_ok=True);d=json.loads(args.geometry.read_text());layers=['F.Cu']+[f'In{i}.Cu' for i in range(1,31)]+['B.Cu'];area=96*45
norm=lambda n:n.replace('{slash}','').lstrip('/')
def cls(n):
 n=norm(n)
 if n=='GND':return 'ground'
 if n=='CPU_VDD2_PWRGOOD_LOOP':return 'low_speed_control'
 if re.search(r'REFCLK|CLKBUF[12]_IN|XTAL|REF_KA_(?:X[12]|DIF0[PN])',n):return 'clock'
 if re.match(r'S\d+_(?:SW|SSD)_[RT]X\d|CPU_(?:G5|PEX)_[RT]X\d|TBT_(?:CPU|AR)_TX\d',n):return 'PCIe'
 if re.match(r'TBT_(?:DP_(?:ML|AUX)|PA_AUX)',n):return 'DP'
 if re.match(r'TBT_(?:CIO_[RT]X|USB2_(?:BOTTOM|RP|TOP))',n):return 'USB_TBT'
 if re.match(r'P12_SLOT|P3V3|VBANK|VIN_[AB]$|PEX_[01]V[89]A?$|AUX_12V|TBT_(?:5V0|VBUS)$|CPU_(?:VCCPRIM|VCCRTC|VCCIN|VCCCORE|VDD)|TBT_PD_(?:LDO|VOUT)|REF_KA_VDD',n) or n in ['BUCK_SW','PEX09_SW','TBT_5V_SW','PEX18_VCC']:return 'power'
 if 'unconnected-' in n:return 'NC'
 return 'low_speed_control'
tracks=collections.defaultdict(list);summ={};netcls={}
for t in d['tracks']:
 t['class']=cls(t['net']);netcls[norm(t['net'])]=t['class'];tracks[t['layer']].append(t)
zs=collections.defaultdict(list);zone_summ=[]
for z in d['zones']:
 p=unary_union([make_valid(Polygon(x['shell'],x['holes'])) for x in z['polygons']]);zs[z['layer']].append((norm(z['net']),p));parts=list(p.geoms) if hasattr(p,'geoms') else [p]
 zone_summ.append({'layer':z['layer'],'net':norm(z['net']),'filled_area_mm2':p.area,'board_fraction':p.area/area,'outlines':len(z['polygons']),'geometric_components':len(parts),'largest_component_mm2':max([x.area for x in parts],default=0),'bounds':list(p.bounds)})
G={k:unary_union([p for n,p in zs[k] if n=='GND']) for k in layers};A={k:unary_union([p for n,p in zs[k]]) for k in layers}
for li,k in enumerate(layers):
 ts=tracks[k]; byclass=collections.defaultdict(lambda:{'segments':0,'length_mm':0,'nets':set()});directions=collections.Counter();region=collections.Counter();tile_lengths=collections.Counter();xys=[]
 for t in ts:
  c=byclass[t['class']];c['segments']+=1;c['length_mm']+=t['length'];c['nets'].add(norm(t['net']));a,b=t['start'],t['end'];xys.extend([a,b]);dx=abs(b[0]-a[0]);dy=abs(b[1]-a[1]);directions['horizontal' if dy<1e-5 else 'vertical' if dx<1e-5 else 'diagonal']+=t['length']
  nn=max(1,math.ceil(t['length']/.25))
  for j in range(nn):
   f=(j+.5)/nn;x=a[0]+f*(b[0]-a[0]);y=a[1]+f*(b[1]-a[1]);dl=t['length']/nn;region['switch_x0_37' if x<37 else 'cpu_x37_69' if x<69 else 'usb_pd_x69_96']+=dl;tile_lengths[(int(x//2),int(y//2))]+=dl
  t['_line']=LineString([a,b])
 length=sum(t['length'] for t in ts);adj=[layers[j] for j in [li-1,li+1] if 0<=j<len(layers)];ag=unary_union([G[j] for j in adj]);aa=unary_union([A[j] for j in adj]);hs=[t for t in ts if t['class'] in ['PCIe','DP','USB_TBT','clock']];hsl=sum(t['length'] for t in hs)
 ground_covered=sum(t['_line'].intersection(ag).length for t in hs);any_covered=sum(t['_line'].intersection(aa).length for t in hs)
 for c in byclass.values():c['nets']=sorted(c['nets'])
 summ[k]={'segments':len(ts),'length_mm':length,'class':dict(byclass),'direction_length_mm':dict(directions),'region_length_mm':dict(region),'route_bbox':([min(p[0] for p in xys),min(p[1] for p in xys),max(p[0] for p in xys),max(p[1] for p in xys)] if xys else None),'summed_trace_copper_area_mm2':sum(t['length']*t['width'] for t in ts),'summed_trace_pitch_area_at_0p1_gap_mm2':sum(t['length']*(t['width']+.1) for t in ts),'nonempty_2mm_tiles':len(tile_lengths),'peak_tile_length_mm':max(tile_lengths.values(),default=0),'adjacent_layers':adj,'HS_clock_length_mm':hsl,'HS_clock_adjacent_GND_projected_mm':ground_covered,'HS_clock_adjacent_any_zone_projected_mm':any_covered,'HS_clock_adjacent_GND_coverage_fraction':ground_covered/hsl if hsl else None,'HS_clock_adjacent_any_zone_coverage_fraction':any_covered/hsl if hsl else None}
 print(k,'len',round(length,1),'classes',[(c,round(v['length_mm'])) for c,v in byclass.items()],'gndref%',round(100*ground_covered/hsl,1) if hsl else '-')
# Non-equivalent same-plane overlays: count track-track short/clearance collisions only, ignoring pads, vias, all zones.
overlays=[];rl=[k for k in layers if tracks[k]]
for ka,kb in itertools.combinations(rl,2):
 ta,tb=tracks[ka],tracks[kb];tree=STRtree([t['_line'] for t in tb]);pairs=0;min_d=None;collision_nets=set();maxwb=max(t['width'] for t in tb)
 for a in ta:
  for j in tree.query(a['_line'].buffer(a['width']/2+maxwb/2+.1)):
   b=tb[j]
   if a['net']==b['net']:continue
   dd=a['_line'].distance(b['_line'])-(a['width']+b['width'])/2
   if dd<.1-1e-6:pairs+=1;collision_nets.add((norm(a['net']),norm(b['net'])));min_d=dd if min_d is None else min(dd,min_d)
 overlays.append({'layers':[ka,kb],'track_pair_conflicts_at_0p1_gap':pairs,'net_pair_conflicts':len(collision_nets),'min_edge_clearance_mm':min_d})
# Differential segment-nets audit: pair matching by terminal _P/_N; routed layer mismatch excludes F/B escape.
nets=collections.defaultdict(list)
for t in d['tracks']:nets[norm(t['net'])].append(t)
pairs=[]
for n,ts in nets.items():
 if not n.endswith('_P') or cls(n) not in ['PCIe','DP','USB_TBT','clock']:continue
 nn=n[:-2]+'_N'
 if nn not in nets:continue
 pn=[n,nn];ls=[sorted({t['layer'] for t in nets[x] if t['layer'] not in ['F.Cu','B.Cu']},key=layers.index) for x in pn];lens=[sum(t['length'] for t in nets[x]) for x in pn]
 pairs.append({'pair':n[:-2],'class':cls(n),'P_internal_layers':ls[0],'N_internal_layers':ls[1],'same_internal_layer_set':ls[0]==ls[1],'P_length_mm':lens[0],'N_length_mm':lens[1],'absolute_length_difference_mm':abs(lens[0]-lens[1])})
result={'source_sha256':d['sha256'],'source_native_version':d['version'],'method':'KiCad native extraction; saved filled polygon geometry; planar projection only, not electrical return-path or SI signoff. Track-overlay screening excludes pads, vias, zones and is not a routability proof. 2mm tile occupancy estimated with <=0.25mm samples. Class names are net-name/manual topology categorization, not netlist electrical validation.','layers':summ,'zones':zone_summ,'net_classes':netcls,'track_only_overlay_screen':overlays,'diff_pair_section_audit':pairs}
(D/'LAYER_ARCHITECTURE_AUDIT.json').write_text(json.dumps(result,indent=2))
with (D/'LAYER_SUMMARY.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['layer','segments','length_mm','PCIe_mm','USB_TBT_mm','DP_mm','clock_mm','low_speed_mm','power_mm','GND_mm','horizontal_mm','vertical_mm','diagonal_mm','active_2mm_tiles','peak_tile_mm','HS_GND_projection_fraction','HS_any_zone_projection_fraction'])
 for k,s in summ.items():w.writerow([k,s['segments'],s['length_mm']]+[s['class'].get(c,{}).get('length_mm',0) for c in ['PCIe','USB_TBT','DP','clock','low_speed_control','power','ground']]+[s['direction_length_mm'].get(c,0) for c in ['horizontal','vertical','diagonal']]+[s['nonempty_2mm_tiles'],s['peak_tile_length_mm'],s['HS_clock_adjacent_GND_coverage_fraction'],s['HS_clock_adjacent_any_zone_coverage_fraction']])
print('total',sum(x['length_mm'] for x in summ.values()),'pair sections',len(pairs),'mismatch',sum(not p['same_internal_layer_set'] for p in pairs));print('best overlays',sorted(overlays,key=lambda x:x['track_pair_conflicts_at_0p1_gap'])[:20])
