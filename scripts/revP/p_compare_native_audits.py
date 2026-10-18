"""Compare hash-bound p_native_audit inventories without canonicalizing net names.
Includes NC pad identities. Deliberate circuit/net spelling ECOs require a
separate exact mapping proof; this tool never silently allows reassignments.
"""
from pathlib import Path
import json,argparse,hashlib

def run(base,candidate,out):
 assert not out.exists(),'Refusing overwrite';a=json.loads(base.read_text());b=json.loads(candidate.read_text());assert a['sources_unchanged'] and b['sources_unchanged']
 for d in [a,b]:
  for path,h in d['source_hashes'].items():
   p=Path(path);assert (hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None)==h,'Input has changed since audit: '+path
 old=a['pad_inventory'];new=b['pad_inventory'];missing=sorted(set(old)-set(new));changes=[{'uuid':u,'before':old[u],'after':new[u]} for u in old.keys()&new.keys() if old[u]['net']!=new[u]['net'] or old[u]['ref_pin']!=new[u]['ref_pin']]
 membership={u:(n['net'],i) for n in b['nets'] for i,g in enumerate(n['groups']) for u in g['pad_uuids']};splits=[]
 for n in a['nets']:
  for g in n['groups']:
   members={membership[u] for u in g['pad_uuids'] if u in membership}
   if len(members)>1:splits.append({'net':n['net'],'ref_pin':g['ref_pin'],'new_components':sorted(members)})
 ac=a['copper_uuid_net_inventory'];bc=b['copper_uuid_net_inventory'];copper=[{'uuid':u,'before':ac[u]['net'],'after':bc[u]['net']} for u in ac.keys()&bc.keys() if ac[u]['net']!=bc[u]['net']]
 same_rules=a['project_sha256']==b['project_sha256'];result={'baseline_board_sha256':a['board_sha256'],'candidate_board_sha256':b['board_sha256'],'baseline_audit_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'candidate_audit_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'project_unchanged':same_rules,'all_original_numbered_pads_including_NC_compared':True,'missing_old_pads':missing,'old_pad_net_or_identity_changes':changes,'old_clusters_split':splits,'surviving_copper_net_changes':copper,'passed':not(missing or changes or splits or copper) and same_rules,'production_ready':False}
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if not isinstance(v,list)}));return result['passed']
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for x in ['baseline','candidate','report']:p.add_argument('--'+x,type=Path,required=True)
 a=p.parse_args();raise SystemExit(0 if run(a.baseline,a.candidate,a.report) else 2)
