from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[1]
out=R/'outputs/PCIe_3board_RevJ'
assert not out.exists(), 'Rev J already exists; do not overwrite work'
shutil.copytree(R/'outputs/PCIe_3board_RevI',out)
scripts=R/'scripts/revJ'; scripts.mkdir(exist_ok=True)
work=R/'work/revJ'; work.mkdir(parents=True,exist_ok=True)
for name in ['i_common.py','i_route.py','i_finalize.py','i_schematic.py','i_check.py','i_validate.py','i_release.py','i_step_roundtrip.py','i_assembly.py']:
    s=(R/'scripts'/name).read_text(encoding='utf-8')
    s=s.replace('parents[1]','parents[2]').replace('PCIe_3board_RevI','PCIe_3board_RevJ').replace('work/revI','work/revJ').replace('REV I','REV J').replace("'revision':'I'","'revision':'J'").replace('(rev "I")','(rev "J")')
    (scripts/name).write_text(s,encoding='utf-8')
shutil.copy2(R/'work/revI/router.exe',work/'router.exe')
print('Created independent Rev J from the validated Rev I')
