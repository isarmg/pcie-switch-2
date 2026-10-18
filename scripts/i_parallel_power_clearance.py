from i_common import *
for name in ['Left_2M2_Vertical','Right_M2_Upstream']:
    file=R/'work/revI'/f'{name}.placed.kicad_pcb';b=p.LoadBoard(str(file));csfile=ROOT/name/'COMPONENTS.json';cs=json.loads(csfile.read_text())
    if name.startswith('Left'):
        for ref,x in [('C106',14),('C206',38)]:b.FindFootprintByReference(ref).SetPosition(v(x,22))
    else:
        u=b.FindFootprintByReference('U23');dx,dy=14-xy(u.GetPosition())[0],26-xy(u.GetPosition())[1]
        for ref in ['U23','L3']+[f'C{301+i}' for i in range(5)]+['R301','R302']:b.FindFootprintByReference(ref).Move(v(dx,dy))
    for c in cs:c['x'],c['y']=xy(b.FindFootprintByReference(c['ref']).GetPosition())
    p.SaveBoard(str(file),b);csfile.write_text(json.dumps(cs,indent=2))
print('Power components cleared from rotated M.2 through-via fanouts.')
