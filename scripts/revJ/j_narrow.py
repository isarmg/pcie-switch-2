from i_common import *

def narrow(a, ports, left):
    a.w=19.5;a.b.SetCopperLayerCount(24)
    for t in list(a.b.GetTracks()):remove(a.b,t)
    for z in list(a.b.Zones()):remove(a.b,z)
    for g in list(a.b.GetDrawings()):remove(a.b,g)
    rect(a.b,0,0,19.5,45,p.Edge_Cuts)
    # Amphenol customer drawing CMDT350X0X001VT rev. 2 (2018-05-18).
    # 0.5 mm same-row pitch; M-key omissions 59..66. Pin indexing follows
    # the M.2 card convention; manufacturer drawing does not print pin numbers.
    foot='Amphenol_MDT350M01001VT_MKey_Vertical_Gen4'
    pads=[(str(n),9.5-n*.25,1.3125 if n%2 else -1.3125,.3,1.375) for n in range(1,76) if n not in range(59,67)]
    pads += [('MP1',-11.45,.55,1.2,2.75),('MP2',11.45,.55,1.2,2.75)]
    a.custom(foot,pads,24.2,3.5,5.5)
    f=p.FootprintLoad(str(a.lib),foot)
    for x,dia in [(-10,1.6),(10,1.1)]:
        q=p.PAD(f);q.SetNumber('');q.SetPosition(v(x,0));q.SetSize(v(dia,dia));q.SetDrillSize(v(dia,dia));q.SetShape(p.PAD_SHAPE_CIRCLE);q.SetAttribute(p.PAD_ATTRIB_NPTH);q.SetLayerSet(layers(p.F_Cu,p.B_Cu,p.F_Mask,p.B_Mask));f.Add(q)
    a.savefoot(f)
    for idx,k in enumerate(ports):
        old=a.b.FindFootprintByReference(f'J{k}');pm={q.GetNumber():q.GetNetname() for q in old.Pads() if q.GetNumber()};remove(a.b,old)
        a.cs=[c for c in a.cs if c['ref']!=f'J{k}'];x=3.55+idx*6.2
        a.place(f'J{k}',('HOST UPSTREAM / ' if (not left and k==4) else f'M{k} SSD / ')+'MDT350M01001VT Gen4',foot,x,17,pm,'F',90,5.5,'https://www.amphenol-cs.com/product/mdt350m01001vt.html')
        # AC capacitors occupy the clear strip below the vertical sockets.
        for j in range(8):
            c=a.b.FindFootprintByReference(f'C{k*100+20+j}');c.SetPosition(v(x,32+j*1.4));c.SetOrientationDegrees(0)
        for j in range(2):
            c=a.b.FindFootprintByReference(f'R{k*100+10+j}')
            if c:c.SetPosition(v(*[[(2.2,2.8),(4.5,2.8)],[(5.7,1.4),(13.8,1.4)],[(15,2.8),(17.3,2.8)]][idx][j]));c.SetOrientationDegrees(0)
        a.text('UP' if not left and k==4 else f'M{k}',x,4,size=.6)
    # Three compact, independent 12V -> 3.3V buck cells on the underside.
    # Keep the original 5A-rated TPS565201 and 4A/slot design-load target.
    ssds=[k for k in ports if left or k!=4]
    for idx,k in enumerate(ssds):
        cell=idx if left else [0,2][idx];cy=[11.5,21.2,35.6][cell];inputy=[15.8,25,40][cell]
        outputs=[[(3.8,3),(3.8,16.5)],[(10,3),(3.8,30)],[(3.8,41),(10,43)]][cell]
        coords={f'U{20+k}':(10,cy),f'L{k}':(3.8,cy),f'C{k*100+1}':(9.5,inputy),f'C{k*100+2}':(12.5,inputy),f'C{k*100+3}':(9.8,cy-2.6),f'C{k*100+4}':outputs[0],f'C{k*100+5}':outputs[1],f'C{k*100+6}':(12.4,cy-3.5),f'R{k*100+1}':(13,cy+2),f'R{k*100+2}':(13,cy)}
        for ref,(xx,yy) in coords.items():a.b.FindFootprintByReference(ref).SetPosition(v(xx if left else 19.5-xx,yy))
    # 18 launches in the outer bank and 9 in the inner bank; all soldered twinax.
    for i in range(27):
        x=(18.15 if i<18 else 15.75) if left else (1.35 if i<18 else 3.75)
        y=2+2.3*i if i<18 else [3,10,13.8,17.6,21.4,24,30,34.8,39.6][i-18]
        a.b.FindFootprintByReference(f'J{101+i}').SetPosition(v(x,y))
    # Power and control wiring exits on the top surface, outside the socket bodies.
    for ref,pt in [('J50',(9.75,1.75)),('J51',(9.75,44.0))]:
        f=a.b.FindFootprintByReference(ref)
        if f.GetLayer()==p.B_Cu:f.Flip(f.GetPosition(),p.FLIP_DIRECTION_LEFT_RIGHT)
        f.SetOrientationDegrees(0);f.SetPosition(v(*pt))
    a.text('GEN4 / 3 x4',9.75,30.4,size=.65)
    if not left:a.b.FindFootprintByReference('TP1').SetPosition(v(17.5,30.5))
    rules=a.pro['board']['design_settings']['rules'];rules.update(min_via_diameter=.3,min_through_hole_diameter=.1,min_via_annular_width=.075)
    a.pro['board']['design_settings']['allow_blind_buried_vias']=True

def main_launches(a):
    # The old auxiliary supply occupies the left edge interior: new pairs use
    # the narrow free corridor between that supply and the fictional BGA body.
    pts=[(19.3,y) for y in [9,22,24.5,27,29.5,32,34.5,37,39.5]]
    for side in ['L','R']:
        for i,(x,y) in enumerate(pts):
            f=a.b.FindFootprintByReference(f'J{119+i if side=="L" else 219+i}')
            f.SetPosition(v(x if side=='L' else 80-x,y))
    # Labels belong in the documentation layer; avoid signal-launch soldermask.
    for g in a.b.GetDrawings():
        if isinstance(g,p.PCB_TEXT) and g.GetLayer()==p.B_SilkS and ('L:' in g.GetText() or 'R:' in g.GetText()):g.SetLayer(p.Dwgs_User)
