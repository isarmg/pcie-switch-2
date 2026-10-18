from pathlib import Path
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2')
src=(R/'scripts/revK/k_step_roundtrip.py').read_text(encoding='utf-8').replace('PCIe_3board_RevK','PCIe_3board_RevL').replace("W=R/'work/revK'","W=R/'work/revL'")
exec(compile(src,str(__file__),'exec'))
