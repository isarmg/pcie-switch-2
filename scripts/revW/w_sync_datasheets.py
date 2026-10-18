"""Preserve and synchronize existing manufacturer links in board/schematic/metadata.
No lookup, pin assignment, or electrical correctness is inferred from these URLs.
"""
import json,re
import pcbnew as p
from w_power_models import DESIGN
F=DESIGN
b=p.LoadBoard(str(F/'Main_12E1S.kicad_pcb'))
meta=json.loads((F/'COMPONENTS.json').read_text());byref={q['ref']:q for q in meta};urls={}
for f in b.GetFootprints():
    ref=f.GetReference();url=f.GetFieldText('Datasheet') or byref[ref].get('datasheet','')
    if url:
        urls[ref]=url;f.GetField('Datasheet').SetText(url);byref[ref]['datasheet']=url
for path in [F/'Local.kicad_sym',*F.glob('*.kicad_sch')]:
    text=path.read_text();lines=[]
    for line in text.splitlines(keepends=True):
        match=re.search(r'\(symbol "(?:Local:)?PART_([^"_]+)"',line)
        if not match and '(symbol (lib_id ' in line:match=re.search(r'\(property "Reference" "([^"]+)"',line)
        if match and match.group(1) in urls:
            url=urls[match.group(1)].replace('\\','\\\\').replace('"','\\"')
            if '(property "Datasheet" ' in line:
                line=re.sub(r'\(property "Datasheet" "[^"]*"',lambda _:f'(property "Datasheet" "{url}"',line)
            else:
                field=f'(property "Datasheet" "{url}" (at 0 0 0) (effects (font (size 1 1)) (hide yes)))'
                # Insert before existing property to keep the outer symbol scope.
                line=line.replace('(property "Reference"',field+'(property "Reference"',1)
        lines.append(line)
    path.write_text(''.join(lines))
(F/'COMPONENTS.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
p.SaveBoard(str(F/'Main_12E1S.kicad_pcb'),b)
print('Synchronized datasheet links:',len(urls))
