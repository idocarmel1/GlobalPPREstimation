## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 22_North_Sea_ICES_WGSAM2015_North_Sea_1991_North_Sea_Rpath_port_(1991), EE tolerance 0.05.

**Verdict: BALANCED** - 0 error(s), 0 indeterminate, 5 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 0 of 69 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: max difference 0.000, group 46 (LargeDemersalFish).

Groups with recomputed EE > 1: none.

P/Q outside 0.02-0.5: 1 (BaleenWhales, 0.002), 2 (ToothedWhales, 0.001), 3 (Seals, 0.003), 4 (SurfaceFeedingSeabirds, 0.003), 65 (DivingSeabirds, 0.005).

BA: carried for 69 group(s) from `Biomass_accumulation.csv`, so the check accounts for it - 1 (BaleenWhales, +0), 2 (ToothedWhales, +0), 3 (Seals, +0), 4 (SurfaceFeedingSeabirds, +0), 5 (JuvenileSharks, +0), 6 (Spurdog, +0), 7 (LargePiscivorousSharks, +0), 8 (SmallSharks, +0), 9 (JuvenileRays, +0), 10 (StarryRayOthers, +0), 11 (ThornbackAndSpottedRay, +0), 12 (SkateCuckooRay, +0), 13 (JuvCod, +0), 14 (AduCod, +0), 15 (JuvWhiting, +0), 16 (AduWhiting, +0), 17 (JuvHaddock, +0), 18 (AduHaddock, +0), 19 (JuvSaithe, +0), 20 (AduSaithe, +0), 21 (Hake, +0), 22 (BlueWhiting, +0), 23 (NorwayPout, +0), 24 (OtherLargeGadoids, +0), 25 (OtherSmallGadoids, +0), 26 (Monkfish, +0), 27 (Gurnards, +0), 28 (JuvHerring, +0), 29 (AduHerring, +0), 30 (Sprat, +0), 31 (Mackerel, +0), 32 (HorseMackerel, +0), 33 (Sandeels, +0), 34 (Plaice, +0), 35 (Dab, +0), 36 (LongRoughDab, +0), 37 (Flounder, +0), 38 (Sole, +0), 39 (LemonSole, +0), 40 (Witch, +0), 41 (Turbot, +0), 42 (Megrim, +0), 43 (Halibut, +0), 44 (Dragonets, +0), 45 (CatfishWolfFish, +0), 46 (LargeDemersalFish, +0), 47 (SmallDemersalFish, +0), 48 (MiscellaneousFilterfeedingPelagicFish, +0), 49 (SquidAndCuttlefish, +0), 50 (FishLarvae, +0), 51 (CarnivorousZooplankton, +0), 52 (HerbivorousAndOmnivorousZooplanktonCopepods, +0), 53 (GelatinousZooplankton, +0), 54 (LargeCrabs, +0), 55 (Nephrops, +0), 56 (EpifaunalMacrobenthosMobileGrazers, +0), 57 (InfaunalMacrobenthos, +0), 58 (Shrimp, +0), 59 (SmallMobileEpifaunaSwarmingCrustaceans, +0), 60 (SmallInfaunaPolychaetes, +0), 61 (SessileEpifauna, +0), 62 (Meiofauna, +0), 63 (BenthicMicrofloraInclBacteriaProtozoa, +0), 64 (PlanktonicMicrofloraInclBacteriaProtozoa, +0), 65 (DivingSeabirds, +0), 66 (Phytoplankton, +0), 67 (DetritusDOMWaterColumn, +0), 68 (DetritusPOMSediment, +0), 69 (Discards, +0). The remaining 0 group(s) carry -9999 and are undecided where their EE does not reconcile without BA.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Warnings

- group 1 (BaleenWhales): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 2 (ToothedWhales): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 3 (Seals): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 4 (SurfaceFeedingSeabirds): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 65 (DivingSeabirds): P/Q = 0.005 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 65 group(s) carry all four of B/P-B/Q-B/EE - Ecopath needs three, so one of them is probably a published model estimate rather than an input; record which in REPORT.md: 1 (BaleenWhales), 2 (ToothedWhales), 3 (Seals), 4 (SurfaceFeedingSeabirds), 5 (JuvenileSharks), 6 (Spurdog), 7 (LargePiscivorousSharks), 8 (SmallSharks) ...
- detritus pools (3): inflow ~3882, consumption ~3602 t/km^2/year, implied EE ~0.928 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | BaleenWhales | 0.067 | 0.02 | 9.9 | 0 | 0 | 0.00202 | 0 | 0 |
| 2 | ToothedWhales | 0.017 | 0.02 | 17.63 | 0 | 0 | 0.00113 | 0 | 0 |
| 3 | Seals | 0.008 | 0.09 | 26.84 | 0 | 0 | 0.00335 | 0 | 0 |
| 4 | SurfaceFeedingSeabirds | 0.002 | 0.237 | 77.28 | 0 | 0 | 0.00307 | 0 | 0 |
| 5 | JuvenileSharks | 0.001 | 0.5 | 2.5 | 0.1943 | 0.194 | 0.2 | 0 | 0 |
| 6 | Spurdog | 0.13 | 0.48 | 2 | 0.2293 | 0.229 | 0.24 | 0.008773 | 0 |
| 7 | LargePiscivorousSharks | 0.001 | 0.44 | 1.6 | 0.6191 | 0.619 | 0.275 | 0.0002724 | 0 |
| 8 | SmallSharks | 0.002 | 0.51 | 2.96 | 0.337 | 0.337 | 0.172 | 0.0002628 | 0 |
| 9 | JuvenileRays | 0.268 | 0.66 | 1.7 | 0.005601 | 0.0056 | 0.388 | 0 | 0 |
| 10 | StarryRayOthers | 0.39 | 0.66 | 1.7 | 0.04987 | 0.0499 | 0.388 | 0.01284 | 0 |
| 11 | ThornbackAndSpottedRay | 0.066 | 0.78 | 2.3 | 0.2171 | 0.217 | 0.339 | 0.01117 | 0 |
| 12 | SkateCuckooRay | 0.05 | 0.35 | 1.8 | 0.386 | 0.386 | 0.194 | 0.006756 | 0 |
| 13 | JuvCod | 0.1002 | 1.79 | 8.012 | 0.9958 | 0.996 | 0.223 | 0.0981 | 0 |
| 14 | AduCod | 0.13 | 1.19 | 3.5 | 0.9202 | 0.92 | 0.34 | 0.1242 | 0 |
| 15 | JuvWhiting | 0.02666 | 2.36 | 17.4 | 0.9386 | 0.939 | 0.136 | 0.006583 | 0 |
| 16 | AduWhiting | 0.43 | 0.89 | 5.46 | 0.9911 | 0.991 | 0.163 | 0.2515 | 0 |
| 17 | JuvHaddock | 0.007705 | 2 | 7.685 | 0.9146 | 0.915 | 0.26 | 0.003921 | 0 |
| 18 | AduHaddock | 0.12 | 1.14 | 2.35 | 0.8508 | 0.851 | 0.485 | 0.09524 | 0 |
| 19 | JuvSaithe | 0.116 | 1 | 8.511 | 0.904 | 0.904 | 0.117 | 0.07416 | 0 |
| 20 | AduSaithe | 0.21 | 0.88 | 3.6 | 0.7156 | 0.716 | 0.244 | 0.1173 | 0 |
| 21 | Hake | 0.014 | 0.82 | 2.2 | 0.6813 | 0.681 | 0.373 | 0.005288 | 0 |
| 22 | BlueWhiting | 0.23 | 2.5 | 9.06 | 0.3336 | 0.334 | 0.276 | 0.06145 | 0 |
| 23 | NorwayPout | 1.31 | 2.2 | 5.05 | 0.9954 | 0.995 | 0.436 | 0.3339 | 0 |
| 24 | OtherLargeGadoids | 0.065 | 1 | 2.5 | 0.95 | 0.95 | 0.4 | 0.03632 | 0 |
| 25 | OtherSmallGadoids | 0.2884 | 1.8 | 4 | 0.99 | 0.99 | 0.45 | 0.02829 | 0 |
| 26 | Monkfish | 0.042 | 0.7 | 1.7 | 0.8533 | 0.853 | 0.412 | 0.02251 | 0 |
| 27 | Gurnards | 0.18 | 0.82 | 3.2 | 0.2811 | 0.281 | 0.256 | 0.008018 | 0 |
| 28 | JuvHerring | 0.1433 | 1.31 | 11.53 | 0.9723 | 0.972 | 0.114 | 0.02156 | 0 |
| 29 | AduHerring | 2.68 | 0.8 | 4.34 | 0.5723 | 0.572 | 0.184 | 0.8593 | 0 |
| 30 | Sprat | 0.579 | 2.28 | 5.28 | 0.848 | 0.848 | 0.432 | 0.1504 | 0 |
| 31 | Mackerel | 0.75 | 0.6 | 1.73 | 0.7504 | 0.75 | 0.347 | 0.2188 | 0 |
| 32 | HorseMackerel | 0.75 | 0.58 | 3.5 | 0.3533 | 0.353 | 0.166 | 0.08868 | 0 |
| 33 | Sandeels | 1.85 | 2.28 | 5.24 | 0.9907 | 0.991 | 0.435 | 0.8506 | 0 |
| 34 | Plaice | 0.58 | 0.85 | 3.42 | 0.857 | 0.857 | 0.249 | 0.381 | 0 |
| 35 | Dab | 2.8 | 0.672 | 4 | 0.2847 | 0.285 | 0.168 | 0.1576 | 0 |
| 36 | LongRoughDab | 0.35 | 0.7 | 4 | 0.557 | 0.557 | 0.175 | 0.001014 | 0 |
| 37 | Flounder | 0.25 | 1.1 | 3.2 | 0.2629 | 0.263 | 0.344 | 0.06336 | 0 |
| 38 | Sole | 0.135 | 0.8 | 3.1 | 0.9236 | 0.924 | 0.258 | 0.06175 | 0 |
| 39 | LemonSole | 0.14 | 0.864 | 4.32 | 0.5019 | 0.502 | 0.2 | 0.01469 | 0 |
| 40 | Witch | 0.082 | 0.9 | 3 | 0.3992 | 0.399 | 0.3 | 0.01633 | 0 |
| 41 | Turbot | 0.027 | 0.86 | 2.1 | 0.583 | 0.583 | 0.41 | 0.01126 | 0 |
| 42 | Megrim | 0.034 | 0.72 | 3.1 | 0.2494 | 0.249 | 0.232 | 0.003478 | 0 |
| 43 | Halibut | 0.033 | 0.16 | 3.14 | 0.2782 | 0.278 | 0.051 | 0.001336 | 0 |
| 44 | Dragonets | 0.045 | 1.44 | 6.9 | 0.9923 | 0.992 | 0.209 | 0 | 0 |
| 45 | CatfishWolfFish | 0.014 | 0.48 | 1.7 | 0.8024 | 0.802 | 0.282 | 0.005392 | 0 |
| 46 | LargeDemersalFish | 0.0252 | 0.55 | 2.54 | 0.9 | 0.9 | 0.217 | 0.008769 | 0 |
| 47 | SmallDemersalFish | 0.3645 | 1.42 | 3.7 | 0.99 | 0.99 | 0.384 | 0.1713 | 0 |
| 48 | MiscellaneousFilterfeedingPelagicFish | 0.02879 | 4 | 10.19 | 0.99 | 0.99 | 0.393 | 0.01022 | 0 |
| 49 | SquidAndCuttlefish | 0.06 | 4.5 | 15 | 0.9947 | 0.995 | 0.3 | 0.002154 | 0 |
| 50 | FishLarvae | 0.3489 | 4 | 20 | 0.99 | 0.99 | 0.2 | 0 | 0 |
| 51 | CarnivorousZooplankton | 3.149 | 4 | 12.5 | 0.99 | 0.99 | 0.32 | 0 | 0 |
| 52 | HerbivorousAndOmnivorousZooplanktonCopepods | 16 | 9.2 | 30 | 0.3847 | 0.385 | 0.307 | 0 | 0 |
| 53 | GelatinousZooplankton | 0.066 | 2.9 | 6.444 | 0.7931 | 0.793 | 0.45 | 0 | 0 |
| 54 | LargeCrabs | 1.2 | 0.55 | 2.75 | 0.9706 | 0.971 | 0.2 | 0.01434 | 0 |
| 55 | Nephrops | 0.98 | 0.37 | 1.85 | 0.9674 | 0.967 | 0.2 | 0.01906 | 0 |
| 56 | EpifaunalMacrobenthosMobileGrazers | 78 | 0.3884 | 1.942 | 0.436 | 0.436 | 0.2 | 0.006648 | 0 |
| 57 | InfaunalMacrobenthos | 136 | 1 | 3.333 | 0.2756 | 0.276 | 0.3 | 0 | 0 |
| 58 | Shrimp | 0.074 | 11 | 22 | 0.9794 | 0.979 | 0.5 | 0.1122 | 0 |
| 59 | SmallMobileEpifaunaSwarmingCrustaceans | 30 | 1.36 | 3.886 | 0.983 | 0.983 | 0.35 | 0 | 0 |
| 60 | SmallInfaunaPolychaetes | 150 | 0.9 | 3 | 0.869 | 0.869 | 0.3 | 0 | 0 |
| 61 | SessileEpifauna | 105 | 0.26 | 1.3 | 0.02844 | 0.0284 | 0.2 | 0 | 0 |
| 62 | Meiofauna | 3.821 | 35 | 125 | 0.99 | 0.99 | 0.28 | 0 | 0 |
| 63 | BenthicMicrofloraInclBacteriaProtozoa | 0.105 | 9470 | 1.894e+04 | 0.9504 | 0.95 | 0.5 | 0 | 0 |
| 64 | PlanktonicMicrofloraInclBacteriaProtozoa | 1.44 | 571 | 1142 | 0.7253 | 0.725 | 0.5 | 0 | 0 |
| 65 | DivingSeabirds | 0.004 | 0.45 | 86.97 | 0 | 0 | 0.00517 | 0 | 0 |
| 66 | Phytoplankton | 7.5 | 286.7 | - | 0.2118 | 0.212 | - | 0 | 0 |
| 67 | DetritusDOMWaterColumn | 25 | - | - | 0.9137 | - | - | 0 | 0 |
| 68 | DetritusPOMSediment | 25 | - | - | 0.9399 | - | - | 0 | 0 |
| 69 | Discards | 1e-06 | - | - | 0.9928 | - | - | 0 | 0 |
