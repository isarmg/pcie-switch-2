from i_common import *
import csv,zipfile,hashlib
# Combined BOM includes the previous revision's main power circuit and new parts.
rows=[]
for n in ['Main_10E1S','Left_2M2_Vertical','Right_M2_Upstream']:
    o=ROOT/n;b=p.LoadBoard(str(o/(n+'.kicad_pcb')));cs={c['ref']:c for c in json.loads((o/'COMPONENTS.json').read_text())}
    if n.startswith('Main'):
        cs={**{c['ref']:c for c in json.loads((BASE/'POWER_COMPONENTS.json').read_text())},**cs}
    for f in b.GetFootprints():
        c=cs.get(f.GetReference(),{});rows.append([n,f.GetReference(),f.GetValue(),str(f.GetFPID().GetLibItemName()),'F' if f.GetLayer()==p.F_Cu else 'B',*xy(f.GetPosition()),f.GetOrientationDegrees(),c.get('height_mm',9.05 if f.GetReference().startswith('J') and n.startswith('Main') and len(f.GetReference())<4 else 3 if f.GetReference()=='U1' else ''),c.get('datasheet','')])
with (ROOT/'BOM.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['Board','Reference','Value','Footprint','Side','X_mm','Y_mm','Rotation_deg','Height_envelope_mm','Datasheet']);w.writerows(rows)
# Put migration instructions next to the delivered CAD package as well as at the project root.
for name in ['Move-ToDesktop.ps1','Desktop-gitignore.append.txt']:
    src=R/'scripts'/name
    if name.endswith('.ps1'):
        text=src.read_text(encoding='utf-8-sig');src.write_text(text,encoding='utf-8-sig')
    shutil.copy2(src,ROOT/name)
files=[f for f in ROOT.rglob('*') if f.is_file() and f.suffix not in ['.zip','.kicad_prl','.lck'] and '-backups' not in str(f) and f.name!='SHA256SUMS.txt']
(ROOT/'SHA256SUMS.txt').write_text('\n'.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.relative_to(ROOT).as_posix() for f in sorted(files))+'\n')
zipfile_path=R/'outputs/PCIe_3board_RevI.zip'
with zipfile.ZipFile(zipfile_path,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
    for f in ROOT.rglob('*'):
        if f.is_file() and f.suffix not in ['.zip','.kicad_prl','.lck'] and '-backups' not in str(f):z.write(f,Path(ROOT.name)/f.relative_to(ROOT))
print('Release',zipfile_path,zipfile_path.stat().st_size,'bytes; BOM',len(rows),'components')
