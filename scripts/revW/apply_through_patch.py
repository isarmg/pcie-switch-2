"""Append only verified GND via UUIDs to a board; no footprint/route/zone edits.
Run using standard Python. Refill and re-run DRC and all-pad audit afterwards.
Via-in-pad and blind-via fabrication are unqualified design assumptions.
"""
from pathlib import Path
import argparse,json
p=argparse.ArgumentParser();p.add_argument('board',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).parent
text=a.board.read_text();ids={r['uuid'] for r in json.loads((root/'through-two.json').read_text())};assert not any(x in text for x in ids),'Patch has already been applied, partly or fully'
end=text.rfind(')');a.output.write_text(text[:end]+(root/'through-two-vias.sexpr').read_text()+text[end:]);print('Appended',len(ids),'GND vias; refill zones and run native DRC before acceptance')
