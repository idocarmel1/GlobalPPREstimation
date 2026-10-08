# Griffiths2019 versus WCP2007 option 1

**The new supplement does not currently make Griffiths2019 a stronger runnable candidate than WCP2007 option 1.** Its final tables have now been extracted and independently verified, but reveal substantial source balance inconsistencies and omit numerical routing for its two non-living pools. Option 1 is specifically the existing experimental **D_fixed_M0** scenario, not A_fixed_EE and not the unchanged WCP2007 source. It returns WARN for all three requested methods; it is not an adopted or native-validated correction.

| Criterion | Griffiths2019 source reconstruction | WCP2007 option1: D_fixed_M0 |
|---|---|---|
| Source structure | 46 groups, baseline2005, 2 detritus pools | 31 groups, mixed-period source, single detritus pool |
| Extraction | Eight imports, taxonomy, canonical JSON and reconstruction created; unknowns preserved | Existing extraction plus isolated experimental juvenile correction |
| Diet transcription | All567 nonzero final S3 cells match DOCX grid and rendered PDF coordinates | Existing verified source; computational loader normalizes rounded diets |
| GE | Not run: loader routing block | WARN; PP budget OK |
| TE | Not run: loader routing block | WARN; PP budget OK |
| With Egestion | Not run: loader routing block | WARN; PP budget OK |
| Main numerical concern | Pomfret used-production residual7128.07195% of production; catch-total conflicts | Remaining maximum production residual0.727940%, adult bigeye |
| Scientific limitation | Missing native routing/GS/return settings and inconsistent published tables | Hypothetical independent-group repair; native multistanza consistency unverified |

The percentages above concern distinct evidence: Griffiths is an independent check of the exact source production equation, whereas WCP's value is the returned diagnostic on the existing loaded experimental model. Griffiths is not being assigned a fabricated diagnostic FAIL or WARN.

## What the supplied supplement changed

The exact4,115,453-byte DOCX is archived. Its final S3 is46 prey rows ×42 consumer columns, with567 nonzero cells; initial S2 is excluded. S4 fleet values and totals were cross-checked against a68-page Word-rendered PDF. Every nonzero diet and every nonblank catch/total matched. The earlier retrieval-only block is historical, not the current explanation.

Source-faithful imports preserve exact fleet cells, scaled once by1e-6, and computed fleet sums. Twenty-two printed Total cells disagree with their fleets. For example, small bigeye landings sum631.834 versus printed2431.834; large bigeye sum498.591 versus printed57.591, in the printed1e-6 units. Both alternatives are retained in the audit, with no model repair. Areas also differ between main-paper domain and several input derivations; no density was silently rescaled.

Pomfret is the clearest balance contradiction. Table1 gives P=0.000294752 and P×EE=0.0002800144 t/km²/year. S3 yields predation0.02128530003 before catch. Large yellowfin alone consumes0.00587225986—about19.92 times the printed Pomfret production. This persists with either catch-total convention and cannot be explained by the small diet-rounding error. The source does not identify which value/native version is wrong.

Two admission attempts, retaining the source diet and testing both strict GS and ordinary GS-default behavior, stop at the same documented multi-detritus error. Missing natural M0/egestion routing and the separate fleet-discard-return representation are distinct issues. The qualitative suspended-discard-pool description does not supply the needed numerical matrix. Neither pooling nor guessed routing was used to force a run.

## Exact benchmark identity and evidence

WCP option1 preserves the original juvenile other-mortality flow M0 while increasing production: small bigeye PB1.4129713563375232 / EE0.7898725981469387; small yellowfin PB2.5304972811160384 / EE0.8816702937266387. Existing B, QB, diet and catch are unchanged by that scenario. It is an experimental explanation of missing fishing turnover, not a recovered source correction. Other loader-completed flows and remaining discrepancies are retained.

The saved D_fixed_M0 diagnostics were reused without rerunning. Their PP budget gaps are GE0.097858%, TE0.134701%, With Egestion0.024524%; each budget check is OK. All solves converge with zero negative source columns, but the remaining adult-bigeye production residual and method warnings keep overall status at WARN. The original unmodified WCP2007 returns FAIL and must not be mislabeled as this option.

`WCP_OPTION1_SAVED_DIRECT_DIAGNOSTICS.json` contains only the full saved three direct diagnostic returns. Original paths and SHA-256 values are recorded in the Griffiths diagnostics/WCP_OPTION1_REFERENCE.json. Griffiths has no direct return because construction stops before diagnose_sppr. Its LOAD_ATTEMPTS.json and CALL_OUTCOMES.json explicitly say so. No global or annual-PPR computation was made.

## Regional applicability and choice implications

| Region | Griffiths2019 target coverage | WCP2007 target coverage |
|---|---:|---:|
| HS_071 |29.09639%|57.57808%|
| EEZ_941 Kiribati Gilbert Islands |99.71577%|99.71577%|
| EEZ_598 Papua New Guinea |99.79181%|100.00000%|

These figures use the actual stored regional polygons and explicit source study rectangles, with WGS84 geodesic intersection. The parent independently added EEZ_598 to SPATIAL_OVERLAP.json. WCP-2007 is already shared with EEZ_598. The existing EEZ_941 archive home is retained; it was chosen in the earlier two-region comparison and does not exclude applicability review for Papua New Guinea.

For HS_071, WCP2007 covers substantially more of the target than Griffiths2019, although neither represents all of it. For both EEZs, geographic coverage is similarly high, so present numerical consistency and ecological scope carry more weight. Griffiths remains a broad pelagic proxy: only9.07086% of its reported ocean model area falls in EEZ_941 and20.73849% in EEZ_598. Neither source fully resolves each EEZ's coastal/reef fisheries.

If choosing a **working sensitivity scenario today**, the evidence favors retaining WCP option1 D_fixed_M0 for further scrutiny over replacing it with the currently inconsistent Griffiths reconstruction. That recommendation is conditional: D is still an unvalidated experimental correction and is not selected or published by this review. For a source-faithful production choice, obtain the original native model or author-supported corrections before adopting either repaired option. Do not rank these studies by total PPR: their domains, periods, source catches and group structures differ, and Griffiths has no valid diagnostic footprint to compare.

Allain2021 remains a separate65-group2013 model whose complete retrieved four-page report lacks the numerical input set. Its previous source review remains applicable. It was not substituted for either model.
