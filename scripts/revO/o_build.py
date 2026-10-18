"""Dense 120x45 derivative: 23 x4 ports plus four power-only upright M.2."""
from pathlib import Path
import sys,json,shutil,math,re,copy
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');STAGE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'scripts/revJ'))
import i_common as c
from i_common import *
S=R/'outputs/PCIe_AllM2_RevN';O=R/'outputs/PCIe_AllM2_RevO';c.ROOT=O;O.mkdir(parents=True,exist_ok=True)
folder=O/'Main_27M2';shutil.copytree(S/'Main_23M2',folder,dirs_exist_ok=True)
shutil.copytree(S/'references',O/'references',dirs_exist_ok=True)
for fn in ['INTEL_268V_PINOUT.json','PEX88096_PINOUT.json','PEX88096_BALLS.csv','CPU_LINK_LENGTHS.json','CPU_PEX_LINK.json','CPU_POWER_DOMAINS.csv','CUSTOM_POWER_PINOUT.csv','USB_MOUNTING_STATUS.json']:
    shutil.copy2(S/fn,O/fn)
bp=folder/'Main_27M2.kicad_pcb';shutil.copy2(folder/'Main_23M2.kicad_pcb',bp)
pro=json.loads((folder/'Main_23M2.kicad_pro').read_text(encoding='utf-8'));pro['meta']['filename']='Main_27M2.kicad_pro'
for fn in ['Main_23M2.kicad_pcb','Main_23M2.kicad_pro','Main_23M2.kicad_sch','Main_23M2.kicad_prl','Main_23M2.step','DRC.json','ERC.json','CONNECTIVITY.net','PIN_MAP.csv','preview.png','bottom.png']:
    f=folder/fn
    if f.exists():f.unlink()
b=p.LoadBoard(str(bp));a=object.__new__(Board);a.name='Main_27M2';a.w=120;a.h=45;a.b=b;a.folder=folder;a.lib=folder/'Local.pretty';a.models=folder/'models';a.plugin=p.PCB_IO_MGR.FindPlugin(p.PCB_IO_MGR.KICAD_SEXP)
a.nets={q.GetNetname():q for q in b.GetNetInfo().NetsByNetcode().values()};a.cs=[];a.newrefs=[]
meta={q['ref']:q for q in json.loads((folder/'COMPONENTS.json').read_text(encoding='utf-8'))}
# Three 47 uF capacitors reserve 141 uF nominal per module; qualification
# still requires at least 52 uF effective under bias and temperature.
for k in range(1,20):
    ref=f'C{5000+k*20+7}';remove(b,b.FindFootprintByReference(ref));meta.pop(ref)
ports=sorted(json.loads((S/'M2_PORTS.json').read_text(encoding='utf-8')),key=lambda q:q['position_mm'][0])
for i,row in enumerate(ports):
    xx=3.45+i*4.35;f=b.FindFootprintByReference(row['ref']);f.SetPosition(v(xx,23.3));row.update(position_mm=[round(xx,6),23.3],protocol_routed=False,power_only=False)
foot='MKey_Vertical_Gen4_24p2x3p5_NoLocatingPegs_DRAFT';template=meta['J501']
module=a.std('Package_DFN_QFN','Texas_B3QFN-14-1EP_5x5.5mm_P0.65mm')
c0805=a.std('Capacitor_SMD','C_0805_2012Metric');c1206=a.std('Capacitor_SMD','C_1206_3216Metric');c0402=a.std('Capacitor_SMD','C_0402_1005Metric');r0402=a.std('Resistor_SMD','R_0402_1005Metric')
new_modules=[];new_caps=[];new_small=[]
for k in range(1,5):
    port=f'P{k:02}';ref=f'J{7000+k}';xx=3.45+(22+k)*4.35
    pm={pin:('/GND' if nn=='/GND' else f'/{port}_3V3' if nn=='/M1_3V3' else c.nc(ref,pin)) for pin,nn in template['pinmap'].items()}
    a.place(ref,f'{port} M-Key 2280 / POWER ONLY / NO-PEG DRAFT',foot,xx,23.3,pm,'F',90,5.5)
    a.cs[-1].update(actual_orderable_part_verified=False,locating_pegs_removed_in_draft=True,physical_pin_numbering_verified=False,power_only=True)
    ports.append({'port':port,'ref':ref,'position_mm':[round(xx,6),23.3],'rotation_deg':90,'side':'F','role':'POWER ONLY; all protocol and sideband pads NC','pex_lanes':[],'rail':f'/{port}_3V3','design_output_budget_A':4,'no_locating_pegs_required':True,'physical_pin_numbering_verified':False,'pcie_gen4_channel_qualified':False,'power_only':True,'protocol_routed':False})
    reg=f'U{7000+k}';bank='/VBANK_B'
    rp={'1':bank,'2':bank,'3':'/GND','4':c.nc(reg,'4'),'5':c.nc(reg,'5'),'6':c.nc(reg,'6'),'7':f'/{port}_3V3','8':f'/{port}_3V3','9':f'/{port}_FB','10':'/GND','11':'/GND','12':'/GND','13':c.nc(reg,'13'),'14':bank,'15':'/GND'}
    a.place(reg,'TPSM53604RDAR / POWER-ONLY SLOT 3.3V 4A',module,0,0,rp,'F',0,4.1,url='https://www.ti.com/lit/ds/symlink/tpsm53604.pdf',names={'1':'VIN','2':'EN','3':'NC','4':'DNC','5':'DNC','6':'PGOOD','7':'VOUT','8':'VOUT','9':'FB','10':'NC','11':'NC','12':'AGND','13':'V5V','14':'VIN','15':'PGND'})
    a.cs[-1]['pin_types']={str(i):('power_in' if i in [1,12,14,15] else 'power_out' if i in [7,13] else 'input' if i in [2,9] else 'open_collector' if i==6 else 'no_connect' if i in [4,5] else 'passive') for i in range(1,16)}
    new_modules.append(reg)
    for i,(val,fp,nn,height) in enumerate([
        ('10uF 50V / GRT31CR61H106ME01L',c1206,bank,1.8),('10uF 50V / GRT31CR61H106ME01L',c1206,bank,1.8),('100nF 50V',c0402,bank,.55),
        *[('47uF 10V / GRM21BR61A476ME15L / DC-BIAS REVIEW',c0805,f'/{port}_3V3',1.45)]*3],1):
        rr=f'C{7000+k*20+i}';a.place(rr,val,fp,0,0,{'1':nn,'2':'/GND'},'F',0,height);new_caps.append(rr)
    for i,val,n1,n2 in [(1,'10k 1%',f'/{port}_3V3',f'/{port}_FB'),(2,'4.32k 1%',f'/{port}_FB','/GND')]:
        rr=f'R{7000+k*10+i}';a.place(rr,val,r0402,0,0,{'1':n1,'2':n2},'F',0,.4);new_small.append(rr)
for q in a.cs:meta[q['ref']]=q
# Dense 0201 passives free the strips around the connector row. Keep 12 V
# input bypass capacitors at 0402/50 V; the PCIe AC capacitors stay 220 nF/16 V.
c0201=a.std('Capacitor_SMD','C_0201_0603Metric');r0201=a.std('Resistor_SMD','R_0201_0603Metric')
compact=[]
for ref,e in meta.items():
    isac=ref.startswith('C') and 6000<int(ref[1:])<6200 and e['value'].startswith('220nF')
    isr=ref.startswith('R') and 5000<int(ref[1:])<7000
    if not (isac or isr):continue
    old=b.FindFootprintByReference(ref);new=p.FootprintLoad(str(a.lib),c0201 if isac else r0201);b.Add(new)
    new.SetFPID(p.LIB_ID('Local',c0201 if isac else r0201));new.SetReference(ref);new.SetValue('220nF 16V / GRM033R61C224KE14D' if isac else old.GetValue());new.Reference().SetVisible(False);new.Value().SetVisible(False)
    for q in new.Pads():
        if q.GetNumber():q.SetNet(a.net(e['pinmap'][q.GetNumber()]))
    remove(b,old);e['height_mm']=.33 if isac else .3
    if isac:e['datasheet']='https://www.murata.com/-/media/webrenewal/tool/library/common-pdf/dynamic-model/component-list-d-mlcc-2504.ashx?cvid=20250523010405000000&la=en'
    compact.append(ref)
oldfixed=set(json.loads((S/'CORE_PLACEMENT_BASELINE.json').read_text(encoding='utf-8')))-{q['ref'] for q in ports}
fixed=oldfixed|{'U6501'}
baseline={f.GetReference():{'position_mm':xy(f.GetPosition()),'rotation_deg':f.GetOrientationDegrees(),'layer':f.GetLayer()} for f in b.GetFootprints() if f.GetReference() in fixed}
assert len(baseline)==274,len(baseline)
# Repack only the added power/passive circuits; fixed platform parts stay put.
for ref in meta:
    if ref in fixed or any(ref==q['ref'] for q in ports) or ref in new_modules+new_caps+new_small:continue
    if re.fullmatch(r'U50\d\d',ref):new_modules.append(ref)
    elif ref.startswith('C'):
        f=b.FindFootprintByReference(ref);bb=f.GetBoundingBox(False,False)
        (new_caps if p.ToMM(bb.GetWidth())*p.ToMM(bb.GetHeight())>2 else new_small).append(ref)
    else:new_small.append(ref)
src=(STAGE/'scripts/revN/n_build.py').read_text(encoding='utf-8')
src=src[src.index('def bounds(f):'):src.index('for ref,base in baseline.items():')]
src=src.replace("regions=[(14.0,35.8,95.0,44.2)","regions=[(90.0,.6,119.4,10.3),(14.0,35.8,119.4,44.2)")
src=src.replace("pack(new_modules,['F','B'])","pack(new_modules,['B','F'])").replace('work/revN','work/revO')
src=src.replace("pack(new_small,['B','F'])",'''step=.025;margin=0;nx=4801;ny=1801;occ={'F':[0]*ny,'B':[0]*ny};allbits=(1<<nx)-1
for f in b.GetFootprints():
    if f.GetReference() in new_small:continue
    side='B' if f.GetLayer()==p.B_Cu else 'F';reserve(bounds(f),side)
    if side=='B':
        for q in f.Pads():
            if q.GetAttribute() in [p.PAD_ATTRIB_NPTH,p.PAD_ATTRIB_PTH]:
                xx,yy=xy(q.GetPosition());rr=max(p.ToMM(q.GetDrillSize().x),p.ToMM(q.GetDrillSize().y))/2+.35;reserve((xx-rr,yy-rr,xx+rr,yy+rr),'F')
pack(new_small,['B','F'])''')
exec(compile(src,str(__file__)+' placement','exec'))
for ref,base in baseline.items():
    f=b.FindFootprintByReference(ref)
    assert xy(f.GetPosition())==tuple(base['position_mm']) and f.GetLayer()==base['layer'] and f.GetOrientationDegrees()==base['rotation_deg'],ref
# Native stock 3D model is unavailable on this installation; show a documented
# closed 5 x 5.5 x 4.1 mm module envelope instead of omitting the devices.
for f in b.GetFootprints():
    if f.GetValue().startswith('TPSM53604') and not list(f.Models()):a.model(f,'TPSM53604_5x5p5x4p1_ENVELOPE',5,5.5,4.1)
    e=meta[f.GetReference()];e.update(x=xy(f.GetPosition())[0],y=xy(f.GetPosition())[1],side='B' if f.GetLayer()==p.B_Cu else 'F',rotation_deg=f.GetOrientationDegrees(),pinmap={q.GetNumber():q.GetNetname() for q in f.Pads() if q.GetNumber()},value=f.GetValue(),footprint=str(f.GetFPID().GetLibItemName()))
for t in b.GetDrawings():
    if isinstance(t,p.PCB_TEXT):t.SetText(t.GetText().replace('REV N','REV O').replace('23 UPRIGHT','27 UPRIGHT'))
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(bp),b)
(folder/'Main_27M2.kicad_pro').write_text(json.dumps(pro,indent=2),encoding='utf-8')
(folder/'COMPONENTS.json').write_text(json.dumps(list(meta.values()),ensure_ascii=False,indent=2),encoding='utf-8')
(O/'M2_PORTS.json').write_text(json.dumps(ports,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'CORE_PLACEMENT_BASELINE.json').write_text(json.dumps(baseline,indent=2),encoding='utf-8')
power=json.loads((S/'POWER_BUDGET.json').read_text(encoding='utf-8'));power.update(ssd_slots=27,total_ssd_output_W=356.4,total_ssd_output_A=108,ssd_input_W_budget=round(356.4/.85,2),input_current_A_budget=round((356.4/.85+85)/12,2),new_module='TPSM53604RDAR x23',power_only_slots=4,power_only_output_W=52.8,output_capacitors_nominal_uF_per_new_regulator=141)
(O/'POWER_BUDGET.json').write_text(json.dumps(power,indent=2),encoding='utf-8')
build=json.loads((S/'BUILD.json').read_text(encoding='utf-8'));build.update(revision='O',m2_slots=27,power_only_slots=4,data_m2_slots=23,retained_geometry_matches_RevM=False,retained_platform_footprints=274,uniform_m2_pitch_mm=4.35,connector_row_envelope_mm=[1.275,11.025,118.725,35.575],connector_face_single_parallel_row_capacity=27)
(O/'BUILD.json').write_text(json.dumps(build,indent=2),encoding='utf-8')
sources=json.loads((O/'references/SOURCES.json').read_text(encoding='utf-8'))
import hashlib
if not any(q.get('file')=='TI_TPSM53604_SNVSBC9C.pdf' for q in sources):sources.append({'file':'TI_TPSM53604_SNVSBC9C.pdf','url':'https://www.ti.com/lit/ds/symlink/tpsm53604.pdf','sha256':hashlib.sha256((O/'references/TI_TPSM53604_SNVSBC9C.pdf').read_bytes()).hexdigest(),'role':'Official TI 4A module datasheet; pin map, package and capacitor/feedback requirements'})
(O/'references/SOURCES.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
print('Built 27 upright slots: 23 x4 and four power only; 274 platform footprints fixed.',flush=True)
print('Dense 0201 passive packages:',len(compact),flush=True)
