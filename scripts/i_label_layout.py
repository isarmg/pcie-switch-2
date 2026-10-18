from pathlib import Path
import re
from i_inspect import children
root=Path(__file__).resolve().parents[1]/'outputs/PCIe_3board_RevI'
count=0
for path in root.glob('*/Connectivity_*.kicad_sch'):
    text=path.read_text(encoding='utf8')
    if '(comment 2 "Label placement revised")' in text:continue
    for part in children(text):
        if not part.startswith('(global_label '):continue
        m=re.search(r'\(at ([^ )]+) ([^ )]+) (0|180)\)',part);left=m[3]=='0';new=part.replace(m[0],f'(at {m[1]} {m[2]} {180 if left else 0})').replace('(justify left)' if left else '(justify right)','(justify right)' if left else '(justify left)');text=text.replace(part,new,1);count+=1
    text=text.replace('(rev "I")','(rev "I") (comment 2 "Label placement revised")',1);path.write_text(text,encoding='utf8')
print('Moved',count,'global labels outward, preserving every pin attachment and UUID.')
