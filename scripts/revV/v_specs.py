from pathlib import Path
import sys,json
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/Users/micro/Desktop/方案/pcie switch 2');O=R/'outputs/PCIe_E1S_96x45_12VPower_RevV';F=O/'Main_12E1S';sys.path.insert(0,str(R/'scripts/revJ'))
from i_common import *
b=p.LoadBoard(str(F/'Main_12E1S.kicad_pcb'));m=json.loads((F/'COMPONENTS.json').read_text(encoding='utf-8'))
url='https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xal/xal40xx/xal4020-222/'
for q in m:
    if q['ref'] in ['L31','L502']:
        q.update(value='XAL4020-222MEC / 2.2uH / DCR max 38.7mOhm / Isat30% 5.6A',height_mm=2.1,datasheet=url)
        f=b.FindFootprintByReference(q['ref']);f.SetValue(q['value']);f.GetField(p.FIELD_T_DATASHEET).SetText(url)
    if q['ref']=='J401':q['input_main_bus_connected']=False
(F/'COMPONENTS.json').write_text(json.dumps(m,indent=2),encoding='utf-8');p.SaveBoard(str(F/'Main_12E1S.kicad_pcb'),b)
for fn in F.glob('*.kicad_sch'):
    s=fn.read_text(encoding='utf-8');s=s.replace('(rev "U")','(rev "V")').replace('2026-10-16','2026-10-17');fn.write_text(s,encoding='utf-8')
budget=dict(input_V=12,input_source='same regulated 12V supply; J101 and J102 independent positive and return cables',input_feeds_A_budget=[20,20],input_capacity_W_budget=480,input_connector_current_rating_qualified=False,fuses='2x Littelfuse 0456025.ER 25A with temperature derating',e1s_slots=12,ssd_per_slot_budget_W=25,total_ssd_output_W=300,total_ssd_12V_current_A=25,banks_ssd_W=[150,150],bank_A_slots=[1,2,3,4,5,11],bank_B_slots=[6,7,8,9,10,12],per_slot_efuse='TPS259470ARPWR',per_slot_current_limit_nominal_A=3334/1100,uvlo_rising_nominal_V=1.2*(1+76100/10000),ovlo_rising_nominal_V=1.2*(1+102000/10000),aux_efuse_limit_nominal_A=3334/750,aux_3v3_output_current_ic_limit_A=3,aux_5v_output_current_ic_limit_A=3,aux_both_outputs_W_at_ic_max=24.9,aux_efficiency_budget_assumption=.85,aux_input_W_budget=24.9/.85,ssd_plus_aux_input_A_budget=25+24.9/.85/12,cpu_and_switch_power_extra=True,cpu_dynamic_vr_implemented=False,fictional_switch_core_regulators_implemented=False,tbt_internal_regulator_distribution_complete=False,custom_power_usb_C_main_bus_connected=False,whole_board_power_routing_complete=False,current_capacity_and_thermal_qualified=False)
(O/'POWER_BUDGET.json').write_text(json.dumps(budget,indent=2),encoding='utf-8')
print('Fixed real low-profile inductor selection and explicit 12V power budget.')
