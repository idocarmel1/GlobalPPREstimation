# Mass balance

**Verdict: NOT BALANCED as the published tables are transcribed.** This verdict concerns the available reconstruction, not a claim that the authors failed to balance their unpublished model.

This final analysis uses the corrected database JSON, exact unnormalized diet proportions, stated biomass/catch/BA, and the source P/Q (database ge). When Q/B is dashed but P/Q is stated, Q/B = (P/B)/(P/Q) is calculated for arithmetic only; no derived Q/B is written to the import files or database. The bundled raw calculation and its normalized database result are retained only as working evidence.

Q/B is derived internally for 33 consumers. Ten consumers have no positive diet entries: 6, 12, 22, 26, 27, 32, 35, 36, 37, 38. Their predation is unreported, so recomputed prey demands are lower bounds. Missing catch for nine groups is likewise treated as zero only for this lower-bound calculation. No unknown detritus fate or assimilation fraction is supplied.

8 groups have lower-bound recomputed EE > 1: 1 (Rastrelliger spp., 1.044), 2 (Scomberomorus spp., 1.116), 4 (Pomfret, 5.386), 5 (Small pelagic fish, 1.072), 22 (Small demersal fish, 1.357), 23 (Medium demersal piscivore, 1.798), 25 (Shellfish, 1.064), 35 (Juvenile small pelagics, 1.127).
31 groups differ from printed EE by more than 0.05; maximum absolute difference 4.436 at group 4 (Pomfret).

Every group has a source-stated absolute BA, including 26 printed zeros and 14 nonzero entries. No BA is inferred to close a gap. Migration terms were not reported in the chapter; they cannot be used to reconcile the discrepancies.

Mammals P/Q = 0.05 / 30.00 = 0.001667 is unusually low and was visually verified in Table 1, printed p.369. The other stated P/Q values are 0.20 or 0.25. Assimilation is not reported, so positive respiration cannot be proved without an import assumption. Under the EwE GS = 0.2 assumption, none implies non-positive respiration; that assumption is not extracted as data. Detritus-pool balance is undecidable because routing and GS are unreported.

The overproduction flags are supported by verified Table 1 B/PB/BA, Table 2 catch, and Table 3 feeding values. Known diet columns with sums above one inflate consumption, but normalizing them would alter the publication and is prohibited. Some EE mismatches can also reflect the conflicting catch versions discussed in REPORT.md.

| Group | Name | Printed EE | Recomputed lower-bound EE | Reported catch | BA |
|---|---|---|---|---|---|
| 1 | Rastrelliger spp. | 0.95 | 1.0439 | 0.166 | 0 |
| 2 | Scomberomorus spp. | 0.95 | 1.1161 | 0.001 | -0.003 |
| 3 | Carangidae | 0.95 | 0.6187 | 0.022 | -0.007 |
| 4 | Pomfret | 0.95 | 5.3864 | 0.003 | 0.001 |
| 5 | Small pelagic fish | 0.95 | 1.0722 | 0.113 | 0 |
| 6 | False trevally | 0.95 | 0.8000 | 0.001 | 0 |
| 7 | Large piscivores | 0.68 | 0.3242 | 0.018 | -0.001 |
| 8 | Sciaenidae | 0.95 | 0.8602 | 0.04 | 0 |
| 9 | Saurida spp. | 0.44 | 0.4074 | 0.032 | 0.012 |
| 10 | Lutianidae | 0.54 | 0.6445 | 0.009 | -0.004 |
| 11 | Plectorhynchidae | 0.95 | 0.4688 | 0.003 | 0 |
| 12 | Priacanthus spp. | 0.30 | 0.4183 | 0.029 | 0 |
| 13 | Sillago spp. | 0.95 | 0.5295 | 0.003 | 0.086 |
| 14 | Nemipterus spp. | 0.66 | 0.4220 | 0.034 | -0.004 |
| 15 | Ariidae | 0.68 | 0.2500 | 0.015 | -0.006 |
| 16 | Rays | 0.26 | 0.1250 | 0.013 | -0.01 |
| 17 | Sharks | 0.57 | 0.4615 | 0.008 | -0.005 |
| 18 | Cephalopod | 0.82 | 0.7299 | 0.151 | -0.1 |
| 19 | Shrimps | 0.95 | 0.6341 | 0.218 | 0 |
| 20 | Crab Lobster | 0.95 | 0.0104 | 0.109 | 0 |
| 21 | Trashfish | 0.88 | 0.9162 | 0.694 | -0.045 |
| 22 | Small demersal fish | 0.95 | 1.3566 | 0.042 | 0 |
| 23 | Medium demersal piscivore | 0.47 | 1.7979 | 0.001 | 0 |
| 24 | Medium demersal benthivore | 0.59 | 0.8638 | 0.007 | -0.042 |
| 25 | Shellfish | 0.95 | 1.0635 | 0.426 | 0 |
| 26 | Jellyfish | 0.00 | 0.0000 | unknown | 0 |
| 27 | Sea cucumber | 0.00 | 0.0000 | unknown | 0 |
| 28 | Seaweeds | 0.00 | 0.0000 | unknown | 0 |
| 29 | Coastal tuna | 0.95 | 0.9375 | 0.011 | 0 |
| 30 | Sergestid shrimp | 0.95 | 0.7134 | 0.041 | 0 |
| 31 | Mammals | 0.00 | 0.0000 | unknown | 0 |
| 32 | Pony fishes | 0.95 | 0.5274 | unknown | 0 |
| 33 | Benthos | 0.65 | 0.7944 | unknown | 0 |
| 34 | Zooplankton | 0.20 | 0.1366 | unknown | 0 |
| 35 | Juvenile small pelagics | 0.95 | 1.1269 | 0.096 | 0 |
| 36 | Juvenile Caranx spp. | 0.95 | 0.3466 | 0.026 | 0 |
| 37 | Juvenile Saurida spp. | 0.95 | 0.7175 | 0.043 | 0 |
| 38 | Juvenile Nemipterus spp. | 0.95 | 0.7575 | 0.058 | 0 |
| 39 | Phytoplankton | 0.44 | 0.4897 | unknown | 0 |
| 40 | Detritus | 0.17 | undecidable | unknown | 0 |
