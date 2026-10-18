"""Read-only all-pad/NC/copper UUID inventory. Requires same-name project and KiCad10."""
import argparse,hashlib,json
from pathlib import Path
from collections import defaultdict
import pcbnew as p

def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest() if f.exists() else None

def run(board,report):
 assert not report.exists(),'Refusing overwrite'
 pro=board.with_suffix('.kicad_pro');assert pro.is_file(),'Same-name project required before loading'
 paths=[board,pro,board.with_suffix('.kicad_dru')];before={str(x):sha(x) for x in paths};b=p.LoadBoard(str(board));conn=b.GetConnectivity();pads={q.m_Uuid.AsString():q for f in b.GetFootprints() for q in f.Pads() if q.GetNumber()};seen=set();nets=defaultdict(list)
 def label(q):return q.GetParentFootprint().GetReference()+'.'+q.GetNumber()
 for uid,q in pads.items():
  if uid in seen:continue
  n=q.GetNetname();g={v.m_Uuid.AsString():v for v in [q,*conn.GetConnectedItems(q)] if isinstance(v,p.PAD) and v.GetNetname()==n};seen.update(g);nets[n].append({'pad_uuids':sorted(g),'ref_pin':sorted({label(v) for v in g.values()}),'populated_ref_pin':sorted({label(v) for v in g.values() if not v.GetParentFootprint().IsDNP()}),'physical_pad_shapes':len(g)})
 inventory={uid:{'ref_pin':label(q),'net':q.GetNetname(),'dnp':q.GetParentFootprint().IsDNP()} for uid,q in pads.items()};copper={t.m_Uuid.AsString():{'net':t.GetNetname(),'type':type(t).__name__,'layer':b.GetLayerName(t.GetLayer())} for t in b.GetTracks()};details=[{'net':n,'intentional_nc':n.startswith('unconnected-'),'groups':g,'component_count':len(g),'populated_component_count':sum(bool(x['populated_ref_pin']) for x in g)} for n,g in sorted(nets.items())];valid=[n for n in details if n['net'] and not n['intentional_nc']];assert before=={str(x):sha(x) for x in paths},'Sources changed'
 d={'board_sha256':sha(board),'project_sha256':sha(pro),'source_hashes':before,'sources_unchanged':True,'audit_script_sha256':sha(Path(__file__)),'kicad_version':p.Version(),'method':'All numbered native physical pad clusters, including NC; saved fills; no net spelling translation','numbered_pad_shapes':len(pads),'unique_ref_pin_count':len({label(q) for q in pads.values()}),'non_NC_net_count':len(valid),'disconnected_non_NC_nets':sum(n['component_count']>1 for n in valid),'disconnected_populated_non_NC_nets':sum(n['populated_component_count']>1 for n in valid),'minimum_non_NC_cluster_joins':sum(n['component_count']-1 for n in valid),'pad_inventory':inventory,'copper_uuid_net_inventory':copper,'nets':details,'production_ready':False,'limitations':['Singleton inputs can still float.','Native DRC capped findings are not total disconnect counts.','No SI, functional, current or manufacturing approval.']};report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({k:v for k,v in d.items() if k not in ['pad_inventory','copper_uuid_net_inventory','nets','source_hashes']}))
if __name__=='__main__':
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--board',type=Path,required=True);a.add_argument('--report',type=Path,required=True);x=a.parse_args();run(x.board,x.report)
