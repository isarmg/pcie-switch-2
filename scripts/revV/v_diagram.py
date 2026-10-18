from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import math
O=Path('C:/Users/micro/Desktop/方案/pcie switch 2/outputs/PCIe_E1S_96x45_12VPower_RevV')
im=Image.new('RGB',(1600,960),'#f5f7fa');d=ImageDraw.Draw(im)
font='C:/Windows/Fonts/msyh.ttc'
def f(n):return ImageFont.truetype(font,n)
def text(x,y,s,n=25,color='#182d47'):d.text((x,y),s,font=f(n),fill=color,spacing=9)
def box(x,y,w,h,title,sub,color='#d9e9fa'):
    d.rounded_rectangle((x,y,x+w,y+h),14,fill=color,outline='#92aac4',width=2);text(x+18,y+15,title,28);text(x+18,y+61,sub,22)
def arrow(a,z,color='#3b6b99'):
    d.line([a,z],fill=color,width=4);ang=math.atan2(z[1]-a[1],z[0]-a[0]);d.polygon([z,(z[0]-15*math.cos(ang-.45),z[1]-15*math.sin(ang-.45)),(z[0]-15*math.cos(ang+.45),z[1]-15*math.sin(ang+.45))],fill=color)
text(55,35,'Rev V  |  12 V 输入与已画供电范围',40)
text(55,98,'96 × 45 mm · 12 × E1.S · 每槽 25 W · 高度与插槽位置保持',25)
box(55,180,300,140,'稳压 12 V 输入','同一电源，两组正负线\nJ101 / J102 · 各 20 A 预算')
box(430,160,380,150,'F1 / F2：25 A 保险丝','每组 TVS + 独立 12 V 铜面\nIn5：A 组；In6：B 组')
box(890,160,635,150,'12 路 TPS259470A 槽位保护','每路名义限流 3.03 A · UV 10.332 V / OV 13.44 V\nA：S01–S05、S11；B：S06–S10、S12')
arrow((355,250),(430,250));arrow((810,235),(890,235))
box(890,360,635,135,'12 × E1.S 电源脚','每槽 12 V / 25 W 预算 · 总计 300 W / 25 A','#dff1e7');arrow((1210,310),(1210,360))
box(430,375,380,130,'U30：辅助支路 eFuse','750 Ω · 名义限流 4.45 A');arrow((620,310),(620,375))
box(430,555,380,130,'U31 / TPS62132','3.3 V · IC 上限 3 A\n时钟、槽位辅助及控制器输入');arrow((560,505),(560,555))
box(890,555,635,130,'U506 / TPS62133 → TPS65982 → J402','5 V · IC 上限 3 A\n雷电口 VBUS；实际外供须完成 PD 固件等验证');arrow((810,445),(850,445));arrow((850,445),(850,620));arrow((850,620),(890,620))
box(55,555,300,130,'J401 自定义 USB-C','保留触点分配\n与主电源母线隔离','#eee8dc')
box(55,750,1470,135,'未实现：CPU 动态 VR / 虚构 switch 核心供电 / 整机启动时序','本图表示已画范围。铜厚、过孔、载流、热、制造与高速信号均未核准；不能据此直接生产或上电。','#f5e2dc')
im.save(O/'Power_12V_Overview.png');print('Saved power overview')
