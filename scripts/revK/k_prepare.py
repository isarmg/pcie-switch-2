from pathlib import Path
from collections import defaultdict, Counter
import json, re, math, csv, sys

sys.stdout.reconfigure(encoding='utf-8')
W = Path(__file__).resolve().parents[2] / 'work/revK'
pages = json.loads((W / 'pdf_priority/Broadcom_PEX88096.json').read_text(encoding='utf-8'))
rows = list('ABCDEFGHJKLMNPRTUVWY') + ['A'+x for x in 'ABCDEFGHJKLMNPRTUVWY'] + ['BA','BB']
text = '\n'.join(pages[113:156]).split('Table 45:',1)[1].split('Package Skew Data',1)[0]
text = re.sub(r'SYS_PWR_ON_RST_\s+N', 'SYS_PWR_ON_RST_N', text)
ballmap = {}
for m in re.finditer(r'\b([A-Z]{1,2})([1-9][0-9]?)\s*([A-Za-z_][A-Za-z_0-9]*(?:\[\d+\])?)', text):
    row, col, signal = m.groups()
    if row in rows and int(col) <= 37:
        ball = row+col
        assert ball not in ballmap or ballmap[ball] == signal
        ballmap[ball] = signal
expected = {r+str(c) for r in rows for c in range(1,38)} - {'A1','A37','BB1','BB37'}
assert set(ballmap) == expected and len(ballmap) == 1550
compact44 = re.sub(r'\s+', '', '\n'.join(pages[71:114]).split('Table 45:',1)[0])
compact44 = compact44.replace('SYS_PWR_ON_RST_N','SYS_PWR_ON_RST_N')
not_in_44 = [(b,s) for b,s in ballmap.items() if s+b not in compact44]
assert not not_in_44, not_in_44

def read_records(f):
    return [dict(x.split('=',1) for x in line.split('|') if '=' in x)
            for line in f.read_text(encoding='utf-8',errors='replace').splitlines()]

source = next((W/'altium_source').rglob('*AIC*.pcbdoc'))
records = defaultdict(list)
for row in read_records(source):
    records[row.get('RECORD','?')].append(row)
components = {c['ID']:c for c in records['Component']}
nets = {n['ID']:n['NAME'] for n in records['Net']}
meta = {}
for sheet in source.parent.rglob('*.schdoc'):
    current = None
    for r in read_records(sheet):
        if r.get('RECORD') == '1':
            current = {'part':r.get('LIBREFERENCE',''), 'sheet':sheet.name,
                       'description':r.get('%UTF8%COMPONENTDESCRIPTION',''), 'pins':{}}
        elif current is not None and r.get('RECORD') == '34' and r.get('NAME') == 'Designator':
            current['ref']=r.get('TEXT');meta[current['ref']]=current
        elif current is not None and r.get('RECORD') == '41' and r.get('NAME') == 'Comment':
            current['value']=r.get('TEXT','')
        elif current is not None and r.get('RECORD') == '2':
            current['pins'][r.get('DESIGNATOR','')] = r.get('NAME','')

def mm(s): return float(s.removesuffix('mil'))*.0254
parts = {}
for cid, c in components.items():
    ref = c.get('SOURCEDESIGNATOR', 'REF'+cid)
    part = dict(meta.get(ref,{}), ref=ref, pattern=c['PATTERN'], source_component_id=cid,
                source_rotation=float(c['ROTATION']), source_layer=c['LAYER'])
    part['pads'] = []
    for q in records['Pad']:
        if q.get('COMPONENT') != cid: continue
        part['pads'].append({'number':q['NAME'],'x':round(mm(q['X'])-mm(c['X']),6),
            'y':round(-mm(q['Y'])+mm(c['Y']),6),'width':mm(q.get('XSIZE',q.get('TOPXSIZE','0mil'))),
            'height':mm(q.get('YSIZE',q.get('TOPYSIZE','0mil'))),'shape':q.get('SHAPE',q.get('TOPSHAPE','ROUND')),
            'rotation':float(q.get('ROTATION','0')), 'layer':q['LAYER'],
            'hole':mm(q.get('HOLESIZE','0mil')), 'plated':q.get('PLATED','TRUE')=='TRUE',
            'net':nets.get(q.get('NET'),'')})
    parts[ref]=part
pex = parts['U2']
assert {q['number'] for q in pex['pads']} == expected
assert all(abs(q['width']-.48)<.001 and abs(q['height']-.48)<.001 for q in pex['pads'])
# Independent package orientation check: reverse the source's 270-degree placement.
for q in pex['pads']:
    m = re.fullmatch(r'([A-Z]+)(\d+)',q['number']);row,col=m.groups()
    localx = int(col)-19; localy=rows.index(row)-20.5
    assert abs(q['x']+localy)<.002 and abs(q['y']-localx)<.002, q['number']
    sig = ballmap[q['number']]
    if sig=='VSS': assert q['net']=='GND'
    elif sig=='VDD': assert q['net']=='P0V9'
    elif sig=='VDDA': assert q['net']=='P0V9A'
    elif sig in ['VDD1x','VDD1xA','VDD18','VDD18A']: assert q['net'] in ['P1V8','P1V8A']

ball_records=[]
for b,s in ballmap.items():
    m=re.fullmatch(r'([A-Z]+)(\d+)',b);r,c=m.groups()
    ball_records.append({'ball':b,'signal':s,'x_mm':int(c)-19,'y_mm':rows.index(r)-20.5})
out={'ball_count':1550,'rows':rows,'columns':37,'pitch_mm':1.0,'pad_diameter_mm':.48,
     'package_mm':[37.5,42.5,2.92], 'ball_records':ball_records,
     'checks':{'table44_vs_table45':True,'cad_ball_set':True,'cad_grid_orientation':True,
               'cad_power_ground_groups':True},
     'power_group_counts':dict(Counter(s for s in ballmap.values() if s.startswith('V'))),
     'source_pdf':'Broadcom_PEX88096_Data Sheet_V2_4 (1).pdf', 'source_pages':[71,72,156]}
(W/'PEX88096_PINOUT.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
(W/'REFERENCE_PARTS.json').write_text(json.dumps(parts,ensure_ascii=False,indent=2),encoding='utf-8')
with (W/'PEX88096_BALLS.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=['ball','signal','x_mm','y_mm']);writer.writeheader();writer.writerows(ball_records)
print('Verified 1550 balls against both datasheet tables and the Altium pad grid/power groups.')
print('Reference components extracted:',len(parts))
print('Key parts:',[(ref,p.get('part')) for ref,p in parts.items() if any(x in p.get('part','') for x in ['9ZXL','9FGV','9DML','TPS','TCA','W25'])])
