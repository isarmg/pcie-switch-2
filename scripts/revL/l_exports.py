from pathlib import Path
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2')
src=(R/'scripts/revK/k_exports.py').read_text(encoding='utf-8').replace('PCIe_3board_RevK','PCIe_3board_RevL').replace("W=R/'work/revK'","W=R/'work/revL'")
# The active viewer settings hide models. Use an existing appearance preset
# that includes all component categories, without changing those preferences.
src=src.replace('r=subprocess.run([CLI]+cmds[kind],capture_output=True)', '''
    cmd=[CLI]+cmds[kind]
    if kind in ['bottom','render']:
        prefs=json.loads(Path('C:/Users/micro/AppData/Roaming/kicad/10.0/3d_viewer.json').read_text(encoding='utf-8'))
        candidates=[q for q in prefs.get('layer_presets',[]) if all(k in q.get('layers',[]) for k in ['th_models','smd_models','virtual_models'])]
        assert candidates,'A render appearance preset with component models is required'
        cmd+=['--preset',candidates[0]['name']]
    r=subprocess.run(cmd,capture_output=True)''')
(R/'work/revL').mkdir(parents=True,exist_ok=True)
exec(compile(src,str(__file__),'exec'))
