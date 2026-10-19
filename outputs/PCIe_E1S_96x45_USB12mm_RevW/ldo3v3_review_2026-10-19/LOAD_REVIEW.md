# TPS65982 LDO3V3 load-budget review
Date 2026-10-19. Read-only source snapshot `pcie-switch-2-recovery-20261019`, HEAD `22600f2c9371c92934a09e4ea6fa4c95897cc041`.

## Result
**No evidence of an unavoidable external DC overcurrent from the identified Flash and resistors. No worst-case supply/stability pass established.** Identified Flash write/erase max25mA plus a deliberately conservative all-pullups-low calculation using nominal resistors is26.4145mA at3.45V, below30mA by3.5855mA. This remaining budget must cover actual resistor tolerances, leakage and dynamic output loads; nominal calculation is not a certified upper bound. TI internal current is not characterized with a max in the consumption table, so do not add its5.64mA typical to claim70mA worst-case compliance. Existing disconnected power/ground remains a separate immediate blocker to operation.

TI explicitly intends LDO_3V3 to power the external Flash and requires the Flash pullups on this supply. Moving it to an unrelated auxiliary supply without rechecking dead-battery boot, sequencing and I/O back-power is not a justified fix.

## Exact net and fitted components
The actual native and COMPONENTS name is `/TBT_PD_LDO_3V3` (native escaped `{slash}TBT_PD_LDO_3V3`), not a literal `TBT_LDO3V3_MAIN`. Native footprint extraction found these9 footprints, all without DNP attr, matching COMPONENTS:
- U503 G1 LDO_3V3 source; B1 VDDIO load of the same TPS65982.
- U505 **W25Q80DVSNJG**, pin8 VCC,pin7 HOLD_N. Native and metadata explicitly name this MPN; not a generic W25Q80 guess.
- R5142 10k to Flash CS_N.
- R5144 10k to Flash WP_N.
- R5154 100k to BUSPOWERZ.
- R5155 10k to I2C2 SDA.
- R5156 10k to I2C2 SCL.
- C5102 100nF and C5111 10µF6.3V: no intentional steady DC load, but charge current and leakage must not be treated as zero under all conditions; actual capacitor MPN pending.

TI VDDIO and powered I/O buffers can add dynamic current into their output nets. These are not another independently specified external IC current that can be guessed. No LEDs or second external IC supply pin found on this net. The5 pullups are not normally all simultaneously low (WP_N only connects to its pullup and Flash input), so the following is a conservative topology screening case, not the claimed normal operating state.

## Official requirements and internal-current meaning
TI TPS65982 **SLVSD02E**, revised August2021, freshly downloaded from https://www.ti.com/lit/ds/symlink/tps65982.pdf:
- §7.5 p13 applies recommended conditions TA=-10…85°C unless noted.
- VLDO_3V3=2.7/3.3/3.45V min/typ/max.
- ILDO_3V3 maximum70mA includes **internal core power plus external LDO_3V3 load**.
- ILDO_3V3EX maximum30mA is the external DC-current limit. The70mA number does not replace or enlarge30mA. The40mA difference is not a published maximum measured internal consumption.
- §11.2: LDO3V3 feeds internal1.8V digital and analog regulators; do not sum their50mA/20mA capability ratings as actual core consumption.
- §7.7 p14 gives sleep58µA,idle1.66mA,active5.64mA **typical only at25°C**, VIN_3V3=VDDIO=3.45V,VBUS=PPCABLE=0. Application code can change consumption. MAX column is blank.
- §11.1.3 warns significant external load when supplied from20V VBUS can cause thermal shutdown. Passing DC-current arithmetic does not close thermal operating-mode limits.

## Exact Winbond official evidence
Downloaded current official document through Winbond's public documentation redirect, not a distributor:
https://www.winbond.com/hq/support/documentation/levelOne.jsp?__locale=en&DocNo=DA00-W25Q80DV
It links directly to https://www.winbond.com/resource-files/W25Q80DV_revN_04242026%20Plus.pdf
Local `winbond.pdf` SHA256 `a8a4f7188bdaeb4bc4ee5ab532083c2f34d2bf717160415bd8212d889b97189e`.
**W25Q80DV Preliminary Revision N, April24,2026**, Industrial and Industrial Plus. Exact W25Q80DVSNJG listed in Industrial Plus ordering table; SN isSOIC8 150mil,J is-40…105°C. Board TPS65982 itself remains limited by its-10…85°C characterization, not105°C simply because Flash supports it.

§9.2 p54: VCC2.7…3.6V. Therefore TI's2.7…3.45V nominal operating envelope overlaps, but its minimum leaves no allowance for additional PCB drop or transient undershoot belowFlash2.7V. Also notes read voltage must not differ by more than±10% from programming/erase/write voltage; source-transition cases need consideration.

§9.4 p56 actual MAX values:
- Standby50µA at<85°C,60µA at<105°C; CS=VCC,VIN=GND/VCC.
- Power-down5µA at<85°C,25µA at<105°C.
- Single Read Data50MHz15mA; clock0.1/0.9VCC,DO open,checkerboard pattern.
- Dual/Quad Output Read80MHz20mA; Quad Output104MHz25mA. These higher modes are not the stated TI12MHz SPI mode0 boot mode.
- Write Status Register25mA; Page Program25mA; Sector/Block Erase25mA; Chip Erase25mA; CS=VCC. These are alternative operations, not concurrent currents to sum.
- Input and I/O leakage±2µA each.
Only capacitance sample-test footnote1 states25°C,3V; do not misapply it as limiting all current max rows. Table itself does not provide a separate12MHz max. Use50MHz read max as a conservative screening proxy without scaling it by12/50 or asserting it is an explicit12MHz guarantee. DO-open condition excludes external capacitive output-load current.

## Quantified load screening
At3.45V and nominal values, each10k held low draws0.345mA; four draw1.38mA. 100k held low draws0.0345mA. Sum1.4145mA.
- Flash read15mA + pullups1.4145mA =16.4145mA (13.5855mA nominal DC headroom).
- Flash write/erase25mA + pullups1.4145mA =26.4145mA (3.5855mA nominal DC headroom).
No resistor tolerance or MPN specified, so use actual Rmin for sign-off. For illustration only if all were±5%, resistor load becomes1.4145/.95=1.48895mA and sum26.48895mA; **±5% is not assigned to BOM by this review**. Leakage, I/O capacitive switching, inrush, regulation/thermal conditions remain additional checks. Do not add typical core to these and call worst-case complete.

## Power and boot sequencing
- TI§9.5.1: Flash powered fromLDO_3V3 to support dead/no-battery; **all Flash pullups must tie LDO_3V3**. Flash supports12MHz,mode0,4kB erase; W25Q80 explicitly recommended. §10.2.1.2.1 and.9 demonstrate same-supply Flash and pullups.
- Winbond§7.1 write protection: CS must trackVCC throughout power-up untilVCCmin andtVSL reached. §9.3 p55: VCCmin toCS low minimum10µs; write-instruction delay minimum5ms, characterized parameters. Must not issue programming/erase before ready; WEL starts cleared.
- R5142 intended CS same-rail pullup supports this topology, but its disconnected supply cannot currently enforce tracking. Flash HOLD_N and VCC also need real connections; a matching net label alone is insufficient.
- LDO3V3 regulator startup, cap effective value, board impedance, waveform timing, programmed boot image and total dynamic loads are not validated by this budget review.

## Connectivity scope
Archived native connectivity evidence `NATIVE_CLUSTERS.txt` reports individual isolated source G1,VDDIO B1,C5102,C5111,Flash VCC/HOLD supply pads; this report did not rerun the full native connectivity verifier. It is explicitly a hypothetical *after proper routing* budget. No claim current board runs, no PCB/code edits.

Publication note: vendor PDFs/images/workbooks and rejected PCB files are not included; local filenames mentioned above identify research inputs, not repository attachments. Formal C5111 remains generic0603 with no selected MPN applied.
