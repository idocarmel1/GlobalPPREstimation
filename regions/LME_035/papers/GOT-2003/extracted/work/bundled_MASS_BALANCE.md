## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 35_Gulf_of_Thailand_35_1_Gulf_of_Thailand_(1973), EE tolerance 0.05.

**Verdict: BALANCED** - 0 error(s), 0 indeterminate, 35 warning(s), 3 note(s).

Biomass accumulation is unknown (-9999) for 0 of 40 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 2.736, group 2 (Scomberomorus spp.).

Groups with recomputed EE > 1: none.

P/Q outside 0.02-0.5: 31 (Mammals, 0.002).

BA: carried for 40 group(s) from `Biomass_accumulation.csv`, so the check accounts for it - 1 (Rastrelliger spp., +0), 2 (Scomberomorus spp., -0.003), 3 (Carangidae, -0.007), 4 (Pomfret, +0.001), 5 (Small pelagic fish, +0), 6 (False trevally, +0), 7 (Large piscivores, -0.001), 8 (Sciaenidae, +0), 9 (Saurida spp., +0.012), 10 (Lutianidae, -0.004), 11 (Plectorhynchidae, +0), 12 (Priacanthus spp., +0), 13 (Sillago spp., +0.086), 14 (Nemipterus spp., -0.004), 15 (Ariidae, -0.006), 16 (Rays, -0.01), 17 (Sharks, -0.005), 18 (Cephalopod, -0.1), 19 (Shrimps, +0), 20 (Crab Lobster, +0), 21 (Trashfish, -0.045), 22 (Small demersal fish, +0), 23 (Medium demersal piscivore, +0), 24 (Medium demersal benthivore, -0.042), 25 (Shellfish, +0), 26 (Jellyfish, +0), 27 (Sea cucumber, +0), 28 (Seaweeds, +0), 29 (Coastal tuna, +0), 30 (Sergestid shrimp, +0), 31 (Mammals, +0), 32 (Pony fishes, +0), 33 (Benthos, +0), 34 (Zooplankton, +0), 35 (Juvenile small pelagics, +0), 36 (Juvenile Caranx spp., +0), 37 (Juvenile Saurida spp., +0), 38 (Juvenile Nemipterus spp., +0), 39 (Phytoplankton, +0), 40 (Detritus, +0). The remaining 0 group(s) carry -9999 and are undecided where their EE does not reconcile without BA.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Warnings

- group 1 (Rastrelliger spp.): printed EE 0.95 vs recomputed 0.816 (diff 0.134), BA 0 carried
- group 2 (Scomberomorus spp.): printed EE 0.95 vs recomputed -1.786 (diff 2.736), BA -0.003 carried
- group 3 (Carangidae): printed EE 0.95 vs recomputed 0.145 (diff 0.805), BA -0.007 carried
- group 4 (Pomfret): printed EE 0.95 vs recomputed 0.568 (diff 0.382), BA 0.001 carried
- group 5 (Small pelagic fish): printed EE 0.95 vs recomputed 0.884 (diff 0.066), BA 0 carried
- group 6 (False trevally): printed EE 0.95 vs recomputed 0.167 (diff 0.783), BA 0 carried
- group 7 (Large piscivores): printed EE 0.68 vs recomputed 0.262 (diff 0.418), BA -0.001 carried
- group 8 (Sciaenidae): printed EE 0.95 vs recomputed 0.860 (diff 0.090), BA 0 carried
- group 10 (Lutianidae): printed EE 0.54 vs recomputed 0.391 (diff 0.149), BA -0.004 carried
- group 11 (Plectorhynchidae): printed EE 0.95 vs recomputed 0.469 (diff 0.481), BA 0 carried
- group 12 (Priacanthus spp.): printed EE 0.3 vs recomputed 0.204 (diff 0.096), BA 0 carried
- group 13 (Sillago spp.): printed EE 0.95 vs recomputed 0.401 (diff 0.549), BA 0.086 carried
- group 14 (Nemipterus spp.): printed EE 0.66 vs recomputed 0.129 (diff 0.531), BA -0.004 carried
- group 15 (Ariidae): printed EE 0.68 vs recomputed 0.250 (diff 0.430), BA -0.006 carried
- group 16 (Rays): printed EE 0.26 vs recomputed 0.125 (diff 0.135), BA -0.01 carried
- group 17 (Sharks): printed EE 0.57 vs recomputed 0.462 (diff 0.108), BA -0.005 carried
- group 18 (Cephalopod): printed EE 0.82 vs recomputed 0.438 (diff 0.382), BA -0.1 carried
- group 19 (Shrimps): printed EE 0.95 vs recomputed 0.226 (diff 0.724), BA 0 carried
- group 20 (Crab Lobster): printed EE 0.95 vs recomputed 0.010 (diff 0.940), BA 0 carried
- group 21 (Trashfish): printed EE 0.88 vs recomputed 0.590 (diff 0.290), BA -0.045 carried
- group 22 (Small demersal fish): printed EE 0.95 vs recomputed 0.717 (diff 0.233), BA 0 carried
- group 23 (Medium demersal piscivore): printed EE 0.47 vs recomputed 0.021 (diff 0.449), BA 0 carried
- group 24 (Medium demersal benthivore): printed EE 0.59 vs recomputed -0.190 (diff 0.780), BA -0.042 carried
- group 25 (Shellfish): printed EE 0.95 vs recomputed 0.840 (diff 0.110), BA 0 carried
- group 29 (Coastal tuna): printed EE 0.95 vs recomputed 0.724 (diff 0.226), BA 0 carried
- group 30 (Sergestid shrimp): printed EE 0.95 vs recomputed 0.080 (diff 0.870), BA 0 carried
- group 31 (Mammals): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 32 (Pony fishes): printed EE 0.95 vs recomputed 0.175 (diff 0.775), BA 0 carried
- group 33 (Benthos): printed EE 0.65 vs recomputed 0.003 (diff 0.647), BA 0 carried
- group 34 (Zooplankton): printed EE 0.2 vs recomputed 0.000 (diff 0.200), BA 0 carried
- group 35 (Juvenile small pelagics): printed EE 0.95 vs recomputed 0.329 (diff 0.621), BA 0 carried
- group 36 (Juvenile Caranx spp.): printed EE 0.95 vs recomputed 0.262 (diff 0.688), BA 0 carried
- group 37 (Juvenile Saurida spp.): printed EE 0.95 vs recomputed 0.600 (diff 0.350), BA 0 carried
- group 38 (Juvenile Nemipterus spp.): printed EE 0.95 vs recomputed 0.661 (diff 0.289), BA 0 carried
- group 39 (Phytoplankton): printed EE 0.44 vs recomputed 0.000 (diff 0.440), BA 0 carried

### Notes

- 23 consumer(s) lack B or Q/B, so predation on their prey is under-counted and every recomputed EE below is a lower bound: 1 (Rastrelliger spp.), 5 (Small pelagic fish), 7 (Large piscivores), 8 (Sciaenidae), 9 (Saurida spp.), 10 (Lutianidae)
- 4 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 2 (Scomberomorus spp.), 3 (Carangidae), 4 (Pomfret), 31 (Mammals)
- detritus pools (1): inflow ~4003, consumption ~0 t/km^2/year, implied EE ~0.000 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Rastrelliger spp. | 0.187 | 3 | - | 0.95 | 0.816 | - | 0.166 | 0 |
| 2 | Scomberomorus spp. | 0.016 | 0.07 | 0.35 | 0.95 | -1.79 | 0.2 | 0.001 | -0.003 |
| 3 | Carangidae | 0.083 | 1.34 | 5.37 | 0.95 | 0.145 | 0.25 | 0.022 | -0.007 |
| 4 | Pomfret | 0.008 | 0.88 | 4.418 | 0.95 | 0.568 | 0.199 | 0.003 | 0.001 |
| 5 | Small pelagic fish | 0.452 | 3 | - | 0.95 | 0.884 | - | 0.113 | 0 |
| 6 | False trevally | 0.003 | 2 | - | 0.95 | 0.167 | - | 0.001 | 0 |
| 7 | Large piscivores | 0.054 | 1.2 | - | 0.68 | 0.262 | - | 0.018 | -0.001 |
| 8 | Sciaenidae | 0.031 | 1.5 | - | 0.95 | 0.86 | - | 0.04 | 0 |
| 9 | Saurida spp. | 0.054 | 2 | - | 0.44 | 0.407 | - | 0.032 | 0.012 |
| 10 | Lutianidae | 0.016 | 0.8 | - | 0.54 | 0.391 | - | 0.009 | -0.004 |
| 11 | Plectorhynchidae | 0.008 | 0.8 | - | 0.95 | 0.469 | - | 0.003 | 0 |
| 12 | Priacanthus spp. | 0.071 | 2 | - | 0.3 | 0.204 | - | 0.029 | 0 |
| 13 | Sillago spp. | 0.111 | 2 | - | 0.95 | 0.401 | - | 0.003 | 0.086 |
| 14 | Nemipterus spp. | 0.093 | 2.5 | - | 0.66 | 0.129 | - | 0.034 | -0.004 |
| 15 | Ariidae | 0.018 | 2 | - | 0.68 | 0.25 | - | 0.015 | -0.006 |
| 16 | Rays | 0.048 | 0.5 | - | 0.26 | 0.125 | - | 0.013 | -0.01 |
| 17 | Sharks | 0.013 | 0.5 | - | 0.57 | 0.462 | - | 0.008 | -0.005 |
| 18 | Cephalopod | 0.344 | 2 | - | 0.82 | 0.438 | - | 0.151 | -0.1 |
| 19 | Shrimps | 0.232 | 5 | - | 0.95 | 0.226 | - | 0.218 | 0 |
| 20 | Crab Lobster | 3.52 | 3 | - | 0.95 | 0.0103 | - | 0.109 | 0 |
| 21 | Trashfish | 0.524 | 4 | - | 0.88 | 0.59 | - | 0.694 | -0.045 |
| 22 | Small demersal fish | 0.158 | 3 | - | 0.95 | 0.717 | - | 0.042 | 0 |
| 23 | Medium demersal piscivore | 0.024 | 2 | - | 0.47 | 0.0208 | - | 0.001 | 0 |
| 24 | Medium demersal benthivore | 0.092 | 2 | - | 0.59 | -0.19 | - | 0.007 | -0.042 |
| 25 | Shellfish | 0.169 | 3 | - | 0.95 | 0.84 | - | 0.426 | 0 |
| 26 | Jellyfish | 2 | 5 | - | 0 | 0 | - | 0 | 0 |
| 27 | Sea cucumber | 1 | 4.5 | - | 0 | 0 | - | 0 | 0 |
| 28 | Seaweeds | 1 | 15 | - | 0 | 0 | - | 0 | 0 |
| 29 | Coastal tuna | 0.019 | 0.8 | - | 0.95 | 0.724 | - | 0.011 | 0 |
| 30 | Sergestid shrimp | 0.051 | 10 | - | 0.95 | 0.0804 | - | 0.041 | 0 |
| 31 | Mammals | 0.1 | 0.05 | 30 | 0 | 0 | 0.00167 | 0 | 0 |
| 32 | Pony fishes | 0.066 | 3.5 | - | 0.95 | 0.175 | - | 0 | 0 |
| 33 | Benthos | 33 | 5 | - | 0.65 | 0.00332 | - | 0 | 0 |
| 34 | Zooplankton | 17.3 | 40 | - | 0.2 | 0.000489 | - | 0 | 0 |
| 35 | Juvenile small pelagics | 0.073 | 4 | - | 0.95 | 0.329 | - | 0.096 | 0 |
| 36 | Juvenile Caranx spp. | 0.025 | 4 | - | 0.95 | 0.262 | - | 0.026 | 0 |
| 37 | Juvenile Saurida spp. | 0.018 | 4 | - | 0.95 | 0.6 | - | 0.043 | 0 |
| 38 | Juvenile Nemipterus spp. | 0.022 | 4 | - | 0.95 | 0.661 | - | 0.058 | 0 |
| 39 | Phytoplankton | 30 | 200 | - | 0.44 | 0 | - | 0 | 0 |
| 40 | Detritus | 1e+04 | - | - | 0.17 | - | - | 0 | 0 |
