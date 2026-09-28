## Mass balance

Checked by `ewe_model_json_creator.py` on the assembled JSON for 3_California_Current_CAL-2016_California_Current_(2000-2014), EE tolerance 0.05.

**Verdict: BALANCED** - 0 error(s), 0 indeterminate, 32 warning(s), 2 note(s).

Biomass accumulation is unknown (-9999) for 0 of 93 group(s). A blank BA cell is treated as unknown, never as zero, so a group whose EE reconciles without BA is *consistent with* steady state rather than shown to be steady state, and a group whose EE does not reconcile is undecidable rather than wrong.

Recomputed vs printed EE: no group has both a printed EE and enough inputs to recompute one.

Groups with recomputed EE > 1: none.

P/Q outside 0.02-0.5: 60 (Common murre, 0.000), 61 (Cassin's auklet, 0.001), 62 (Rhino. auklet, 0.001), 63 (Tufted Puffin, 0.000), 64 (Cali. gull, 0.001), 65 (Western Gull, 0.001), 66 (Kittiwake, 0.000), 67 (Albatross, 0.000), 68 (Fulmar, 0.000), 69 (Shearwater, 0.000), 70 (Leach's S. Petrel, 0.000), 71 (Transient Orcas, 0.002), 72 (Resident Orcas, 0.002), 73 (Porpoises, 0.002), 74 (Humpback whale, 0.005), 75 (Minke whale, 0.006), 76 (Fin whale, 0.006), 77 (Sperm whale, 0.002), 78 (Harbor seals, 0.003), 79 (Sea Lions, 0.005), 81 (Adult N. Ele. Seal, 0.015), 82 (Fur seals, 0.002), 83 (Blue whale, 0.009), 84 (Gray whale, 0.003), 85 (Dolphins, 0.002), 86 (Brandt's corm., 0.002), 87 (Double corm., 0.001), 88 (Pelagic cormorant, 0.001), 89 (Murrelet, 0.000), 90 (Pigeon Guillemot, 0.001), 91 (Caspian tern, 0.001), 92 (Brown Pelican, 0.002).

BA: carried for 93 group(s) from `Biomass_accumulation.csv`, so the check accounts for it - 1 (phytoplankton, +0), 2 (infauna, +0), 3 (amphipods, +0), 4 (epibenthic, +0), 5 (micro-zoop, +0), 6 (copepods, +0), 7 (euphausiids, +0), 8 (carniv-zoops, +0), 9 (small jellies, +0), 10 (large jellies, +0), 11 (pandalid shp, +0), 12 (benthic shp, +0), 13 (Dungeness, +0), 14 (tanner crb, +0), 15 (mesopelagics, +0), 16 (Benthic fish, +0), 17 (surf perch, +0), 18 (Other cephal., +0), 19 (Market squid, +0), 20 (Sardine, +0), 21 (Anchovy, +0), 22 (Herring, +0), 23 (Pacific Mackerel, +0), 24 (Sand lance, +0), 25 (Whitebait smelt, +0), 26 (Other smelt, +0), 27 (Saury, +0), 28 (Juv. rock., +0), 29 (Juv. hake, +0), 30 (Juv. flat., +0), 31 (Juv. round., +0), 32 (Juv. thorny., +0), 33 (Yellowtail rock., +0), 34 (Black rock., +0), 35 (Nearshore rock., +0), 36 (Yelloweye rock., +0), 37 (Greenstriped, +0), 38 (Shelf rock., +0), 39 (Shortbelly, +0), 40 (Petrale sole, +0), 41 (Halibut, +0), 42 (Hake, +0), 43 (Lingcod, +0), 44 (Arrowtooth, +0), 45 (Sablefish, +0), 46 (Albacore, +0), 47 (Salmon, +0), 48 (Grenadiers, +0), 49 (Dogfish, +0), 50 (Canary rock., +0), 51 (P. Ocean Perch, +0), 52 (Widow rock., +0), 53 (Splitnose rock., +0), 54 (Slope rock., +0), 55 (Shortspine thorny., +0), 56 (Longspine thorny., +0), 57 (Flatfish, +0), 58 (Skates, +0), 59 (Sharks, +0), 60 (Common murre, +0), 61 (Cassin's auklet, +0), 62 (Rhino. auklet, +0), 63 (Tufted Puffin, +0), 64 (Cali. gull, +0), 65 (Western Gull, +0), 66 (Kittiwake, +0), 67 (Albatross, +0), 68 (Fulmar, +0), 69 (Shearwater, +0), 70 (Leach's S. Petrel, +0), 71 (Transient Orcas, +0), 72 (Resident Orcas, +0), 73 (Porpoises, +0), 74 (Humpback whale, +0), 75 (Minke whale, +0), 76 (Fin whale, +0), 77 (Sperm whale, +0), 78 (Harbor seals, +0), 79 (Sea Lions, +0), 80 (Juv. Ele. Seal, +0), 81 (Adult N. Ele. Seal, +0), 82 (Fur seals, +0), 83 (Blue whale, +0), 84 (Gray whale, +0), 85 (Dolphins, +0), 86 (Brandt's corm., +0), 87 (Double corm., +0), 88 (Pelagic cormorant, +0), 89 (Murrelet, +0), 90 (Pigeon Guillemot, +0), 91 (Caspian tern, +0), 92 (Brown Pelican, +0), 93 (Detritus, +0). The remaining 0 group(s) carry -9999 and are undecided where their EE does not reconcile without BA.

Migration (E) reported by the source: not represented in these files; where a source reports it the recomputed EE will legitimately differ.

### Warnings

- group 60 (Common murre): P/Q = 0.000 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 61 (Cassin's auklet): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 62 (Rhino. auklet): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 63 (Tufted Puffin): P/Q = 0.000 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 64 (Cali. gull): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 65 (Western Gull): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 66 (Kittiwake): P/Q = 0.000 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 67 (Albatross): P/Q = 0.000 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 68 (Fulmar): P/Q = 0.000 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 69 (Shearwater): P/Q = 0.000 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 70 (Leach's S. Petrel): P/Q = 0.000 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 71 (Transient Orcas): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 72 (Resident Orcas): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 73 (Porpoises): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 74 (Humpback whale): P/Q = 0.005 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 75 (Minke whale): P/Q = 0.006 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 76 (Fin whale): P/Q = 0.006 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 77 (Sperm whale): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 78 (Harbor seals): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 79 (Sea Lions): P/Q = 0.005 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 81 (Adult N. Ele. Seal): P/Q = 0.015 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 82 (Fur seals): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 83 (Blue whale): P/Q = 0.009 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 84 (Gray whale): P/Q = 0.003 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 85 (Dolphins): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 86 (Brandt's corm.): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 87 (Double corm.): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 88 (Pelagic cormorant): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 89 (Murrelet): P/Q = 0.000 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 90 (Pigeon Guillemot): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 91 (Caspian tern): P/Q = 0.001 outside the usual 0.02-0.5 range - check the P/B and Q/B columns
- group 92 (Brown Pelican): P/Q = 0.002 outside the usual 0.02-0.5 range - check the P/B and Q/B columns

### Notes

- 25 consumer(s) lack B or Q/B, so predation on their prey is under-counted and every recomputed EE below is a lower bound: 2 (infauna), 3 (amphipods), 4 (epibenthic), 5 (micro-zoop), 6 (copepods), 7 (euphausiids)
- detritus pools (1): inflow ~33.97, consumption ~0.1424 t/km^2/year, implied EE ~0.004 (indicative - export is not separated, it uses recomputed EE where the source gave none, and any unknown BA is left out of the flows entirely)

### Per-group recomputation

`EE calc` is computed without a BA term wherever BA is unknown.

| # | Group | B | P/B | Q/B | EE | EE calc | P/Q | catch | BA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | phytoplankton | - | 120 | 0 | 0.4009 | - | - | 0 | 0 |
| 2 | infauna | - | 2.5 | 12 | 0.8401 | - | 0.208 | 0 | 0 |
| 3 | amphipods | - | 3.5 | 22 | 0.8 | - | 0.159 | 0 | 0 |
| 4 | epibenthic | - | 2 | 10 | 0.8 | - | 0.2 | 0 | 0 |
| 5 | micro-zoop | - | 100 | 300 | 0.8 | - | 0.333 | 0 | 0 |
| 6 | copepods | - | 14 | 70 | 0.8 | - | 0.2 | 0 | 0 |
| 7 | euphausiids | - | 8 | 40 | 0.8 | - | 0.2 | 0 | 0 |
| 8 | carniv-zoops | - | 2 | 10 | 0.8 | - | 0.2 | 0 | 0 |
| 9 | small jellies | - | 9 | 30 | 0.8 | - | 0.3 | 0 | 0 |
| 10 | large jellies | - | 3 | 12 | 0.8 | - | 0.25 | 0 | 0 |
| 11 | pandalid shp | - | 2 | 10 | 0.8 | - | 0.2 | 0.1056 | 0 |
| 12 | benthic shp | - | 2.5 | 12 | 0.8 | - | 0.208 | 0.0001026 | 0 |
| 13 | Dungeness | - | 0.75 | 3.8 | 0.6417 | - | 0.197 | 0.09198 | 0 |
| 14 | tanner crb | - | 0.3 | 1.5 | 0.8 | - | 0.2 | 0 | 0 |
| 15 | mesopelagics | 9.934 | 0.6 | 3 | - | 0.424 | 0.2 | 0 | 0 |
| 16 | Benthic fish | - | 0.5 | 2.5 | 0.8 | - | 0.2 | 0 | 0 |
| 17 | surf perch | - | 1.3 | 6 | 0.8 | - | 0.217 | 0 | 0 |
| 18 | Other cephal. | - | 2 | 6 | 0.8 | - | 0.333 | 0 | 0 |
| 19 | Market squid | - | 2.75 | 10 | 0.8 | - | 0.275 | 0.267 | 0 |
| 20 | Sardine | 3.241 | 0.515 | 5 | - | 0.842 | 0.103 | 0.4875 | 0 |
| 21 | Anchovy | 1.502 | 1.09 | 6 | - | 0.829 | 0.182 | 0.03866 | 0 |
| 22 | Herring | 0.6623 | 1.6 | 7.489 | - | 0.868 | 0.214 | 0.006461 | 0 |
| 23 | Pacific Mackerel | 0.4918 | 0.514 | 6 | - | 0.503 | 0.0857 | 0.02689 | 0 |
| 24 | Sand lance | - | 1 | 3.65 | 0.8 | - | 0.274 | 0 | 0 |
| 25 | Whitebait smelt | 0.08027 | 1.6 | 6 | - | 0.65 | 0.267 | 0 | 0 |
| 26 | Other smelt | - | 1.5 | 6 | 0.8 | - | 0.25 | 0 | 0 |
| 27 | Saury | 1.15 | 1.6 | 3.65 | - | 0.152 | 0.438 | 0 | 0 |
| 28 | Juv. rock. | - | 1.5 | 6 | 0.8 | - | 0.25 | 0 | 0 |
| 29 | Juv. hake | - | 1.75 | 6.101 | 0.8 | - | 0.287 | 0 | 0 |
| 30 | Juv. flat. | - | 1 | 4 | 0.8 | - | 0.25 | 0 | 0 |
| 31 | Juv. round. | - | 1.5 | 5.125 | 0.8 | - | 0.293 | 0 | 0 |
| 32 | Juv. thorny. | - | 0.5 | 2.5 | 0.8 | - | 0.2 | 0 | 0 |
| 33 | Yellowtail rock. | 0.5452 | 0.146 | 1.7 | - | 0.761 | 0.0859 | 0.01377 | 0 |
| 34 | Black rock. | 0.1242 | 0.129 | 2.01 | - | 0.738 | 0.0642 | 0.003147 | 0 |
| 35 | Nearshore rock. | 0.08012 | 0.158 | 2.01 | - | 0.672 | 0.0786 | 0.001686 | 0 |
| 36 | Yelloweye rock. | 0.008984 | 0.0505 | 2.2 | - | 0.154 | 0.023 | 4.4e-05 | 0 |
| 37 | Greenstriped | 0.09782 | 0.125 | 2.2 | - | 0.474 | 0.0568 | 0.0001251 | 0 |
| 38 | Shelf rock. | 0.44 | 0.159 | 2.2 | - | 0.595 | 0.0723 | 0.001528 | 0 |
| 39 | Shortbelly | 0.3603 | 0.26 | 2.2 | - | 0.866 | 0.118 | 2.48e-08 | 0 |
| 40 | Petrale sole | 0.07856 | 0.32 | 1.7 | - | 0.889 | 0.188 | 0.005351 | 0 |
| 41 | Halibut | 0.1851 | 0.47 | 2.12 | - | 0.0803 | 0.222 | 0.003187 | 0 |
| 42 | Hake | 8.044 | 0.41 | 1.957 | - | 0.783 | 0.21 | 0.9469 | 0 |
| 43 | Lingcod | 0.3125 | 0.295 | 2.4 | - | 0.652 | 0.123 | 0.003636 | 0 |
| 44 | Arrowtooth | 0.3441 | 0.264 | 2.12 | - | 0.616 | 0.125 | 0.0342 | 0 |
| 45 | Sablefish | 0.8962 | 0.0984 | 2 | - | 0.686 | 0.0492 | 0.02502 | 0 |
| 46 | Albacore | 0.09562 | 0.36 | 7.3 | - | 0.106 | 0.0493 | 0.003645 | 0 |
| 47 | Salmon | 0.1246 | 1.76 | 5.3 | - | 0.949 | 0.332 | 0.02537 | 0 |
| 48 | Grenadiers | 0.3644 | 0.2 | 1 | - | 0.444 | 0.2 | 0.0003644 | 0 |
| 49 | Dogfish | 0.8591 | 0.0694 | 2.5 | - | 0.949 | 0.0278 | 0.004742 | 0 |
| 50 | Canary rock. | 0.07756 | 0.113 | 1.66 | - | 0.648 | 0.0681 | 0.00218 | 0 |
| 51 | P. Ocean Perch | 0.1009 | 0.0689 | 2.07 | - | 0.971 | 0.0333 | 0.002278 | 0 |
| 52 | Widow rock. | 0.2594 | 0.1287 | 2.2 | - | 0.982 | 0.0585 | 0.00509 | 0 |
| 53 | Splitnose rock. | 0.3367 | 0.07478 | 1.91 | - | 0.941 | 0.0392 | 0.001206 | 0 |
| 54 | Slope rock. | 0.2303 | 0.06465 | 1.91 | - | 0.919 | 0.0338 | 0.003044 | 0 |
| 55 | Shortspine thorny. | 1.098 | 0.0545 | 0.47 | - | 0.527 | 0.116 | 0.003502 | 0 |
| 56 | Longspine thorny. | 0.3088 | 0.1213 | 0.35 | - | 0.939 | 0.347 | 0.003078 | 0 |
| 57 | Flatfish | 3.569 | 0.35 | 2 | - | 0.783 | 0.175 | 0.04902 | 0 |
| 58 | Skates | 0.4024 | 0.2216 | 2 | - | 0.49 | 0.111 | 0.003941 | 0 |
| 59 | Sharks | - | 0.18 | 2.8 | 0.75 | - | 0.0643 | 0.002676 | 0 |
| 60 | Common murre | 0.003272 | 0.08409 | 169.5 | - | 0 | 0.000496 | 0 | 0 |
| 61 | Cassin's auklet | 0.001226 | 0.2339 | 266.9 | - | 0 | 0.000876 | 0 | 0 |
| 62 | Rhino. auklet | 0.0002763 | 0.119 | 202.2 | - | 0 | 0.000588 | 0 | 0 |
| 63 | Tufted Puffin | 0.000181 | 0.065 | 181.1 | - | 0 | 0.000359 | 0 | 0 |
| 64 | Cali. gull | 0.0006518 | 0.1353 | 193.9 | - | 0 | 0.000698 | 0 | 0 |
| 65 | Western Gull | 0.0009632 | 0.1322 | 168.7 | - | 0 | 0.000784 | 0 | 0 |
| 66 | Kittiwake | 0.000127 | 0.09289 | 216.2 | - | 0 | 0.00043 | 0 | 0 |
| 67 | Albatross | 0.0007513 | 0.04042 | 124.2 | - | 0 | 0.000325 | 0 | 0 |
| 68 | Fulmar | 0.0002405 | 0.04338 | 199.7 | - | 0 | 0.000217 | 0 | 0 |
| 69 | Shearwater | 0.003636 | 0.07 | 182.8 | - | 0 | 0.000383 | 0 | 0 |
| 70 | Leach's S. Petrel | 0.000596 | 0.124 | 407.9 | - | 0 | 0.000304 | 0 | 0 |
| 71 | Transient Orcas | 0.002673 | 0.02542 | 14.88 | - | 0 | 0.00171 | 0 | 0 |
| 72 | Resident Orcas | 0.001095 | 0.02542 | 14.88 | - | 0 | 0.00171 | 0 | 0 |
| 73 | Porpoises | 0.02651 | 0.07 | 36.52 | - | 0.0902 | 0.00192 | 0 | 0 |
| 74 | Humpback whale | 0.2499 | 0.0377 | 7.58 | - | 0.0838 | 0.00497 | 0 | 0 |
| 75 | Minke whale | 0.005196 | 0.0511 | 8.69 | - | 0.124 | 0.00588 | 0 | 0 |
| 76 | Fin whale | 0.1401 | 0.0377 | 6.517 | - | 0.168 | 0.00578 | 0 | 0 |
| 77 | Sperm whale | 0.01829 | 0.021 | 8.812 | - | 0.238 | 0.00238 | 0 | 0 |
| 78 | Harbor seals | 0.01962 | 0.08265 | 24.59 | - | 0.0564 | 0.00336 | 0 | 0 |
| 79 | Sea Lions | 0.09872 | 0.076 | 15.1 | - | 0.118 | 0.00503 | 0 | 0 |
| 80 | Juv. Ele. Seal | 0.03795 | 0.3104 | 14.76 | - | 0 | 0.021 | 0 | 0 |
| 81 | Adult N. Ele. Seal | 0.0775 | 0.2276 | 14.76 | - | 0.0106 | 0.0154 | 0 | 0 |
| 82 | Fur seals | 0.007867 | 0.091 | 52.04 | - | 0.0382 | 0.00175 | 0 | 0 |
| 83 | Blue whale | 0.6394 | 0.05 | 5.5 | - | 0.0653 | 0.00909 | 0 | 0 |
| 84 | Gray whale | 0.9735 | 0.037 | 11.83 | - | 0.116 | 0.00313 | 0 | 0 |
| 85 | Dolphins | 0.07128 | 0.07563 | 32.33 | - | 0.0835 | 0.00234 | 0 | 0 |
| 86 | Brandt's corm. | 0.0007252 | 0.235 | 138.1 | - | 0 | 0.0017 | 0 | 0 |
| 87 | Double corm. | 0.0003644 | 0.15 | 147 | - | 0 | 0.00102 | 0 | 0 |
| 88 | Pelagic cormorant | 0.0002634 | 0.15 | 142.6 | - | 0 | 0.00105 | 0 | 0 |
| 89 | Murrelet | 2.78e-05 | 0.1208 | 255.1 | - | 0 | 0.000473 | 0 | 0 |
| 90 | Pigeon Guillemot | 9.5e-05 | 0.175 | 205.9 | - | 0 | 0.00085 | 0 | 0 |
| 91 | Caspian tern | 9.36e-05 | 0.1089 | 189.9 | - | 0 | 0.000573 | 0 | 0 |
| 92 | Brown Pelican | 0.0002703 | 0.2 | 120.7 | - | 0 | 0.00166 | 0 | 0 |
| 93 | Detritus | 10 | 0 | 0 | - | - | - | 0 | 0 |
