from i_common import *
for n in ['Left_2M2_Vertical','Right_M2_Upstream']:
    file=R/'work/revI'/f'{n}.placed.kicad_pcb';b=p.LoadBoard(str(file));right=n.startswith('Right');csfile=ROOT/n/'COMPONENTS.json';cs=json.loads(csfile.read_text())
    for c in cs:
        f=b.FindFootprintByReference(c['ref'])
        if re.fullmatch(r'C[123]02',c['ref']):f.Move(v(0,.7));f.SetOrientationDegrees(0)
        if re.fullmatch(r'C[123]01',c['ref']):f.Move(v(0,1.3))
        if right and re.fullmatch(r'J1(0[1-9]|1[0-8])',c['ref']):f.SetPosition(v(1.4,1.3+2*(int(c['ref'][1:])-101)))
        c['x'],c['y']=xy(f.GetPosition())
        if 'Twinax_' in str(f.GetFPID().GetLibItemName()):
            for g in list(f.GraphicalItems()):
                if g.GetLayer()==p.B_CrtYd:remove(f,g)
            x,y=xy(f.GetPosition());rect(f,x-.95,y-.975,x+.95,y+.975,p.B_CrtYd)
    if right:
        for t in b.GetDrawings():
            if isinstance(t,p.PCB_TEXT) and '12V IN' in t.GetText():t.SetPosition(v(24,34.8))
    p.SaveBoard(str(file),b);csfile.write_text(json.dumps(cs,indent=2))
print('Adjusted buck clearances and right launch positions to remain inside the keyed board outline.')
