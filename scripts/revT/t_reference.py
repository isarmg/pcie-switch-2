"""Transcribe supplied Alpine Ridge and TI TPS65982 package data for KiCad."""
from pathlib import Path
import json,re,urllib.request
W=Path(__file__).resolve().parents[2]/'work/revT'
a=json.loads((W/'Alpine-Ridge DP Datasheet_PAGES.json').read_text(encoding='utf-8'))
text='\n'.join(a[35:41]).replace('V CC0P9_ANA_PCIE_2','VCC0P9_ANA_PCIE_2')
pins=dict(re.findall(r'\b([A-Z]{1,2}\d{1,2})\s+([A-Z][A-Z0-9_]*)\b',text))
assert len(pins)==337,len(pins)
rows='A B C D E F G H J K L M N P R T U V W Y AA AB AC'.split()
inner=[4,5,6,8,9,11,12,13,15,16,18,19,20]
records=[]
for ball,sig in pins.items():
    rr,cc=re.fullmatch(r'([A-Z]+)(\d+)',ball).groups();ri=rows.index(rr)+1;ci=int(cc)
    outer=ri in [1,2,22,23] or ci in [1,2,22,23]
    if outer:x,y=(ci-12)*.46,(ri-12)*.46
    else:x,y=(inner.index(ci)-6)*.65,(inner.index(ri)-6)*.65
    records.append(dict(ball=ball,signal=sig,x_mm=round(x,3),y_mm=round(y,3),region='0.46mm outer rings' if outer else '0.65mm inner array'))
assert sum(q['region'].startswith('0.46') for q in records)==168
ar=dict(part='Alpine Ridge DP / DSL6540 reference',balls=337,body_mm=[10.7,10.7],height_mm_max=.889,land_diameter_mm_provisional=.23,source='User-supplied Alpine-Ridge DP Datasheet.pdf',source_pages=[36,37,38,39,40,41,42,635,636],manufacturer_view='TOP VIEW A1 upper-left',host_mode=True,pins=records)
(W/'ALPINE_RIDGE_PINOUT.json').write_text(json.dumps(ar,indent=2),encoding='utf-8')
pdrows={
'A':'GND LDO_1V8D SPI_CLK SPI_POCI I2C_SDA2 PP_HV PP_HV PP_HV HV_GATE2 SENSEN PP_5V0'.split(),
'B':'VDDIO GPIO0 SPI_CSZ SPI_PICO I2C_SCL2 I2C_IRQ2Z PP_HV GND HV_GATE1 SENSEP PP_5V0'.split(),
'C':{1:'I2C_IRQ1Z',2:'GPIO1',10:'GPIO4',11:'PP_5V0'},
'D':{1:'I2C_SDA1',2:'I2C_SCL1',5:'DEBUG_CTL2',6:'HRESET',7:'GPIO7',8:'GND',10:'GPIO2',11:'PP_5V0'},
'E':{1:'LDO_BMC',2:'UART_TX',4:'DEBUG_CTL1',5:'GND',6:'GND',7:'GND',8:'GND',10:'GPIO5',11:'MRESET'},
'F':{1:'I2C_ADDR',2:'UART_RX',4:'SWD_DATA',5:'GND',6:'GND',7:'GND',8:'GND',10:'BUSPOWERZ',11:'RESETZ'},
'G':{1:'LDO_3V3',2:'R_OSC',4:'SWD_CLK',5:'GND',6:'GND',7:'GND',8:'GND',10:'GPIO6',11:'GPIO3'},
'H':{1:'VIN_3V3',2:'VOUT_3V3',4:'GND',5:'GND',6:'GPIO8',7:'SS',8:'GND',10:'PP_CABLE',11:'VBUS'},
'J':{1:'AUX_P',2:'AUX_N',10:'VBUS',11:'VBUS'},
'K':'LDO_1V8A DEBUG2 DEBUG4 LSX_P2R USB_RP_N C_USB_TP C_USB_BP C_SBU1 RPD_G1 RPD_G2 VBUS'.split(),
'L':'GND DEBUG1 DEBUG3 LSX_R2P USB_RP_P C_USB_TN C_USB_BN C_SBU2 C_CC1 C_CC2 NC'.split()}
records=[]
for ri,(rr,vals) in enumerate(pdrows.items()):
    for ci,sig in (enumerate(vals,1) if isinstance(vals,list) else vals.items()):records.append(dict(ball=f'{rr}{ci}',signal=sig,x_mm=(ci-6)*.5,y_mm=(ri-5)*.5))
assert len(records)==96
pd=dict(part='TPS65982ABZBHR',balls=96,body_mm=[6,6],height_mm_max=1,land_diameter_mm_provisional=.27,source='TI TPS65982 SLVSD02E Rev E',source_url='https://www.ti.com/lit/ds/symlink/tps65982.pdf',source_pages=[5,6,7,8,9,10,91,113,114,115,116,117],pins=records)
(W/'TPS65982_PINOUT.json').write_text(json.dumps(pd,indent=2),encoding='utf-8')
for name,url in [('TPS62133','https://www.ti.com/lit/ds/symlink/tps62133.pdf'),('SN74AXC1T45','https://www.ti.com/lit/ds/symlink/sn74axc1t45.pdf')]:
    path=W/(name+'.pdf')
    if not path.exists():urllib.request.urlretrieve(url,path)
print('337 Alpine Ridge balls / 96 TPS65982 balls transcribed; mixed-pitch coordinates checked.')
