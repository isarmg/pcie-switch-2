from pathlib import Path
import json,html
from PIL import Image,ImageDraw,ImageFont
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_USB12mm_RevW';m={q['ref']:q for q in json.loads((O/'Main_12E1S/COMPONENTS.json').read_text(encoding='utf-8'))}
im=Image.new('RGB',(1120,830),'#fafbfc');dr=ImageDraw.Draw(im);parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="830" viewBox="0 0 1120 830"><rect width="1120" height="830" fill="#fafbfc"/>']
def coord(x,y):return (60+x*10,100+y*10)
def rect(x,y,w,h,fill,stroke='#345643'):
 xx,yy=coord(x,y);dr.rectangle((xx,yy,xx+w*10,yy+h*10),fill=fill,outline=stroke,width=2);parts.append(f'<rect x="{xx}" y="{yy}" width="{w*10}" height="{h*10}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
def text(x,y,s,size=20,fill='#213d4b',center=False):
 xx,yy=coord(x,y);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',size);box=dr.textbbox((0,0),s,font=font);width=box[2]-box[0];dr.text((xx-width/2 if center else xx,yy),s,font=font,fill=fill);anchor='middle' if center else 'start';parts.append(f'<text x="{xx}" y="{yy+size}" font-family="Microsoft YaHei,sans-serif" font-size="{size}" fill="{fill}" text-anchor="{anchor}">{html.escape(s)}</text>')
def line(x1,y1,x2,y2,fill='#6596b0',width=2):
 a=coord(x1,y1);b=coord(x2,y2);dr.line((a,b),fill=fill,width=width);parts.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{fill}" stroke-width="{width}"/>')
rect(0,0,96,45,'#e7eee9')
for ref,w,h,color,label in [('U1',33,33,'#9a7447','虚构 PEX90064'),('U502',27,27.5,'#577a89','Ultra 9 288V / 32GB'),('U501',10.7,10.7,'#70a694','雷电 3'),('U503',6,6,'#70a694','PD')]:
 x=96-m[ref]['x'];y=m[ref]['y'];rect(x-w/2,y-h/2,w,h,color,'#ffffff');text(x,y-1,label,15 if w<20 else 20,'#ffffff',True)
for ref,label in [('J401','供电 USB-C'),('J402','雷电 USB-C')]:
 x=96-m[ref]['x'];y=m[ref]['y'];rect(x-2,y-4,4,8,'#1c729c');line(x-1,y,x+1,y,'#ffffff');line(x,y-1,x,y+1,'#ffffff');text(x,y+5,label,17,'#17475e',True);line(x,y,x,55)
line(0,35,0,55)
for x1,x2,y in [(0,12,49),(12,24,53.5)]:
 line(x1,y,x2,y,'#165c83',3);line(x1,y,x1+.8,y-.5,'#165c83');line(x1,y,x1+.8,y+.5,'#165c83');line(x2,y,x2-.8,y-.5,'#165c83');line(x2,y,x2-.8,y+.5,'#165c83');text((x1+x2)/2,y-2.5,'12 mm',22,'#165c83',True)
text(0,-7,'CPU / switch 面：左侧接口 · 中部 CPU · 右侧 switch',26)
text(79,-3.4,'96 × 45 mm',19)
text(0,59,'尺寸按封装中心测量；两个 USB-C 的中心均位于板高 22.5 mm。',19,'#435966')
text(0,63,'USB-C 竖直安装、贴片固定脚。辅助器件及完整铜线见 KiCad 工程。',18,'#435966')
text(0,67,'接口电路沿用已选的雷电 3 方案；本图只示出主要器件和位置尺寸。',17,'#697b83')
parts.append('</svg>');(O/'USB_12mm_CPU_Switch_View.svg').write_text('\n'.join(parts),encoding='utf-8');im.save(O/'USB_12mm_CPU_Switch_View.png')
print('Saved CPU/switch face dimension diagram',flush=True)
