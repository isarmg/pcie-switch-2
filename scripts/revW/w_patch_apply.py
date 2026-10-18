from pathlib import Path
src=Path(__file__).with_name('w_bridge_apply.py').read_text(encoding='utf-8').replace('bridge/','finalpatch/')
src=src.replace("pd['island_bridge_via_extensions']=json.loads((W/'finalpatch/extensions.json').read_text(encoding='utf-8'))", "pd.setdefault('island_bridge_via_extensions',[]).extend(json.loads((W/'finalpatch/extensions.json').read_text(encoding='utf-8')))")
exec(compile(src,__file__,'exec'),globals())
