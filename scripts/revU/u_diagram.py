from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_12slot_RevU'
S=2;im=Image.new('RGB',(1900*S,1080*S),'#f8fafc');dr=ImageDraw.Draw(im)
font=lambda size:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',size*S)
def text(x,y,s,size=24,color='#102c3d'):dr.text((x*S,y*S),s,font=font(size),fill=color)
def line(pts,color='#183c4d',w=2):dr.line([(x*S,y*S) for x,y in pts],fill=color,width=w*S)
def rect(z,fill,outline,w=1):dr.rectangle(tuple(q*S for q in z),fill=fill,outline=outline,width=w*S)
def xy(x,y):return (120+15*x,180+15*y)
def dimension(a,b,label,vertical=False):
    line([a,b]);dx,dy=(0,1) if vertical else (1,0)
    for p,sign in [(a,1),(b,-1)]:
        base=(p[0]+sign*dx*8,p[1]+sign*dy*8)
        dr.polygon([(p[0]*S,p[1]*S),((base[0]-dy*4)*S,(base[1]+dx*4)*S),((base[0]+dy*4)*S,(base[1]-dx*4)*S)],fill='#183c4d')
    x,y=(a[0]+b[0])/2,(a[1]+b[1])/2
    text(x+12 if vertical else x-45,y-16 if vertical else y-36,label,23)
text(80,30,'96 × 45 mm · 12 个竖直 E1.S · 名义侧边距 7.25 mm',36)
text(80,92,'从 E1.S 面正视：浅色矩形为插入后硬盘的投影，正式 STEP 不包含硬盘模型。',23,'#526b76')
rect([*xy(0,0),*xy(96,45)],'#d6ebe2','#1b5e47',3)
ports=sorted(json.loads((O/'E1S_PORTS.json').read_text()),key=lambda q:q['position_mm'][0])
for i,q in enumerate(ports):
    x,y=q['position_mm'];rect([*xy(x-2.95,6.25),*xy(x+2.95,37.75)],'#e9f0f5','#769bb3',2)
    # Samtec footprint body/courtyard are off-center to its origin.
    rect([*xy(x-1.7,14.0),*xy(x+1.7,39.1)],'#425058','#29393e',2)
    xx,yy=xy(x,26.54);line([(xx-14,yy),(xx+14,yy)],'#ffdd82',2);line([(xx,yy-10),(xx,yy+10)],'#ffdd82',2)
    text(*xy(x-1.9,9.0),str(i+1),21)
    text(*xy(x-2.1,40.5),q['ref'],17)
line([xy(0,37.75),xy(101,37.75)],'#be513a',2);line([xy(96,45),xy(101,45)],'#be513a',2)
dimension(xy(100,37.75),xy(100,45),'7.25 mm',True)
line([xy(0,0),xy(0,-2.5)]);line([xy(96,0),xy(96,-2.5)]);dimension(xy(0,-2),xy(96,-2),'96 mm')
line([xy(0,0),xy(-3,0)]);line([xy(0,45),xy(-3,45)]);dimension(xy(-2.5,0),xy(-2.5,45),'45 mm',True)
text(120,895,'插槽原点 Y = 26.54 mm；硬盘下侧边 Y = 37.75 mm；PCB 底边 Y = 45.00 mm。',25)
text(120,943,'硬盘另一侧名义余量 6.25 mm；槽距 8 mm；适用于 31.5 mm 侧宽、5.9 mm 厚度的 E1.S 包络。',23)
text(120,991,'7.25 mm 为名义几何尺寸，未计连接器、硬盘及装配公差。布局/布线草案，非可生产设计。',22,'#8a4533')
im.resize((1900,1080),Image.Resampling.LANCZOS).save(O/'Mechanical_7p25mm.png')
print(O/'Mechanical_7p25mm.png')
