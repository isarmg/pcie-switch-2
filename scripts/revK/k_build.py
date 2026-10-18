"""Rev K is a placement/net-assignment draft, not a fabrication release.

Run with KiCad's bundled Python. All dimensions are mm. The main board is
reconstructed as an unrouted layout because the former switch was fictional.
"""
from pathlib import Path
from collections import Counter
import sys, json, re, shutil, csv, math, hashlib
sys.stdout.reconfigure(encoding='utf-8')
HERE=Path(__file__).resolve().parents[2]
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2')
sys.path.insert(0,str(R/'scripts/revJ'))
import i_common as c
from i_common import p,v,xy,layers,line,rect,remove,pad,uid
O=R/'outputs/PCIe_3board_RevK';SRC=R/'outputs/PCIe_3board_RevJ'
DATA=HERE/'work/revK'
c.ROOT=O
O.mkdir(exist_ok=True)
for n in ['Main_10E1S','Left_2M2_Vertical','Right_M2_Upstream']:
    dest=O/n
    shutil.copytree(SRC/n,dest,dirs_exist_ok=True)
    if n.startswith('Main'):
        for f in list(dest.iterdir()):
            if f.name.startswith('Connectivity_') or f.name in ['DRC.json','ERC.json','CONNECTIVITY.net','ROUTING_STATUS.json','preview.png','bottom.png','PIN_MAP.csv','Local.kicad_sym'] or f.suffix=='.step':
                f.unlink()
    for f in list(dest.glob('*.lck'))+list(dest.glob('*.kicad_prl')):f.unlink()
for name in ['TWINAX_MAP.csv','MIGRATION.json']:
    shutil.copy2(SRC/name,O/name)
shutil.copytree(SRC/'references',O/'references',dirs_exist_ok=True)
for name in ['PEX88096_PINOUT.json','PEX88096_BALLS.csv','REFERENCE_PARTS.json']:
    shutil.copy2(DATA/name,O/name)
source_pdfs=['Broadcom_PEX88096_Data Sheet_V2_4 (1).pdf','W25Q32JW-1.8V 32MB SPIFLASH.pdf',
 'tps3808可编程延迟复位芯片.pdf','9ZXL0651-9ZXL0851六输出八输出固定85差分阻抗LP HCSL时钟缓冲器.pdf',
 '9FGV0241双输出固定差分100阻抗LP HCSL时钟发生器.PDF','9DML0451四输出固定85差分阻抗双输入LP HCSL时钟切换器.pdf',
 'tca9548a八通道I2C开关切换器.pdf']
source_manifest=[]
for name in source_pdfs:
    f=Path('C:/Users/micro/Downloads')/name;shutil.copy2(f,O/'references'/name)
    source_manifest.append({'file':name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'role':'user-provided reference'})
(O/'references/SOURCES.json').write_text(json.dumps(source_manifest,ensure_ascii=False,indent=2),encoding='utf-8')

n='Main_10E1S';folder=O/n;bp=folder/(n+'.kicad_pcb');b=p.LoadBoard(str(bp))
a=object.__new__(c.Board);a.name=n;a.w=110;a.h=45;a.b=b;a.folder=folder;a.lib=folder/'Local.pretty';a.models=folder/'models'
a.plugin=p.PCB_IO_MGR.FindPlugin(p.PCB_IO_MGR.KICAD_SEXP);a.cs=[];a.newrefs=[]
a.nets={q.GetNetname():q for q in b.GetNetInfo().NetsByNetcode().values()}
meta={q['ref']:q for q in json.loads((folder/'COMPONENTS.json').read_text())}
for f in b.GetFootprints():f.Move(v(15,0))
for t in list(b.GetTracks()):remove(b,t)
for z in list(b.Zones()):remove(b,z)
for g in list(b.GetDrawings()):remove(b,g)
rect(b,0,0,110,45,p.Edge_Cuts)
# The former random switch cannot be reused as the real device's footprint.
old=b.FindFootprintByReference('U1');legacy={q.GetNetname() for q in old.Pads() if q.GetNetname() and not q.GetNetname().startswith('unconnected-')}
remove(b,old)
pinout=json.loads((O/'PEX88096_PINOUT.json').read_text())
balls=pinout['ball_records'];by_signal={q['signal']:q['ball'] for q in balls}
net_to_signal={}
port_lane={**{f'S{i:02}':4*i for i in range(1,11)},'M1':44,'M2':48,'M4':52,'M3':56,'M5':60,'UP':64}
for nn in legacy:
    m=re.fullmatch(r'/(S\d\d)_SW_(TX|RX)([0-3])_([PN])',nn)
    if not m:m=re.fullmatch(r'/(M[1-5]|UP)_(TX|RX)([0-3])_([PN])',nn)
    if m:
        port,direction,lane,pol=m.groups();net_to_signal[nn]=f'{direction}{pol}[{port_lane[port]+int(lane)}]'
assert len(net_to_signal)==256
signal_to_net={s:nn for nn,s in net_to_signal.items()}
for lane in range(4):
    for direction in ['TX','RX']:
        for pol in 'PN':signal_to_net[f'{direction}{pol}[{lane}]']=f'/CPU_PEX_{direction}{lane}_{pol}'
power_map={'VSS':'/GND','VDD':'/PEX_0V9','VDDA':'/PEX_0V9A',
 'VDD1x':'/PEX_1V8','VDD1xA':'/PEX_1V8A','VDD18':'/PEX_1V8','VDD18A':'/PEX_1V8A'}
for pol in 'PN':
    signal_to_net['SYS_REF_CLK_'+pol]='/PEX_SYS_REFCLK_'+pol
    signal_to_net['S0_PCE_REF_CLK_'+pol]='/CPU_REFCLK_'+pol
signal_to_net.update({'SYS_PWR_ON_RST_N':'/PEX_SYS_RESET_N','S0_PCE_PERST_N':'/CPU_PERST_1V8_N',
 'SPI_CLK':'/PEX_SPI_CLK','SPI_FLASH_CS_N':'/PEX_SPI_CS_N',
 'SPI_SDIO[0]':'/PEX_SPI_IO0','SPI_SDIO[1]':'/PEX_SPI_IO1','SPI_SDIO[2]':'/PEX_SPI_IO2','SPI_SDIO[3]':'/PEX_SPI_IO3',
 'SPI_RST_N':'/PEX_SPI_RESET_N','I2C5_SCL':'/PEX_MGMT_SCL_1V8','I2C5_SDA':'/PEX_MGMT_SDA_1V8'})
for sig in ['DFT_SHIFT_CLK','DFT_SCAN_ENABLE','DFT_IDDT','DFT_TN','DBG_MODE[0]','DBG_MODE[1]','DBG_MODE[2]','DBG_MODE[3]','MODE_SEL[0]','MODE_SEL[1]','MODE_SEL[2]','MODE_SEL[3]','MODE_SEL[4]','MODE_SEL[5]','MODE_SEL[6]','MODE_SEL[7]','MODE_SEL[8]','TRST_L']:
    signal_to_net[sig]='/PEX_STRAP_'+sig.replace('[','').replace(']','')
f=p.FOOTPRINT(b);f.SetFPID(p.LIB_ID('Local','Broadcom_PEX88096_BGA1550_37p5x42p5_1mm'));f.SetAttributes(p.FP_SMD)
for q in balls:
    pp=p.PAD(f);pp.SetNumber(q['ball']);pp.SetPosition(v(q['x_mm'],q['y_mm']));pp.SetSize(v(.48,.48));pp.SetShape(p.PAD_SHAPE_CIRCLE)
    pp.SetAttribute(p.PAD_ATTRIB_SMD);pp.SetLayerSet(layers(p.F_Cu,p.F_Paste,p.F_Mask));pp.SetLocalSolderMaskMargin(p.FromMM(.0127));f.Add(pp)
rect(f,-18.75,-21.25,18.75,21.25,p.F_Fab,.1);rect(f,-18.95,-21.45,18.95,21.45,p.F_CrtYd)
line(f,(-18.75,-19.5),(-17,-21.25),p.F_Fab,.2)
f.SetLibDescription('1550 balls, 1mm pitch, 0.48mm pads from supplied Altium reference. Signals verified against PEX88096-DS109 tables 44 and 45. Reference land pattern still requires fabrication review.')
a.model(f,'PEX88096_37p5x42p5_2p92_envelope',37.5,42.5,2.92,color='0.16,0.17,0.18');a.savefoot(f)
b.Add(f);f.SetReference('U1');f.SetValue('Broadcom PEX88096 / SS02-0B00-00');f.Flip(v(0,0),p.FLIP_DIRECTION_LEFT_RIGHT);f.SetPosition(v(22.5,22.5))
pinmap={}
for pp in f.Pads():
    sig=next(q['signal'] for q in balls if q['ball']==pp.GetNumber())
    nn=power_map.get(sig,signal_to_net.get(sig,c.nc('U1',pp.GetNumber())))
    pp.SetNet(a.net(nn));pinmap[pp.GetNumber()]=nn
meta['U1']={'ref':'U1','value':f.GetValue(),'footprint':str(f.GetFPID().GetLibItemName()),'pinmap':pinmap,
 'pin_names':{q['ball']:q['signal'] for q in balls},'height_mm':2.92,'datasheet':source_pdfs[0],
 'side':'B','x':22.5,'y':22.5,'status':'real pinout, unrouted placement draft'}

# Keep all inherited circuits visible, but free the new chip bodies of other parts.
# Existing back-side power support moves to the front side into the two new wings.
support=[]
for ff in list(b.GetFootprints()):
    ref=ff.GetReference()
    if ff.GetLayer()!=p.B_Cu or ref=='U1' or ref.startswith(('J1','J2')):continue
    support.append(ff)
left_positions={'F1':(6.5,5),'D1':(6.5,12),'C1':(11,12),'U30':(6.5,19),'R301':(3,16),'R302':(3,19),'R303':(3,22),'R304':(3,25),
 'R305':(10,19),'C301':(10,22),'U31':(6.5,29),'L31':(6.5,35),'R311':(3,32),'C311':(10,28),'C312':(3,28),
 'C313':(10,31),'C314':(6,41),'C315':(11,41),'J301':(6.5,44),'J303':(10,38)}
right_positions={'F2':(103.5,13),'D2':(103.5,20),'C2':(98.5,20),'U41':(99,28),'U42':(106,28),
 'J302':(103.5,44),'J304':(99,39)}
for k,base in [(41,96),(42,103)]:
    right_positions.update({f'R{k}1':(base,25),f'R{k}2':(base,28),f'R{k}3':(base+4,25),f'R{k}4':(base+4,31),f'R{k}5':(base,34),f'C{k}1':(base+4,34),f'C{k}2':(base+4,22)})
# Their final positions are packed into actual free areas after the new parts
# are present. Keep the original component side and orientation.
for idx in range(101,119):b.FindFootprintByReference('J'+str(idx)).SetPosition(v(1.25,2+(idx-101)*2.3))
for idx in range(201,219):b.FindFootprintByReference('J'+str(idx)).SetPosition(v(108.75,2+(idx-201)*2.3))
for first,x in [(119,6.5),(219,105.0)]:
    for idx in range(first,first+9):
        ff=b.FindFootprintByReference('J'+str(idx));ff.Flip(ff.GetPosition(),p.FLIP_DIRECTION_LEFT_RIGHT)
        ff.SetPosition(v(x,4.2+(idx-first)*4.7))

def mechanical(ref,name,sx,sy,height,x,y,color):
    fp=p.FOOTPRINT(b);fp.SetFPID(p.LIB_ID('Local',name));fp.SetAttributes(p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES)
    rect(fp,-sx/2,-sy/2,sx/2,sy/2,p.F_Fab,.12);rect(fp,-sx/2-.25,-sy/2-.25,sx/2+.25,sy/2+.25,p.F_CrtYd)
    fp.SetLibDescription('MECHANICAL RESERVATION ONLY. No real ball map or electrical land pattern.');a.model(fp,name,sx,sy,height,color=color);a.savefoot(fp)
    b.Add(fp);fp.SetReference(ref);fp.SetValue(name);fp.Flip(v(0,0),p.FLIP_DIRECTION_LEFT_RIGHT);fp.SetPosition(v(x,y))
    meta[ref]={'ref':ref,'value':name,'footprint':name,'x':x,'y':y,'side':'B','height_mm':height,'pinmap':{},'mechanical_only':True}
    return fp
mechanical('U501','Intel_JHL9580_MECH_13x13_UNVERIFIED',13,13,2,96,23,'0.18,0.20,0.23')
mechanical('U502','Intel_Core_Ultra7_268V_MECH_27p5x27',27.5,27,1.7,64.5,22.5,'0.25,0.28,0.30')

# Vertical, low-profile 24-contact receptacle. Geometry comes from GCT USB4160
# drawing Rev A2 (31 January 2023), pp. 1-2; rated for USB 3.2 Gen2, not TB5.
usb='GCT_USB4160_24P_Vertical_7p46_DRAFT_TB5_UNQUALIFIED'
uf=p.FOOTPRINT(b);uf.SetFPID(p.LIB_ID('Local',usb));uf.SetAttributes(p.FP_SMD)
for side in 'AB':
    for ii in range(1,13):
        xx=-2.75+(ii-1)*.5 if side=='A' else 2.75-(ii-1)*.5
        yy=-1.43 if side=='A' else 1.43
        q=p.PAD(uf);q.SetNumber(side+str(ii));q.SetPosition(v(xx,yy));q.SetSize(v(.30,1.15));q.SetShape(p.PAD_SHAPE_RECT);q.SetAttribute(p.PAD_ATTRIB_SMD);q.SetLayerSet(layers(p.F_Cu,p.F_Mask,p.F_Paste));uf.Add(q)
for xx in [-4,4]:
    q=p.PAD(uf);q.SetPosition(v(xx,0));q.SetSize(v(.71,.71));q.SetDrillSize(v(.71,.71));q.SetShape(p.PAD_SHAPE_CIRCLE);q.SetAttribute(p.PAD_ATTRIB_NPTH);q.SetLayerSet(p.LSET.AllCuMask());uf.Add(q)
    for yy in [-1.43,1.43]:
        q=p.PAD(uf);q.SetNumber('SH');q.SetPosition(v(xx,yy));q.SetSize(v(1.60,1.10));q.SetShape(p.PAD_SHAPE_OVAL);q.SetAttribute(p.PAD_ATTRIB_PTH);q.SetDrillShape(p.PAD_DRILL_SHAPE_OBLONG);q.SetDrillSize(v(1.10,.60));ls=p.LSET.AllCuMask();ls.AddLayer(p.F_Mask);ls.AddLayer(p.B_Mask);q.SetLayerSet(ls);uf.Add(q)
rect(uf,-4.47,-1.845,4.47,1.845,p.F_Fab,.1);rect(uf,-4.95,-2.25,4.95,2.25,p.F_CrtYd)
uf.SetLibDescription('Vertical USB4160 land pattern from manufacturer drawing Rev A2. 7.46mm profile, 24 contacts, two 0.71mm locating holes. TB5 use and custom power ratings are unqualified.')
# Closed STEP primitives show a real vertical mating cavity and tongue; simplified
# to the drawing envelopes rather than scaling a horizontal USB connector.
a.model(uf,'USB4160_base',8.94,3.69,1.56,color='0.08,0.09,0.10')
for xx in [-4.37,4.37]:a.model(uf,'USB4160_end_wall',.20,3.16,5.90,(xx,0,1.56),'0.63,0.65,0.68')
for yy in [-1.48,1.48]:a.model(uf,'USB4160_side_wall',8.54,.20,5.90,(0,yy,1.56),'0.63,0.65,0.68')
a.model(uf,'USB4160_tongue',6.70,.70,5.0,(0,0,1.56),'0.07,0.08,0.09')
a.savefoot(uf)
shutil.copy2(DATA/'USB4160.pdf',O/'references/GCT_USB4160_RevA2.pdf')
positive={4,6,7,8,9};negative={1,2,3,10,11,12}
custom={side+str(i):('/CUSTOM_12V_RAW' if i in positive else '/GND' if i in negative else '/CUSTOM_DET_'+side) for side in 'AB' for i in range(1,13)}
custom['SH']='/GND'
tb={'A1':'/GND','A2':'/TB5_TX1_P','A3':'/TB5_TX1_N','A4':'/TB5_VBUS','A5':'/TB5_CC1','A6':'/TB5_USB2_DP','A7':'/TB5_USB2_DN','A8':'/TB5_SBU1','A9':'/TB5_VBUS','A10':'/TB5_RX2_N','A11':'/TB5_RX2_P','A12':'/GND',
 'B1':'/GND','B2':'/TB5_TX2_P','B3':'/TB5_TX2_N','B4':'/TB5_VBUS','B5':'/TB5_CC2','B6':'/TB5_USB2_DP','B7':'/TB5_USB2_DN','B8':'/TB5_SBU2','B9':'/TB5_VBUS','B10':'/TB5_RX1_N','B11':'/TB5_RX1_P','B12':'/GND','SH':'/GND'}
for ref,value,x,pm in [('J401','CUSTOM 12V POWER / NOT USB',101.5,custom),('J402','THUNDERBOLT 5 / SI PART TBD',96.5,tb)]:
    a.place(ref,value,usb,x,6.0,pm,'B',90,7.46,url='https://gct.co/connector/usb4160')

# Expose the two proprietary detect contacts without pretending that the socket
# alone implements a power controller or safe current sharing.
r0402=a.std('Resistor_SMD','R_0402_1005Metric');c0402=a.std('Capacitor_SMD','C_0402_1005Metric')
for ref,x,nn in [('R401',104,'/CUSTOM_DET_A'),('R402',104,'/CUSTOM_DET_B')]:
    a.place(ref,'100k',r0402,x,14 if ref=='R401' else 16,{'1':nn,'2':'/GND'},'B',0,.4)

# Copy the actual pad geometries and pin assignments of the reference support ICs.
# Their support circuits are retained as reference data, not falsely claimed routed.
reference=json.loads((O/'REFERENCE_PARTS.json').read_text(encoding='utf-8'))
chosen=[('KU1','U601',46.5,7,6,6,1.0),('KU3','U602',46.5,17,6,6,1.0),
        ('KU2','U603',46.5,27,4,4,1.0),('KU5','U604',46.5,36,4,4,1.0),
        ('FU1','U605',83.5,31,2.9,1.6,1.45),('FU2','U606',96,36,5.3,5.3,2.0),
        ('SU1','U607',83.5,20,4,4,1.0)]
support_net_map={'GND':'/GND','P1V8':'/PEX_1V8','P1V8A':'/PEX_1V8A','P0V9':'/PEX_0V9','P0V9A':'/PEX_0V9A',
 'SYS_REFCLKP':'/PEX_SYS_REFCLK_P','SYS_REFCLKN':'/PEX_SYS_REFCLK_N',
 'P3V3':'/P3V3_AUX','P3V3AUX':'/P3V3_AUX','SYS_PWRONRST#':'/PEX_SYS_RESET_N',
 'SPI_FLASH_CS#':'/PEX_SPI_CS_N','SPI_CLK':'/PEX_SPI_CLK',
 **{'SPI_SDIO'+str(i):'/PEX_SPI_IO'+str(i) for i in range(4)}}
for sr,ref,x,y,sx,sy,h in chosen:
    rr=reference[sr];fp=p.FOOTPRINT(b);name='REF_'+rr['part'].split('_')[0]+'_'+sr
    fp.SetFPID(p.LIB_ID('Local',name));pm={}
    for q in rr['pads']:
        pp=p.PAD(fp);pp.SetNumber(q['number']);pp.SetPosition(v(q['x'],q['y']));pp.SetSize(v(q['width'],q['height']));pp.SetShape(p.PAD_SHAPE_CIRCLE if q['shape']=='ROUND' else p.PAD_SHAPE_RECT);pp.SetAttribute(p.PAD_ATTRIB_SMD);pp.SetLayerSet(layers(p.F_Cu,p.F_Mask,p.F_Paste));pp.SetOrientationDegrees(q['rotation']);fp.Add(pp)
        pm[q['number']]=support_net_map.get(q['net'],'/REF_'+q['net']) if q['net'] else c.nc(ref,q['number'])
    rect(fp,-sx/2,-sy/2,sx/2,sy/2,p.F_Fab,.1)
    bb=fp.GetBoundingBox(False,False);rect(fp,min(-sx/2,p.ToMM(bb.GetX()))-.15,min(-sy/2,p.ToMM(bb.GetY()))-.15,max(sx/2,p.ToMM(bb.GetRight()))+.15,max(sy/2,p.ToMM(bb.GetBottom()))+.15,p.F_CrtYd)
    a.model(fp,name,sx,sy,h);a.savefoot(fp)
    a.place(ref,rr['part']+' / SUPPORT NETWORK PENDING',name,x,y,pm,'B',0,h,names=rr.get('pins',{}))

def bounds(ff):
    bb=ff.GetBoundingBox(False,False)
    return tuple(p.ToMM(x) for x in [bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom()])
def overlap(aa,bb,gap=.18):
    return not (aa[2]+gap<=bb[0] or bb[2]+gap<=aa[0] or aa[3]+gap<=bb[1] or bb[3]+gap<=aa[1])
packed_refs={ff.GetReference() for ff in support}
obstacles=[bounds(ff) for ff in b.GetFootprints() if ff.GetLayer()==p.B_Cu and ff.GetReference() not in packed_refs]
# Unused strips above/below the CPU and around the USB/TB5 block provide the
# placement area; do not overlap a chip merely because its land pattern is sparse.
regions=[(51,37,78,44.3),(87.5,31,107.3,44.3),(51,.7,78,8.0),
         (78.8,11.5,88.8,44.3),(87.5,11.0,107.3,16.0)]
support.sort(key=lambda ff:-(bounds(ff)[2]-bounds(ff)[0])*(bounds(ff)[3]-bounds(ff)[1]))
for ff in support:
    ff.SetPosition(v(0,0));bb=bounds(ff);ww=bb[2]-bb[0];hh=bb[3]-bb[1];found=None
    if hh>7 and ww<7:
        ff.SetOrientationDegrees(ff.GetOrientationDegrees()+90)
        bb=bounds(ff);ww=bb[2]-bb[0];hh=bb[3]-bb[1]
    for reg in regions:
        yy=reg[1]
        while yy+hh<=reg[3]+.001 and found is None:
            xx=reg[0]
            while xx+ww<=reg[2]+.001:
                trial=(xx,yy,xx+ww,yy+hh)
                if not any(overlap(trial,ob) for ob in obstacles):found=(xx-bb[0],yy-bb[1],trial);break
                xx+=.25
            yy+=.25
        if found:break
    assert found,('No free placement area',ff.GetReference(),ww,hh)
    ff.SetPosition(v(found[0],found[1]));obstacles.append(found[2])

# Input alternatives remain on separate domains. The custom interface is not
# directly paralleled to either existing high-current input without protection.
for ff in b.GetFootprints():
    ref=ff.GetReference()
    if ref in ['U501','U502']:continue
    entry=meta.setdefault(ref,{})
    entry.update({'ref':ref,'value':ff.GetValue(),'footprint':str(ff.GetFPID().GetLibItemName()),
       'x':xy(ff.GetPosition())[0],'y':xy(ff.GetPosition())[1],
       'side':'F' if ff.GetLayer()==p.F_Cu else 'B','rotation_deg':ff.GetOrientationDegrees(),
       'pinmap':{q.GetNumber():q.GetNetname() for q in ff.Pads() if q.GetNumber()}})
for ent in a.cs:meta[ent['ref']].update(ent)
(folder/'COMPONENTS.json').write_text(json.dumps(list(meta.values()),ensure_ascii=False,indent=2),encoding='utf-8')
p.SaveBoard(str(bp),b)
pro=json.loads((folder/(n+'.kicad_pro')).read_text());pro['meta']['filename']=n+'.kicad_pro';(folder/(n+'.kicad_pro')).write_text(json.dumps(pro,indent=2))

# Labels read correctly when viewed from the switch/component side (bottom).
for txt,xx,yy,sz in [('CUSTOM 12V',101.5,12,.7),('TB5 PORT',96.5,12,.7),('JHL9580',96,23,.85),
 ('Core Ultra 7 268V',64.5,22.5,1.1),('PEX88096',22.5,22.5,1.6),
 ('1550 balls / REAL PINOUT',22.5,25,1.0),('NO USB / CUSTOM CABLE',98,43,.65)]:
    a.text(txt,xx,yy,p.B_Fab,sz)
for g in b.GetDrawings():
    if isinstance(g,p.PCB_TEXT) and g.GetLayer()==p.B_Fab:g.SetMirrored(True)
a.text('REV K / 110 x 45 / PLACEMENT AND NET-ASSIGNMENT DRAFT / ROUTING PENDING',55,48,p.Dwgs_User,1)
p.SaveBoard(str(bp),b)

with (folder/'PIN_MAP.csv').open('w',encoding='utf-8-sig',newline='') as out:
    w=csv.writer(out);w.writerow(['Reference','Pad','Signal','Net','Side','X_mm','Y_mm'])
    for ff in sorted(b.GetFootprints(),key=lambda f:f.GetReference()):
        for q in ff.Pads():
            if q.GetNumber():w.writerow([ff.GetReference(),q.GetNumber(),meta[ff.GetReference()].get('pin_names',{}).get(q.GetNumber(),''),q.GetNetname(),'F' if ff.GetLayer()==p.F_Cu else 'B',*xy(q.GetPosition())])
with (O/'CUSTOM_POWER_PINOUT.csv').open('w',encoding='utf-8-sig',newline='') as out:
    w=csv.writer(out);w.writerow(['Contact','Function','Note'])
    for k,nn in custom.items():w.writerow([k,nn,'PROPRIETARY 12V ONLY; NOT USB/PD; contact current unqualified'])
(O/'BUILD.json').write_text(json.dumps({'revision':'K','main_mm':[110,45],'main_state':'unrouted placement and net assignment draft',
 'real_pex_ballmap':True,'intel_cpu_ballmap':False,'intel_jhl9580_ballmap':False,
 'custom_power_contacts':{'positive_12V':10,'ground':12,'detect':2},'custom_power_main_bus_connected':False,
 'usb_orientation':'vertical entry, 90-degree PCB rotation, long axis parallel to E1.S',
 'usb_height_mm':7.46,'usb_actual_tb5_qualified':False,
 'daughter_boards':'unchanged Rev J; individual CAD/DRC retained','ordering_view':'viewed from B.Cu/switch side',
 'left_to_right':['J401 custom power','J402 TB5','U502 Core Ultra 7 268V','U1 PEX88096'],
 'JHL9580':'under the two USB-shaped ports','production_ready':False},ensure_ascii=False,indent=2),encoding='utf-8')
(folder/'ROUTING_STATUS.json').write_text(json.dumps({'state':'unrouted','reason':'Replace fictional switch with real 1550-ball PEX88096; reconstruct electrical design against supplied reference before routing.','stale_RevJ_tracks_removed':True,'production_ready':False},indent=2))
# Copy the reproducible scripts into the migrated project.
for src in (HERE/'scripts/revK').glob('*.py'):
    dest=R/'scripts/revK'/src.name
    if src.resolve()!=dest.resolve():shutil.copy2(src,dest)
ignore=R/'.gitignore';s=ignore.read_text();rule='/outputs/PCIe_3board_RevK/*.zip'
if rule not in s:ignore.write_text(s.rstrip()+'\n'+rule+'\n')
print('Rev K main board built: 110 x 45 mm, true PEX88096 BGA1550, Intel mechanical reservations and two ports.')
print('Main intentionally unrouted; Rev J retained. No production-ready claim.')
