from pathlib import Path
src=Path(__file__).with_name('v_reserve_power_layer.py').read_text(encoding='utf-8')
src=src.replace('In5','In6').replace('bank A','bank B').replace('VBANK_A','VBANK_B').replace('bank_A','bank_B').replace('assert len(tasks)==12','assert len(tasks)>0').replace('POWER_LAYER_RESERVATION.json','POWER_LAYER_RESERVATION_B.json')
src=src.replace("available=set(cu)-{p.In6_Cu,p.F_Cu,p.B_Cu}","available=set(cu)-{p.In5_Cu,p.In6_Cu,p.F_Cu,p.B_Cu}")
exec(compile(src,str(__file__),'exec'))
