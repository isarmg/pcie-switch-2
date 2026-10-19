# C5111 LDO3V3 MLCC research — 2026-10-19

## Recommendation
Use **GRM21BZ71E106KE15L** as a concrete **0805 design-validation candidate**, not a guaranteed stability sign-off. 10µF ±10%, 25V, X7R(MURATA), -55…125°C, maximum body 2.2×1.45×1.45mm. It offers approximately 8–8.5µF at 3.45V on the manufacturer typical DC curve (1kHz/1Vrms). This is materially better typical margin than the examined 0603 10µF option, without the initial-capacitance upper-limit concern of 22µF±20%. The full specification supports suffix L (180mm plastic tape), or K, **not an assumed D suffix**.

No evaluated option establishes a guaranteed combined bias/temperature/aging capacitance minimum. Do not claim LDO stability passed. Verify low-excitation effective capacitance at operating bias and temperature, aging/lifetime budget and regulator transient/stability on the assembled board before release.

## TI requirement, freshly rechecked
Official TPS65982 SLVSD02E Rev.E, https://www.ti.com/lit/ds/symlink/tps65982.pdf : table11-1 gives LDO3V3 rated voltage6.3V, effective minimum5µF, typical placed10µF, maximum25µF. §7.5 gives output2.7/3.3/3.45V min/typ/max. Supply capacitance section requires tolerance and voltage derating to be considered. Count total connected capacitance, including any shared VDDIO decoupling.

## Examined candidates and limits
All values below are visual approximate readings of original manufacturer Oct2026 TechPDFs, not precise CSV measurements or guaranteed minima.

- GRM188Z71A106KA73 (0603,10µF±10%,10V,X7R(MURATA)): at3.45V approximately -39…-42%, or5.8–6.1µF, tested1kHz/1Vrms. Low-AC curve alone approaches -25% at nearzero amplitude. Its small DC-only margin is insufficient for a strong recommendation. Max body1.8×1.0×1.0mm.
- GRM188C81A226ME01D (0603,22µF±20%,10V,X6S,-55…105°C): at3.45V approximately -50…-53%, or10.3–11µF,120Hz/.5Vrms. This is a promising lower-bound *typical* result in same nominal package. However specified initial17.6–26.4µF includes values above TI25µF maximum, before any additional connected capacitance. Bias typical reduction does not establish compliance through all operating/startup conditions. Cannot recommend unconditionally. Max body1.8×1.0×1.0mm.
- GRM21BR71A106KE51 (0805,10µF±10%,10V,X7R): roughly6.8–7µF at3.45V,.5Vrms; low-AC effect substantial. Larger package alone does not imply sufficient margin.
- GRM21BR61C106KE15 (0805,10µF±10%,16V,X5R): around6.3–6.6µF; only85°C rated. Not preferred.
- GRM21BC81E106KE51 (0805,10µF±10%,25V,X6S): around7.5–8µF at3.45V but low-AC curve approaches -45%; not preferred versus Z7 candidate.
- **GRM21BZ71E106KE15L**,0805,10µF±10%,25V: approximately8–8.5µF at3.45V,1kHz/1Vrms. Low-AC curve alone approaches -30% nearzero AC. Do not multiply separate curves into a claimed guaranteed combined value. Initial9–11µF is comfortably below25µF, but actual total upper/lower budget still requires verification.

## Temperature, aging, and guarantee boundary
Preferred Z7 specification calls its characteristic X7R(MURATA), not an ordinary unbiased X7R assumption: ±15% temperature change is specified with **50% rated voltage applied (12.5V)**, with the detailed capacitance-change test definition. That is not evidence of a ±15% residual-capacitance bound at3.45V. No temperature curve is populated in its TechPDF. The reference sheet explicitly warns high-K capacitance decreases with aging and calls for actual-environment checks, without giving a universal numeric lifetime floor. The TechPDF explicitly says only typical specifications. Initial tolerance, temperature limits and independently measured bias/AC plots must not be combined into a manufacturer-guaranteed bound.

## Land pattern handoff
Official reference-sheet reflow table and diagram have a=inner gap,b=each pad length along body,c=pad width. These are recommendations requiring actual PCB evaluation, not an assertion all other footprints are forbidden.
- Selected0805,2.0×1.25±.2: a1.0–1.4,b.6–.8,c1.2–1.4mm. Practical nominal choice a1.2,b.7,c1.3 produces pad centers1.9mm apart,total copper2.6×1.3mm. Max body2.2×1.45,maxheight1.45. With .25mm per-side body clearance, transverse courtyard should be at least1.95mm; choose longitudinal courtyard based on copper/body and assembly rules. Rotate long axis vertically in narrow lane if appropriate; verify all nearby pads, vias, layers and clearance.
- Examined0603 ±.2 body: a.7–.9,b.7–.8,c.8–1.0mm; maxbody1.8×1.0,maxheight1.0. Existing pad.9×.95,center1.55 => gap.65, hence not within this vendor recommendation (a too small,b too long). Same nominal0603 does not mean already vendor-land-matched. Example a.8,b.75,c.9 =>center1.55,total2.3×.9.

## Official sources and provenance
Manufacturer current SimSurfing dataset downloaded https://ds.murata.com/simsurfing_data/data/mlcc.zip (CSV dated2026-10-19); selected part bases are present. This confirms current model/catalog presence, not stock or a formal production-lifecycle commitment. No procurement was performed.

Exact preferred specification (download succeeded; local spec0805.pdf):
https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM21BZ71E106KE15-01A.pdf

Exact0603 22µF specification (local spec0603.pdf, reflow diagram rendered land.png):
https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM188C81A226ME01-01A.pdf

Typical electrical graphs downloaded with each evaluated base MPN in this URL pattern (local PDFs and inspected PNGs retained):
https://ds.murata.com/simserve/characteristics?ReqType=TechPDF&partnumber=GRM21BZ71E106KE15&ModeType=&techpdfname=technical_pdf_Capacitor01&lang=en

Product webpage retrieval returned403; it was not used to infer lifecycle. No Main PCB/Git writes; this report and evidence only.

Publication note: vendor PDFs/images/workbooks and rejected PCB files are not included; local filenames mentioned above identify research inputs, not repository attachments. Formal C5111 remains generic0603 with no selected MPN applied.
