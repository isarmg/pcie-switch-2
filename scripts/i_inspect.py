from pathlib import Path
import pcbnew as p,re,json
def children(s):
    out=[];d=0;q=False;e=False;a=None
    for i,c in enumerate(s):
        if e:e=False;continue
        if q and c=='\\':e=True;continue
        if c=='"':q=not q;continue
        if q:continue
        if c=='(':
            if d==1:a=i
            d+=1
        elif c==')':
            d-=1
            if d==1 and a is not None:out.append(s[a:i+1]);a=None
    return out
if __name__=='__main__':
    s=Path('C:/Program Files/KiCad/10.0/share/kicad/symbols/Connector.kicad_sym').read_text()
    sy=next(z for z in children(s) if z.startswith('(symbol "Bus_M.2_Socket_M"'))
    pins={}
    for part in children(sy):
        if not part.startswith('(symbol '):continue
        for z in children(part):
            if z.startswith('(pin '):pins[re.search(r'\(number "([^"]+)',z)[1]]=re.search(r'\(name "([^"]+)',z)[1]
    Path('work/revI/m2_pins.json').write_text(json.dumps(pins,indent=2));print(pins)
    f=p.FootprintLoad('C:/Program Files/KiCad/10.0/share/kicad/demos/cm5_minima/CM5IO.pretty','M.2 M Key socket')
    print('Demo pads',[(q.GetNumber(),p.ToMM(q.GetPosition().x),p.ToMM(q.GetPosition().y),p.ToMM(q.GetSize().x),p.ToMM(q.GetSize().y)) for q in f.Pads()][:12])
