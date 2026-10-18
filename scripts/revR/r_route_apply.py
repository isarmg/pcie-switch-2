from pathlib import Path
src=(Path(__file__).resolve().parent.parent/'revL/l_route_apply.py').read_text(encoding='utf-8')
src=src.replace('PCIe_3board_RevL','PCIe_E1S_82x45_RevR').replace('work/revL','work/revR').replace('109.6','81.6')
src=src.replace("d=json.loads((W/'cpu_routes.json').read_text())",'''current=p.LoadBoard(str(folder/'Main_10E1S.kicad_pcb'))
paths={f.GetReference():f.GetPath() for f in current.GetFootprints()}
for f in b.GetFootprints():f.SetPath(paths[f.GetReference()])
d=json.loads((W/'cpu_routes.json').read_text())''')
exec(compile(src,str(__file__),'exec'))
