from pathlib import Path
src=(Path(__file__).resolve().parent.parent/'revN/n_exports.py').read_text(encoding='utf-8').replace('PCIe_AllM2_RevN','PCIe_AllM2_RevO').replace('work/revN','work/revO')
exec(compile(src,str(__file__),'exec'))
