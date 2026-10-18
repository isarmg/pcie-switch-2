from i_common import *
import random,csv
ROOT.mkdir(exist_ok=True)
M2P=json.loads((R/'scripts/m2_pins.json').read_text())
MURL='https://klsele.com/products/connectors/Card-connectors/M-2-NGFF-connectors/10763.html'
EURL='https://www.ti.com/lit/ds/symlink/tps25947.pdf'
def library(a):
    for lib,n in [('Resistor_SMD','R_0402_1005Metric'),('Capacitor_SMD','C_0402_1005Metric'),('Capacitor_SMD','C_0603_1608Metric'),('Capacitor_SMD','C_0805_2012Metric'),('Capacitor_SMD','C_1210_3225Metric'),('Package_TO_SOT_SMD','SOT-23-6'),('Inductor_SMD','L_Coilcraft_XAL5030-XXX')]:a.std(lib,n)
    if not (a.lib/'TI_RPW0010A_TPS25947.kicad_mod').exists():shutil.copy2(BASE/'E1S.pretty/TI_RPW0010A_TPS25947.kicad_mod',a.lib/'TI_RPW0010A_TPS25947.kicad_mod');shutil.copy2(BASE/'models/TI_RPW0010A_TPS25947.step',a.models/'TI_RPW0010A_TPS25947.step')
    a.custom('Twinax_85R_Solder_DRAFT', [('P',-.45,0,.4,.5),('N',.45,0,.4,.5),('G',0,-.7,1.7,.35),('G',0,.7,1.7,.35)],1.7,1.75)
    # Preliminary vertical M-key land geometry. Must be replaced by supplier drawing before fabrication.
    a.custom('M2_MKey_VERTICAL_5p3_DRAFT',[(str(n),-9.25+(n-1)*.25,-2.7 if n%2 else 2.7,.3,1.2) for n in range(1,76) if n not in range(59,67)]+[('MP1',-10.7,0,1.5,3.5),('MP2',10.7,0,1.5,3.5)],23,4.4,5.3)
    a.custom('Wire_12V_GND_3A',[('1',-1.5,0,2,2.5),('2',1.5,0,2,2.5)],5,2.5)
    a.custom('Control_8_Wire',[ (str(i+1),(i-3.5)*.9,0,.5,1.2) for i in range(8)],7.5,1.2)
def efuse(a,ref,x,y,vin,vout,limitR='1.10k',side='B',prefix='/EXT_'):
    num=int(ref[1:]);pr=prefix+str(num)+'_';pm={'1':pr+'UV','2':pr+'OV','3':nc(ref,3),'4':nc(ref,4),'5':vin,'6':vout,'7':pr+'DVDT','8':'/GND','9':pr+'ILM','10':nc(ref,10)}
    a.place(ref,'TPS259470ARPWR','TI_RPW0010A_TPS25947',x,y,pm,side,height=1,url=EURL)
    for j,val,dx,dy,nn1,nn2,rot in [(1,'76.1k',-2.5,-2.2,vin,pr+'UV',0),(2,'10k',-2.5,0,pr+'UV','/GND',90),(3,'102k',2.5,-2.2,vin,pr+'OV',0),(4,'10k',2.5,0,pr+'OV','/GND',90),(5,limitR,2.5,2.2,pr+'ILM','/GND',90)]:a.place(f'R{num*10+j}',val,'R_0402_1005Metric',x+dx,y+dy,{'1':nn1,'2':nn2},side,rot,.4)
    a.place(f'C{num*10+1}','10nF','C_0402_1005Metric',x,y+2.6,{'1':pr+'DVDT','2':'/GND'},side,height=.55)
    a.place(f'C{num*10+2}','100nF 50V','C_0603_1608Metric',x,y-2.6,{'1':vin,'2':'/GND'},side,height=.9)
def buck(a,k,x,y):
    pre=f'/M{k}_';out=f'/M{k}_3V3';u=f'U{20+k}';pm={'1':'/GND','2':pre+'SW','3':'/CABLE12','4':pre+'FB','5':'/CABLE12','6':pre+'BST'}
    a.place(u,'TPS565201DDCR','SOT-23-6',x,y,pm,'B',height=1.1,url='https://www.ti.com/lit/ds/symlink/tps565201.pdf',names={'1':'GND','2':'SW','3':'VIN','4':'VFB','5':'EN','6':'VBST'})
    a.place(f'L{k}','2.2uH XAL5030-222MEC','L_Coilcraft_XAL5030-XXX',x-6,y,{'1':pre+'SW','2':out},'B',height=3.1,url='https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xal/xal50xx/xal5030-222/')
    for j,val,foot,dx,dy,n1,n2,ang,h in [(1,'10uF 25V X7R','C_0805_2012Metric',0,4,'/CABLE12','/GND',0,1.45),(2,'100nF 50V','C_0402_1005Metric',-1,2.2,'/CABLE12','/GND',90,.55),(3,'100nF 25V','C_0402_1005Metric',-.2,-2.6,pre+'BST',pre+'SW',0,.55),(4,'22uF 16V X7R','C_1210_3225Metric',-6,-5,out,'/GND',0,2.8),(5,'22uF 16V X7R','C_1210_3225Metric',-6,5,out,'/GND',0,2.8)]:a.place(f'C{k*100+j}',val,foot,x+dx,y+dy,{'1':n1,'2':n2},'B',ang,h)
    a.place(f'R{k*100+1}','33.2k','R_0402_1005Metric',x+3,y+2,{'1':out,'2':pre+'FB'},'B',height=.4)
    a.place(f'R{k*100+2}','10k','R_0402_1005Metric',x+3,y,{'1':pre+'FB','2':'/GND'},'B',90,.4)
    # Local slot decoupling in addition to converter output capacitors.
    a.place(f'C{k*100+6}','1uF 16V','C_0603_1608Metric',x-5,y-10,{'1':out,'2':'/GND'},'B',height=.9)
def m2(a,k,x,y):
    ref=f'J{k}';pm={};pre=f'/M{k}_'
    for n,name in M2P.items():
        if name.startswith('GND'):nn='/GND'
        elif '3.3V' in name:nn=pre+'3V3'
        elif name.startswith(('PET','PER')):
            d='TX' if name.startswith('PET') else 'RX';lane=re.search(r'(\d)',name)[1];pol='P' if name[3]=='p' else 'N';nn=pre+f'{d}{lane}_{pol}'+('_AC' if d=='TX' else '')
        elif name.startswith('REFCLK'):nn=pre+'CLK_'+('P' if name.endswith('p') else 'N')
        elif n=='50':nn=pre+'PERST'
        elif n=='52':nn=pre+'CLKREQ'
        elif n=='54':nn=pre+'WAKE'
        elif n=='69':nn='/GND'
        else:nn=nc(ref,n)
        pm[n]=nn
    pm.update(MP1='/GND',MP2='/GND')
    f=a.place(ref,'M-Key 2280 VERTICAL / LAND DRAFT','M2_MKey_VERTICAL_5p3_DRAFT',x,y,pm,height=5.3,url=MURL,names=M2P)
    for lane in range(4):
        for pol,j in [('P',0),('N',1)]:
            ix=lane*2+j;a.place(f'C{k*100+20+ix}','220nF 16V AC','C_0402_1005Metric',x-8+ix*2.2,y-6,{'1':pre+f'TX{lane}_{pol}','2':pre+f'TX{lane}_{pol}_AC'},height=.55,angle=90)
    for i,n in enumerate(['CLKREQ','WAKE']):a.place(f'R{k*100+10+i}','10k','R_0402_1005Metric',x+4+i*3,y+6,{'1':pre+'3V3','2':pre+n},height=.4)
    a.text(f'M{k} / 2280 VERTICAL',x,y+8,size=.6);return f

# Each lane uses two twinax pairs. Port naming is from the switch perspective.
ports=[('L','M1',False),('L','M2',False),('R','M3',False),('R','UP',True)]
pairmap=[]
for side in ['L','R']:
    idx=0
    for _,port,up in [q for q in ports if q[0]==side]:
        for lane in range(4):
            for d in ['TX','RX']:
                pairmap.append(dict(side=side,index=idx,port=port,function=f'{d}{lane}',netP=f'/{port}_{d}{lane}_P',netN=f'/{port}_{d}{lane}_N',direction='switch to remote' if d=='TX' else 'remote to switch'));idx+=1
        pairmap.append(dict(side=side,index=idx,port=port,function='CLK',netP=f'/{port}_CLK_P',netN=f'/{port}_CLK_N',direction='host to switch' if up else 'switch to SSD'));idx+=1

main=Board('Main_10E1S',80,45,32,True);library(main)
for t in main.b.GetTracks():
    if isinstance(t,p.PCB_VIA) and t.GetViaType()==p.VIATYPE_THROUGH and (t.GetNetname().startswith('/VBANK_') or t.GetNetname().startswith('/P12_SLOT') or t.GetNetname()=='/P3V3_AUX'):
        t.SetViaType(p.VIATYPE_BLIND);t.SetLayerPair(p.F_Cu,p.In18_Cu)
for f in list(main.b.GetFootprints()):
    if re.fullmatch(r'H[1-4]',f.GetReference()):remove(main.b,f)
for d in list(main.b.GetDrawings()):
    if isinstance(d,p.PCB_TEXT) and 'REV H' in d.GetText():d.SetText('REV I / 56 LANES / DRAFT')
main.text('L: 2x M.2 x4',8,44,p.B_SilkS,.55);main.text('R: M.2 + UP x4',71,44,p.B_SilkS,.55)
for row in pairmap:
    side=row['side'];i=row['index'];x=1.25 if side=='L' else 78.75;y=2+2.3*i;ref=f'J{101+i if side=="L" else 201+i}'
    row['main_ref']=ref;main.place(ref,f'{row["port"]} {row["function"]}','Twinax_85R_Solder_DRAFT',x,y,{'P':row['netP'],'N':row['netN'],'G':'/GND'},'B')
for side,x,vin,ref in [('L',7,'/VIN_A','U41'),('R',73,'/VIN_B','U42')]:
    efuse(main,ref,x,4.3,vin,f'/CABLE12_{side}')
    main.place('J301' if side=='L' else 'J302','12V protected / GND','Wire_12V_GND_3A',5.5 if side=='L' else 74.5,10,{'1':f'/CABLE12_{side}','2':'/GND'},'B')
    ps=[q[1] for q in ports if q[0]==side];nets=[f'/{po}_{sig}' for po in ps for sig in ['PERST','CLKREQ','WAKE']]+['/GND','/GND']
    main.place('J303' if side=='L' else 'J304',f'{side} control / custom','Control_8_Wire',x,42,{str(j+1):nn for j,nn in enumerate(nets)},'B')
# Preserve the original 256 sparse balls and their routing. Add 144 interior balls.
bg=main.b.FindFootprintByReference('U1');bg.SetValue('FICTIONAL_BGA400_56lane');bg.SetFPID(p.LIB_ID('Local','FICTIONAL_BGA400_56lane'))
rows='A B C D E F G H J K L M N P R T U V W Y AA AB AC AD AE AF AG AH AJ AK AL AM'.split();spots=[]
for iy in range(10,22):
    for ix in range(10,22):spots.append((rows[iy]+str(ix+1),24.5+ix,7+iy))
random.Random(20260929).shuffle(spots)
signals=[nn for q in pairmap for nn in [q['netP'],q['netN']]]+[f'/{po}_{s}' for _,po,_ in ports for s in ['PERST','CLKREQ','WAKE']]
for i,(n,x,y) in enumerate(spots):
    q=p.PAD(bg);q.SetNumber(n);q.SetPosition(v(x,y));q.SetSize(v(.45,.45));q.SetShape(p.PAD_SHAPE_CIRCLE);q.SetAttribute(p.PAD_ATTRIB_SMD);q.SetLayerSet(layers(p.B_Cu,p.B_Mask,p.B_Paste));q.SetNet(main.net(signals[i] if i<len(signals) else nc('U1',n)));bg.Add(q)
main.text('FICTIONAL BGA400 / NOT A REAL SWITCH PINOUT',40,42,p.B_SilkS,.55)
# New signal layers are below all existing Rev H signal layers; reserve In20/22/24/26/28/30 as ground references.
for i in [20,22,24,26,28,30]:main.zone('/GND',getattr(p,f'In{i}_Cu'),[(.4,.4),(79.6,.4),(79.6,44.6),(.4,44.6)])
main.save()

left=Board('Left_2M2_Vertical',52,45,12);right=Board('Right_M2_Upstream',44,45,12)
for a,side in [(left,'L'),(right,'R')]:
    library(a)
    for row in [q for q in pairmap if q['side']==side]:
        i=row['index'];ref=f'J{101+i}';row['daughter_ref']=ref
        a.place(ref,f'{row["port"]} {row["function"]}','Twinax_85R_Solder_DRAFT',a.w-1.4 if side=='L' else 1.4,2+2.3*i,{'P':row['netP'],'N':row['netN'],'G':'/GND'},'B')
    a.place('J50','12V protected / GND','Wire_12V_GND_3A',43 if side=='L' else 8,4,{'1':'/CABLE12','2':'/GND'},'B')
    ps=[q[1] for q in ports if q[0]==side];nets=[f'/{po}_{sig}' for po in ps for sig in ['PERST','CLKREQ','WAKE']]+['/GND','/GND']
    a.place('J51','Control / custom','Control_8_Wire',31 if side=='L' else 20,4,{str(j+1):nn for j,nn in enumerate(nets)},'B')
    for i in [1,3,5,7,9]:a.zone('/GND',getattr(p,f'In{i}_Cu'),[(.4,.4),(a.w-.4,.4),(a.w-.4,44.6),(.4,44.6)])
    a.text('VERTICAL M-KEY / LAYOUT DRAFT',a.w/2,1.1,size=.65)
    a.text('12V IN / 3.3V SSD / 8 LANES',a.w/2,43.5,p.B_SilkS,.65)
for k,x in [(1,14),(2,38)]:m2(left,k,x,17);buck(left,k,x+2,32)
m2(right,3,26,13);buck(right,3,31,27)
# PCIe x4 upstream edge, exact standard-library finger geometry and keyed outline.
edge=right.std('Connector_PCBEdge','BUS_PCIexpress_x4')
pm={f'{r}{n}':nc('J4',f'{r}{n}') for r in 'AB' for n in range(1,33)}
for n in [4,12,15,18,20,23,24,27,28,31]:pm['A'+str(n)]='/GND'
for n in [4,7,13,16,18,21,22,25,26,29,32]:pm['B'+str(n)]='/GND'
for lane,nums in enumerate([(16,17,14,15),(21,22,19,20),(25,26,23,24),(29,30,27,28)]):
    # Add-in card A=host receiver (switch TX), B=host transmitter (switch RX).
    ap,an,bp,bn=nums;pm['A'+str(ap)]=f'/UP_TX{lane}_P_AC';pm['A'+str(an)]=f'/UP_TX{lane}_N_AC';pm['B'+str(bp)]=f'/UP_RX{lane}_P';pm['B'+str(bn)]=f'/UP_RX{lane}_N'
pm.update(A11='/UP_PERST',A13='/UP_CLK_P',A14='/UP_CLK_N',B11='/UP_WAKE',A1='/PRSNT_LOOP',B31='/PRSNT_LOOP')
right.place('J4','PCIe x4 UPSTREAM EDGE','BUS_PCIexpress_x4',5.5,41.55,pm)
# Rebuild the board perimeter to join to the stock footprint's open top corners.
for s in list(right.b.GetDrawings()):
    if s.GetLayer()==p.Edge_Cuts:remove(right.b,s)
pts=[(4.85,36.6),(0,36.6),(0,0),(44,0),(44,36.6),(39.15,36.6)]
for aa,zz in zip(pts,pts[1:]):line(right.b,aa,zz,p.Edge_Cuts)
for lane in range(4):
    for j,pol in enumerate(['P','N']):right.place(f'C{420+lane*2+j}','220nF 16V AC','C_0402_1005Metric',8+2.2*(lane*2+j),32,{'1':f'/UP_TX{lane}_{pol}','2':f'/UP_TX{lane}_{pol}_AC'},height=.55,angle=90)
# CLKREQ is optional on desktop PCIe edge; reserve it at a test pad instead of assigning a non-standard pin.
right.custom('Testpad_1',[('1',0,0,1,1)],1,1)
right.place('TP1','UP CLKREQ reserved','Testpad_1',41,30,{'1':'/UP_CLKREQ'})
right.text('UP x4 / SELF POWERED',23,35,size=.6)
for a in [left,right]:a.save()
with (ROOT/'TWINAX_MAP.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(pairmap[0]));w.writeheader();w.writerows(pairmap)
(ROOT/'BUILD.json').write_text(json.dumps({'revision':'I','main_mm':[80,45],'left_mm':[52,45],'right_mm':[44,45],'main_layers':32,'daughter_layers':12,'m2_vertical':True,'m2_footprint_verified':False,'fictional_bga_balls':400,'pcie_lanes':56,'data_pairs_per_cable':16,'clock_pairs_per_cable':2,'route_status':'placement complete; routing pending'},indent=2))
print('Built main and two vertical M.2 daughterboards. New signals',len(signals))
