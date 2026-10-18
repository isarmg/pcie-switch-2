"""Synchronize existing datasheet links and correct inherited netclass coverage.
No inferred pin mappings. Preserve all rule numeric values and ERC/DRC settings.
Marks the existing, padless mechanical JHL9580 placeholder PCB-only; this is not
an implemented Thunderbolt controller. Does not make an electrical surrogate.
"""
from pathlib import Path
import argparse,json,re
import pcbnew as p
ROOT=Path(__file__).resolve().parents[2]
DEFAULT=ROOT/'outputs/PCIe_AllM2_RevP/Main_20M2'
def sync(folder):
    board=folder/'Main_20M2.kicad_pcb';b=p.LoadBoard(str(board))
    meta=json.loads((folder/'COMPONENTS.json').read_text());cs={q['ref']:q for q in meta};urls={}
    for f in b.GetFootprints():
        ref=f.GetReference();url=f.GetFieldText('Datasheet') or cs[ref].get('datasheet','')
        if url:urls[ref]=url;f.GetField('Datasheet').SetText(url);cs[ref]['datasheet']=url
        if cs[ref].get('mechanical_only'):
            assert not any(q.GetNumber() for q in f.Pads()),ref
            f.SetAttributes(f.GetAttributes()|p.FP_BOARD_ONLY)
    for path in [folder/'Local.kicad_sym',*folder.glob('*.kicad_sch')]:
        lines=[]
        for line in path.read_text().splitlines(keepends=True):
            m=re.search(r'\(symbol "(?:Local:)?PART_([^"_]+)"',line)
            if not m and '(symbol (lib_id ' in line:m=re.search(r'\(property "Reference" "([^"]+)"',line)
            if m and m[1] in urls:
                url=urls[m[1]].replace('\\','\\\\').replace('"','\\"')
                if '(property "Datasheet" ' in line:line=re.sub(r'\(property "Datasheet" "[^"]*"',lambda _:f'(property "Datasheet" "{url}"',line)
                else:line=line.replace('(property "Reference"',f'(property "Datasheet" "{url}" (at 0 0 0) (effects (font (size 1 1)) (hide yes)))(property "Reference"',1)
            lines.append(line)
        path.write_text(''.join(lines))
    (folder/'COMPONENTS.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    p.SaveBoard(str(board),b)
    project=folder/'Main_20M2.kicad_pro';pro=json.loads(project.read_text());before={k:v for k,v in pro['net_settings'].items() if k!='netclass_patterns'}
    # KiCad's matcher treats a literal {slash} prefix as an expression; use the
    # tested wildcard suffix form plus display-name aliases, and verify each net.
    data=['{slash}M*_TX*','{slash}M*_RX*','{slash}N*_TX*','{slash}N*_RX*','{slash}CPU_PEX_TX*','{slash}CPU_PEX_RX*','{slash}CPU_G5_TX*','{slash}CPU_G5_RX*']
    clock=['{slash}M*_CLK_*','{slash}N*_CLK_*','{slash}CPU_CLKBUF*_IN_*','{slash}PEX_SYS_REFCLK_*','{slash}CPU_REFCLK_*']
    # CPU_PEX_* is filtered against actual names by the ECO verifier; no width or
    # skew value is claimed to be an impedance-qualified design rule.
    pro['net_settings']['netclass_patterns']=[{'netclass':kind,'pattern':pat} for kind,patterns in [('PCIe_DATA_DRAFT',data),('REFCLK_DRAFT',clock)] for x in patterns for pat in [x.replace('{slash}','/'),x.replace('{slash}','*}')]]
    assert before=={k:v for k,v in pro['net_settings'].items() if k!='netclass_patterns'}
    project.write_text(json.dumps(pro,indent=2)+'\n')
    print('Synchronized existing datasheet URLs:',len(urls),'; mechanical-only footprint and RevP netclass patterns updated')
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--folder',type=Path,default=DEFAULT);sync(a.parse_args().folder)
