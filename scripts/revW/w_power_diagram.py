from pathlib import Path
src=(Path(__file__).resolve().parents[2]/'scripts/revV/v_diagram.py').read_text(encoding='utf-8').replace('PCIe_E1S_96x45_12VPower_RevV','PCIe_E1S_96x45_USB12mm_RevW').replace('(1600,960)','(1600,1170)').replace('Rev V  |','Rev W  |')
src=src.replace("box(55,750,1470,135,'未实现：CPU 动态 VR / 虚构 switch 核心供电 / 整机启动时序'", "box(55,750,1470,135,'新增：虚构 switch 的参考 0.9 V / 1.8 V 电源','来源：12 V B 组；TPS548D22（40 A IC）+ TPSM63610（8 A IC）；模拟域分别经低 DCR 电感滤波。','#dff1e7')\nbox(55,945,1470,135,'未实现：CPU 动态 VR / 雷电其余内部电源分配 / 整机启动时序'")
exec(compile(src,__file__,'exec'),globals())
