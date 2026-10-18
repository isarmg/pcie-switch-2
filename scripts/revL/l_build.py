"""Continue Rev K using Intel's actual 2833-ball map; retain explicit open items."""
from pathlib import Path
from collections import Counter
import sys,json,re,shutil,csv,hashlib
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2')
STAGE=Path(__file__).resolve().parents[2]
W=STAGE/'work/revL'
O=R/'outputs/PCIe_3board_RevL'
S=R/'outputs/PCIe_3board_RevK'
sys.path.insert(0,str(R/'scripts/revJ'))
import i_common as c
from i_common import p,v,xy,layers,rect,line,remove,pad
c.ROOT=O
shutil.copytree(S,O,dirs_exist_ok=True)
folder=O/'Main_10E1S';bp=folder/'Main_10E1S.kicad_pcb'
for f in list(folder.glob('Connectivity_*.kicad_sch'))+list(folder.glob('*.lck')):
    f.unlink()
for name in ['DRC.json','ERC.json','CONNECTIVITY.net','Main_10E1S.step','preview.png','bottom.png','switch_oblique.png','switch_face.svg','ROUTING_STATUS.json']:
    f=folder/name
    if f.exists():f.unlink()
for name in ['VALIDATION.json','STEP_VALIDATION.json','SHA256SUMS.txt','README.md']:
    f=O/name
    if f.exists():f.unlink()
b=p.LoadBoard(str(bp))
a=object.__new__(c.Board);a.name='Main_10E1S';a.w=110;a.h=45;a.b=b;a.folder=folder;a.lib=folder/'Local.pretty';a.models=folder/'models'
a.plugin=p.PCB_IO_MGR.FindPlugin(p.PCB_IO_MGR.KICAD_SEXP);a.cs=[];a.newrefs=[]
a.nets={q.GetNetname():q for q in b.GetNetInfo().NetsByNetcode().values()}
meta={q['ref']:q for q in json.loads((folder/'COMPONENTS.json').read_text(encoding='utf-8'))}
cpu=json.loads((W/'INTEL_268V_PINOUT.json').read_text(encoding='utf-8'))
tables=json.loads((W/'intel_tables.json').read_text(encoding='utf-8'))
bm=tables['825698-001_Ballout.xlsx']['Ballmap'];cross={str(row[0])+str(col):value for row in bm[1:] for col,value in zip(bm[0][1:],row[1:]) if value is not None}
assert len(cross)==2833 and all(cross[q['ball']]==q['signal'] for q in cpu['pins'])
old=b.FindFootprintByReference('U502');remove(b,old)

# Intel provides nonuniform "balls anywhere" coordinates. Never create a regular
# 0.5-mm matrix from the row/column names. Positive mechanical Y is up.
name='Intel_Core_Ultra_200V_BGA2833_27p5x27_ExactXY_DraftLands'
f=p.FOOTPRINT(b);f.SetFPID(p.LIB_ID('Local',name));f.SetAttributes(p.FP_SMD)
for q in cpu['pins']:
    pp=p.PAD(f);pp.SetNumber(q['ball']);pp.SetPosition(v(q['x_um']/1000,-q['y_um']/1000))
    pp.SetSize(v(.25,.25));pp.SetShape(p.PAD_SHAPE_CIRCLE);pp.SetAttribute(p.PAD_ATTRIB_SMD)
    pp.SetLayerSet(layers(p.F_Cu,p.F_Paste,p.F_Mask));pp.SetLocalSolderMaskMargin(p.FromMM(.0125));pp.SetLocalSolderPasteMargin(p.FromMM(-.0125));f.Add(pp)
rect(f,-13.75,-13.5,13.75,13.5,p.F_Fab,.10);rect(f,-14,-13.75,14,13.75,p.F_CrtYd,.05)
line(f,(12.75,13.5),(13.75,12.5),p.F_Fab,.2)
f.SetLibDescription('Exact 2833 positions and names: Intel 829568-004 embedded 825698-001_Ballout.xlsx, independently checked against Ballmap. KiCad (X,Y)=(manufacturer X,-manufacturer Y). 0.25mm copper / 0.225mm paste are PROVISIONAL lands, not an Intel recommended land pattern. Confirm package drawing 751493, paste, orientation and assembly process before manufacturing.')
a.model(f,'Intel_268V_32GB_27p5x27_Hmax1p676',27.5,27,1.676,color='0.25,0.28,0.30')
a.savefoot(f);b.Add(f);f.SetReference('U502');f.SetValue('Intel Core Ultra 7 268V / BGA2833')
f.Flip(v(0,0),p.FLIP_DIRECTION_LEFT_RIGHT);f.SetOrientationDegrees(270);f.SetPosition(v(64.5,22.5))

signal_net={}
for lane in range(4):
    for pol in 'PN':
        signal_net[f'PCIE_{lane+5}_TX_{pol}']=f'/CPU_G5_TX{lane}_{pol}'
        signal_net[f'PCIE_{lane+5}_RX_{pol}']=f'/CPU_G5_RX{lane}_{pol}'
for k in range(3):
    for pol in 'PN':signal_net[f'CLKOUT_{pol}{k}']=(f'/CPU_REFCLK_{pol}' if k==0 else f'/CPU_CLKBUF{k}_IN_{pol}')
signal_net.update({'XTAL_IN':'/CPU_XTAL_IN','XTAL_OUT':'/CPU_XTAL_OUT','RTCX1':'/CPU_RTCX1','RTCX2':'/CPU_RTCX2',
 'RTCRST#':'/CPU_RTCRST_N','SRTCRST#':'/CPU_SRTCRST_N','VIDSCK':'/CPU_SVID_CLK_1V25','VIDSOUT':'/CPU_SVID_DATA_1V25','VIDALERT#':'/CPU_SVID_ALERT_1V25_N',
 'PLT_PWROK':'/CPU_PLT_PWROK_1V8','SYS_PWROK':'/CPU_SYS_PWROK_1V8','RSMRST#':'/CPU_RSMRST_1V8_N','SYS_RESET#':'/CPU_SYS_RESET_1V8_N',
 'EPD_ON_IN':'/CPU_EPD_ON_IN','EPD_ON_OUT':'/CPU_EPD_ON_OUT','VDD2PWRGOOD_IN':'/CPU_VDD2_PWRGOOD_LOOP','VDD2PWRGOOD_OUT':'/CPU_VDD2_PWRGOOD_LOOP',
 'SPI0_CLK':'/CPU_SPI_CLK_PAD','SPI0_CS0#':'/CPU_SPI_CS0_N','SPI0_MISO':'/CPU_SPI_IO1','SPI0_MOSI':'/CPU_SPI_IO0','SPI0_IO2':'/CPU_SPI_IO2','SPI0_IO3':'/CPU_SPI_IO3',
 'CLK_S_RCOMP':'/CPU_CLK_RCOMP','PCIE4_RCOMP':'/CPU_PCIE4_RCOMP','PCIE5_RCOMP':'/CPU_PCIE5_RCOMP','USB2_RCOMP':'/CPU_USB2_RCOMP','USB32_RCOMP':'/CPU_USB32_RCOMP'})
gpio_map={'GPP_B13':'/CPU_PERST_1V8_N','GPP_C09':'/CPU_CLKREQ0_N','GPP_C10':'/CPU_CLKREQ1_N','GPP_C11':'/CPU_CLKREQ2_N',
 'GPP_V03':'/CPU_PWRBTN_1V8_N','GPP_V04':'/CPU_SLP_S3_1V8_N','GPP_V05':'/CPU_SLP_S4_1V8_N','GPP_V09':'/CPU_SLP_S5_1V8_N','GPP_V16':'/CPU_VCCST_EN_1V8'}
rail_names=sorted({q['signal'] for q in cpu['pins'] if q['interface']=='Power' and q['signal']!='VSS' and not any(k in q['signal'] for k in ['SENSE','EDGECAP','FLTR','PWRGOOD']) and not q['signal'].startswith('VID')})
pinmap={};types={}
for q in cpu['pins']:
    sig=q['signal'];primary=sig.split('/')[0];nn=signal_net.get(sig,gpio_map.get(primary))
    if sig=='VSS':nn='/GND'
    elif sig in rail_names or q['interface']=='Power' and any(k in sig for k in ['SENSE','EDGECAP','FLTR']):nn='/CPU_'+sig
    nn=nn or c.nc('U502',q['ball']);pinmap[q['ball']]=nn
    io=q['io'];typ={'I':'input','O':'output','I/O':'bidirectional','IOD':'open_collector'}.get(io,'passive')
    if sig in rail_names or sig=='VSS':typ='power_in'
    elif 'SENSE' in sig:typ='input'
    elif sig in ['VIDSCK','VIDSOUT']:typ='open_collector' if sig=='VIDSCK' else 'bidirectional'
    elif sig=='VIDALERT#':typ='input'
    if primary=='GPP_B13':typ='output'
    types[q['ball']]=typ
for pp in f.Pads():pp.SetNet(a.net(pinmap[pp.GetNumber()]))
meta['U502']={'ref':'U502','value':f.GetValue(),'footprint':name,'pinmap':pinmap,'pin_names':{q['ball']:q['signal'] for q in cpu['pins']},'pin_types':types,
 'height_mm':1.676,'side':'B','x':64.5,'y':22.5,'rotation_deg':90,'mechanical_only':False,'datasheet':'Intel 829568-004 + embedded 825698-001_Ballout.xlsx',
 'status':'true manufacturer ball coordinates and signal names; provisional PCB land diameter; electrical design incomplete'}

# Turn the actual switch so its lane 0-3 upstream bank faces the CPU.
pex=b.FindFootprintByReference('U1');pex.SetOrientationDegrees(0)
fixed={'U1','U502','U501','J401','J402'}
for ref,y in [('U601',4.9),('U602',40.1)]:b.FindFootprintByReference(ref).SetPosition(v(46.2,y));fixed.add(ref)
r0402=a.std('Resistor_SMD','R_0402_1005Metric');c0402=a.std('Capacitor_SMD','C_0402_1005Metric');c0603=a.std('Capacitor_SMD','C_0603_1608Metric')
def place(ref,value,foot,pm,height=.5,angle=0,x=0,y=0,fixed_pos=False,names=None):
    ff=a.place(ref,value,foot,x,y,pm,'B',angle,height,names=names)
    if fixed_pos:fixed.add(ref)
    return ff
def rc(ref,value,net,other='/GND',cap=False,foot=None,**kw):
    return place(ref,value,foot or (c0402 if cap else r0402),{'1':net,'2':other},**kw)

# One correctly oriented AC capacitor per conductor at each transmitter.
link_records=[]
for lane in range(4):
    for j,pol in enumerate('PN'):
        i=lane*2+j
        cu=rc(f'C{801+i}','220nF 6.3V X5R',f'/CPU_G5_TX{lane}_{pol}',f'/CPU_PEX_RX{lane}_{pol}',cap=True,angle=180,x=49.2,y=30.2-lane*2.4+(j-.5)*1.2,fixed_pos=True)
        px=rc(f'C{811+i}','220nF 6.3V X5R',f'/CPU_PEX_TX{lane}_{pol}',f'/CPU_G5_RX{lane}_{pol}',cap=True,angle=0,x=43.1,y=18-lane*2.4+(j-.5)*1.2,fixed_pos=True)
        link_records.append({'lane':lane,'polarity':pol,'cpu_tx_ball':next(q['ball'] for q in cpu['pins'] if q['signal']==f'PCIE_{lane+5}_TX_{pol}'),
          'cpu_rx_ball':next(q['ball'] for q in cpu['pins'] if q['signal']==f'PCIE_{lane+5}_RX_{pol}'),
          'cpu_tx_cap':cu.GetReference(),'pex_tx_cap':px.GetReference(),
          'pex_rx_ball':next(q['number'] for q in [] ) if False else next(q.GetNumber() for q in pex.Pads() if q.GetNetname()==f'/CPU_PEX_RX{lane}_{pol}'),
          'pex_tx_ball':next(q.GetNumber() for q in pex.Pads() if q.GetNetname()==f'/CPU_PEX_TX{lane}_{pol}')})

# BIOS interface: 256 Mbit = 32 MiB, 1.8 V. Land pattern is the KiCad WSON
# family pattern; package/EP tolerances remain a part-selection review item.
flash=a.std('Package_SON','WSON-8-1EP_6x5mm_P1.27mm_EP3.4x4.3mm')
place('U701','W25Q256JWPIQ / 1.8V 32MiB BIOS',flash,{'1':'/CPU_SPI_CS0_N','2':'/CPU_SPI_IO1','3':'/CPU_SPI_IO2','4':'/GND','5':'/CPU_SPI_IO0','6':'/CPU_SPI_CLK_FLASH','7':'/CPU_SPI_IO3','8':'/CPU_VCCPRIM_1P8','9':'/GND'},.8,names={'1':'CS#','2':'IO1','3':'IO2','4':'GND','5':'IO0','6':'CLK','7':'IO3','8':'VCC','9':'EP'})
rc('R701','22R provisional SI tuning','/CPU_SPI_CLK_PAD','/CPU_SPI_CLK_FLASH')
for ref,nn in [('R702','/CPU_SPI_CS0_N'),('R703','/CPU_SPI_IO2'),('R704','/CPU_SPI_IO3')]:rc(ref,'10k',nn,'/CPU_VCCPRIM_1P8')
rc('C701','100nF','/CPU_VCCPRIM_1P8',cap=True);rc('C702','1uF','/CPU_VCCPRIM_1P8',cap=True)

# The two crystal loads must be tuned to the selected crystal and measured
# board stray capacitance. They are not claimed as an Intel reference design.
xt=a.std('Crystal','Crystal_SMD_3225-4Pin_3.2x2.5mm');rt=a.std('Crystal','Crystal_SMD_2012-2Pin_2.0x1.2mm')
place('Y701','38.4MHz crystal / load and ESR selection pending',xt,{'1':'/CPU_XTAL_IN','2':'/GND','3':'/CPU_XTAL_OUT','4':'/GND'},.8)
place('Y702','32.768kHz crystal / load and ESR selection pending',rt,{'1':'/CPU_RTCX1','2':'/CPU_RTCX2'},.6)
for ref,nn,val in [('C703','/CPU_XTAL_IN','18pF DNP TUNE'),('C704','/CPU_XTAL_OUT','18pF DNP TUNE'),('C705','/CPU_RTCX1','8.2pF DNP TUNE'),('C706','/CPU_RTCX2','8.2pF DNP TUNE')]:
    z=rc(ref,val,nn,cap=True);z.SetDNP(True)
rc('R705','180R 1% / Intel clock topology','/CPU_CLK_RCOMP')
for ref,nn in [('R706','/CPU_PCIE4_RCOMP'),('R707','/CPU_PCIE5_RCOMP')]:
    z=rc(ref,'TBD RCOMP / DNP / Intel PDG required',nn);z.SetDNP(True)
rc('R708','200R 1%','/CPU_USB2_RCOMP');rc('R709','200R 1%','/CPU_USB32_RCOMP')

# Independent 1.5 V RTC supply; no coin-cell and no false 3 V RTC connection.
ldo=a.std('Package_TO_SOT_SMD','SOT-23-5')
place('U702','TPS7A0215PDBVR / RTC 1.5V',ldo,{'1':'/P3V3_AUX','2':'/GND','3':'/P3V3_AUX','4':c.nc('U702','4'),'5':'/CPU_VCCRTC'},1.45,
      names={'1':'IN','2':'GND','3':'EN','4':'NC','5':'OUT'})
rc('C707','1uF','/P3V3_AUX',cap=True);rc('C708','1uF','/CPU_VCCRTC',cap=True)
for ref,nn in [('R710','/CPU_RTCRST_N'),('R711','/CPU_SRTCRST_N')]:rc(ref,'100k',nn,'/CPU_VCCRTC')
for ref,nn in [('C709','/CPU_RTCRST_N'),('C710','/CPU_SRTCRST_N')]:rc(ref,'100nF RC reset draft',nn,cap=True)
rc('R712','10k','/CPU_SYS_RESET_1V8_N','/CPU_VCCPRIM_1P8')
rc('R713','10k','/CPU_PWRBTN_1V8_N','/CPU_VCCPRIM_1P8')
for i in range(3):rc(f'R{714+i}','0R / request clock always on',f'/CPU_CLKREQ{i}_N')

# Two buffer inputs are driven independently; no multi-drop clock input stub.
# Firmware must enable CLKOUT0/1/2 at 100MHz, non-SSC, and the selected GPIO mux.
clock_targets=[['PEX_SYS_REFCLK']+[f'S{i:02}_REFCLK' for i in range(1,8)],
               [f'S{i:02}_REFCLK' for i in range(8,11)]+[f'M{i}_CLK' for i in range(1,6)]]
outpins=[(13,14),(16,17),(21,22),(25,26),(28,29),(32,33),(35,36),(39,40)]
for k,ref in enumerate(['U601','U602'],1):
    ff=b.FindFootprintByReference(ref);pm={}
    for pp in ff.Pads():
        n=int(pp.GetNumber());pm[str(n)]='/GND' if n in [2,11,18,23,24,30,31,37,41,49] else '/P3V3_AUX' if n in [1,3,10,15,19,27,34,38,42,47,48] else f'/CLKBUF{k}_VDDA' if n==44 else c.nc(ref,str(n))
    pm.update({'4':f'/CPU_CLKBUF{k}_IN_P','5':f'/CPU_CLKBUF{k}_IN_N'})
    for (pn,nn),target in zip(outpins,clock_targets[k-1]):pm[str(pn)]='/'+target+'_P';pm[str(nn)]='/'+target+'_N'
    for pp in ff.Pads():pp.SetNet(a.net(pm[pp.GetNumber()]))
    meta[ref]['pinmap']=pm;ff.SetValue('9ZXL0851EKILFT / CPU common clock 100MHz')
    rc(f'R{720+k}','0R analog supply link / filter pending','/P3V3_AUX',f'/CLKBUF{k}_VDDA')
    for j in range(9):rc(f'C{720+(k-1)*10+j}','100nF',f'/CLKBUF{k}_VDDA' if j==8 else '/P3V3_AUX',cap=True)
for ref in ['U603','U604']:
    ff=b.FindFootprintByReference(ref);ff.SetDNP(True);ff.SetValue(meta[ref]['value'].split(' / ')[0]+' / DNP ALTERNATE CLOCK')

# Preserve exact net names at E1.S/twinax clock endpoints rather than leaving
# renamed clock outputs attached only to a buffer.
for ff in b.GetFootprints():
    for pp in ff.Pads():
        nn=pp.GetNetname()
        m=re.fullmatch(r'/(S\d\d)_REFCLK_([PN])',nn)
        if m:continue
        m=re.fullmatch(r'/(S\d\d)_(?:CLK|SW_REFCLK)_([PN])',nn)
        if m:pp.SetNet(a.net('/'+m[1]+'_REFCLK_'+m[2]))

# Supervisor: reset stays asserted with the CPU platform reset and when 0.9V
# drops. The complete multi-rail startup sequencer remains an explicit open item.
ff=b.FindFootprintByReference('U605')
pm={'1':'/PEX_SYS_RESET_N','2':'/GND','3':'/CPU_PERST_1V8_N','4':'/PEX_RESET_CT','5':'/PEX_0V9','6':'/P3V3_AUX'}
for pp in ff.Pads():pp.SetNet(a.net(pm[pp.GetNumber()]))
meta['U605']['pinmap']=pm
rc('C741','47nF / reset delay','/PEX_RESET_CT',cap=True);rc('C742','100nF','/P3V3_AUX',cap=True)
rc('R724','10k','/PEX_SYS_RESET_N','/PEX_1V8');rc('R725','10k','/CPU_PERST_1V8_N','/CPU_VCCPRIM_1P8')

# Representative decoupling on each independent rail. Counts and values are
# placement budgets only until the CPU PMIC design and PDN simulation exist.
for i,rail in enumerate(rail_names):
    rc(f'C{901+i*2}','100nF / PDN budget',f'/CPU_{rail}',cap=True)
    rc(f'C{902+i*2}','4.7uF / PDN budget',f'/CPU_{rail}',cap=True,foot=c0603,height=.9)
edge=sorted({q['signal'] for q in cpu['pins'] if 'EDGECAP' in q['signal']})
for i,nn in enumerate(edge):rc(f'C{951+i}','4.7uF / EDGECAP value pending PDG','/CPU_'+nn,cap=True,foot=c0603,height=.9)
for i,nn in enumerate(['VCCPRIM_1P8_FLTRB_CAP','VCCPRIM_1P8_FLTRA_IN','VCCPRIM_1P8_FLTRB_IN','VCCPRIM_VNNAON_FLTR']):
    rc(f'C{965+i}','1uF / filter value pending PDG','/CPU_'+nn,cap=True)
for i,nn in enumerate(['VCCPRIM_1P8_FLTRA_IN','VCCPRIM_1P8_FLTRB_IN','VCCPRIM_VNNAON_FLTR']):
    source='/CPU_VCCPRIM_VNNAON' if 'VNNAON' in nn else '/CPU_VCCPRIM_1P8'
    z=rc(f'R{730+i}','DNP / filter link pending Intel PDG',source,'/CPU_'+nn);z.SetDNP(True)

# Probe-only contacts expose sequencing and SVID for future PMIC work. These
# tiny test pads are not high-current CPU power connectors.
tp='Probe_0p5mm'
a.custom(tp,[('1',0,0,.5,.5)],.5,.5)
control=['/CPU_SVID_CLK_1V25','/CPU_SVID_DATA_1V25','/CPU_SVID_ALERT_1V25_N','/CPU_PLT_PWROK_1V8','/CPU_SYS_PWROK_1V8','/CPU_RSMRST_1V8_N','/CPU_SYS_RESET_1V8_N','/CPU_PWRBTN_1V8_N','/CPU_VCCST_EN_1V8','/CPU_SLP_S3_1V8_N','/CPU_SLP_S4_1V8_N','/CPU_SLP_S5_1V8_N']
for i,nn in enumerate(control):place(f'TP{701+i}','PROBE '+nn,tp,{'1':nn},0)

# Compact placement within the existing outline and body clearances.
def bounds(ff):
    bb=ff.GetBoundingBox(False,False)
    return tuple(p.ToMM(z) for z in [bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom()])
def overlap(aa,bb,gap=.15):return not(aa[2]+gap<=bb[0] or bb[2]+gap<=aa[0] or aa[3]+gap<=bb[1] or bb[3]+gap<=aa[1])
movable=[ff for ff in b.GetFootprints() if ff.GetLayer()==p.B_Cu and ff.GetReference() not in fixed and not re.fullmatch(r'J[12]\d\d',ff.GetReference())]
mrefs={ff.GetReference() for ff in movable}
obs=[bounds(ff) for ff in b.GetFootprints() if ff.GetLayer()==p.B_Cu and ff.GetReference() not in mrefs]
regions=[(51.3,37.0,78,44.2),(51.3,.8,78,8.0),(79.0,.8,89,44.2),(89,30.2,107.2,44.2),(42.0,9.0,50.7,35.5),(88.0,11.3,107.2,16.0)]
movable.sort(key=lambda ff:-(bounds(ff)[2]-bounds(ff)[0])*(bounds(ff)[3]-bounds(ff)[1]))
for ff in movable:
    ff.SetPosition(v(0,0));found=None
    for rot in [0,90]:
        if rot:ff.SetOrientationDegrees(ff.GetOrientationDegrees()+90)
        bb=bounds(ff);ww=bb[2]-bb[0];hh=bb[3]-bb[1]
        for x0,y0,x1,y1 in regions:
            yy=y0
            while yy+hh<=y1+.001 and found is None:
                xx=x0
                while xx+ww<=x1+.001:
                    trial=(xx,yy,xx+ww,yy+hh)
                    if not any(overlap(trial,ob) for ob in obs):found=(xx-bb[0],yy-bb[1],trial);break
                    xx+=.2
                yy+=.2
            if found:break
        if found:break
    assert found,('cannot place',ff.GetReference(),ww,hh)
    ff.SetPosition(v(*found[:2]));obs.append(found[2])

for ent in a.cs:meta[ent['ref']]=ent
for ff in b.GetFootprints():
    ref=ff.GetReference();ent=meta.setdefault(ref,{})
    ent.update(ref=ref,value=ff.GetValue(),footprint=str(ff.GetFPID().GetLibItemName()),x=xy(ff.GetPosition())[0],y=xy(ff.GetPosition())[1],side='B' if ff.GetLayer()==p.B_Cu else 'F',rotation_deg=ff.GetOrientationDegrees(),pinmap={q.GetNumber():q.GetNetname() for q in ff.Pads() if q.GetNumber()},dnp=ff.IsDNP())
(folder/'COMPONENTS.json').write_text(json.dumps(list(meta.values()),ensure_ascii=False,indent=2),encoding='utf-8')
for g in b.GetDrawings():
    if isinstance(g,p.PCB_TEXT) and ('REV K' in g.GetText() or g.GetText()=='Core Ultra 7 268V'):remove(b,g)
a.text('REV L / REAL CPU BALLMAP / CPU PCIe + BOOT SUPPORT / PMIC AND FULL ROUTING PENDING',55,48,p.Dwgs_User,.9)
p.SaveBoard(str(bp),b)
pro=json.loads((folder/'Main_10E1S.kicad_pro').read_text());rules=pro['board']['design_settings']['rules']
rules['min_clearance']=.075;rules['min_track_width']=.075;rules['min_via_diameter']=.25;rules['min_through_hole_diameter']=.1;rules['min_via_annular_width']=.05
(folder/'Main_10E1S.kicad_pro').write_text(json.dumps(pro,indent=2))

ref=O/'references/Intel_268V';ref.mkdir(parents=True,exist_ok=True)
for q in (STAGE/'work/intel_datasheets').iterdir():
    if q.suffix.lower() in ['.pdf','.xlsx']:shutil.copy2(q,ref/q.name)
cpu['checks']={'pinlist_count':2833,'ballmap_count':2833,'signal_crosscheck_mismatches':0,'unique_coordinates':2833,'coordinates_used_without_grid_approximation':True}
cpu['pcb_lands']={'diameter_mm':.25,'paste_aperture_mm':.225,'status':'provisional; not a published Intel recommendation'}
(O/'INTEL_268V_PINOUT.json').write_text(json.dumps(cpu,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'CPU_PEX_LINK.json').write_text(json.dumps(link_records,indent=2))
(O/'BUILD.json').write_text(json.dumps({'revision':'L','main_mm':[110,45],'cpu_bga_balls':2833,'cpu_ball_coordinates':'exact manufacturer XY, ballmap crosscheck passed','cpu_lands':'0.25mm provisional; package 751493 still required','cpu_pcie':'PCIE_5..8 -> PEX lane 0..3 via 16 AC capacitors; link target Gen4 x4','cpu_pmic_implemented':False,'jhl9580':'deferred per user, mechanical placeholder retained','daughter_boards':'unchanged Rev K/Rev J','production_ready':False},ensure_ascii=False,indent=2),encoding='utf-8')
with (O/'CPU_POWER_DOMAINS.csv').open('w',encoding='utf-8-sig',newline='') as fp:
    cw=csv.writer(fp);cw.writerow(['Rail','Ball_count','Control','Supply_status'])
    counts=Counter(q['signal'] for q in cpu['pins'])
    for rail in rail_names:cw.writerow([rail,counts[rail],'SVID IMVP9.2' if rail in ['VCC_PCORE','VCC_ECORE','VCCGT','VCCSA','VCCL2','VDDQ'] else 'Fixed or sequenced; confirm Intel PDG','RTC LDO fitted' if rail=='VCCRTC' else 'PMIC not implemented'])
with (folder/'PIN_MAP.csv').open('w',encoding='utf-8-sig',newline='') as fp:
    cw=csv.writer(fp);cw.writerow(['Reference','Ball_or_pad','Signal','Net','Side','X_mm','Y_mm'])
    for ff in sorted(b.GetFootprints(),key=lambda z:z.GetReference()):
        for pp in ff.Pads():
            if pp.GetNumber():cw.writerow([ff.GetReference(),pp.GetNumber(),meta[ff.GetReference()].get('pin_names',{}).get(pp.GetNumber(),''),pp.GetNetname(),'B' if ff.GetLayer()==p.B_Cu else 'F',*xy(pp.GetPosition())])
print('Rev L main: real BGA2833, x4 link with TX/RX correctly crossed, boot/RTC/support circuits.',len(list(b.GetFootprints())),'parts',flush=True)
