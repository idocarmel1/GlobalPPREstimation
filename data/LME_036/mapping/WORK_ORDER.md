# Mapping work order — LME_036

catch years        : 1950-2019
taxa to map        : 374
total catch        : 387,582,302 tonnes over the whole period
Ecopath models     : 2

## Model selection — check `usable` before mapping

| author | title | usable | notes |
| --- | --- | --- | --- |
| Cheung W.L. (2007) | Vulnerability of marine fishes to fishing: from global overv | **yes** | prefer model for 2000 |

A model marked `no` must not be mapped. Say so and stop.

## Model `36_1_South_China_Sea_SCS-2007_Northern_South_China_Sea_(2000s)`

39 groups, 20 SPPR methods. Group names below are verbatim and authoritative — copy them exactly.

| seq | group_name | type | TL | biomass | model catch |
| --- | --- | --- | --- | --- | --- |
| 1 | `Phytoplankton` | PP | 1 | 323 | 0 |
| 2 | `Benthic producer` | PP | 1 | 153 | 0.0056 |
| 3 | `Zooplankton` | Regular | 2 | 9 | 0.0948 |
| 4 | `Jellyfish` | Regular | 3.104 | 1.53 | 0.044 |
| 5 | `Polychaetes` | Regular | 2 | 2.24 | 0 |
| 6 | `Echinoderms` | Regular | 2.333 | 1.98 | 0.0021 |
| 7 | `Benthic crustaceans` | Regular | 2.2 | 1.43 | 0.0391 |
| 8 | `Non-ceph molluscs` | Regular | 2.178 | 2.68 | 0.7623 |
| 9 | `Sessile/other invertebrates` | Regular | 2.6 | 2.61 | 0.003 |
| 10 | `Shrimps` | Regular | 2.314 | 0.194 | 0.6788 |
| 11 | `Crabs` | Regular | 2.524 | 0.368 | 0.1997 |
| 12 | `Cephalopods` | Regular | 3.291 | 0.68 | 0.2733 |
| 13 | `Threadfin bream (nemipterids)` | Regular | 3.211 | 0.26 | 0.657 |
| 14 | `Bigeyes (priacanthids)` | Regular | 3.472 | 0.13 | 0.206 |
| 15 | `Lizard fish (synodontids)` | Regular | 3.857 | 0.032 | 0.0234 |
| 16 | `Juvenile Hairtail (trichiurids)` | Regular | 3.878 | 0.015 | 0.028 |
| 17 | `Adult hairtail (trichiurids)` | Regular | 3.914 | 0.012 | 0.0072 |
| 18 | `Pomfret (stromateids)` | Regular | 3.587 | 0.108 | 0.239 |
| 19 | `Snappers` | Regular | 3.769 | 0.0013 | 0.0011 |
| 20 | `Adult groupers` | Regular | 3.759 | 0.0064 | 0.0089 |
| 21 | `Croakers (≤ 30 cm)` | Regular | 3.313 | 0.07 | 0.0351 |
| 22 | `Juvenile large croakers` | Regular | 3.239 | 0.04 | 0.071 |
| 23 | `Croakers (> 30 cm)` | Regular | 3.473 | 0.0094 | 0.008 |
| 24 | `Demesral fish (≤ 30 cm)` | Regular | 3.009 | 0.316 | 0.1788 |
| 25 | `Juvenile demersal fish (> 30 cm)` | Regular | 3.044 | 0.143 | 0.3165 |
| 26 | `Adult demersal fish (> 30 cm)` | Regular | 3.427 | 0.021 | 0.0352 |
| 27 | `Benthopelagic fish` | Regular | 2.781 | 0.922 | 0.6025 |
| 28 | `Melon seed` | Regular | 3.035 | 0.07 | 0.0499 |
| 29 | `Pelagic fish (≤ 30 cm)` | Regular | 2.782 | 1.772 | 2.345 |
| 30 | `Juvenile large pelagic fish` | Regular | 2.893 | 0.289 | 0.7384 |
| 31 | `Pelagic fish (> 30 cm)` | Regular | 3.367 | 0.079 | 0.0821 |
| 32 | `Demersal sharks and rays` | Regular | 3.509 | 0.001 | 0.001 |
| 33 | `Pelagic sharks and rays` | Regular | 3.99 | 0.0011 | 0.0007 |
| 34 | `Seabirds` | Regular | 3.415 | 0.0022 | 0 |
| 35 | `Pinnipeds` | Regular | 4.146 | 0.0046 | 0 |
| 36 | `Other mammals` | Regular | 3.923 | 0.0158 | 0 |
| 37 | `Marine turtles` | Regular | 2.972 | 0.0002 | 0 |
| 38 | `Detritus` | DET | 1 | 100 | 0 |
| 39 | `diet_import` | Import | 1 | 1 | 0 |

`taxon_descr` carries membership for 38 of 39 groups — use it before the paper.
- `Phytoplankton`: Phytoplankton dominated by diatoms, followed by dinoflagellates.
- `Benthic producer`: Benthic algae.
- `Zooplankton`: Acetes spp.; definition: Zooplankton; explicitly includes the landed Mo shrimp Acetes spp.
- `Jellyfish`: Medusae of Cnidaria.
- `Polychaetes`: Polychaeta.
- `Echinoderms`: Echinodermata.
- `Benthic crustaceans`: Benthic crustaceans excluding shrimps and crabs; Oratosquilla spp. supplies the P/B estimate.
- `Non-ceph molluscs`: Non-cephalopod Mollusca.
- `Sessile/other invertebrates`: Sessile and other invertebrates, separate from polychaetes, echinoderms, crustaceans and molluscs.
- `Shrimps`: Metapenaeopsis palmensis; M. barbata; definition: Shrimps including penaeids; Acetes is explicitly in Zooplankton.
- `Crabs`: Crabs.
- `Cephalopods`: Loligo edulis; L. chinensis; definition: Cephalopoda, dominated by Loligo squid.
- `Threadfin bream (nemipterids)`: Nemipterus virgatus; N. bathybius; N. japonicus; definition: Family Nemipteridae.
- `Bigeyes (priacanthids)`: Family Priacanthidae.
- `Lizard fish (synodontids)`: Saurida tumbil; S. undosquamis; definition: Family Synodontidae.
- `Juvenile Hairtail (trichiurids)`: Trichiurus lepturus; definition: Family Trichiuridae, juvenile stanza younger than 18 months.
- `Adult hairtail (trichiurids)`: Trichiurus lepturus; definition: Family Trichiuridae, adult stanza from 18 months.
- `Pomfret (stromateids)`: Family Stromateidae. Other pomfret-like families are excluded from the stated taxonomic definition.
- `Snappers`: Family Lutjanidae.
- `Adult groupers`: Family Serranidae; the final table calls this Adult groupers but supplies no separate juvenile grouper compartment.
- `Croakers (≤ 30 cm)`: Agyrosomus spp.; Pennahia spp.; Pennahia (Agyrosomus) argentatus; definition: Small Sciaenidae <=30 cm; Pennahia is explicitly listed despite differing SAU size classes.
- `Juvenile large croakers`: Larimichthys crocea; definition: Large Sciaenidae >30 cm maximum length, immature fish younger than 24 months.
- `Croakers (> 30 cm)`: Larimichthys crocea; definition: Large Sciaenidae >30 cm maximum length, adult fish from 24 months.
- `Demesral fish (≤ 30 cm)`: Demersal fish with maximum total length <=30 cm, except taxa in dedicated groups.
- `Juvenile demersal fish (> 30 cm)`: Demersal fish with maximum total length >30 cm, juvenile stanza; dedicated groups excluded.
- `Adult demersal fish (> 30 cm)`: Demersal fish with maximum total length >30 cm, adult stanza from 18 months; dedicated groups excluded.
- `Benthopelagic fish`: Final table has one Benthopelagic fish group. Appendix separately describes small <=30 cm and large >30 cm benthopelagic fish; their relationship to the final single pool is not resolved.
- `Melon seed`: Psenopsis anomala; definition: Psenopsis anomala.
- `Pelagic fish (≤ 30 cm)`: Pelagic fish with maximum total length <=30 cm, including sardines, thryssa and anchovies.
- `Juvenile large pelagic fish`: Pelagic fish with maximum total length >30 cm, juvenile stanza; source paragraph mistakenly says demersal, but heading, examples and stanza names establish pelagic.
- `Pelagic fish (> 30 cm)`: Pelagic fish with maximum total length >30 cm, adult stanza from 18 months; includes scombrids.
- `Demersal sharks and rays`: Demersal elasmobranchs. No species list documented.
- `Pelagic sharks and rays`: Pelagic elasmobranchs. No species list documented.
- `Seabirds`: Seabirds; no species list documented.
- `Pinnipeds`: Pinnipeds; no species list documented.
- `Other mammals`: Other marine mammals; no species list documented.
- `Marine turtles`: Marine turtles; no species list documented.
- `Detritus`: Non-living detritus.

## Model `36_2_South_China_Sea_SCS-2007_Northern_South_China_Sea_(1970s)`

39 groups, 20 SPPR methods. Group names below are verbatim and authoritative — copy them exactly.

| seq | group_name | type | TL | biomass | model catch |
| --- | --- | --- | --- | --- | --- |
| 1 | `Phytoplankton` | PP | 1 | 323 | 0 |
| 2 | `Benthic producer` | PP | 1 | 153 | 0.0056 |
| 3 | `Zooplankton` | Regular | 2 | 33.8 | 0.01 |
| 4 | `Jellyfish` | Regular | 3.104 | 0.146 | 0.0012 |
| 5 | `Polychaetes` | Regular | 2 | 3.421 | 0 |
| 6 | `Echinoderms` | Regular | 2.333 | 3.065 | 0.0039 |
| 7 | `Benthic crustaceans` | Regular | 2.2 | 2.649 | 0.0019 |
| 8 | `Non-ceph molluscs` | Regular | 2.178 | 13.75 | 0.0056 |
| 9 | `Sessile/other invertebrates` | Regular | 2.6 | 3.114 | 0.0011 |
| 10 | `Shrimps` | Regular | 2.314 | 0.422 | 0.035 |
| 11 | `Crabs` | Regular | 2.524 | 0.731 | 0.01 |
| 12 | `Cephalopods` | Regular | 3.291 | 0.465 | 0.0244 |
| 13 | `Threadfin bream (nemipterids)` | Regular | 3.211 | 1.04 | 0.044 |
| 14 | `Bigeyes (priacanthids)` | Regular | 3.472 | 0.318 | 0.035 |
| 15 | `Lizard fish (synodontids)` | Regular | 3.857 | 0.3 | 0.084 |
| 16 | `Juvenile Hairtail (trichiurids)` | Regular | 3.878 | 0.034 | 0.0038 |
| 17 | `Adult hairtail (trichiurids)` | Regular | 3.914 | 0.0426 | 0.0152 |
| 18 | `Pomfret (stromateids)` | Regular | 3.587 | 0.065 | 0.0053 |
| 19 | `Snappers` | Regular | 3.769 | 0.014 | 0.0053 |
| 20 | `Adult groupers` | Regular | 3.759 | 0.04 | 0.0029 |
| 21 | `Croakers (≤ 30 cm)` | Regular | 3.313 | 0.289 | 0.016 |
| 22 | `Juvenile large croakers` | Regular | 3.239 | 0.0425 | 0.011 |
| 23 | `Croakers (> 30 cm)` | Regular | 3.473 | 0.095 | 0.044 |
| 24 | `Demesral fish (≤ 30 cm)` | Regular | 3.009 | 1.541 | 0.0902 |
| 25 | `Juvenile demersal fish (> 30 cm)` | Regular | 3.044 | 0.112 | 0.0288 |
| 26 | `Adult demersal fish (> 30 cm)` | Regular | 3.427 | 0.195 | 0.115 |
| 27 | `Benthopelagic fish` | Regular | 2.781 | 0.47 | 0.0303 |
| 28 | `Melon seed` | Regular | 3.035 | 0.114 | 0.0057 |
| 29 | `Pelagic fish (≤ 30 cm)` | Regular | 2.782 | 1.05 | 0.146 |
| 30 | `Juvenile large pelagic fish` | Regular | 2.893 | 0.118 | 0.0096 |
| 31 | `Pelagic fish (> 30 cm)` | Regular | 3.367 | 0.158 | 0.038 |
| 32 | `Demersal sharks and rays` | Regular | 3.509 | 0.04 | 0.0158 |
| 33 | `Pelagic sharks and rays` | Regular | 3.99 | 0.028 | 0.0051 |
| 34 | `Seabirds` | Regular | 3.415 | 0.0022 | 0 |
| 35 | `Pinnipeds` | Regular | 4.146 | 0.0046 | 0.0002 |
| 36 | `Other mammals` | Regular | 3.923 | 0.0158 | 0.0001 |
| 37 | `Marine turtles` | Regular | 2.972 | 0.0002 | 0.0001 |
| 38 | `Detritus` | DET | 1 | 100 | 0 |
| 39 | `diet_import` | Import | 1 | 1 | 0 |

`taxon_descr` carries membership for 38 of 39 groups — use it before the paper.
- `Phytoplankton`: Phytoplankton dominated by diatoms, followed by dinoflagellates.
- `Benthic producer`: Benthic algae.
- `Zooplankton`: Acetes spp.; definition: Zooplankton; explicitly includes the landed Mo shrimp Acetes spp.
- `Jellyfish`: Medusae of Cnidaria.
- `Polychaetes`: Polychaeta.
- `Echinoderms`: Echinodermata.
- `Benthic crustaceans`: Benthic crustaceans excluding shrimps and crabs; Oratosquilla spp. supplies the P/B estimate.
- `Non-ceph molluscs`: Non-cephalopod Mollusca.
- `Sessile/other invertebrates`: Sessile and other invertebrates, separate from polychaetes, echinoderms, crustaceans and molluscs.
- `Shrimps`: Metapenaeopsis palmensis; M. barbata; definition: Shrimps including penaeids; Acetes is explicitly in Zooplankton.
- `Crabs`: Crabs.
- `Cephalopods`: Loligo edulis; L. chinensis; definition: Cephalopoda, dominated by Loligo squid.
- `Threadfin bream (nemipterids)`: Nemipterus virgatus; N. bathybius; N. japonicus; definition: Family Nemipteridae.
- `Bigeyes (priacanthids)`: Family Priacanthidae.
- `Lizard fish (synodontids)`: Saurida tumbil; S. undosquamis; definition: Family Synodontidae.
- `Juvenile Hairtail (trichiurids)`: Trichiurus lepturus; definition: Family Trichiuridae, juvenile stanza younger than 18 months.
- `Adult hairtail (trichiurids)`: Trichiurus lepturus; definition: Family Trichiuridae, adult stanza from 18 months.
- `Pomfret (stromateids)`: Family Stromateidae. Other pomfret-like families are excluded from the stated taxonomic definition.
- `Snappers`: Family Lutjanidae.
- `Adult groupers`: Family Serranidae; the final table calls this Adult groupers but supplies no separate juvenile grouper compartment.
- `Croakers (≤ 30 cm)`: Agyrosomus spp.; Pennahia spp.; Pennahia (Agyrosomus) argentatus; definition: Small Sciaenidae <=30 cm; Pennahia is explicitly listed despite differing SAU size classes.
- `Juvenile large croakers`: Larimichthys crocea; definition: Large Sciaenidae >30 cm maximum length, immature fish younger than 24 months.
- `Croakers (> 30 cm)`: Larimichthys crocea; definition: Large Sciaenidae >30 cm maximum length, adult fish from 24 months.
- `Demesral fish (≤ 30 cm)`: Demersal fish with maximum total length <=30 cm, except taxa in dedicated groups.
- `Juvenile demersal fish (> 30 cm)`: Demersal fish with maximum total length >30 cm, juvenile stanza; dedicated groups excluded.
- `Adult demersal fish (> 30 cm)`: Demersal fish with maximum total length >30 cm, adult stanza from 18 months; dedicated groups excluded.
- `Benthopelagic fish`: Final table has one Benthopelagic fish group. Appendix separately describes small <=30 cm and large >30 cm benthopelagic fish; their relationship to the final single pool is not resolved.
- `Melon seed`: Psenopsis anomala; definition: Psenopsis anomala.
- `Pelagic fish (≤ 30 cm)`: Pelagic fish with maximum total length <=30 cm, including sardines, thryssa and anchovies.
- `Juvenile large pelagic fish`: Pelagic fish with maximum total length >30 cm, juvenile stanza; source paragraph mistakenly says demersal, but heading, examples and stanza names establish pelagic.
- `Pelagic fish (> 30 cm)`: Pelagic fish with maximum total length >30 cm, adult stanza from 18 months; includes scombrids.
- `Demersal sharks and rays`: Demersal elasmobranchs. No species list documented.
- `Pelagic sharks and rays`: Pelagic elasmobranchs. No species list documented.
- `Seabirds`: Seabirds; no species list documented.
- `Pinnipeds`: Pinnipeds; no species list documented.
- `Other mammals`: Other marine mammals; no species list documented.
- `Marine turtles`: Marine turtles; no species list documented.
- `Detritus`: Non-living detritus.

## Taxa, by tonnage

`coarse` marks a label above genus: it may legitimately span several groups, which is what the composite syntax is for.

| # | cum % | tonnes | taxon | rank | common name | SAU functional group | SAU commercial group | TL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 9.4 | 36,494,986 | `Marine fishes not identified` | **category** | Marine fishes nei | Medium demersals (30 - 89 cm) | Other fishes & inverts | 3.28 |
| 2 | 14.8 | 20,943,613 | `Trichiurus lepturus` | species | Largehead hairtail | Large benthopelagics (>=90 cm) | Perch-likes | 4.42 |
| 3 | 19.9 | 19,842,390 | `Scyphozoa` | **phylum** | True jellyfishes | Jellyfish | Other fishes & inverts | 3.46 |
| 4 | 23.5 | 13,852,256 | `Synodontidae` | **family** | Lizardfishes, sauries | Medium demersals (30 - 89 cm) | Other fishes & inverts | 4.30 |
| 5 | 27.0 | 13,356,624 | `Alepes` | genus | Crevalles | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.32 |
| 6 | 29.9 | 11,518,482 | `Carangidae` | **family** | Jacks, pompanos | Medium pelagics (30 - 89 cm) | Perch-likes | 4.05 |
| 7 | 32.8 | 10,987,962 | `Mollusca` | genus | Clams, seasnails, squids, octopuses | Other demersal invertebrates | Molluscs | 2.10 |
| 8 | 35.3 | 9,781,315 | `Acetes japonicus` | species | Akiami paste shrimp | Shrimps | Crustaceans | 2.54 |
| 9 | 37.8 | 9,772,010 | `Perciformes` | **order** | Perch-likes | Medium demersals (30 - 89 cm) | Perch-likes | 3.53 |
| 10 | 40.2 | 9,101,609 | `Nemipterus` | genus | Threadfin breams | Small demersals (<30 cm) | Perch-likes | 3.72 |
| 11 | 42.5 | 8,992,342 | `Miscellaneous marine crustaceans` | **category** | Marine crabs, shrimps, lobsters nei | Shrimps | Crustaceans | 2.70 |
| 12 | 44.7 | 8,732,447 | `Leiognathidae` | **family** | Slipmouths, ponyfishes | Small benthopelagics (<30 cm) | Perch-likes | 3.24 |
| 13 | 46.9 | 8,554,508 | `Engraulis japonicus` | species | Japanese anchovy | Small pelagics (<30 cm) | Anchovies | 3.14 |
| 14 | 48.9 | 7,754,916 | `Scomberomorus` | genus | Spanish mackerels | Large pelagics (>=90 cm) | Perch-likes | 4.35 |
| 15 | 50.9 | 7,594,398 | `Scombridae` | **family** | Mackerels, tunas, bonitos | Medium pelagics (30 - 89 cm) | Perch-likes | 4.26 |
| 16 | 52.8 | 7,364,109 | `Sparidae` | **family** | Porgies, seabreams | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.31 |
| 17 | 54.6 | 6,844,599 | `Sciaenidae` | **family** | Drums, croakers | Medium demersals (30 - 89 cm) | Perch-likes | 3.76 |
| 18 | 56.1 | 5,867,364 | `Dendrobranchiata` | genus | Shrimps and prawns | Shrimps | Crustaceans | 3.24 |
| 19 | 57.5 | 5,559,746 | `Sardinella` | genus | Sardinellas | Small pelagics (<30 cm) | Herring-likes | 2.77 |
| 20 | 58.9 | 5,351,659 | `Marine finfishes not identified` | **category** | Finfishes | Medium demersals (30 - 89 cm) | Other fishes & inverts | 3.23 |
| 21 | 60.0 | 4,439,432 | `Priacanthus` | genus | Bigeyes | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.81 |
| 22 | 61.1 | 4,293,769 | `Penaeidae` | **family** | Commercial shrimps and prawns | Shrimps | Crustaceans | 3.31 |
| 23 | 62.3 | 4,279,273 | `Loliginidae` | **family** | Common pencil squids | Cephalopods | Other fishes & inverts | 3.90 |
| 24 | 63.3 | 4,253,440 | `Scomber japonicus` | species | Pacific chub mackerel | Medium pelagics (30 - 89 cm) | Perch-likes | 3.38 |
| 25 | 64.4 | 3,963,781 | `Portunus trituberculatus` | species | Gazami crab | Lobsters, crabs | Crustaceans | 3.73 |
| 26 | 65.4 | 3,962,408 | `Monacanthidae` | **family** | Filefishes | Medium reef assoc. fish (30 - 89 cm) | Other fishes & inverts | 3.00 |
| 27 | 66.4 | 3,907,800 | `Trachysalambria curvirostris` | species | Southern rough shrimp | Shrimps | Crustaceans | 2.70 |
| 28 | 67.4 | 3,769,191 | `Larimichthys crocea` | species | Large yellow croaker | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.72 |
| 29 | 68.3 | 3,540,794 | `Clupeidae` | **family** | Herrings, sardines, menhadens | Small pelagics (<30 cm) | Herring-likes | 3.16 |
| 30 | 69.1 | 3,307,960 | `Muraenesox cinereus` | species | Daggertooth pike conger | Large demersals (>=90 cm) | Other fishes & inverts | 4.38 |
| 31 | 70.0 | 3,288,015 | `Portunus pelagicus` | species | Blue swimming crab | Lobsters, crabs | Crustaceans | 2.48 |
| 32 | 70.8 | 3,259,139 | `Engraulidae` | **family** | Anchovies, round herrings | Small pelagics (<30 cm) | Anchovies | 3.20 |
| 33 | 71.6 | 3,141,062 | `Pampus` | genus | Silver pomfrets | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.41 |
| 34 | 72.4 | 3,102,945 | `Nemipteridae` | **family** | Threadfins, whiptail breams | Small demersals (<30 cm) | Perch-likes | 3.51 |
| 35 | 73.2 | 2,938,422 | `Sepiidae` | **family** | Cuttlefishes | Cephalopods | Other fishes & inverts | 3.60 |
| 36 | 73.9 | 2,787,864 | `Decapterus` | genus | Scads | Medium pelagics (30 - 89 cm) | Perch-likes | 3.63 |
| 37 | 74.6 | 2,520,689 | `Teuthida` | genus | Squids | Cephalopods | Other fishes & inverts | 4.13 |
| 38 | 75.2 | 2,376,467 | `Saurida tumbil` | species | Greater lizardfish | Medium demersals (30 - 89 cm) | Other fishes & inverts | 4.40 |
| 39 | 75.8 | 2,367,798 | `Scombroidei` | **suborder** | Tunas, bonitos, billfishes | Large pelagics (>=90 cm) | Tuna & billfishes | 4.20 |
| 40 | 76.4 | 2,362,914 | `Decapoda` | genus | Crabs, lobsters, shrimps | Lobsters, crabs | Crustaceans | 3.43 |
| 41 | 77.0 | 2,320,947 | `Auxis thazard` | species | Frigate tuna | Medium pelagics (30 - 89 cm) | Tuna & billfishes | 4.37 |
| 42 | 77.5 | 2,037,785 | `Priacanthidae` | **family** | Bigeyes, catalufas | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.79 |
| 43 | 78.0 | 2,011,554 | `Ariidae` | **family** | Sea catfishes, coblers | Medium demersals (30 - 89 cm) | Other fishes & inverts | 3.48 |
| 44 | 78.5 | 1,933,877 | `Sepiida` | genus | Cuttlefishes, bobtail squids | Cephalopods | Other fishes & inverts | 3.70 |
| 45 | 79.0 | 1,914,728 | `Harpadon nehereus` | species | Bombay-duck | Medium benthopelagics (30 - 89 cm) | Other fishes & inverts | 4.20 |
| 46 | 79.5 | 1,800,384 | `Squillidae` | **family** | Squilla mantis shrimps | Shrimps | Crustaceans | 3.50 |
| 47 | 80.0 | 1,752,301 | `Todarodes pacificus` | species | Japanese flying squid | Cephalopods | Other fishes & inverts | 4.28 |
| 48 | 80.4 | 1,751,878 | `Elasmobranchii` | genus | Sharks, rays, skates | Large sharks (>=90 cm) | Sharks & rays | 4.05 |
| 49 | 80.9 | 1,719,985 | `Rastrelliger brachysoma` | species | Short mackerel | Medium pelagics (30 - 89 cm) | Perch-likes | 2.72 |
| 50 | 81.3 | 1,707,092 | `Chondrichthyes` | genus | Sharks, rays, chimaeras | Large sharks (>=90 cm) | Sharks & rays | 4.00 |
| 51 | 81.7 | 1,626,326 | `Thunnus albacares` | species | Yellowfin tuna | Large pelagics (>=90 cm) | Tuna & billfishes | 4.41 |
| 52 | 82.1 | 1,518,853 | `Stolephorus` | genus | Garment anchovies | Small pelagics (<30 cm) | Anchovies | 3.44 |
| 53 | 82.5 | 1,502,866 | `Scomberomorus commerson` | species | Narrow-barred Spanish mackerel | Large pelagics (>=90 cm) | Perch-likes | 4.50 |
| 54 | 82.9 | 1,469,581 | `Rastrelliger kanagurta` | species | Indian mackerel | Medium pelagics (30 - 89 cm) | Perch-likes | 3.19 |
| 55 | 83.2 | 1,441,250 | `Rastrelliger` | genus | Indian mackerels | Medium pelagics (30 - 89 cm) | Perch-likes | 3.10 |
| 56 | 83.6 | 1,384,242 | `Epinephelus` | genus | Seabasses, hinds | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.84 |
| 57 | 84.0 | 1,371,662 | `Mullidae` | **family** | Goatfishes | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.46 |
| 58 | 84.3 | 1,347,860 | `Decapterus macrosoma` | species | Shortfin scad | Medium pelagics (30 - 89 cm) | Perch-likes | 3.40 |
| 59 | 84.6 | 1,285,182 | `Katsuwonus pelamis` | species | Skipjack tuna | Large pelagics (>=90 cm) | Tuna & billfishes | 4.43 |
| 60 | 85.0 | 1,236,075 | `Penaeus chinensis` | species | Fleshy prawn | Shrimps | Crustaceans | 2.00 |
| 61 | 85.3 | 1,185,037 | `Selaroides leptolepis` | species | Yellowstripe scad | Small pelagics (<30 cm) | Perch-likes | 3.84 |
| 62 | 85.6 | 1,175,466 | `Mugilidae` | **family** | Mullets, grey mullets | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 2.53 |
| 63 | 85.9 | 1,163,811 | `Ilisha elongata` | species | Elongate ilisha | Medium pelagics (30 - 89 cm) | Herring-likes | 3.79 |
| 64 | 86.1 | 1,101,836 | `Sardinops sagax` | species | South American pilchard | Medium pelagics (30 - 89 cm) | Herring-likes | 2.84 |
| 65 | 86.4 | 1,092,321 | `Sardinella lemuru` | species | Bali sardinella | Small pelagics (<30 cm) | Herring-likes | 2.48 |
| 66 | 86.7 | 1,078,983 | `Coryphaena hippurus` | species | Common dolphinfish | Large pelagics (>=90 cm) | Perch-likes | 4.37 |
| 67 | 87.0 | 1,035,520 | `Cololabis saira` | species | Pacific saury | Medium pelagics (30 - 89 cm) | Other fishes & inverts | 3.71 |
| 68 | 87.2 | 1,021,215 | `Netuma thalassina` | species | Giant catfish | Large demersals (>=90 cm) | Other fishes & inverts | 3.54 |
| 69 | 87.5 | 991,701 | `Priacanthus macracanthus` | species | Red bigeye | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.11 |
| 70 | 87.7 | 970,414 | `Nemipterus virgatus` | species | Golden threadfin bream | Medium demersals (30 - 89 cm) | Perch-likes | 3.99 |
| 71 | 88.0 | 961,636 | `Parastromateus niger` | species | Black pomfret | Medium benthopelagics (30 - 89 cm) | Perch-likes | 2.93 |
| 72 | 88.2 | 949,667 | `Mugil cephalus` | species | Flathead grey mullet | Large benthopelagics (>=90 cm) | Perch-likes | 2.14 |
| 73 | 88.5 | 945,101 | `Cephalopoda` | **class** | Squids, cuttlefishes, octopuses | Cephalopods | Other fishes & inverts | 3.81 |
| 74 | 88.7 | 891,414 | `Leiognathus` | genus | Ponyfishes | Small benthopelagics (<30 cm) | Perch-likes | 3.22 |
| 75 | 88.9 | 841,026 | `Octopodidae` | **family** | Octopuses | Cephalopods | Other fishes & inverts | 3.59 |
| 76 | 89.1 | 824,452 | `Dasyatis` | genus | Rough whip stingrays | Large rays (>=90 cm) | Sharks & rays | 3.28 |
| 77 | 89.4 | 816,088 | `Euthynnus affinis` | species | Kawakawa | Large pelagics (>=90 cm) | Tuna & billfishes | 4.50 |
| 78 | 89.6 | 803,742 | `Auxis` | genus | Bullet and frigate tunas | Medium pelagics (30 - 89 cm) | Tuna & billfishes | 4.24 |
| 79 | 89.8 | 794,371 | `Pampus argenteus` | species | Silver pomfret | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.30 |
| 80 | 90.0 | 757,719 | `Spratelloides gracilis` | species | Silver-stripe round herring | Small pelagics (<30 cm) | Herring-likes | 3.06 |
| 81 | 90.2 | 749,930 | `Bivalvia` | genus | Clams | Other demersal invertebrates | Molluscs | 2.23 |
| 82 | 90.3 | 697,209 | `Dussumieria` | genus | Rainbow sardines | Small pelagics (<30 cm) | Herring-likes | 3.40 |
| 83 | 90.5 | 685,948 | `Carcharhinus` | genus | Sharp-nosed sharks | Large sharks (>=90 cm) | Sharks & rays | 4.26 |
| 84 | 90.7 | 665,695 | `Lutjanus` | genus | Snappers | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.02 |
| 85 | 90.9 | 664,922 | `Penaeus merguiensis` | species | Banana prawn | Shrimps | Crustaceans | 3.77 |
| 86 | 91.0 | 662,622 | `Octopoda` | **class** | Octopuses, argonauts | Cephalopods | Other fishes & inverts | 3.58 |
| 87 | 91.2 | 647,037 | `Clupanodon thrissa` | species | Chinese gizzard shad | Small pelagics (<30 cm) | Herring-likes | 3.01 |
| 88 | 91.4 | 639,879 | `Sardinella fimbriata` | species | Fringescale sardinella | Small pelagics (<30 cm) | Herring-likes | 2.70 |
| 89 | 91.5 | 635,370 | `Ruvettus pretiosus` | species | Oilfish | Large benthopelagics (>=90 cm) | Perch-likes | 4.18 |
| 90 | 91.7 | 632,669 | `Lates calcarifer` | species | Barramundi | Large demersals (>=90 cm) | Perch-likes | 4.35 |
| 91 | 91.8 | 616,682 | `Carangoides` | genus | Trevallies | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.34 |
| 92 | 92.0 | 615,678 | `Scomberomorus niphonius` | species | Japanese Spanish mackerel | Large pelagics (>=90 cm) | Perch-likes | 4.50 |
| 93 | 92.2 | 612,070 | `Megalaspis cordyla` | species | Torpedo scad | Medium pelagics (30 - 89 cm) | Perch-likes | 4.24 |
| 94 | 92.3 | 588,901 | `Scomberomorus guttatus` | species | Indo-Pacific king mackerel | Medium pelagics (30 - 89 cm) | Perch-likes | 4.28 |
| 95 | 92.5 | 588,587 | `Atrobucca nibe` | species | Blackmouth croaker | Medium demersals (30 - 89 cm) | Perch-likes | 3.03 |
| 96 | 92.6 | 577,894 | `Trichiuridae` | **family** | Cutlassfishes | Large benthopelagics (>=90 cm) | Perch-likes | 4.15 |
| 97 | 92.8 | 559,808 | `Thunnus tonggol` | species | Longtail tuna | Large pelagics (>=90 cm) | Tuna & billfishes | 4.50 |
| 98 | 92.9 | 555,200 | `Penaeus indicus` | species | Indian white prawn | Shrimps | Crustaceans | 2.70 |
| 99 | 93.0 | 548,978 | `Rhopilema esculentum` | species | Flame jellyfish | Jellyfish | Other fishes & inverts | 3.01 |
| 100 | 93.2 | 539,337 | `Clupeiformes` | **order** | Herrings, shads, anchovies | Small pelagics (<30 cm) | Other fishes & inverts | 3.24 |
| 101 | 93.3 | 538,900 | `Miichthys miiuy` | species | Mi-iuy croaker | Medium demersals (30 - 89 cm) | Perch-likes | 3.50 |
| 102 | 93.5 | 533,638 | `Platycephalidae` | **family** | Flatheads | Medium demersals (30 - 89 cm) | Scorpionfishes | 3.90 |
| 103 | 93.6 | 517,939 | `Lutjanidae` | **family** | Snappers | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.02 |
| 104 | 93.7 | 511,850 | `Chelidonichthys kumu` | species | Bluefin gurnard | Medium demersals (30 - 89 cm) | Scorpionfishes | 3.68 |
| 105 | 93.9 | 505,881 | `Chirocentrus dorab` | species | Dorab wolf-herring | Large benthopelagics (>=90 cm) | Herring-likes | 4.20 |
| 106 | 94.0 | 502,330 | `Parapenaeopsis` | genus | Leafy-legged shrimps | Shrimps | Crustaceans | 2.72 |
| 107 | 94.1 | 484,204 | `Lutjanus malabaricus` | species | Malabar blood snapper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.48 |
| 108 | 94.2 | 478,311 | `Charybdis` | genus | Whirlpool swimming crabs | Lobsters, crabs | Crustaceans | 2.70 |
| 109 | 94.4 | 464,825 | `Penaeus japonicus` | species | Kuruma prawn | Shrimps | Crustaceans | 2.70 |
| 110 | 94.5 | 463,221 | `Caesionidae` | **family** | Fusiliers | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.39 |
| 111 | 94.6 | 448,521 | `Trichiurus` | genus | Hairtails | Large benthopelagics (>=90 cm) | Perch-likes | 4.42 |
| 112 | 94.7 | 444,175 | `Sphyraena` | genus | Barracudas, sennets | Large pelagics (>=90 cm) | Perch-likes | 4.40 |
| 113 | 94.8 | 443,125 | `Metapenaeus` | genus | Indo-Pacific prawns | Shrimps | Crustaceans | 2.70 |
| 114 | 94.9 | 433,579 | `Pennahia` | genus | Pennah croakers | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.73 |
| 115 | 95.0 | 421,914 | `Selar crumenophthalmus` | species | Bigeye scad | Medium pelagics (30 - 89 cm) | Perch-likes | 3.81 |
| 116 | 95.1 | 403,968 | `Penaeus` | genus | Tiger prawns | Shrimps | Crustaceans | 2.70 |
| 117 | 95.2 | 379,841 | `Himantura` | genus | Whiprays | Large rays (>=90 cm) | Sharks & rays | 3.85 |
| 118 | 95.3 | 371,399 | `Menidae` | **family** | Moonfishes | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.45 |
| 119 | 95.4 | 364,075 | `Scolopsis` | genus | Monocle breams | Small reef assoc. fish (<30 cm) | Perch-likes | 3.30 |
| 120 | 95.5 | 362,008 | `Siganus` | genus | Spinefoots | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 2.11 |
| 121 | 95.6 | 354,062 | `Pagrus auratus` | species | Silver seabream | Large demersals (>=90 cm) | Perch-likes | 3.59 |
| 122 | 95.7 | 353,362 | `Nemipterus hexodon` | species | Ornate threadfin bream | Small demersals (<30 cm) | Perch-likes | 3.93 |
| 123 | 95.8 | 343,866 | `Penaeus penicillatus` | species | Redtail prawn | Shrimps | Crustaceans | 2.70 |
| 124 | 95.9 | 339,240 | `Thunnus obesus` | species | Bigeye tuna | Large pelagics (>=90 cm) | Tuna & billfishes | 4.49 |
| 125 | 96.0 | 332,603 | `Muraenesocidae` | **family** | Pike congers | Large demersals (>=90 cm) | Other fishes & inverts | 3.90 |
| 126 | 96.0 | 321,623 | `Dussumieria acuta` | species | Rainbow sardine | Small pelagics (<30 cm) | Herring-likes | 3.40 |
| 127 | 96.1 | 317,045 | `Pennahia argentata` | species | Silver croaker | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.47 |
| 128 | 96.2 | 314,942 | `Stephanolepis cirrhifer` | species | Threadsail filefish | Small demersals (<30 cm) | Other fishes & inverts | 2.84 |
| 129 | 96.3 | 314,846 | `Stromateidae` | **family** | Butterfishes | Small benthopelagics (<30 cm) | Perch-likes | 3.62 |
| 130 | 96.4 | 313,147 | `Lutjanus johnii` | species | John's snapper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.20 |
| 131 | 96.5 | 311,414 | `Elagatis bipinnulata` | species | Rainbow runner | Large pelagics (>=90 cm) | Perch-likes | 4.27 |
| 132 | 96.5 | 306,284 | `Saurida` | genus | Lizardfishes | Medium demersals (30 - 89 cm) | Other fishes & inverts | 4.35 |
| 133 | 96.6 | 301,377 | `Serranidae` | **family** | Basses, groupers, hinds | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.98 |
| 134 | 96.7 | 300,639 | `Tegillarca granosa` | species | Granular ark | Other demersal invertebrates | Molluscs | 2.00 |
| 135 | 96.8 | 297,657 | `Pristipomoides` | genus | Jobfishes | Medium demersals (30 - 89 cm) | Perch-likes | 3.91 |
| 136 | 96.8 | 284,226 | `Apogonidae` | **family** | Cardinalfishes | Small reef assoc. fish (<30 cm) | Perch-likes | 3.54 |
| 137 | 96.9 | 281,173 | `Miscellaneous aquatic invertebrates` | **category** | Aquatic invertebrates | Other demersal invertebrates | Other fishes & inverts | 2.43 |
| 138 | 97.0 | 273,604 | `Scomber australasicus` | species | Blue mackerel | Medium pelagics (30 - 89 cm) | Perch-likes | 4.23 |
| 139 | 97.1 | 265,684 | `Sepia` | genus | Sepia cuttlefishes | Cephalopods | Other fishes & inverts | 3.69 |
| 140 | 97.1 | 264,465 | `Epinephelus coioides` | species | Orange-spotted grouper | Large reef assoc. fish (>=90 cm) | Perch-likes | 4.00 |
| 141 | 97.2 | 263,763 | `Larimichthys polyactis` | species | Yellow croaker | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.64 |
| 142 | 97.3 | 263,264 | `Tetraodontidae` | **family** | Puffers, tobies | Large reef assoc. fish (>=90 cm) | Other fishes & inverts | 3.50 |
| 143 | 97.3 | 259,369 | `Exocoetidae` | **family** | Flyingfishes | Small pelagics (<30 cm) | Other fishes & inverts | 3.57 |
| 144 | 97.4 | 257,736 | `Upeneus` | genus | Upeneid goatfishes | Small reef assoc. fish (<30 cm) | Perch-likes | 3.54 |
| 145 | 97.5 | 256,610 | `Seriola` | genus | Amberjacks | Large benthopelagics (>=90 cm) | Perch-likes | 4.39 |
| 146 | 97.5 | 251,359 | `Conger myriaster` | species | Whitespotted conger | Medium demersals (30 - 89 cm) | Other fishes & inverts | 3.98 |
| 147 | 97.6 | 250,541 | `Mugil` | genus | Grey mullets | Medium demersals (30 - 89 cm) | Perch-likes | 2.26 |
| 148 | 97.6 | 243,310 | `Psettodes erumei` | species | Indian halibut | Small to medium flatfishes (<90 cm) | Flatfishes | 4.39 |
| 149 | 97.7 | 228,664 | `Acetes` | genus | Acetes shrimps | Shrimps | Crustaceans | 2.70 |
| 150 | 97.8 | 227,463 | `Cypselurus poecilopterus` | species | Yellowing flyingfish | Small pelagics (<30 cm) | Other fishes & inverts | 3.40 |
| 151 | 97.8 | 223,375 | `Decapterus russelli` | species | Indian scad | Medium pelagics (30 - 89 cm) | Perch-likes | 3.68 |
| 152 | 97.9 | 223,229 | `Lethrinidae` | **family** | Emperors, scavengers | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.59 |
| 153 | 97.9 | 213,903 | `Scomberoides` | genus | Queenfishes | Medium pelagics (30 - 89 cm) | Perch-likes | 4.47 |
| 154 | 98.0 | 208,223 | `Caranx` | genus | Jacks | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.12 |
| 155 | 98.0 | 206,326 | `Muraenesox` | genus | Congers | Large demersals (>=90 cm) | Other fishes & inverts | 3.99 |
| 156 | 98.1 | 195,010 | `Cephalopholis boenak` | species | Chocolate hind | Small reef assoc. fish (<30 cm) | Perch-likes | 4.07 |
| 157 | 98.1 | 185,635 | `Decapterus maruadsi` | species | Japanese scad | Small pelagics (<30 cm) | Perch-likes | 3.40 |
| 158 | 98.2 | 185,557 | `Veneridae` | **family** | Venus clams | Other demersal invertebrates | Molluscs | 2.00 |
| 159 | 98.2 | 177,315 | `Isurus` | genus | Mako sharks | Large sharks (>=90 cm) | Sharks & rays | 4.50 |
| 160 | 98.3 | 173,833 | `Sphyraenidae` | **family** | Barracudas | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.40 |
| 161 | 98.3 | 172,675 | `Mene maculata` | species | Moonfish | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.45 |
| 162 | 98.4 | 164,669 | `Chirocentrus` | genus | Wolf herrings | Large pelagics (>=90 cm) | Herring-likes | 4.30 |
| 163 | 98.4 | 163,446 | `Portunus` | genus | Swimmer crabs | Lobsters, crabs | Crustaceans | 3.26 |
| 164 | 98.4 | 161,685 | `Pleuronectiformes` | **order** | Flatfishes | Small to medium flatfishes (<90 cm) | Flatfishes | 3.57 |
| 165 | 98.5 | 146,826 | `Paralichthys olivaceus` | species | Bastard halibut | Large flatfishes (>=90 cm) | Flatfishes | 4.25 |
| 166 | 98.5 | 140,605 | `Polynemidae` | **family** | Threadfins | Small demersals (<30 cm) | Perch-likes | 3.62 |
| 167 | 98.6 | 138,824 | `Caranx ignobilis` | species | Giant trevally | Large reef assoc. fish (>=90 cm) | Perch-likes | 4.22 |
| 168 | 98.6 | 133,964 | `Pomadasys` | genus | Grunters | Medium demersals (30 - 89 cm) | Perch-likes | 3.59 |
| 169 | 98.6 | 133,446 | `Gastropoda` | **class** | Sea snails | Other demersal invertebrates | Molluscs | 3.06 |
| 170 | 98.7 | 132,192 | `Psenopsis anomala` | species | Pacific rudderfish | Small benthopelagics (<30 cm) | Perch-likes | 4.00 |
| 171 | 98.7 | 128,648 | `Platycephalus indicus` | species | Bartail flathead | Medium demersals (30 - 89 cm) | Scorpionfishes | 3.60 |
| 172 | 98.7 | 125,296 | `Ommastrephidae` | **family** | Arrow squids | Cephalopods | Other fishes & inverts | 4.09 |
| 173 | 98.8 | 123,268 | `Gobiidae` | **family** | Gobies | Small reef assoc. fish (<30 cm) | Perch-likes | 3.11 |
| 174 | 98.8 | 120,879 | `Cephea` | genus | Cepheid jellyfishes | Jellyfish | Other fishes & inverts | 3.46 |
| 175 | 98.8 | 117,051 | `Haemulidae` | **family** | Grunts, sweetlips, bonnetmouths | Medium demersals (30 - 89 cm) | Perch-likes | 3.36 |
| 176 | 98.9 | 115,007 | `Mytilidae` | **family** | Sea mussels | Other demersal invertebrates | Molluscs | 2.00 |
| 177 | 98.9 | 108,217 | `Upeneus moluccensis` | species | Goldband goatfish | Small reef assoc. fish (<30 cm) | Perch-likes | 3.63 |
| 178 | 98.9 | 102,837 | `Perna viridis` | species | Brown mussel | Other demersal invertebrates | Molluscs | 2.00 |
| 179 | 98.9 | 101,597 | `Terapon` | genus | Terapons | Medium demersals (30 - 89 cm) | Perch-likes | 3.50 |
| 180 | 99.0 | 100,275 | `Pampus chinensis` | species | Chinese silver pomfret | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.60 |
| 181 | 99.0 | 98,320 | `Rhizostomeae` | genus | Oral arm jellyfishes | Jellyfish | Other fishes & inverts | 3.46 |
| 182 | 99.0 | 91,699 | `Sillago` | genus | Smelt-whitings | Medium demersals (30 - 89 cm) | Perch-likes | 3.33 |
| 183 | 99.0 | 91,368 | `Scyllaridae` | **family** | Slipper lobsters | Lobsters, crabs | Crustaceans | 2.87 |
| 184 | 99.1 | 90,336 | `Anodontostoma chacunda` | species | Chacunda gizzard shad | Small pelagics (<30 cm) | Herring-likes | 2.84 |
| 185 | 99.1 | 87,913 | `Echinoidea` | **superfamily** | Sea urchins, sea hedgehogs | Other demersal invertebrates | Other fishes & inverts | 2.51 |
| 186 | 99.1 | 86,849 | `Ariomma indica` | species | Indian driftfish | Small benthopelagics (<30 cm) | Perch-likes | 3.63 |
| 187 | 99.1 | 85,439 | `Lutjanus quinquelineatus` | species | Five-lined snapper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.68 |
| 188 | 99.1 | 85,261 | `Platycaranx talamparoides` | species | Imposter trevally | Medium pelagics (30 - 89 cm) | Perch-likes | 4.40 |
| 189 | 99.2 | 83,320 | `Planiliza haematocheilus` | species | So-iny mullet | Medium demersals (30 - 89 cm) | Perch-likes | 2.50 |
| 190 | 99.2 | 82,892 | `Plotosus` | genus | Eel catfishes | Medium reef assoc. fish (30 - 89 cm) | Other fishes & inverts | 3.49 |
| 191 | 99.2 | 82,219 | `Hemiramphus` | genus | Halfbeaks | Medium pelagics (30 - 89 cm) | Other fishes & inverts | 3.05 |
| 192 | 99.2 | 80,523 | `Scomber` | genus | Chub mackerels | Medium pelagics (30 - 89 cm) | Perch-likes | 3.65 |
| 193 | 99.2 | 78,675 | `Cypselurus` | genus | Cypselurid flyingfishes | Small pelagics (<30 cm) | Other fishes & inverts | 3.40 |
| 194 | 99.3 | 77,708 | `Sergestidae` | **family** | Sergestid shrimp | Shrimps | Crustaceans | 2.93 |
| 195 | 99.3 | 76,938 | `Prionace glauca` | species | Blue shark | Large sharks (>=90 cm) | Sharks & rays | 4.35 |
| 196 | 99.3 | 75,931 | `Xiphias gladius` | species | Swordfish | Large pelagics (>=90 cm) | Tuna & billfishes | 4.53 |
| 197 | 99.3 | 73,960 | `Scylla serrata` | species | Indo-Pacific swamp crab | Lobsters, crabs | Crustaceans | 3.17 |
| 198 | 99.3 | 72,518 | `Malacostraca` | genus | Lobsters, crabs, shrimps, krill | Shrimps | Crustaceans | 3.00 |
| 199 | 99.4 | 67,627 | `Scyris indica` | species | Indian threadfish | Large reef assoc. fish (>=90 cm) | Perch-likes | 4.09 |
| 200 | 99.4 | 67,586 | `Metapenaeus joyneri` | species | Shiba shrimp | Shrimps | Crustaceans | 3.20 |
| 201 | 99.4 | 64,264 | `Gadiformes` | **order** | Cods | Medium benthopelagics (30 - 89 cm) | Cod-likes |  |
| 202 | 99.4 | 63,101 | `Cynoglossus` | genus | Tonguesoles | Small to medium flatfishes (<90 cm) | Flatfishes | 3.36 |
| 203 | 99.4 | 61,206 | `Gerreidae` | **family** | Mojarras, silverbellies | Small benthopelagics (<30 cm) | Perch-likes | 3.03 |
| 204 | 99.4 | 61,158 | `Panulirus longipes` | species | Longlegged spiny lobster | Lobsters, crabs | Crustaceans | 2.60 |
| 205 | 99.5 | 60,883 | `Epinephelus maculatus` | species | Highfin grouper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.98 |
| 206 | 99.5 | 60,002 | `Pagrus major` | species | Japanese seabream | Large demersals (>=90 cm) | Perch-likes | 3.70 |
| 207 | 99.5 | 58,952 | `Caesio` | genus | Caesios | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.40 |
| 208 | 99.5 | 56,191 | `Penaeus monodon` | species | Giant tiger prawn | Shrimps | Crustaceans | 2.60 |
| 209 | 99.5 | 55,100 | `Carcharhinidae` | **family** | Requiem sharks | Large sharks (>=90 cm) | Sharks & rays | 4.24 |
| 210 | 99.5 | 52,149 | `Paralichthyidae` | **family** | Largetooth flounders | Small to medium flatfishes (<90 cm) | Flatfishes | 4.06 |
| 211 | 99.5 | 50,464 | `Sillaginidae` | **family** | Smelt-whitings | Medium demersals (30 - 89 cm) | Perch-likes | 3.25 |
| 212 | 99.6 | 48,626 | `Thryssa` | genus | Thryssas | Small pelagics (<30 cm) | Anchovies | 3.34 |
| 213 | 99.6 | 48,027 | `Rachycentridae` | **family** | Cobias | Large pelagics (>=90 cm) | Perch-likes | 3.96 |
| 214 | 99.6 | 47,318 | `Tylosurus crocodilus` | species | Hound needlefish | Large pelagics (>=90 cm) | Other fishes & inverts | 4.43 |
| 215 | 99.6 | 46,027 | `Acanthuridae` | **family** | Surgeons, tangs, unicornfishes | Small reef assoc. fish (<30 cm) | Perch-likes | 2.28 |
| 216 | 99.6 | 44,028 | `Trachurus japonicus` | species | Japanese jack mackerel | Medium demersals (30 - 89 cm) | Perch-likes | 3.40 |
| 217 | 99.6 | 43,593 | `Lactarius lactarius` | species | False trevally | Medium pelagics (30 - 89 cm) | Perch-likes | 3.97 |
| 218 | 99.6 | 43,239 | `Lethrinus` | genus | Emperors | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.75 |
| 219 | 99.6 | 42,725 | `Balistidae` | **family** | Triggerfishes | Medium reef assoc. fish (30 - 89 cm) | Other fishes & inverts | 3.25 |
| 220 | 99.7 | 40,576 | `Gymnocranius` | genus | Largeeye breams | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.40 |
| 221 | 99.7 | 39,116 | `Penaeus latisulcatus` | species | Western king prawn | Shrimps | Crustaceans | 2.70 |
| 222 | 99.7 | 38,768 | `Dussumieria elopsoides` | species | Slender rainbow sardine | Small pelagics (<30 cm) | Herring-likes | 3.40 |
| 223 | 99.7 | 37,103 | `Megalops cyprinoides` | species | Indo-Pacific tarpon | Large pelagics (>=90 cm) | Other fishes & inverts | 3.48 |
| 224 | 99.7 | 36,704 | `Plectorhinchus` | genus | Sweetlips | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.43 |
| 225 | 99.7 | 35,013 | `Apostichopus japonicus` | species | Japanese sea cucumber | Other demersal invertebrates | Other fishes & inverts | 2.30 |
| 226 | 99.7 | 34,494 | `Portunidae` | **family** | Swimming crabs | Lobsters, crabs | Crustaceans | 3.56 |
| 227 | 99.7 | 33,815 | `Haliotidae` | **family** | Abalones, ear shells | Other demersal invertebrates | Molluscs | 2.00 |
| 228 | 99.7 | 31,524 | `Batoidea` | **superfamily** | Batoids, skates, rays, sawfishes | Large rays (>=90 cm) | Sharks & rays | 3.72 |
| 229 | 99.7 | 30,687 | `Istiophorus` | genus | Sailfishes | Large pelagics (>=90 cm) | Tuna & billfishes | 4.50 |
| 230 | 99.7 | 30,429 | `Platycaranx malabaricus` | species | Malabar trevally | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.88 |
| 231 | 99.7 | 29,856 | `Nemipterus japonicus` | species | Japanese threadfin bream | Small demersals (<30 cm) | Perch-likes | 3.77 |
| 232 | 99.8 | 29,599 | `Bothidae` | **family** | Lefteye flounders | Small to medium flatfishes (<90 cm) | Flatfishes | 3.77 |
| 233 | 99.8 | 26,691 | `Drepane` | genus | Sicklefishes | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.32 |
| 234 | 99.8 | 25,443 | `Lateolabrax japonicus` | species | Japanese seabass | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.36 |
| 235 | 99.8 | 25,391 | `Auxis rochei` | species | Bullet tuna | Medium pelagics (30 - 89 cm) | Tuna & billfishes | 4.13 |
| 236 | 99.8 | 24,745 | `Nibea mitsukurii` | species | Honnibe croaker | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.50 |
| 237 | 99.8 | 24,335 | `Meretrix lusoria` | species | Japanese hard clam | Other demersal invertebrates | Molluscs | 2.00 |
| 238 | 99.8 | 23,564 | `Hemiramphidae` | **family** | Halfbeaks, garfishes | Medium pelagics (30 - 89 cm) | Other fishes & inverts | 2.82 |
| 239 | 99.8 | 23,341 | `Istiophorus platypterus` | species | Indo-Pacific sailfish | Large pelagics (>=90 cm) | Tuna & billfishes | 4.50 |
| 240 | 99.8 | 22,197 | `Modiolus` | genus | Horse mussels | Other demersal invertebrates | Molluscs |  |
| 241 | 99.8 | 21,704 | `Istiompax indica` | species | Black marlin | Large pelagics (>=90 cm) | Tuna & billfishes | 4.50 |
| 242 | 99.8 | 20,945 | `Marine pelagic fishes not identified` | **category** | Pelagic fishes | Medium pelagics (30 - 89 cm) | Other fishes & inverts | 3.35 |
| 243 | 99.8 | 20,916 | `Sardinella zunasi` | species | Japanese sardinella | Small pelagics (<30 cm) | Herring-likes | 3.12 |
| 244 | 99.8 | 20,766 | `Muraenidae` | **family** | Moray eels | Large reef assoc. fish (>=90 cm) | Other fishes & inverts | 4.07 |
| 245 | 99.8 | 20,754 | `Rachycentron canadum` | species | Cobia | Large pelagics (>=90 cm) | Perch-likes | 3.96 |
| 246 | 99.8 | 19,836 | `Mierspenaeopsis hardwickii` | species | Spear shrimp | Shrimps | Crustaceans | 2.71 |
| 247 | 99.8 | 19,683 | `Ibacus ciliatus` | species | Sand Crayfish | Lobsters, crabs | Crustaceans | 2.60 |
| 248 | 99.8 | 19,284 | `Istiophoridae` | **family** | Billfishes | Large pelagics (>=90 cm) | Tuna & billfishes | 4.48 |
| 249 | 99.9 | 19,220 | `Panulirus polyphagus` | species | Mud spiny lobster | Lobsters, crabs | Crustaceans | 2.94 |
| 250 | 99.9 | 17,707 | `Mierspenaeopsis sculptilis` | species | Rainbow shrimp | Shrimps | Crustaceans |  |
| 251 | 99.9 | 17,607 | `Acanthurus` | genus | Surgeonfishes | Small reef assoc. fish (<30 cm) | Perch-likes | 2.03 |
| 252 | 99.9 | 17,531 | `Palinuridae` | **family** | Spiny lobsters | Lobsters, crabs | Crustaceans | 3.14 |
| 253 | 99.9 | 16,551 | `Terapontidae` | **family** | Grunters, tigerperches | Medium demersals (30 - 89 cm) | Perch-likes | 3.64 |
| 254 | 99.9 | 16,488 | `Octopus vulgaris` | species | Common octopus | Cephalopods | Other fishes & inverts | 3.60 |
| 255 | 99.9 | 16,466 | `Solenocera crassicornis` | species | Coastal mud shrimp | Shrimps | Crustaceans | 2.20 |
| 256 | 99.9 | 15,292 | `Thunnus alalunga` | species | Albacore | Large pelagics (>=90 cm) | Tuna & billfishes | 4.30 |
| 257 | 99.9 | 15,243 | `Scorpaenidae` | **family** | Scorpionfishes, rockfishes | Large reef assoc. fish (>=90 cm) | Scorpionfishes | 3.92 |
| 258 | 99.9 | 14,833 | `Carcharhinus falciformis` | species | Silky shark | Large sharks (>=90 cm) | Sharks & rays | 4.51 |
| 259 | 99.9 | 14,210 | `Metapenaeus affinis` | species | Jinga shrimp | Shrimps | Crustaceans |  |
| 260 | 99.9 | 14,184 | `Marine groundfishes not identified` | **category** | Groundfishes | Medium demersals (30 - 89 cm) | Other fishes & inverts | 3.22 |
| 261 | 99.9 | 13,862 | `Sardinella albella` | species | White sardinella | Small reef assoc. fish (<30 cm) | Herring-likes | 2.68 |
| 262 | 99.9 | 13,498 | `Placuna placenta` | species | Windowpane oyster | Other demersal invertebrates | Molluscs | 2.41 |
| 263 | 99.9 | 13,212 | `Scaridae` | **family** | Parrotfishes | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 2.00 |
| 264 | 99.9 | 12,661 | `Seriolina nigrofasciata` | species | Blackbanded trevally | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.17 |
| 265 | 99.9 | 12,120 | `Saurida undosquamis` | species | Brushtooth lizardfish | Medium demersals (30 - 89 cm) | Other fishes & inverts | 4.46 |
| 266 | 99.9 | 11,737 | `Atule mate` | species | Yellowtail scad | Small pelagics (<30 cm) | Perch-likes |  |
| 267 | 99.9 | 11,670 | `Scarus` | genus | Parrots | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 2.00 |
| 268 | 99.9 | 11,596 | `Thunnus` | genus | Tunas | Large pelagics (>=90 cm) | Tuna & billfishes |  |
| 269 | 99.9 | 11,439 | `Ruditapes philippinarum` | species | Japanese carpet shell | Other demersal invertebrates | Molluscs | 2.00 |
| 270 | 99.9 | 11,158 | `Metapenaeus tenuipes` | species | Stork shrimp | Shrimps | Crustaceans |  |
| 271 | 99.9 | 10,924 | `Acanthocybium solandri` | species | Wahoo | Large pelagics (>=90 cm) | Perch-likes | 4.26 |
| 272 | 99.9 | 10,716 | `Acanthopagrus schlegelii` | species | Blackhead seabream | Medium demersals (30 - 89 cm) | Perch-likes | 3.24 |
| 273 | 99.9 | 10,347 | `Lobotes surinamensis` | species | Tripletail | Large benthopelagics (>=90 cm) | Perch-likes | 4.04 |
| 274 | 99.9 | 10,311 | `Sepioteuthis lessoniana` | species | Bigfin reef squid | Cephalopods | Other fishes & inverts | 3.98 |
| 275 | 99.9 | 9,740 | `Eleutheronema tetradactylum` | species | Fourfinger threadfin | Large demersals (>=90 cm) | Perch-likes | 4.06 |
| 276 | 99.9 | 9,252 | `Scatophagus` | genus | Scats | Medium demersals (30 - 89 cm) | Perch-likes | 2.75 |
| 277 | 99.9 | 9,130 | `Thunnus orientalis` | species | Pacific bluefin tuna | Large pelagics (>=90 cm) | Tuna & billfishes | 4.05 |
| 278 | 100.0 | 8,875 | `Siganus canaliculatus` | species | White-spotted spinefoot | Small reef assoc. fish (<30 cm) | Perch-likes | 2.76 |
| 279 | 100.0 | 8,213 | `Polydactylus sexfilis` | species | Sixfinger threadfin | Medium demersals (30 - 89 cm) | Perch-likes | 3.43 |
| 280 | 100.0 | 8,128 | `Hilsa kelee` | species | Kelee shad | Small pelagics (<30 cm) | Herring-likes | 3.25 |
| 281 | 100.0 | 7,779 | `Thenus orientalis` | species | Flathead lobster | Lobsters, crabs | Crustaceans | 2.50 |
| 282 | 100.0 | 7,635 | `Acetes sibogae` | species | Alamang shrimp | Shrimps | Crustaceans |  |
| 283 | 100.0 | 7,428 | `Kajikia audax` | species | Striped marlin | Large pelagics (>=90 cm) | Tuna & billfishes | 4.58 |
| 284 | 100.0 | 7,114 | `Penaeus semisulcatus` | species | Green tiger prawn | Shrimps | Crustaceans | 2.00 |
| 285 | 100.0 | 6,714 | `Siganidae` | **family** | Rabbitfishes | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 2.11 |
| 286 | 100.0 | 6,285 | `Gerres` | genus | Silver biddies | Small benthopelagics (<30 cm) | Perch-likes | 3.27 |
| 287 | 100.0 | 5,965 | `Gnathanodon speciosus` | species | Golden trevally | Large reef assoc. fish (>=90 cm) | Perch-likes | 3.84 |
| 288 | 100.0 | 5,062 | `Epinephelus malabaricus` | species | Malabar grouper | Large reef assoc. fish (>=90 cm) | Perch-likes | 4.16 |
| 289 | 100.0 | 4,859 | `Hyporhamphus` | genus | Sea garfishes | Small reef assoc. fish (<30 cm) | Other fishes & inverts | 3.30 |
| 290 | 100.0 | 4,702 | `Makaira mazara` | species | Indo-Pacific blue marlin | Large pelagics (>=90 cm) | Tuna & billfishes | 4.46 |
| 291 | 100.0 | 4,657 | `Hyporhamphus sajori` | species | Japanese halfbeak | Medium pelagics (30 - 89 cm) | Other fishes & inverts | 3.40 |
| 292 | 100.0 | 4,464 | `Carcharhinus longimanus` | species | Oceanic whitetip shark | Large sharks (>=90 cm) | Sharks & rays | 4.16 |
| 293 | 100.0 | 4,224 | `Ambassidae` | **family** | Asiatic glassfishes | Small demersals (<30 cm) | Perch-likes | 3.30 |
| 294 | 100.0 | 3,981 | `Gazza minuta` | species | Toothpony | Small demersals (<30 cm) | Perch-likes | 4.19 |
| 295 | 100.0 | 3,973 | `Aluterus` | genus | Aluterid filefishes | Large reef assoc. fish (>=90 cm) | Other fishes & inverts | 2.81 |
| 296 | 100.0 | 3,668 | `Hemitriakis japanica` | species | Japanese topeshark | Large sharks (>=90 cm) | Sharks & rays |  |
| 297 | 100.0 | 3,665 | `Echinodermata` | genus | Sea urchins, stars, cucumbers | Other demersal invertebrates | Other fishes & inverts | 2.30 |
| 298 | 100.0 | 3,656 | `Dasyatidae` | **family** | Whiptail stingrays | Large rays (>=90 cm) | Sharks & rays | 3.38 |
| 299 | 100.0 | 3,455 | `Chanos chanos` | species | Milkfish | Large benthopelagics (>=90 cm) | Other fishes & inverts | 2.03 |
| 300 | 100.0 | 3,433 | `Sphyraena obtusata` | species | Obtuse barracuda | Medium reef assoc. fish (30 - 89 cm) | Perch-likes |  |
| 301 | 100.0 | 3,360 | `Parupeneus barberinus` | species | Dash-and-dot goatfish | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.22 |
| 302 | 100.0 | 3,238 | `Psettodidae` | **family** | Turbots, Indian halibuts | Small to medium flatfishes (<90 cm) | Flatfishes | 3.83 |
| 303 | 100.0 | 3,062 | `Panulirus` | genus | Spiny lobsters | Lobsters, crabs | Crustaceans | 2.60 |
| 304 | 100.0 | 2,949 | `Rhincodon typus` | species | Whale shark | Large sharks (>=90 cm) | Sharks & rays |  |
| 305 | 100.0 | 2,888 | `Cheilopogon unicolor` | species | Limpidwing flyingfish | Medium pelagics (30 - 89 cm) | Other fishes & inverts | 3.70 |
| 306 | 100.0 | 2,876 | `Mizuhopecten yessoensis` | species | Yesso scallop | Other demersal invertebrates | Molluscs | 2.10 |
| 307 | 100.0 | 2,533 | `Evynnis tumifrons` | species | Yellowback seabream | Medium demersals (30 - 89 cm) | Perch-likes | 3.97 |
| 308 | 100.0 | 2,518 | `Ephippidae` | **family** | Spade-, batfishes, scats | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.57 |
| 309 | 100.0 | 2,470 | `Mola mola` | species | Ocean sunfish | Large pelagics (>=90 cm) | Other fishes & inverts | 3.68 |
| 310 | 100.0 | 2,466 | `Latidae` | **family** | Lates perches | Large demersals (>=90 cm) | Perch-likes | 4.35 |
| 311 | 100.0 | 2,347 | `Ranina ranina` | species | Kona crab  | Lobsters, crabs | Crustaceans | 3.92 |
| 312 | 100.0 | 2,124 | `Ozius guttatus` | species | Spottedbelly rock crab | Lobsters, crabs | Crustaceans |  |
| 313 | 100.0 | 2,055 | `Sphyraena barracuda` | species | Great barracuda | Large pelagics (>=90 cm) | Perch-likes | 4.49 |
| 314 | 100.0 | 1,949 | `Melicertus canaliculatus` | species | Witch prawn | Shrimps | Crustaceans |  |
| 315 | 100.0 | 1,918 | `Seriola dumerili` | species | Greater amberjack | Large reef assoc. fish (>=90 cm) | Perch-likes | 4.50 |
| 316 | 100.0 | 1,660 | `Labridae` | **family** | Wrasses, gropers, tuskfishes | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.46 |
| 317 | 100.0 | 1,608 | `Octopus` | genus | Octopuses, pikas | Cephalopods | Other fishes & inverts | 3.80 |
| 318 | 100.0 | 1,502 | `Plotosidae` | **family** | Eeltail catfishes | Medium reef assoc. fish (30 - 89 cm) | Other fishes & inverts | 3.49 |
| 319 | 100.0 | 1,462 | `Alopias` | genus | Thresher sharks | Large sharks (>=90 cm) | Sharks & rays | 4.50 |
| 320 | 100.0 | 1,459 | `Elops machnata` | species | Tenpounder | Large pelagics (>=90 cm) | Other fishes & inverts | 3.97 |
| 321 | 100.0 | 1,410 | `Pellona ditchela` | species | Indian pellona | Small pelagics (<30 cm) | Herring-likes | 3.37 |
| 322 | 100.0 | 1,379 | `Chaetodontidae` | **family** | Butterflyfishes | Small reef assoc. fish (<30 cm) | Perch-likes | 3.24 |
| 323 | 100.0 | 1,376 | `Congridae` | **family** | Conger, garden eels | Large demersals (>=90 cm) | Other fishes & inverts |  |
| 324 | 100.0 | 1,362 | `Lethrinus miniatus` | species | Trumpet emperor | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.19 |
| 325 | 100.0 | 1,337 | `Scylla` | genus | Mud crabs | Lobsters, crabs | Crustaceans | 3.17 |
| 326 | 100.0 | 1,190 | `Hemitrygon akajei` | species | Whip stingray | Large rays (>=90 cm) | Sharks & rays | 3.84 |
| 327 | 100.0 | 1,186 | `Lepidocybium flavobrunneum` | species | Escolar | Large bathypelagics (>=90 cm) | Perch-likes |  |
| 328 | 100.0 | 1,155 | `Charybdis feriatus` | species | Crucifix crab | Lobsters, crabs | Crustaceans |  |
| 329 | 100.0 | 1,100 | `Encrasicholina punctifer` | species | Buccaneer anchovy | Small pelagics (<30 cm) | Anchovies | 3.25 |
| 330 | 100.0 | 1,093 | `Spongia` | genus | Bathing sponges | Other demersal invertebrates | Other fishes & inverts | 2.00 |
| 331 | 100.0 | 995 | `Amusium pleuronectes` | species | Asian moon scallop | Other demersal invertebrates | Molluscs | 2.00 |
| 332 | 100.0 | 951 | `Scatophagus argus` | species | Spotted scat | Medium demersals (30 - 89 cm) | Perch-likes | 2.99 |
| 333 | 100.0 | 923 | `Podophthalmus vigil` | species | Periscope crab | Lobsters, crabs | Crustaceans |  |
| 334 | 100.0 | 919 | `Drepane punctata` | species | Spotted sicklefish | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.32 |
| 335 | 100.0 | 914 | `Charybdis anisodon` | species | Twospined arm swimming crab | Lobsters, crabs | Crustaceans |  |
| 336 | 100.0 | 809 | `Beryx` | genus | Alfonsinos | Medium benthopelagics (30 - 89 cm) | Other fishes & inverts |  |
| 337 | 100.0 | 797 | `Magallana gigas` | species | Pacific cupped oyster | Other demersal invertebrates | Molluscs | 2.00 |
| 338 | 100.0 | 686 | `Sillago sihama` | species | Silver sillago | Medium demersals (30 - 89 cm) | Perch-likes | 3.33 |
| 339 | 100.0 | 675 | `Pteriomorphia` | genus | Clams, cockles, arkshells | Other demersal invertebrates | Molluscs | 2.27 |
| 340 | 100.0 | 648 | `Metapenaeus ensis` | species | Greasyback shrimp | Shrimps | Crustaceans | 2.70 |
| 341 | 100.0 | 626 | `Macolor` | genus | Snappers | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.99 |
| 342 | 100.0 | 566 | `Haliotis` | genus | Abalones | Other demersal invertebrates | Molluscs |  |
| 343 | 100.0 | 507 | `Berycidae` | **family** | Alfonsinos, redfishes | Medium benthopelagics (30 - 89 cm) | Other fishes & inverts | 3.99 |
| 344 | 100.0 | 455 | `Makaira` | genus | Blue marlins | Large pelagics (>=90 cm) | Tuna & billfishes | 4.47 |
| 345 | 100.0 | 430 | `Lutjanus bohar` | species | Two-spot red snapper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.27 |
| 346 | 100.0 | 347 | `Pomadasys argenteus` | species | Silver grunt | Medium demersals (30 - 89 cm) | Perch-likes | 3.47 |
| 347 | 100.0 | 294 | `Caranx sexfasciatus` | species | Bigeye trevally | Large reef assoc. fish (>=90 cm) | Perch-likes | 4.50 |
| 348 | 100.0 | 262 | `Spratelloides` | genus | Round herrings | Small reef assoc. fish (<30 cm) | Herring-likes |  |
| 349 | 100.0 | 253 | `Nibea albiflora` | species | Yellow drum | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.50 |
| 350 | 100.0 | 243 | `Bramidae` | **family** | Pomfrets | Medium pelagics (30 - 89 cm) | Perch-likes | 4.14 |
| 351 | 100.0 | 187 | `Anguilliformes` | **order** | Eels, morays | Large demersals (>=90 cm) | Other fishes & inverts | 3.89 |
| 352 | 100.0 | 159 | `Crassostrea` | genus | Cupped oysters | Other demersal invertebrates | Molluscs |  |
| 353 | 100.0 | 148 | `Hippocampus` | genus | Seahorses | Small reef assoc. fish (<30 cm) | Other fishes & inverts | 3.33 |
| 354 | 100.0 | 111 | `Holothuriidae` | **family** | Fleshy sea cucumbers | Other demersal invertebrates | Other fishes & inverts |  |
| 355 | 100.0 | 107 | `Isurus oxyrinchus` | species | Shortfin mako | Large sharks (>=90 cm) | Sharks & rays | 4.50 |
| 356 | 100.0 | 103 | `Amblygaster sirm` | species | Spotted sardinella | Small pelagics (<30 cm) | Herring-likes | 3.20 |
| 357 | 100.0 | 89 | `Lampris guttatus` | species | Opah | Large bathypelagics (>=90 cm) | Other fishes & inverts | 4.22 |
| 358 | 100.0 | 85 | `Pectinidae` | **family** | Scallops | Other demersal invertebrates | Molluscs |  |
| 359 | 100.0 | 44 | `Gymnosarda unicolor` | species | Dogtooth tuna | Large reef assoc. fish (>=90 cm) | Tuna & billfishes | 4.50 |
| 360 | 100.0 | 36 | `Tenualosa toli` | species | Toli shad | Medium pelagics (30 - 89 cm) | Herring-likes |  |
| 361 | 100.0 | 33 | `Sphyrna` | genus | Hammerhead sharks | Large sharks (>=90 cm) | Sharks & rays | 4.20 |
| 362 | 100.0 | 29 | `Ostreidae` | **family** | True oysters | Other demersal invertebrates | Molluscs | 2.00 |
| 363 | 100.0 | 24 | `Tripneustes gratilla` | species | Shortspine urchin | Other demersal invertebrates | Other fishes & inverts | 2.00 |
| 364 | 100.0 | 12 | `Lutjanus argentimaculatus` | species | Mangrove red snapper | Large reef assoc. fish (>=90 cm) | Perch-likes |  |
| 365 | 100.0 | 9 | `Pomatomus saltatrix` | species | Bluefish | Large pelagics (>=90 cm) | Perch-likes | 4.53 |
| 366 | 100.0 | 6 | `Sphyraena jello` | species | Pickhandle barracuda | Large reef assoc. fish (>=90 cm) | Perch-likes | 4.50 |
| 367 | 100.0 | 5 | `Echinozoa` | **phylum** | Sea urchins and sea cucumbers | Other demersal invertebrates | Other fishes & inverts |  |
| 368 | 100.0 | 2 | `Tetrapturus angustirostris` | species | Shortbill spearfish | Large pelagics (>=90 cm) | Tuna & billfishes |  |
| 369 | 100.0 | 1 | `Sphyrna lewini` | species | Scalloped hammerhead | Large sharks (>=90 cm) | Sharks & rays |  |
| 370 | 100.0 | 1 | `Trochus niloticus` | species | Commercial top | Other demersal invertebrates | Molluscs |  |
| 371 | 100.0 | 1 | `Holothuroidea` | **superfamily** | Sea cucumbers | Other demersal invertebrates | Other fishes & inverts |  |
| 372 | 100.0 | 0 | `Pinctada` | genus | Mother of pearl oysters | Other demersal invertebrates | Molluscs |  |
| 373 | 100.0 | 0 | `Carcharhinus amblyrhynchos` | species | Blacktail reef shark | Large sharks (>=90 cm) | Sharks & rays |  |
| 374 | 100.0 | 0 | `Sphyrnidae` | **family** | Hammer, bonnet, scoophead sharks | Large sharks (>=90 cm) | Sharks & rays |  |

## Where the difficulty is

93 of 374 labels sit above genus and together carry **182,486,655 tonnes (47.1 % of the catch)**.
Leaving these unresolved is what caps coverage near 78 %. Read `references/coarse-taxa-playbook.md` before deciding any of them.

The ten largest:

- `Marine fishes not identified` — 36,494,986 t (9.4 %), SAU: Medium demersals (30 - 89 cm) / Other fishes & inverts
- `Scyphozoa` — 19,842,390 t (5.1 %), SAU: Jellyfish / Other fishes & inverts
- `Synodontidae` — 13,852,256 t (3.6 %), SAU: Medium demersals (30 - 89 cm) / Other fishes & inverts
- `Carangidae` — 11,518,482 t (3.0 %), SAU: Medium pelagics (30 - 89 cm) / Perch-likes
- `Perciformes` — 9,772,010 t (2.5 %), SAU: Medium demersals (30 - 89 cm) / Perch-likes
- `Miscellaneous marine crustaceans` — 8,992,342 t (2.3 %), SAU: Shrimps / Crustaceans
- `Leiognathidae` — 8,732,447 t (2.3 %), SAU: Small benthopelagics (<30 cm) / Perch-likes
- `Scombridae` — 7,594,398 t (2.0 %), SAU: Medium pelagics (30 - 89 cm) / Perch-likes
- `Sparidae` — 7,364,109 t (1.9 %), SAU: Medium benthopelagics (30 - 89 cm) / Perch-likes
- `Sciaenidae` — 6,844,599 t (1.8 %), SAU: Medium demersals (30 - 89 cm) / Perch-likes
