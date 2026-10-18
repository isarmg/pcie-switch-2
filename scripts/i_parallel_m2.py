from i_common import *
for name in ['Left_2M2_Vertical','Right_M2_Upstream']:
    file=R/'work/revI'/f'{name}.placed.kicad_pcb';b=p.LoadBoard(str(file));csfile=ROOT/name/'COMPONENTS.json';cs=json.loads(csfile.read_text());right=name.startswith('Right')
    for k in ([3] if right else [1,2]):
        f=b.FindFootprintByReference(f'J{k}');center=f.GetPosition();angle=f.GetOrientationDegrees()
        if abs(angle-90)<.01:continue
        refs=[f'J{k}']+[f'C{k*100+20+i}' for i in range(8)]+[f'R{k*100+10+i}' for i in range(2)]
        for ref in refs:
            q=b.FindFootprintByReference(ref);q.Rotate(center,p.EDA_ANGLE(90,p.DEGREES_T))
            if right:q.Move(v(0,4))
        for t in b.GetDrawings():
            if isinstance(t,p.PCB_TEXT) and t.GetText().startswith(f'M{k} /'):t.SetText(f'M{k} / PARALLEL E1.S');t.SetPosition(v(14 if k==1 else 38 if k==2 else 26,3.5));t.SetTextSize(v(.6,.6))
    for c in cs:
        f=b.FindFootprintByReference(c['ref']);c['x'],c['y']=xy(f.GetPosition());c['rotation_deg']=f.GetOrientationDegrees()
    p.SaveBoard(str(file),b);csfile.write_text(json.dumps(cs,indent=2))
info=json.loads((ROOT/'BUILD.json').read_text());info['m2_planes']='YZ, perpendicular to carrier XY, parallel to main E1.S slots';(ROOT/'BUILD.json').write_text(json.dumps(info,indent=2))
print('All three M.2 sockets now rotated 90 degrees in PCB plane, parallel to E1.S slots.')
