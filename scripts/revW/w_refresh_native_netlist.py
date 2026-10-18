"""Install a fresh official XML netlist after proving all logical ref.pin networks unchanged.
Usage: SCRIPT DESIGN_DIR FRESH_XML PROOF_JSON. No PCB/source schematic is changed.
Generate FRESH_XML using kicad-cli sch export netlist --format kicadxml.
"""
from pathlib import Path
import sys,xml.etree.ElementTree as E,json,hashlib
D,new,proof=map(Path,sys.argv[1:4]);old=D/'CONNECTIVITY.net';a=E.parse(old).getroot();b=E.parse(new).getroot()
def nodes(r):return {(q.attrib['ref'],q.attrib['pin']):n.attrib['name'].replace('{slash}','/') for n in r.findall('./nets/net') for q in n.findall('node')}
x,y=nodes(a),nodes(b);assert x==y, 'Logical pin/net mapping change requires explicit ECO review'
meta={c['ref']:c for c in json.loads((D/'COMPONENTS.json').read_text())}
for c in b.findall('./components/comp'):
 m=meta[c.attrib['ref']];assert c.findtext('value')==m['value'];assert c.findtext('footprint')=='Local:'+m['footprint'];assert (c.find('./property[@name="dnp"]') is not None)==bool(m.get('dnp',False)),c.attrib['ref']
sha=lambda v:hashlib.sha256(v).hexdigest();r={'old_sha256':sha(old.read_bytes()),'fresh_sha256':sha(new.read_bytes()),'unchanged_logical_ref_pin_nodes':len(x),'all_values_footprints_dnp_match_metadata':True,'source_of_truth':'Fresh official export of native hierarchical schematic; historical cached model types and DNP properties refreshed.'}
old.write_bytes(new.read_bytes());proof.write_text(json.dumps(r,indent=2)+'\n')
