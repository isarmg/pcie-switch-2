"""TB3 host derivative; real supplied controller ball maps, explicitly fake switch."""
from pathlib import Path
from collections import defaultdict,Counter
import sys,json,shutil,math,re
sys.stdout.reconfigure(encoding='utf-8')
STAGE=Path(__file__).resolve().parents[2]
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
S=R/'outputs/PCIe_E1S_82x45_FakePEX90064_RevS';O=R/'outputs/PCIe_E1S_82x45_TB3Host_RevT';W=STAGE/'work/revT'
shutil.copytree(S,O,dirs_exist_ok=True);folder=O/'Main_10E1S';bp=folder/'Main_10E1S.kicad_pcb'
b=p.LoadBoard(str(bp))
pro=folder/'Main_10E1S.kicad_pro';settings=json.loads(pro.read_text(encoding='utf-8'))
# Provisional HDI rule for the 0.10mm drilled blind vias, requiring fabricator
# confirmation. Preserve the 0.25mm hole-to-hole and 0.40mm board-edge rules.
settings['board']['design_settings']['rules']['min_hole_clearance']=.10
settings['board']['design_settings']['rules']['min_via_diameter']=.20
for cl in settings['net_settings']['classes']:cl['clearance']=.075
pro.write_text(json.dumps(settings,indent=2),encoding='utf-8')
for obj in list(b.GetTracks())+list(b.Zones()):remove(b,obj)
for name in ['DRC.json','ERC.json','CONNECTIVITY.net','Main_10E1S.step','preview.png','bottom.png','PIN_MAP.csv']:
    f=folder/name
    if f.is_file():f.unlink()
for name in ['VALIDATION.json','STEP_VALIDATION.json','SHA256SUMS.txt','SIGNAL_ROUTES.json','SIGNAL_ROUTE_LENGTHS.json']:
    f=O/name
    if f.is_file():f.unlink()
meta={q['ref']:q for q in json.loads((folder/'COMPONENTS.json').read_text(encoding='utf-8'))}
a=object.__new__(Board);a.b=b;a.folder=folder;a.lib=folder/'Local.pretty';a.models=folder/'models';a.cs=[];a.newrefs=[];a.w=82;a.h=45;a.name='Main_10E1S'
a.plugin=p.PCB_IO_MGR.FindPlugin(p.PCB_IO_MGR.KICAD_SEXP);a.nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
# Switch-side view mirrors X: the high-X end is the user's left edge.
# Both upright USB-C ports are centered at half the 45mm board height.
for ref in ['J401','J402']:
    f=b.FindFootprintByReference(ref);x,y=xy(f.GetPosition());f.SetPosition(v(x,22.5));meta[ref]['y']=22.5
    for pp in list(f.Pads()):
        if pp.GetAttribute()==p.PAD_ATTRIB_NPTH:remove(f,pp)
    # Locator-free SMT concept, because plastic locating stakes would project
    # into the E1.S housings on the opposite face in the new central position.
    f.Models().clear()
    for name,sx,sy,h,off,col in [
        ('USB_SMT_Frame_End',.5,3,7.46,(-3.95,0,0),'0.65,0.67,0.69'),
        ('USB_SMT_Frame_End',.5,3,7.46,(3.95,0,0),'0.65,0.67,0.69'),
        ('USB_SMT_Frame_Side',7.4,.5,7.46,(0,-1.25,0),'0.65,0.67,0.69'),
        ('USB_SMT_Frame_Side',7.4,.5,7.46,(0,1.25,0),'0.65,0.67,0.69'),
        ('USB_SMT_Base',8.4,3,.45,(0,0,0),'0.18,0.19,0.20'),
        ('USB_SMT_Tongue',7.0,.6,7.0,(0,0,0),'0.12,0.13,0.14')]:a.model(f,name,sx,sy,h,off,col)
    meta[ref].update(plastic_locators='none; locator-free custom SMT concept',mechanical_model='simplified closed frame, no through-board stakes')
    # Also save the modified local footprint for subsequent edits.
    local=p.FootprintLoad(str(a.lib),str(f.GetFPID().GetLibItemName()))
    for pp in list(local.Pads()):
        if pp.GetAttribute()==p.PAD_ATTRIB_NPTH:remove(local,pp)
    local.Models().clear()
    for mm in f.Models():
        m=p.FP_3DMODEL();m.m_Filename=mm.m_Filename;m.m_Offset=mm.m_Offset;m.m_Rotation=mm.m_Rotation;m.m_Scale=mm.m_Scale;local.Models().append(m)
    a.savefoot(local)
newrefs=set();fixednew=set();connections=[]
def setpin(ref,pin,nn):
    f=b.FindFootprintByReference(ref);pad(f,pin).SetNet(a.net(nn));meta[ref]['pinmap'][str(pin)]=nn
def add(ref,value,foot,pm,x=0,y=0,side='B',angle=0,h=.6,names=None,fixed=False,url=''):
    f=a.place(ref,value,foot,x,y,pm,side,angle,h,url,names);meta[ref]=a.cs[-1];newrefs.add(ref)
    if fixed:fixednew.add(ref)
    return f
def bga(ref,value,name,info,pm,x,y,angle=0):
    f=p.FOOTPRINT(b);f.SetFPID(p.LIB_ID('Local',name));f.SetAttributes(p.FP_SMD)
    for q in info['pins']:
        pp=p.PAD(f);pp.SetNumber(q['ball']);pp.SetPosition(v(q['x_mm'],q['y_mm']));pp.SetSize(v(*([info['land_diameter_mm_provisional']]*2)));pp.SetShape(p.PAD_SHAPE_CIRCLE);pp.SetAttribute(p.PAD_ATTRIB_SMD);pp.SetLayerSet(layers(p.F_Cu,p.F_Mask,p.F_Paste));f.Add(pp)
    sx,sy=info['body_mm'];rect(f,-sx/2,-sy/2,sx/2,sy/2,p.F_Fab,.1);rect(f,-sx/2-.2,-sy/2-.2,sx/2+.2,sy/2+.2,p.F_CrtYd)
    line(f,(-sx/2,-sy/2+.8),(-sx/2+.8,-sy/2),p.F_Fab,.15)
    f.SetLibDescription('Ball names and mixed-pitch geometry transcribed from supplied/official datasheet. Provisional land diameter; assembly land pattern requires qualification.')
    a.model(f,name,sx,sy,info['height_mm_max']);a.savefoot(f)
    return add(ref,value,name,pm,x,y,'B',angle,info['height_mm_max'],{q['ball']:q['signal'] for q in info['pins']},True)
cap='C_0201_0603Metric_DenseCourtyard_1p30x0p55'
c0402=a.std('Capacitor_SMD','C_0402_1005Metric');c0603=a.std('Capacitor_SMD','C_0603_1608Metric')
r0201=a.std('Resistor_SMD','R_0201_0603Metric');r0402=a.std('Resistor_SMD','R_0402_1005Metric')
dense=p.FootprintLoad(str(a.lib),r0201);r0201='R_0201_DenseCourtyard_1p0x0p4';dense.SetFPID(p.LIB_ID('Local',r0201))
for gg in list(dense.GraphicalItems()):
    if gg.GetLayer()==p.F_CrtYd:remove(dense,gg)
rect(dense,-.5,-.2,.5,.2,p.F_CrtYd,.05);dense.SetLibDescription('Stock KiCad 0201 copper/paste/model, reduced 1.0x0.4mm courtyard; dense assembly requires qualification.');a.savefoot(dense)
qfn=a.std('Package_DFN_QFN','VQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm')
sc70=a.std('Package_TO_SOT_SMD','SOT-363_SC-70-6');sot23=a.std('Package_TO_SOT_SMD','SOT-23');sot236=a.std('Package_TO_SOT_SMD','SOT-23-6')
flash=a.std('Package_SO','SOIC-8_3.9x4.9mm_P1.27mm')
ind=a.custom('INDUCTOR_4x4_LowProfile_DRAFT',[(1,-1.55,0,1.3,3.4),(2,1.55,0,1.3,3.4)],4,4,1.8)
xtal=a.std('Crystal','Crystal_SMD_3225-4Pin_3.2x2.5mm')
def C(ref,value,nn,other='/GND',foot=c0402):return add(ref,value,foot,{'1':nn,'2':other})
def Rr(ref,value,nn,other='/GND',foot=r0201):return add(ref,value,foot,{'1':nn,'2':other},h=.3)
ar=json.loads((W/'ALPINE_RIDGE_PINOUT.json').read_text(encoding='utf-8'));pd=json.loads((W/'TPS65982_PINOUT.json').read_text(encoding='utf-8'))
am={q['ball']:nc('U501',q['ball']) for q in ar['pins']};ab={q['signal']:q['ball'] for q in ar['pins']}
pm={q['ball']:nc('U503',q['ball']) for q in pd['pins']};pb={q['signal']:q['ball'] for q in pd['pins']}
def A(sig,nn):am[ab[sig]]=nn
def P(sig,nn):pm[pb[sig]]=nn
for q in ar['pins']:
    sig=q['signal']
    if sig in ['VSS','VSS_ANA','SVR_VSS','TEST_EN','TEST_EDM','FUSE_VQPS_64','FUSE_VQPS_128']:am[q['ball']]='/GND'
    elif sig in ['VCC3P3_SX','VCC3P3_S0','VCC3P3_SVR','VCC3P3A']:am[q['ball']]='/P3V3_AUX'
    elif sig.startswith(('VCC0P9','VCC3P3')):am[q['ball']]='/TBT_'+sig
    elif sig=='SVR_IND':am[q['ball']]='/TBT_SVR_SW'
# Internally switched domain outputs remain separate; only the specified feedback
# pins connect to the external SVR output. Do not short the regulator outputs.
A('VCC0P9_SVR_SENSE','/TBT_VCC0P9_SVR');A('VCC0P9_LVR_SENSE','/TBT_VCC0P9_SVR')
for sig in ['TEST_PWR_GOOD','RBIAS','RSENSE','PCIE_RBIAS','DPSNK_RBIAS','DPSRC_RBIAS','PA_USB2_RBIAS','PB_USB2_RBIAS']:
    A(sig,'/TBT_'+sig)
for j,(sig,val) in enumerate([('TEST_PWR_GOOD','100R'),('RBIAS','4.75k 0.5%'),('RSENSE','4.75k 0.5%'),('PCIE_RBIAS','3.01k 1%'),('DPSNK_RBIAS','14k 1%'),('DPSRC_RBIAS','14k 1%'),('PA_USB2_RBIAS','499R 1%'),('PB_USB2_RBIAS','499R 1%')],5101):Rr('R'+str(j),val,'/TBT_'+sig)
for j,sig in enumerate(['DPSNK0_DDC_CLK','DPSNK0_DDC_DATA','DPSNK1_DDC_CLK','DPSNK1_DDC_DATA'],5111):A(sig,'/TBT_'+sig);Rr('R'+str(j),'100k','/TBT_'+sig)
for j,sig in enumerate(['POC_GPIO_2','POC_GPIO_3','POC_GPIO_4','POC_GPIO_5','POC_GPIO_6'],5121):A(sig,'/TBT_'+sig);Rr('R'+str(j),'10k / always-on host strap','/TBT_'+sig,'/P3V3_AUX')
A('PERST_N','/TBT_PCIE_PERST_3V3_N');A('RESET_N','/TBT_RESET_N')
A('POC_GPIO_0','/TBT_PD_IRQ_N');A('POC_GPIO_1','/TBT_UNUSED_PORTB_IRQ_N');Rr('R5128','10k','/TBT_UNUSED_PORTB_IRQ_N','/P3V3_AUX')
cpu=json.loads((O/'INTEL_288V_PINOUT.json').read_text(encoding='utf-8'))['pins'];cpu_by={q['signal'].split('/')[0]:q['ball'] for q in cpu}
capcount=0
def ac_pair(group,kind,source_ref,source_pins,target_ref,target_pins,layer,cap_value='100nF 16V'):
    global capcount
    for pol,sp,tp in zip('PN',source_pins,target_pins):
        capcount+=1;ref=f'C{5200+capcount}';na=f'/TBT_{group}_SRC_{pol}';nb=f'/TBT_{group}_DST_{pol}'
        if source_ref=='U501':am[sp]=na
        else:setpin(source_ref,sp,na)
        if target_ref=='U501':am[tp]=nb
        else:setpin(target_ref,tp,nb)
        add(ref,cap_value,cap,{'1':na,'2':nb},69,1.1+1.36*(capcount-1),'B',90,.33,fixed=True)
        connections.append(dict(group='TBT_'+group,kind=kind,nets=[na,nb],layer_index=layer,paired=True,cap=ref))
for lane in range(4):
    ac_pair(f'CPU_TX{lane}','TB3_PCIE', 'U502',[cpu_by[f'PCIE_{lane+1}_TX_{pol}'] for pol in 'PN'],'U501',[ab[f'PCIE_RX{lane}_{pol}'] for pol in 'PN'],19,'220nF 16V')
for lane in range(4):
    ac_pair(f'AR_TX{lane}','TB3_PCIE','U501',[ab[f'PCIE_TX{lane}_{pol}'] for pol in 'PN'],'U502',[cpu_by[f'PCIE_{lane+1}_RX_{pol}'] for pol in 'PN'],22,'220nF 16V')
for lane in range(4):
    ac_pair(f'DP_ML{lane}','TB3_DP','U502',[cpu_by[f'DDIA_TX_{pol}[{lane}]'] for pol in 'PN'],'U501',[ab[f'DPSNK0_ML{lane}_{pol}'] for pol in 'PN'],25)
# The controller's PA PHY changes direction for DisplayPort alternate modes;
# series capacitors on all four CIO pairs are a provisional topology choice.
for group,arpins,jpins,li in [('CIO_TX0',['PA_TX0_P','PA_TX0_N'],['A2','A3'],23),('CIO_TX1',['PA_TX1_P','PA_TX1_N'],['B2','B3'],24),('CIO_RX0',['PA_RX0_P','PA_RX0_N'],['B11','B10'],26),('CIO_RX1',['PA_RX1_P','PA_RX1_N'],['A11','A10'],27)]:
    ac_pair(group,'TB3_CIO','U501',[ab[z] for z in arpins],'J402',jpins,28)
assert capcount==32
def direct(group,kind,refs_pins,li):
    nets=[]
    for pol,rows in zip('PN',zip(*refs_pins)):
        nn=f'/TBT_{group}_{pol}';nets.append(nn)
        for ref,pin in rows:
            if ref=='U501':am[pin]=nn
            elif ref=='U503':pm[pin]=nn
            else:setpin(ref,pin,nn)
    connections.append(dict(group='TBT_'+group,kind=kind,nets=nets,layer_index=li,paired=True))
direct('DP_AUX','TB3_DP',[[('U502',cpu_by[f'DDIA_AUX_{pol}']) for pol in 'PN'],[('U501',ab[f'DPSNK0_AUX_{pol}']) for pol in 'PN']],29)
direct('REFCLK','TB3_REFCLK',[[('U602','25'),('U602','26')],[('U501',ab[f'PCIE_REFCLK_100_IN_{pol}']) for pol in 'PN']],30)
direct('PA_AUX','TB3_SIDEBAND',[[('U501',ab[f'PA_DPSRC_AUX_{pol}']) for pol in 'PN'],[('U503',pb[f'AUX_{pol}']) for pol in 'PN']],29)
direct('USB2_RP','TB3_USB2',[[('U501',ab[f'PA_USB2_D_{pol}']) for pol in 'PN'],[('U503',pb[f'USB_RP_{pol}']) for pol in 'PN']],30)
for group,ballpins,jpins,li in [('USB2_TOP',['K6','L6'],['A6','A7'],29),('USB2_BOTTOM',['K7','L7'],['B6','B7'],30)]:direct(group,'TB3_USB2',[[('U503',pn) for pn in ballpins],[('J402',pn) for pn in jpins]],li)
for sig,nn in [('C_CC1','CC1'),('C_CC2','CC2'),('C_SBU1','SBU1'),('C_SBU2','SBU2')]:P(sig,'/TBT_'+nn)
for pin,nn in [('A5','CC1'),('B5','CC2'),('A8','SBU1'),('B8','SBU2'),('A4','VBUS'),('A9','VBUS'),('B4','VBUS'),('B9','VBUS')]:setpin('J402',pin,'/TBT_'+nn)
for sig,nn in [('PA_LSRX','/TBT_LSX_P2R'),('PA_LSTX','/TBT_LSX_R2P'),('GPIO_0','/TBT_PD_I2C_SDA'),('GPIO_1','/TBT_PD_I2C_SCL'),('PA_DPSRC_HPD','/TBT_PD_HPD')]:A(sig,nn)
for sig,nn in [('LSX_P2R','/TBT_LSX_P2R'),('LSX_R2P','/TBT_LSX_R2P'),('I2C_SDA1','/TBT_PD_I2C_SDA'),('I2C_SCL1','/TBT_PD_I2C_SCL'),('I2C_IRQ1Z','/TBT_PD_IRQ_N'),('GPIO4','/TBT_PD_HPD')]:P(sig,nn)
for i,nn in enumerate(['PD_I2C_SDA','PD_I2C_SCL','PD_IRQ_N'],5131):Rr('R'+str(i),'10k','/TBT_'+nn,'/P3V3_AUX')
# Independent 3.3V flash supplies. The user's 1.8V JW flash is not substituted.
for ur,tag,supply in [('U504','AR','/TBT_VCC3P3_LC'),('U505','PD','/TBT_PD_LDO_3V3')]:
    fpm={'1':f'/TBT_{tag}_SPI_CS_N','2':f'/TBT_{tag}_SPI_MISO','3':f'/TBT_{tag}_FLASH_WP_N','4':'/GND','5':f'/TBT_{tag}_SPI_MOSI','6':f'/TBT_{tag}_SPI_CLK','7':supply,'8':supply}
    add(ur,'W25Q80DVSSIG / 3.3V 8Mbit NVM / image pending',flash,fpm,h=1.75,names={'1':'CS_N','2':'DO','3':'WP_N','4':'GND','5':'DI','6':'CLK','7':'HOLD_N','8':'VCC'})
    Rr('R'+('5141' if tag=='AR' else '5142'),'10k',fpm['1'],supply);Rr('R'+('5143' if tag=='AR' else '5144'),'10k',fpm['3'],supply)
    C('C'+('5101' if tag=='AR' else '5102'),'100nF',supply)
for sig,nn in [('EE_CS_N','SPI_CS_N'),('EE_CLK','SPI_CLK'),('EE_DI','SPI_MOSI'),('EE_DO','SPI_MISO'),('GPIO_2','FLASH_WP_N')]:A(sig,'/TBT_AR_'+nn)
for sig,nn in [('SPI_CSZ','SPI_CS_N'),('SPI_CLK','SPI_CLK'),('SPI_PICO','SPI_MOSI'),('SPI_POCI','SPI_MISO')]:P(sig,'/TBT_PD_'+nn)
for q in pd['pins']:
    sig=q['signal'];pin=q['ball']
    if sig in ['GND','PP_HV','RPD_G1','RPD_G2','HRESET']:pm[pin]='/GND'
    elif sig in ['PP_5V0','PP_CABLE']:pm[pin]='/TBT_5V0'
    elif sig in ['VBUS','SENSEN','SENSEP']:pm[pin]='/TBT_VBUS'
    elif sig=='VIN_3V3':pm[pin]='/P3V3_AUX'
    elif sig in ['LDO_3V3','VDDIO']:pm[pin]='/TBT_PD_LDO_3V3'
    elif sig in ['LDO_1V8D','LDO_1V8A','LDO_BMC','VOUT_3V3','SS']:pm[pin]='/TBT_PD_'+sig
for sig,nn in [('R_OSC','/TBT_PD_R_OSC'),('I2C_ADDR','/TBT_PD_I2C_ADDR'),('UART_TX','/TBT_PD_UART_LOOP'),('UART_RX','/TBT_PD_UART_LOOP'),('RESETZ','/TBT_PD_RESET_N'),('BUSPOWERZ','/TBT_PD_BUSPOWERZ'),('I2C_SDA2','/TBT_PD_I2C2_SDA'),('I2C_SCL2','/TBT_PD_I2C2_SCL')]:P(sig,nn)
Rr('R5151','15k 0.1%','/TBT_PD_R_OSC',foot=r0402);Rr('R5152','0R / I2C address strap','/TBT_PD_I2C_ADDR');Rr('R5153','100k','/TBT_PD_UART_LOOP');Rr('R5154','100k','/TBT_PD_BUSPOWERZ','/TBT_PD_LDO_3V3')
for j,nn in enumerate(['I2C2_SDA','I2C2_SCL'],5155):Rr('R'+str(j),'10k','/TBT_PD_'+nn,'/TBT_PD_LDO_3V3')
unused_gpio=['GPIO0','GPIO1','GPIO2','GPIO3','GPIO5','GPIO6','GPIO7','GPIO8','MRESET','DEBUG1','DEBUG2','DEBUG3','DEBUG4','DEBUG_CTL1','DEBUG_CTL2']
for j,sig in enumerate(unused_gpio,5161):P(sig,'/TBT_PD_UNUSED_'+sig);Rr('R'+str(j),'1M / firmware strap review','/TBT_PD_UNUSED_'+sig)
for j,(nn,val,fp) in enumerate([('VIN_3V3','10uF 6.3V',c0603),('LDO_3V3','10uF 6.3V',c0603),('LDO_1V8D','2.2uF 6.3V',c0402),('LDO_1V8A','2.2uF 6.3V',c0402),('LDO_BMC','2.2uF 6.3V',c0402),('VOUT_3V3','1uF 6.3V',c0402),('SS','220nF',c0402)],5110):
    C('C'+str(j),val,'/P3V3_AUX' if nn=='VIN_3V3' else '/TBT_PD_'+nn,foot=fp)
C('C5117','4.7uF 10V','/TBT_5V0',foot=c0603);C('C5118','2.2uF 25V / effective >=0.5uF at 5V required','/TBT_VBUS',foot=c0402)
C('C5119','330pF 25V','/TBT_CC1');C('C5120','330pF 25V','/TBT_CC2')
# AR internal regulator / distinct switched output domains.
add('L501','0.68uH / Isat >=2.5A @ <10% drop / select part',ind,{'1':'/TBT_SVR_SW','2':'/TBT_VCC0P9_SVR'},h=1.8)
rails=sorted({nn for nn in am.values() if nn.startswith('/TBT_VCC')})
for j,nn in enumerate(rails,5131):C('C'+str(j),'100nF 6.3V',nn)
C('C5151','22uF 6.3V / SVR output provisional','/TBT_VCC0P9_SVR',foot=c0603);C('C5152','4.7uF 6.3V','/P3V3_AUX',foot=c0603)
A('XTAL_25_IN','/TBT_XTAL_IN');A('XTAL_25_OUT','/TBT_XTAL_OUT')
add('Y501','25MHz / 20pF / 30ppm / ESR <=50R / select part',xtal,{'1':'/TBT_XTAL_IN','2':'/GND','3':'/TBT_XTAL_OUT','4':'/GND'},h=.8)
C('C5153','20pF C0G','/TBT_XTAL_IN');C('C5154','20pF C0G','/TBT_XTAL_OUT')
add('U510','TPS3808G33DBVR / AR reset delay',sot236,{'1':'/TBT_RESET_N','2':'/GND','3':'/TBT_PD_RESET_N','4':'/TBT_RESET_CT','5':'/P3V3_AUX','6':'/P3V3_AUX'},h=1.45)
Rr('R5181','10k','/TBT_RESET_N','/P3V3_AUX');C('C5155','10nF / approx 57.6ms','/TBT_RESET_CT');C('C5156','100nF','/P3V3_AUX')
add('U511','SN74AXC1T45DCKR / PERST 1.8V to 3.3V',sc70,{'1':'/CPU_VCCPRIM_1P8','2':'/GND','3':'/CPU_PERST_1V8_N','4':'/TBT_PCIE_PERST_3V3_N','5':'/CPU_VCCPRIM_1P8','6':'/P3V3_AUX'},h=1.1)
A('DPSNK0_HPD','/TBT_HPD_3V3');setpin('U502',cpu_by['GPP_E04'],'/TBT_HPD_1V8')
add('U512','SN74AXC1T45DCKR / HPDA 3.3V to 1.8V',sc70,{'1':'/CPU_VCCPRIM_1P8','2':'/GND','3':'/TBT_HPD_1V8','4':'/TBT_HPD_3V3','5':'/GND','6':'/P3V3_AUX'},h=1.1)
for j,nn in enumerate(['/CPU_VCCPRIM_1P8','/P3V3_AUX','/CPU_VCCPRIM_1P8','/P3V3_AUX'],5157):C('C'+str(j),'100nF',nn)
# Refclock remains continuously enabled; CLKREQ/WAKE/hotplug are exposed for
# platform integration rather than tying 3.3V outputs directly to CPU GPIO.
for j,sig in enumerate(['PCIE_CLKREQ_N','GPIO_4','GPIO_5'],5191):A(sig,'/TBT_'+sig);Rr('R'+str(j),'10k','/TBT_'+sig,'/P3V3_AUX')
add('U506','TPS62133RGTR / 12V to 5V 3A USB source',qfn,{'1':'/TBT_5V_SW','2':'/TBT_5V_SW','3':'/TBT_5V_SW','4':'/TBT_5V_PG','5':'/GND','6':'/GND','7':'/GND','8':'/GND','9':'/TBT_5V_SS','10':'/AUX_12V_PROTECTED','11':'/AUX_12V_PROTECTED','12':'/AUX_12V_PROTECTED','13':'/AUX_12V_PROTECTED','14':'/TBT_5V0','15':'/GND','16':'/GND','17':'/GND'},74,40.7,'F',0,1,fixed=True,url='https://www.ti.com/lit/ds/symlink/tps62133.pdf')
add('L502','2.2uH / >=4A / low profile / select part',ind,{'1':'/TBT_5V_SW','2':'/TBT_5V0'},79,40.7,'F',0,1.8,fixed=True)
C('C5161','10uF 25V','/AUX_12V_PROTECTED',foot=c0603);C('C5162','100nF 25V','/AUX_12V_PROTECTED');C('C5163','22uF 10V','/TBT_5V0',foot=c0603);C('C5164','3.3nF','/TBT_5V_SS');Rr('R5194','100k','/TBT_5V_PG','/TBT_5V0')
remove(b,b.FindFootprintByReference('U501'));meta.pop('U501')
bga('U501','DSL6540 / Alpine Ridge DP / TB3 HOST / NVM pending','ALPINE_RIDGE_DP_BGA337_MixedPitch_10p7x10p7',ar,am,75.1,11.9,180)
bga('U503','TPS65982 / Type-C DFP / 5V3A source / NVM pending','TI_TPS65982_BGA96_6x6_P0p5',pd,pm,76,35.2,0)
meta['J402'].update(value='THUNDERBOLT 3 HOST / VERTICAL SMT SHELL DRAFT',tb5_qualified=False,tb3_qualified=False)
b.FindFootprintByReference('J402').SetValue(meta['J402']['value'])
# Keep the sensitive analog parts near their controller, rather than letting
# a size-only packing pass place a crystal, bias or reset capacitor far away.
def localpart(ref,x,y,ang=0,side='B'):
    f=b.FindFootprintByReference(ref);assert f,ref
    if (f.GetLayer()==p.B_Cu)!=(side=='B'):f.Flip(f.GetPosition(),p.FLIP_DIRECTION_LEFT_RIGHT)
    f.SetOrientationDegrees(ang);f.SetPosition(v(x,y));fixednew.add(ref)
localpart('Y501',73.5,3);localpart('L501',78.75,3.05);localpart('C5151',74.85,5.55)
localpart('C5153',70.3,2.4);localpart('C5154',70.3,4.4)
for ref,x,y in [('R5101',70.25,1),('R5102',70.25,1.6),('R5103',70.25,3.35),('R5104',70.25,5.3),('R5105',70.25,5.95),('R5106',72,.9),('R5107',73.2,.9),('R5108',74.4,.9)]:localpart(ref,x,y)
for i in range(4):localpart(f'R{5111+i}',76.95+1.2*i,5.85)
localpart('U510',71.1,29.6,90)
for ref,x in [('U511',75),('U512',79)]:localpart(ref,x,28.8)
for ref,x,y in [('C5155',70.6,32.6),('R5181',73.45,31.6),('C5156',75,31),('C5157',77.2,31),('C5158',79.4,31),('C5159',80.8,33),('C5160',80.8,35)]:localpart(ref,x,y,90 if x>80 else 0)
for i in range(15):localpart(f'R{5161+i}',73.7+1.3*(i%5),39.25+1.05*(i//5))
for i,ref in enumerate(['R5151','R5152','R5153','R5154','R5155','R5156']):localpart(ref,70.6,33.7+1.05*i)
localpart('C5110',70.8,41);localpart('C5111',70.8,43)
for ref,x in [('C5112',73.8),('C5113',76),('C5114',78.2),('C5115',80.4)]:localpart(ref,x,43)
localpart('C5116',80.8,37,90)
for ref,x,y,ang in [('C5117',74,37.2,0),('C5163',79,37.2,0),('C5161',73,43.7,0),('C5162',76,43.7,0),('C5164',76.6,37.4,0),('R5194',76.325,40.7,90),('C5118',80.95,25.5,90),('C5119',81,28,90),('C5120',81,30.5,90)]:localpart(ref,x,y,ang,'F')
# Preserve all large devices and signal coupling caps. Repack the small support
# parts to make room for actual controllers, NVM and the 5V source stage.
fixed={}
fixedrefs={f'J{k}' for k in range(1,13)}|{'U1','U502','J401','J402','U601','U602','U701','F1','F2','U501','U503','U506','L502'}|{f'C{k}' for k in list(range(801,809))+list(range(811,819))+list(range(4001,4081))}|fixednew
for f in b.GetFootprints():
    if f.GetReference() in fixedrefs:fixed[f.GetReference()]={}
src=(STAGE/'scripts/revR/r_build.py').read_text(encoding='utf-8');src=src[src.index('def bounds(f):'):src.index('title=b.GetTitleBlock()')]
src=src.replace("'F':[(.6,.6,81.4,10.7),(.6,36.2,81.4,44.4),(.6,.6,81.4,44.4)]","'F':[(.6,36.2,81.4,44.4),(.6,.6,81.4,10.7),(.6,.6,81.4,44.4)]")
exec(compile(src,'TB3 support packing','exec'))
for q in ar['pins']:q['net']=am[q['ball']]
for q in pd['pins']:q['net']=pm[q['ball']]
(O/'ALPINE_RIDGE_PINOUT.json').write_text(json.dumps(ar,indent=2),encoding='utf-8');(O/'TPS65982_PINOUT.json').write_text(json.dumps(pd,indent=2),encoding='utf-8')
(O/'TB3_LINKS.json').write_text(json.dumps(connections,indent=2),encoding='utf-8')
reference=O/'references/Thunderbolt3';reference.mkdir(parents=True,exist_ok=True)
for fn in ['Alpine-Ridge DP Datasheet.pdf','Titan Ridge DD Datasheet.pdf','Universal Serial Bus 4.pdf']:shutil.copy2(Path('C:/Users/micro/Downloads')/fn,reference/fn)
for fn in ['TPS65982.pdf','TPS62133.pdf','SN74AXC1T45.pdf']:shutil.copy2(W/fn,reference/fn)
title=b.GetTitleBlock();title.SetTitle('82x45 / 10 E1.S / 288V 32GB / FAKE PEX90064 / TB3 HOST');title.SetRevision('T');title.SetDate('2026-10-16')
for t in b.GetDrawings():
    if isinstance(t,p.PCB_TEXT) and 'JHL9580' in t.GetText():t.SetText(t.GetText().replace('JHL9580','TB3 HOST'))
p.SaveBoard(str(bp),b);(folder/'COMPONENTS.json').write_text(json.dumps(list(meta.values()),ensure_ascii=False,indent=2),encoding='utf-8')
build=json.loads((O/'BUILD.json').read_text(encoding='utf-8'));build.update(revision='T',thunderbolt_generation=3,thunderbolt_role='HOST DFP to external devices',thunderbolt_controller='DSL6540 / Alpine Ridge DP reference',thunderbolt_ball_count=337,pd_controller='TPS65982',pd_ball_count=96,host_pcie='CPU PCIe1..4, Gen3 x4 negotiated',dp_input='CPU DDIA to DPSNK0',usb_source_max='5V / 3A provisional',actual_thunderbolt_nvm_loaded=False,thunderbolt_certified=False,added_components=len(newrefs),whole_board_routing_complete=False,electrical_design_complete=False,production_ready=False)
(O/'BUILD.json').write_text(json.dumps(build,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'TB3_STATUS.json').write_text(json.dumps(dict(host_role=True,port='J402 Port A',port_B_unused=True,ar_pinout_source='supplied Alpine-Ridge DP datasheet 2015',pd_pinout_source='TI SLVSD02E',lands_provisional=True,smtshell_connector_part_unverified=True,nvm_firmware_pending=True,BIOS_ACPI_GPIO_pinmux_pending=True,clock_request_and_wake_platform_integration_pending=True,esd_selection_pending=True,full_power_current_thermal_validation_pending=True,si_and_timing_validation_pending=True,external_5V_source_current_provisional_A=3),indent=2),encoding='utf-8')
print('Rev T:',len(meta),'footprints; real 337 + 96 ball maps; TB3 host topology, 32 AC caps, dual NVM and 5V source.',flush=True)
