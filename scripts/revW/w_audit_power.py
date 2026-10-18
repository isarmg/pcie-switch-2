from pathlib import Path
src=(Path(__file__).resolve().parents[2]/'scripts/revV/v_audit_power.py').read_text(encoding='utf-8').replace('PCIe_E1S_96x45_12VPower_RevV','PCIe_E1S_96x45_USB12mm_RevW').replace('work/revV','work/revW')
src=src.replace("rails=set(d['planes'])|{'/GND'}","rails=set(d['planes'])|{'/GND','/PEX09_SW'}")
extra=(Path(__file__).with_name('w_contact_graph.py')).read_text(encoding='utf-8')
src=src.replace("checks=d['pad_stitches'][:]",extra+"\nchecks=d['pad_stitches'][:]")
exec(compile(src,__file__,'exec'),globals())
