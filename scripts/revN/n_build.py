"""120x45 all-M.2 derivative; preserve all retained Rev M placements."""
from pathlib import Path
import sys,json,shutil,math,re,copy
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');STAGE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'scripts/revJ'))
import i_common as c
from i_common import *
S=R/'outputs/PCIe_Main_RevM';O=R/'outputs/PCIe_AllM2_RevN';c.ROOT=O;O.mkdir(parents=True,exist_ok=True)
folder=O/'Main_23M2';shutil.copytree(S/'Main_10E1S',folder,dirs_exist_ok=True)
shutil.copytree(S/'references',O/'references',dirs_exist_ok=True)
for fn in ['INTEL_268V_PINOUT.json','PEX88096_PINOUT.json','PEX88096_BALLS.csv','CPU_LINK_LENGTHS.json','CPU_PEX_LINK.json','CPU_POWER_DOMAINS.csv','CUSTOM_POWER_PINOUT.csv','USB_MOUNTING_STATUS.json']:
    shutil.copy2(S/fn,O/fn)
shutil.copy2(STAGE/'work/revN/TI_TPSM53604_SNVSBC9C.pdf',O/'references/TI_TPSM53604_SNVSBC9C.pdf')
bp=folder/'Main_23M2.kicad_pcb';shutil.copy2(folder/'Main_10E1S.kicad_pcb',bp)
pro=json.loads((folder/'Main_10E1S.kicad_pro').read_text(encoding='utf-8'));pro['meta']['filename']='Main_23M2.kicad_pro'
for fn in ['Main_10E1S.kicad_pcb','Main_10E1S.kicad_pro','Main_10E1S.kicad_sch','Main_10E1S.kicad_prl','Main_10E1S.step','DRC.json','ERC.json','CONNECTIVITY.net','PIN_MAP.csv','preview.png','bottom.png']:
    f=folder/fn
    if f.exists():f.unlink()
b=p.LoadBoard(str(bp));a=object.__new__(Board);a.name='Main_23M2';a.w=120;a.h=45;a.b=b;a.folder=folder;a.lib=folder/'Local.pretty';a.models=folder/'models';a.plugin=p.PCB_IO_MGR.FindPlugin(p.PCB_IO_MGR.KICAD_SEXP)
a.nets={q.GetNetname():q for q in b.GetNetInfo().NetsByNetcode().values()};a.cs=[];a.newrefs=[]
meta={q['ref']:q for q in json.loads((folder/'COMPONENTS.json').read_text(encoding='utf-8'))}
delete={f'J{i}' for i in range(1,11)}|{f'U{i}' for i in range(11,21)}|{f'C{i}' for i in range(101,131)}|{f'R{i}' for i in range(101,151)}
removed=[]
for f in list(b.GetFootprints()):
    if f.GetReference() in delete:removed.append(f.GetReference());meta.pop(f.GetReference());remove(b,f)
assert len(removed)==100,len(removed)
baseline={f.GetReference():{'position_mm':xy(f.GetPosition()),'rotation_deg':f.GetOrientationDegrees(),'layer':f.GetLayer()} for f in b.GetFootprints()}
for g in list(b.GetDrawings()):
    if g.GetLayer()==p.Edge_Cuts:remove(b,g)
    elif isinstance(g,p.PCB_TEXT) and ('E1.S' in g.GetText() or 'E1S' in g.GetText()):remove(b,g)
rect(b,0,0,120,45,p.Edge_Cuts)
for f in b.GetFootprints():
    for q in f.Pads():
        nn=q.GetNetname();m=re.fullmatch(r'/S(\d\d)_REFCLK0_([PN])',nn)
        if m:q.SetNet(a.net(f'/N{m[1]}_CLK_{m[2]}'))
        elif re.match(r'/S\d\d_',nn):q.SetNet(a.net(c.nc(f.GetReference(),q.GetNumber())))
for ref in ['J11','J12']:
    b.FindFootprintByReference(ref).SetValue('12V 25A FEED / DESIGN TARGET, COPPER AND CABLE TBD')
for ref in ['F1','F2']:b.FindFootprintByReference(ref).SetValue('25A FUSE / MPN AND THERMAL REVIEW TBD')
ports=json.loads((S/'M2_PORTS.json').read_text(encoding='utf-8'))
for row in ports:
    base={'M1':44,'M2':48,'M3':56,'M4':52}[row['port']];row['pex_lanes']=list(range(base,base+4))
foot='MKey_Vertical_Gen4_24p2x3p5_NoLocatingPegs_DRAFT'
template=next(q for q in meta.values() if q['ref']=='J501')
lane_starts=list(range(4,44,4))+list(range(60,96,4));assert len(lane_starts)==19
pex=b.FindFootprintByReference('U1');pex_pins={name:pin for pin,name in meta['U1']['pin_names'].items()}
pexpads={q.GetNumber():q for q in pex.Pads()}
new_modules=[];new_caps=[];new_small=[]
module=a.std('Package_DFN_QFN','Texas_B3QFN-14-1EP_5x5.5mm_P0.65mm')
c0805=a.std('Capacitor_SMD','C_0805_2012Metric');c1206=a.std('Capacitor_SMD','C_1206_3216Metric');c0402=a.std('Capacitor_SMD','C_0402_1005Metric');c0603=a.std('Capacitor_SMD','C_0603_1608Metric');r0402=a.std('Resistor_SMD','R_0402_1005Metric')
for k,start in enumerate(lane_starts,1):
    port=f'N{k:02}';ref=f'J{6000+k}';x=15.7+(k-1)*4.35;y=23.3
    pm={pin:nn.replace('/M1_',f'/{port}_').replace('(J501-',f'({ref}-') for pin,nn in template['pinmap'].items()}
    a.place(ref,f'{port} M-Key 2280 / x4 / NO-PEG DRAFT',foot,x,y,pm,'F',90,5.5)
    a.cs[-1].update(actual_orderable_part_verified=False,locating_pegs_removed_in_draft=True,physical_pin_numbering_verified=False)
    ports.append({'port':port,'ref':ref,'position_mm':[round(x,6),y],'rotation_deg':90,'side':'F','role':'NVMe SSD downstream x4','pex_lanes':list(range(start,start+4)),'rail':f'/{port}_3V3','design_output_budget_A':4,'no_locating_pegs_required':True,'physical_pin_numbering_verified':False,'pcie_gen4_channel_qualified':False})
    for lane in range(4):
        for direction in ['TX','RX']:
            for pol in 'PN':
                pin=pex_pins[f'{direction}{pol}[{start+lane}]'];pexpads[pin].SetNet(a.net(f'/{port}_{direction}{lane}_{pol}'))
    bank='/VBANK_A' if k<=10 else '/VBANK_B';reg=f'U{5000+k}'
    rp={'1':bank,'2':bank,'3':'/GND','4':c.nc(reg,'4'),'5':c.nc(reg,'5'),'6':c.nc(reg,'6'),'7':f'/{port}_3V3','8':f'/{port}_3V3','9':f'/{port}_FB','10':'/GND','11':'/GND','12':'/GND','13':c.nc(reg,'13'),'14':bank,'15':'/GND'}
    a.place(reg,'TPSM53604RDAR / 12V to 3.3V 4A RESERVATION',module,0,0,rp,'F',0,4.1,url='https://www.ti.com/lit/ds/symlink/tpsm53604.pdf',names={'1':'VIN','2':'EN','3':'NC','4':'DNC','5':'DNC','6':'PGOOD','7':'VOUT','8':'VOUT','9':'FB','10':'NC','11':'NC','12':'AGND','13':'V5V','14':'VIN','15':'PGND'})
    a.cs[-1]['pin_types']={str(i):('power_in' if i in [1,3,10,11,12,14,15] else 'power_out' if i in [7,8,13] else 'input' if i in [2,9] else 'open_collector' if i==6 else 'no_connect') for i in range(1,16)}
    a.cs[-1]['status']='4A design reservation, 52uF effective output minimum; power routing/thermal/DC-bias qualification incomplete'
    new_modules.append(reg)
    # TI's published input and feedback network; output capacitor budget is
    # deliberately generous but still subject to the actual DC-bias curves.
    for i,(val,fp,nn,height) in enumerate([
        ('10uF 50V / GRT31CR61H106ME01L',c1206,bank,1.8),('10uF 50V / GRT31CR61H106ME01L',c1206,bank,1.8),
        ('100nF 50V',c0402,bank,.55),
        *[('47uF 10V / GRM21BR61A476ME15L / DC-BIAS REVIEW',c0805,f'/{port}_3V3',1.45)]*4],1):
        rr=f'C{5000+k*20+i}';a.place(rr,val,fp,0,0,{'1':nn,'2':'/GND'},'F',0,height);new_caps.append(rr)
    for i,val,n1,n2 in [(1,'10k 1%',f'/{port}_3V3',f'/{port}_FB'),(2,'4.32k 1%',f'/{port}_FB','/GND'),(3,'10k',f'/{port}_3V3',f'/{port}_CLKREQ'),(4,'10k',f'/{port}_3V3',f'/{port}_WAKE'),(5,'100k / RESET HELD LOW, DRIVER PENDING',f'/{port}_PERST','/GND')]:
        rr=f'R{5000+k*10+i}';a.place(rr,val,r0402,0,0,{'1':n1,'2':n2},'F',0,.4);new_small.append(rr)
    for lane in range(4):
        for j,pol in enumerate('PN'):
            rr=f'C{6000+k*10+lane*2+j+1}';nn=f'/{port}_TX{lane}_{pol}'
            a.place(rr,'220nF 16V AC',c0402,0,0,{'1':nn,'2':nn+'_AC'},'F',0,.55);new_small.append(rr)

# Existing 16-output buffers retain their positions. Reuse the freed M5 output
# for N11 and add eight more outputs for N12..N19 from CPU CLKOUT3.
buf=b.FindFootprintByReference('U602')
for q in buf.Pads():
    if q.GetNumber() in ['39','40']:q.SetNet(a.net('/N11_CLK_'+('P' if q.GetNumber()=='39' else 'N')))
cpu=b.FindFootprintByReference('U502')
for q in cpu.Pads():
    sig=meta['U502']['pin_names'][q.GetNumber()]
    if sig in ['CLKOUT_P3','CLKOUT_N3']:q.SetNet(a.net('/CPU_CLKBUF3_IN_'+sig[7]))
bm=copy.deepcopy(meta['U601']);bpmap=dict(bm['pinmap']);clock_ref='U6501'
for pin,nn in list(bpmap.items()):
    if nn.startswith('unconnected-'):bpmap[pin]=c.nc(clock_ref,pin)
    elif nn.startswith('/CPU_CLKBUF1_IN_'):bpmap[pin]=nn.replace('CLKBUF1','CLKBUF3')
    elif nn=='/CLKBUF1_VDDA':bpmap[pin]='/CLKBUF3_VDDA'
for k,(pp,pn) in enumerate([(13,14),(16,17),(21,22),(25,26),(28,29),(32,33),(35,36),(39,40)],12):
    bpmap[str(pp)]=f'/N{k:02}_CLK_P';bpmap[str(pn)]=f'/N{k:02}_CLK_N'
a.place(clock_ref,'9ZXL0851EKILFT / N12-N19 CLOCK, ICC CONFIG PENDING',bm['footprint'],115.1,23.3,bpmap,'B',0,bm.get('height_mm',1),names=bm.get('pin_names',{}))
clock_fixed=clock_ref
for i in range(10):
    rr=f'C{6501+i}';a.place(rr,'100nF',c0402,0,0,{'1':'/P3V3_AUX','2':'/GND'},'F',0,.55);new_small.append(rr)
for rr,val,fp,nn,h in [('C6511','4.7uF 10V',c0603,'/P3V3_AUX',.9),('C6512','1uF 10V',c0603,'/CLKBUF3_VDDA',.9)]:
    a.place(rr,val,fp,0,0,{'1':nn,'2':'/GND'},'F',0,h);new_caps.append(rr)
a.place('R6501','0R / AVDD FILTER REVIEW',r0402,0,0,{'1':'/P3V3_AUX','2':'/CLKBUF3_VDDA'},'F',0,.4);new_small.append('R6501')
for q in a.cs:meta[q['ref']]=q
allrefs=[f.GetReference() for f in b.GetFootprints()];assert len(allrefs)==len(set(allrefs)),'duplicate refs'

# Conservative placement of only the added circuitry. All retained Rev M
# footprints stay fixed. This does not claim completed power-loop routing.
def bounds(f):
    bb=f.GetBoundingBox(False,False);return tuple(p.ToMM(z) for z in [bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom()])
step=.05;margin=.01;nx=2401;ny=901;occ={'F':[0]*ny,'B':[0]*ny};allbits=(1<<nx)-1
def raster(bb):
    x0,y0,x1,y1=bb
    return max(0,math.floor((x0-margin)/step)),max(0,math.floor((y0-margin)/step)),min(nx-1,math.ceil((x1+margin)/step)),min(ny-1,math.ceil((y1+margin)/step))
def reserve(bb,side):
    x0,y0,x1,y1=raster(bb);mask=((1<<(x1-x0+1))-1)<<x0
    for y in range(y0,y1+1):occ[side][y]|=mask
def free(bb,side):
    x0,y0,x1,y1=raster(bb);mask=((1<<(x1-x0+1))-1)<<x0
    return not any(occ[side][y]&mask for y in range(y0,y1+1))
movable=set(new_modules+new_caps+new_small)
for f in b.GetFootprints():
    if f.GetReference() not in movable:
        side='B' if f.GetLayer()==p.B_Cu else 'F';reserve(bounds(f),side)
        if side=='B':
            for q in f.Pads():
                if q.GetAttribute() in [p.PAD_ATTRIB_NPTH,p.PAD_ATTRIB_PTH]:
                    xx,yy=xy(q.GetPosition());rr=max(p.ToMM(q.GetDrillSize().x),p.ToMM(q.GetDrillSize().y))/2+.35;reserve((xx-rr,yy-rr,xx+rr,yy+rr),'F')
def pack(refs,sides):
    fs=[b.FindFootprintByReference(r) for r in refs];fs.sort(key=lambda f:-(bounds(f)[2]-bounds(f)[0])*(bounds(f)[3]-bounds(f)[1]))
    for f in fs:
        found=None;f.SetPosition(v(0,0))
        for side in sides:
            if (f.GetLayer()==p.B_Cu)!=(side=='B'):f.Flip(v(0,0),p.FLIP_DIRECTION_LEFT_RIGHT)
            for rot in [0,90]:
                f.SetOrientationDegrees(rot);bb=bounds(f);ww=bb[2]-bb[0];hh=bb[3]-bb[1]
                # Prefer the bottom power strip and the added right-hand area.
                regions=[(14.0,35.8,95.0,44.2),(110.0,.6,119.4,44.4),(.6,.6,119.4,44.4)] if side=='F' else [(110,.6,119.4,44.4),(.6,.6,119.4,44.4)]
                for x0,y0,x1,y1 in regions:
                    first=math.ceil(x0/step);last=math.floor((x1-ww)/step)
                    if last<first:continue
                    allowed=((1<<(last-first+1))-1)<<(first-1)
                    width=math.ceil((ww+margin)/step)+2
                    for iy in range(math.ceil(y0/step),math.floor((y1-hh)/step)+1):
                        yy=iy*step;blocked=0
                        yr0=max(0,iy-1);yr1=min(ny-1,iy+math.ceil((hh+margin)/step))
                        for row in occ[side][yr0:yr1+1]:blocked|=row
                        starts=(~blocked)&allbits;span=1
                        while span*2<=width:starts&=starts>>span;span*=2
                        if width>span:starts&=starts>>(width-span)
                        candidates=starts&allowed
                        while candidates:
                            bit=candidates&-candidates;ix=bit.bit_length();xx=ix*step
                            trial=(xx,yy,xx+ww,yy+hh)
                            if free(trial,side):found=(xx-bb[0],yy-bb[1],trial,side);break
                            candidates^=bit
                        if found:break
                    if found:break
                if found:break
            if found:break
        if not found:
            debug=R/'work/revN';debug.mkdir(parents=True,exist_ok=True)
            p.SaveBoard(str(debug/'Placement_partial.kicad_pcb'),b)
            print('Free rectangle area by side:',{s:round((nx*ny-sum(z.bit_count() for z in rows))*step*step,2) for s,rows in occ.items()},flush=True)
            raise AssertionError(('cannot place',f.GetReference(),ww,hh))
        f.SetPosition(v(*found[:2]));reserve(found[2],found[3])
    print('Packed',len(refs),'parts; free area',{s:round((nx*ny-sum(z.bit_count() for z in rows))*step*step,2) for s,rows in occ.items()},flush=True)
pack(new_modules,['F','B']);pack(new_caps,['F','B']);pack(new_small,['B','F'])
for ref,base in baseline.items():
    f=b.FindFootprintByReference(ref)
    assert xy(f.GetPosition())==tuple(base['position_mm']) and f.GetLayer()==base['layer'] and f.GetOrientationDegrees()==base['rotation_deg'],('retained placement moved',ref)
for f in b.GetFootprints():
    e=meta[f.GetReference()];e.update(x=xy(f.GetPosition())[0],y=xy(f.GetPosition())[1],side='B' if f.GetLayer()==p.B_Cu else 'F',rotation_deg=f.GetOrientationDegrees(),pinmap={q.GetNumber():q.GetNetname() for q in f.Pads() if q.GetNumber()},value=f.GetValue(),footprint=str(f.GetFPID().GetLibItemName()))
for z in list(b.Zones()):remove(b,z)
for i in range(12,31,2):a.zone('/GND',getattr(p,f'In{i}_Cu'),[(.4,.4),(119.6,.4),(119.6,44.6),(.4,44.6)])
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(bp),b)
(folder/'Main_23M2.kicad_pro').write_text(json.dumps(pro,indent=2),encoding='utf-8')
(folder/'COMPONENTS.json').write_text(json.dumps(list(meta.values()),ensure_ascii=False,indent=2),encoding='utf-8')
(O/'M2_PORTS.json').write_text(json.dumps(ports,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'CORE_PLACEMENT_BASELINE.json').write_text(json.dumps(baseline,indent=2),encoding='utf-8')
(O/'POWER_BUDGET.json').write_text(json.dumps({'input_V':12,'ssd_slots':23,'per_slot_V':3.3,'per_slot_A':4,'total_ssd_output_W':303.6,'total_ssd_output_A':92,'assumed_conversion_efficiency_for_budget':.85,'ssd_input_W_budget':round(303.6/.85,2),'platform_reserve_W':85,'input_current_A_budget':round((303.6/.85+85)/12,2),'input_design_target_A':50,'input_feeds_A':[25,25],'new_module':'TPSM53604RDAR x19','existing_end_slot_regulators':'TPS565201 x4','input_copper_cable_fuse_thermal_qualified':False,'output_capacitance_effective_min_uF':52,'output_capacitors_nominal_uF_per_new_regulator':188,'dc_bias_and_thermal_qualified':False},indent=2),encoding='utf-8')
(O/'BUILD.json').write_text(json.dumps({'revision':'N','main_mm':[120,45],'boards':1,'daughter_boards':0,'e1s_slots':0,'m2_slots':23,'m2_no_peg_draft':True,'retained_geometry_matches_RevM':True,'new_central_m2_pitch_mm':4.35,'data_lanes':96,'host_lanes':[0,1,2,3],'downstream_x4_ports':23,'port_firmware_configured':False,'cpu_bga_balls':2833,'pex_bga_balls':1550,'cpu_pmic_implemented':False,'production_ready':False},indent=2),encoding='utf-8')
(folder/'ROUTING_STATUS.json').write_text(json.dumps({'cpu_x4_and_refclock_copper_connections':34,'slot_data_net_assignments_complete':True,'slot_copper_routing_complete':False,'power_loop_routing_complete':False,'impedance_validated':False,'thermal_qualified':False,'whole_board_state':'placement and net-assignment draft; only retained CPU link has copper routing','production_ready':False},indent=2),encoding='utf-8')
print('120x45 all-M.2 derivative: 23 x4 slots, 19 new 4A power modules; all retained placements unchanged.',flush=True)
