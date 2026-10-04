# Sea of Okhotsk Figure 9 researcher readings variant (2000–2014)

Source: Gorbatenko and Melnikov (2019), Table 3 p154, Figure 9 p157; Gorbatenko dissertation (2018) p60 for bacteria conversion. This is a provisional derivative of the preserved extraction, not a second published model. See the parent REPORT.md, accepted_decisions.json and READINESS.json.

The writer used --dir-name import_tables to keep this variant's eight import files together. All 22 groups are retained in the intermediate extraction.json and the parent faithful model.json. The raw database converter is being checked for known omissions and must not replace the faithful parent model.

## Biomass accumulation

Living BA, fisheries and migration are unknown. The article methods/prose and supporting sources were searched; none supplies group-specific annual closure values. No explicit closed Ecopath steady state is established. Detritus imports/exports are assumed zero by the researcher; detritus BA is a residual to calculate after all living budgets exist, not zero.

## Conventions applied

GS=.2 for 20 consumers; all unassimilated consumption and other mortality route to the sole detritus group. Missing displayed feeding arrows are zero by researcher instruction. F62=.023 with .025 alternative, F67=.05 are human readings; their routes remain tentative. F77 prey15 replaces19 after visual tracing; F13 and F22 retain endpoints with improved visual confidence. Bacteria wet/C9.4 is explicit supporting evidence. Unknowns remain blank; source B and P/B are unchanged.

## Deliberate blanks

B/PB/QB for separate microbes, figure-based copepod/euphausiid QB and their six wet diet fractions, detritus wet/C and stock, EE, living catches/BA/migration. The prose has independent copepod/euphausiid QB alternatives, recorded separately. Producers and detritus have no biological GS. TL was not printed for this network.

## Unresolved and flagged

32 routes remain tentative, including three duplicate adopted prey/consumer pairs. Figure/prose consumption and Table/Figure production disagree. A source-derived conversion differs from an adopted assumption. Normalized diets and zero formatting errors do not imply balance or native loadability.

## Validation

The dedicated import checks and preserved 22-group budget audit are recorded in the parent package. Do not use the raw converter's group classifications as source evidence.

## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 52_Sea_of_Okhotsk_GM2019-Fig9_Sea_of_Okhotsk_pelagic_figure_reconstruction_(2000-2014), EE tolerance 0.05.

**Verdict: NOT BALANCED** - 4 error(s), 6 indeterminate, 7 warning(s), 0 note(s).

Biomass accumulation is unknown (-9999) for 19 of 19 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: no group has both a printed EE and enough inputs to recompute one.

Groups with recomputed EE > 1: 9 (Squid III, 6.634), 10 (Herring, 8.870), 11 (Deep-sea smelt, 2.426), 13 (Capelin, 24.433), 16 (Squid IV, 1.509), 19 (Pollock greater than 60 cm, 6.333).

P/Q outside 0.02-0.5: 6 (Hyperiids, 1.143), 7 (Chaetognaths, 0.891), 8 (Salmon, 0.914), 14 (Jellyfish, 56.700), 17 (Predatory salmon, 0.015), 18 (Baleen whales, 0.003), 20 (Predatory fish, 0.005), 21 (Predatory mammals, 0.006).

BA: not stated for any group. Every EE below is recomputed without a BA term, which is a lower bound on what the model may actually contain, not a steady-state result.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Errors

- group 6 (Hyperiids): P/Q = 1.143 with GS = 0.2 implies non-positive respiration (needs P/Q < 0.80)
- group 7 (Chaetognaths): P/Q = 0.891 with GS = 0.2 implies non-positive respiration (needs P/Q < 0.80)
- group 8 (Salmon): P/Q = 0.914 with GS = 0.2 implies non-positive respiration (needs P/Q < 0.80)
- group 14 (Jellyfish): P/Q = 56.700 with GS = 0.2 implies non-positive respiration (needs P/Q < 0.80)

### Indeterminate (BA unknown)

- group 9 (Squid III): recomputed EE = 6.634 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 10 (Herring): recomputed EE = 8.870 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 11 (Deep-sea smelt): recomputed EE = 2.426 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 13 (Capelin): recomputed EE = 24.433 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 16 (Squid IV): recomputed EE = 1.509 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation
- group 19 (Pollock greater than 60 cm): recomputed EE = 6.333 > 1 without BA, and BA is unknown - undecidable until the source is checked for biomass accumulation

### Warnings

- group 1 (Phytoplankton): only 2 of B/P-B/Q-B/EE given (B, P/B) - Ecopath needs three
- group 4 (Copepods): only 2 of B/P-B/Q-B/EE given (B, P/B) - Ecopath needs three
- group 5 (Euphausiids): only 2 of B/P-B/Q-B/EE given (B, P/B) - Ecopath needs three
- group 17 (Predatory salmon): P/Q = 0.015 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 18 (Baleen whales): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 20 (Predatory fish): P/Q = 0.005 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 21 (Predatory mammals): P/Q = 0.006 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Phytoplankton | 40.93 | 220 | - | - | 0 | - | 0 | unknown |
| 4 | Copepods | 70.14 | 15.2 | - | - | 0.221 | - | 0 | unknown |
| 5 | Euphausiids | 38.02 | 10.1 | - | - | 0.183 | - | 0 | unknown |
| 6 | Hyperiids | 3.821 | 11.7 | 10.24 | - | 0.171 | 1.14 | 0 | unknown |
| 7 | Chaetognaths | 27.66 | 6 | 6.731 | - | 0.00963 | 0.891 | 0 | unknown |
| 8 | Salmon | 0.5181 | 1.14 | 1.247 | - | 0.293 | 0.914 | 0 | unknown |
| 9 | Squid III | 0.3238 | 2.5 | 38.18 | - | 6.63 | 0.0655 | 0 | unknown |
| 10 | Herring | 1.619 | 0.34 | 13.42 | - | 8.87 | 0.0253 | 0 | unknown |
| 11 | Deep-sea smelt | 1.166 | 0.29 | 2.762 | - | 2.43 | 0.105 | 0 | unknown |
| 12 | Pollock less than 30 cm | 0.5181 | 2.5 | 20.62 | - | 0.0801 | 0.121 | 0 | unknown |
| 13 | Capelin | 0.5181 | 0.35 | 14.25 | - | 24.4 | 0.0246 | 0 | unknown |
| 14 | Jellyfish | 2.655 | 10 | 0.1764 | - | 0.00424 | 56.7 | 0 | unknown |
| 15 | Pollock 30-60 cm | 5.518 | 0.7 | 7.15 | - | 0.205 | 0.0979 | 0 | unknown |
| 16 | Squid IV | 0.3238 | 2.5 | 19.31 | - | 1.51 | 0.129 | 0 | unknown |
| 17 | Predatory salmon | 0.01295 | 0.84 | 54.37 | - | 0 | 0.0155 | 0 | unknown |
| 18 | Baleen whales | 0.467 | 0.01 | 3.13 | - | 0 | 0.0032 | 0 | unknown |
| 19 | Pollock greater than 60 cm | 0.3238 | 0.2 | 1.521 | - | 6.33 | 0.132 | 0 | unknown |
| 20 | Predatory fish | 0.07772 | 0.2 | 39.93 | - | 0 | 0.00501 | 0 | unknown |
| 21 | Predatory mammals | 0.158 | 0.03 | 4.742 | - | 0 | 0.00633 | 0 | unknown |
