from pathlib import Path
import sys,json
from pypdf import PdfReader
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');W=Path(__file__).resolve().parents[2]/'work/revW';W.mkdir(parents=True,exist_ok=True)
src=R/'outputs/PCIe_E1S_96x45_12VPower_RevV/references/Thunderbolt3/Alpine-Ridge DP Datasheet.pdf'
reader=PdfReader(src);pages=[p.extract_text(extraction_mode='layout') or '' for p in reader.pages];(W/'alpine.txt').write_text('\n'.join(f'\n=== PAGE {i+1} ===\n{s}' for i,s in enumerate(pages)),encoding='utf-8')
for i,s in enumerate(pages):
    if any(q in s for q in ['Power Delivery','Power Rails','Power Tree','VCC0P9_SVR','VCC3P3_LC','Internal Voltage']):
        print('PAGE',i+1,':',s[:240].replace('\n',' '))
d=json.loads((R/'work/revL/intel_tables.json').read_text(encoding='utf-8'))['829568-001_Electrical_Specification.xlsx']['Power_Rail_DC_Specifications']
for i,r in enumerate(d):
    if any(str(q).strip() in ['VCCRTC','VCCPRIM_1P8','VCCPRIM_3P3','V1P8U_MEM','VCCPRIM_VNNAON','VCCPRIM_VNNAONLV','VCCPRIM_IO'] for q in r):print('CPU',i,[q for q in r if q is not None])
