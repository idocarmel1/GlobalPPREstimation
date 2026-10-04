# Sea of Okhotsk Figure 9 researcher readings revision (2000–2014)

Status: **BLOCKED — not yet loadable and balanced for researcher validation.** This is a derivative of the preserved Figure-only reconstruction. The original extraction, existing selected NE model, validation DOCX and map remain untouched. Artifact arithmetic and import formatting were verified; biological balance and native EwE load are not established.

**Source:** Gorbatenko and Melnikov (2019), DOI10.26428/1606-9919-2019-198-143-163, Table 3 printed p.154/PDF p.12, Figure 9 printed p.157/PDF p.15; explicit bacteria conversion from Gorbatenko (2018) dissertation p.60. LME 52, local model ID GM2019-Fig9,22 groups(21 living,1 detritus),20 consumers, fisheries unknown. Revision date2026-10-03.

## Accepted readings and source corrections

- F62 preferred0.023; alternative0.025 retained in F62_0p025_sensitivity.json, as requested by the researcher. F67=0.05 human confirmed. Source-readable fields and the original ledger still retain the overprinted uncertainty.
- F77 source changes from large pollock19 to medium pollock15, destination predatory fish20, flow0.01. This follows the actual green shaft and arrowhead; no balance criterion was used as tracing evidence.
- F13 and F22 endpoints are unchanged, with improved visual routing confidence. F78 remains15→21 tentative, literal0.05. Other dense red routes and three duplicated adopted pairs remain unresolved.
- Bacteria wet/carbon 9.4 is explicitly supported by dissertation p.60. Protozoa10 is only a conflicting derivation, not adopted. Detritus factor remains unknown.

With these decisions the Figure-only variant has20/20 numerical carbon diet columns,18/20 wet columns and32 tentative routes. These counts establish arithmetic completeness under adopted routes, not source approval.

## All conversion factors

Factor means tonnes wet mass per tonne carbon. Multiply carbon flow by the **prey's** factor before calculating wet diet fractions; the consumer's body factor cannot convert its total food consumption.

| ID | Group | Wet/carbon | Evidence |
|---|---|---:|---|
| 1 | Phytoplankton | 20.0 | 2019 Table 3 |
| 2 | Bacteria | 9.4 | Dissertation p60, explicit supporting-source factor |
| 3 | Protozoa | Unknown | Unknown |
| 4 | Copepods | 14.0 | 2019 Table 3 |
| 5 | Euphausiids | 10.6 | 2019 Table 3 |
| 6 | Hyperiids | 14.50 | 2019 Table 3 |
| 7 | Chaetognaths | 20.0 | 2019 Table 3 |
| 8 | Salmon | 8.20 | 2019 Table 3 |
| 9 | Squid III | 11.90 | 2019 Table 3 |
| 10 | Herring | 7.20 | 2019 Table 3 |
| 11 | Deep-sea smelt | 8.70 | 2019 Table 3 |
| 12 | Pollock less than 30 cm | 10.20 | 2019 Table 3 |
| 13 | Capelin | 8.80 | 2019 Table 3 |
| 14 | Jellyfish | 285.20 | 2019 Table 3 |
| 15 | Pollock 30-60 cm | 11.11 | 2019 Table 3 |
| 16 | Squid IV | 11.94 | 2019 Table 3 |
| 17 | Predatory salmon | 8.20 | 2019 Table 3 |
| 18 | Baleen whales | 5.43 | 2019 Table 3 |
| 19 | Pollock greater than 60 cm | 11.11 | 2019 Table 3 |
| 20 | Predatory fish | 5.43 | 2019 Table 3; tentative crosswalk |
| 21 | Predatory mammals | 5.43 | 2019 Table 3 |
| 22 | Detritus | Unknown | Unknown |

The2019 pooled microheterotroph row has9.4; it does not independently establish both individual microbial factors. Dissertationp60 protozoa 27 gC/m² and270 g wet/m² imply10, but the corresponding whole-Sea total conflicts. Table 3's predatory-fish Other**** mapping remains tentative.

## User assumptions

GS = 0.2 for20 consumers. All other mortality and unassimilated consumption route100% to detritus22. Detritus import/export=0. Detritus accumulation is the uncomputed residual BA_D=Σ(GS×Q+other mortality+actual discarded biomass entering detritus)−Q_D. It is not assumed zero. Living catches, BA and net migration remain unknown.

## Remaining basic inputs and diets

Bacteria and protozoa still lack separate annual whole-Sea B and P/B. Their Q/B cannot be identified without stocks; bacteria's wet Q also needs the detritus conversion. Copepod and euphausiid wet diets each have three unknown positive fractions because the protozoa prey factor is unknown. Their other prey fractions cannot be normalized until the denominator exists. Their Q/B is independently recoverable from prose:2945/108.3=27.192982456/year and1445.6/58.7=24.626916525/year. These prose alternatives are not silently substituted for Figure-derived Q/B.

Baleen whale Q is now0.21415million tC/year or2.25652million wet tonnes/year; using Table 3B0.721 gives Q/B3.129708738/year. F62=.025 instead adds0.002million tC and0.0144million wet tonnes/year to whale Q. It cannot fix the current failing groups.

## Existing balance failures

The three carbon energy failures below use Figure production and adopted incoming arrows, with GS = 0.2. Flows are million tC/year; respiration R=.8Q−P must be positive.

| Consumer | P | Q | R |
|---|---:|---:|---:|
| Hyperiids | 4.752 | 4.383 | -1.2456 |
| Salmon | 0.105 | 0.0731 | -0.04652 |
| Jellyfish | 0.144 | 0.0505 | -0.10360 |

All three also haveP>Q, so setting GS = 0 would not cure them. Chaetognaths instead pass carbon R=+3.7528 but fail the wet B×PB/Q diagnostic, R=−26.28032million wet tonnes/year. Different prey/body water content makes wet mass unsuitable as a direct carbon-energy identity here. Source-stock conversions and printed carbon stocks also conflict for some groups; a complete carbon model must document a consistent input variant.

Predation exceeds Figure production for six groups under the adopted full route interpretation. This ratio becomes an implied EE only in the diagnostic with zero living catch, BA and net migration; those zero values are **not** adopted inputs.

| Prey | Figure P | Predation | Predation/P | Clear-route lower bound already fails? |
|---|---:|---:|---:|---|
| Squid III | 0.105 | 0.6968 | 6.636190 | No |
| Herring | 0.119 | 1.04714 | 8.799496 | No |
| Deep-sea smelt | 0.06 | 0.14554 | 2.425667 | Yes |
| Capelin | 0.03 | 0.7774 | 25.913333 | Yes |
| Squid IV | 0.1 | 0.158 | 1.580000 | Yes |
| Pollock greater than 60 cm | 0.009 | 0.057 | 6.333333 | No |

Even clear routes give smelt0.125>0.06, capelin0.115>0.03, squidIV0.158>0.1(or Table 3P0.105). Minimum carbon production deficits are0.065,0.085,0.058million tC/year. Catch/positive BA/outward migration worsen a deficit; net inward migration or negative BA could offset it, but no annual measured values are identified. These stock-balance terms cannot fix negative consumer respiration at fixedP,Q,GS.

## Article results available for testing closure hypotheses

Table 3 stocks, turnover and production; Figure 9 carbon flows; prose annual Q by species/groups; Table 2 percentages of zooplankton production eaten; tier production totals and the food split of the nekton community. Independent wet Q targets(million tonnes/year): copepods 2945,euphausiids 1445.6,hyperiids 152.5,chaetognaths 320,herring 36.9,smelt 10.29,capelin 14.74,small pollock 16.5,medium pollock 80.8,pooled squid 32.4. Total nekton195 is better supported by most prose/ratio checks and the2016 target194.9, while the abstract159 conflicts and its English carbon unit is erroneous. These are competing recorded source targets.

The production equation P=predation+catch+BA+net outward migration+other mortality constrains a combined residual; the paper does not independently identify catch, BA and migration. Seasonal herring survey changes are explained by coverage and cannot be treated as measured annual BA/import. Methods include growth and mortality losses, so there is no evidence for treating Table 3P/B simply as surviving-stock growth or a source mortality Z.

Additional dissertation targets are saved in ../../research_20261003/article_constraints/FOLLOWUP_RECOVERIES.md: salmon III Q1.79694million wet tonnes/year for pink/chum/sockeye,2000–2014; derived Q/B2.246175 with2019B0.8. Jellyfish Q3.1771million wet tonnes/year covers2006–2014 and different stock5.0975million tonnes. Its independently converted copepod/euphausiid/chaetognath food gives carbon Q≥0.209584623, enough for the illustrative carbon energy minimum, but its feeding links are absent from the Figure-only network. These are alternate supporting-source evidence, not a validated mixed-source model.

## Biomass accumulation

Methods/prose and supporting source surveys supply no matching group-specific annual living BA/net migration/catch values or explicit closed steady-state assertion. All corresponding unknowns are preserved. Detritus BA is an allowed residual, calculable after complete living budgets; stock depletion feasibility would require an initial detritus stock.

## Import validation and converter audit

Eight mandatory imports are in import_tables/, writer override --dir-name import_tables documented there. Import validation:0 errors,9 warnings. Wet mass-balance checker:10 errors,9 warnings,2 notes(4 energy and6 predation flags). Its inferred detritus count and under-counted microbial feeding are artifacts of missing basics, not evidence of actual extra detritus pools. Dedicated22-group carbon/flow audits govern scientific interpretation.

The raw database conversion is retained but rejected:19 groups, omitted2/3/22, wrongly classified4/5 as producers, sole-detritus routing lost. Its native check reports4 errors/6 indeterminate/7 warnings, and does not establish native loadability. The faithful parent model.json preserves all22 groups and440 diet cells. No normalization or fitted source values was used to force balance.

## Text supplementation

The user's2026-10-03 instruction to inspect whether Figure 9 omits links is handled in ../../research_20261003/text_feeding_audit/. The strict Figure-only revision is preserved. Any extra prose-supported links or fractions are separate evidence, with unallocated remainder and qualitative links retained as unknowns. See that audit's FINDINGS.md for the exact completeness wording and extraction; do not conflate a generalized scheme with an explicit claim about all omitted arrows.

## English article

The complete 26-page unofficial English PDF is in the papers/OKH-GM2019 source bundle. All311 table numbers and original Figure 9 pixels were checked; source inconsistencies were preserved. Original Russian sources remain authoritative.
