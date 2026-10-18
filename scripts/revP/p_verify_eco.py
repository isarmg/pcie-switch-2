"""Verify Rev P local reset ECO, class coverage, and pre-existing copper invariants.
Usage: KiCad-python p_verify_eco.py --baseline pre-patch.pcb --output report.json
Only approved local copper additions may be absent from the baseline. No claim
is made that reset bias constitutes a release driver or completed ground rail.
"""
from pathlib import Path
from collections import Counter
import argparse,fnmatch,hashlib,json
import pcbnew as p
ROOT=Path(__file__).resolve().parents[2]
DEFAULT=ROOT/'outputs/PCIe_AllM2_RevP/Main_20M2/Main_20M2.kicad_pcb'
def display(x):return x.replace('{slash}','/')
def signature(b):
    result={}
    for t in b.GetTracks():
        common={'net':display(t.GetNetname()),'type':'via' if isinstance(t,p.PCB_VIA) else 'track'}
        if isinstance(t,p.PCB_VIA):common.update(pos=[t.GetPosition().x,t.GetPosition().y],top=t.TopLayer(),bottom=t.BottomLayer(),drill=t.GetDrill(),width=t.GetWidth(t.TopLayer()),via_type=t.GetViaType())
        else:common.update(start=[t.GetStart().x,t.GetStart().y],end=[t.GetEnd().x,t.GetEnd().y],layer=t.GetLayer(),width=t.GetWidth())
        result[t.m_Uuid.AsString()]=common
    return result
def verify(board,baseline):
    b=p.LoadBoard(str(board));old=p.LoadBoard(str(baseline));conn=b.GetConnectivity();fs={f.GetReference():f for f in b.GetFootprints()}
    def pad(r,n):return next(q for q in fs[r].Pads() if q.GetNumber()==n)
    def group(q):return {t.GetParentFootprint().GetReference()+'.'+t.GetNumber() for t in conn.GetConnectedItems(q) if isinstance(t,p.PAD)}|{q.GetParentFootprint().GetReference()+'.'+q.GetNumber()}
    oldtracks=signature(old);newtracks=signature(b)
    removed=[u for u in oldtracks if u not in newtracks];changed=[u for u in oldtracks if u in newtracks and oldtracks[u]!=newtracks[u]]
    assert not removed and not changed,('pre-existing copper changed',removed,changed)
    reset=[]
    for i,r in enumerate(['R3005','R3015','R3025','R3035'],1):
        con=f'J{500+i}';signal=group(pad(con,'50'));ground=group(pad(con,'51'))
        assert r+'.1' in signal,(r,'signal not connected')
        assert r+'.2' in ground,(r,'ground not connected')
        assert display(pad(r,'1').GetNetname())==f'/M{i}_PERST'
        assert display(pad(r,'2').GetNetname())=='/GND'
        reset.append({'port':f'M{i}','ref':r,'connector_pin50_to_pull_down_copper_connected':True,'pull_down_to_connector_pin51_copper_connected':True,'ground_connected_to_input_J11_or_J12':any(q.startswith(('J11.','J12.')) for q in ground),'reset_release_driver_implemented':False,'signal_cluster':sorted(signal),'ground_cluster':sorted(ground)})
    pro=json.loads(board.with_suffix('.kicad_pro').read_text());patterns=pro['net_settings']['netclass_patterns'];classes=Counter();errors=[]
    for n in b.GetNetInfo().NetsByNetcode().values():
        if not n.GetNetname():continue
        expected={row['netclass'] for row in patterns if fnmatch.fnmatchcase(n.GetNetname(),row['pattern'])}
        actual=set(n.GetNetClassName().split(','))-{'Default'}
        if actual!=expected:errors.append({'net':n.GetNetname(),'expected':sorted(expected),'actual':n.GetNetClassName()})
        for c in actual:classes[c]+=1
        readable=display(n.GetNetname())
        if any(fnmatch.fnmatchcase(readable,pat) for pat in ['/M*_TX*','/M*_RX*','/N*_TX*','/N*_RX*','/CPU_G5_TX*','/CPU_G5_RX*','/CPU_PEX_TX*','/CPU_PEX_RX*']):assert 'PCIe_DATA_DRAFT' in actual,readable
        if any(fnmatch.fnmatchcase(readable,pat) for pat in ['/M*_CLK_*','/N*_CLK_*','/CPU_CLKBUF*_IN_*','/CPU_REFCLK_*','/PEX_SYS_REFCLK_*']):assert 'REFCLK_DRAFT' in actual,readable
    assert not errors,errors
    return {'board_sha256':hashlib.sha256(board.read_bytes()).hexdigest(),'baseline_sha256':hashlib.sha256(baseline.read_bytes()).hexdigest(),'baseline_copper_objects_unchanged':len(oldtracks),'new_copper_objects':len(set(newtracks)-set(oldtracks)),'reset_bias_local_connections':reset,'netclass_counts':dict(classes),'netclass_numeric_rules_impedance_qualified':False,'production_ready':False}
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--board',type=Path,default=DEFAULT);a.add_argument('--baseline',type=Path,required=True);a.add_argument('--output',type=Path,required=True);args=a.parse_args();r=verify(args.board,args.baseline);args.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='reset_bias_local_connections'},indent=2))
