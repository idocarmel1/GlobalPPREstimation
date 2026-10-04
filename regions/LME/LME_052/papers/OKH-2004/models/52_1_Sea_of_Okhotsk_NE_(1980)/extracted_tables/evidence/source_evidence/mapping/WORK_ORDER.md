# Mapping work order — LME_052

catch years        : 1950-2019
taxa to map        : 151
total catch        : 242,338,606 tonnes over the whole period
Ecopath models     : 2

## Model selection — check `usable` before mapping

| author | title | usable | notes |
| --- | --- | --- | --- |
| (2004) | A model of the Okhotsk Sea with a focus on the northeast | **partial** | ONLY NE is good; SD explodes for TE |

A model marked `no` must not be mapped. Say so and stop.

## Model `52_1_Sea_of_Okhotsk_NE_(1980)`

30 groups, 20 SPPR methods. Group names below are verbatim and authoritative — copy them exactly.

| seq | group_name | type | TL | biomass | model catch |
| --- | --- | --- | --- | --- | --- |
| 1 | `Baleen whales` | Regular | 3.92 | 0.958 | 0 |
| 2 | `Toothed whales` | Regular | 4.556 | 0.01 | 0 |
| 3 | `Sperm whales` | Regular | 5.095 | 0.011 | 0 |
| 4 | `Pinnipeds` | Regular | 4.96 | 0.053 | 0 |
| 5 | `Seabirds` | Regular | 4.689 | 0.005 | 0 |
| 6 | `Walleye pollock` | Regular | 3.744 | 2.475 | 0 |
| 7 | `Juv. pollock` | Regular | 3.753 | 2.119 | 0 |
| 8 | `Pacific herring` | Regular | 3.953 | 0.818 | 0 |
| 9 | `Salmon` | Regular | 3.878 | 0.147 | 0 |
| 10 | `Capelin` | Regular | 3.502 | 2.58 | 0 |
| 11 | `Pacific Sardine` | Regular | 2.158 | 0.667 | 0 |
| 12 | `Other Gadidae` | Regular | 3.917 | 0.306 | 0 |
| 13 | `Pleuronectidae` | Regular | 3.395 | 1.186 | 0 |
| 14 | `Cottidae` | Regular | 4.267 | 0.212 | 0 |
| 15 | `Other bottom fishes` | Regular | 3.857 | 0.515 | 0 |
| 16 | `Ammodytidae` | Regular | 3.003 | 0.314 | 0 |
| 17 | `Myctophidae` | Regular | 3.205 | 1.491 | 0 |
| 18 | `Bathylagidae` | Regular | 3.756 | 14.7 | 0 |
| 19 | `Other mesopelagic fishes` | Regular | 4.093 | 1.578 | 0 |
| 20 | `Crabs and shrimps` | Regular | 3.035 | 2.599 | 0 |
| 21 | `Squids` | Regular | 4.187 | 1.541 | 0 |
| 22 | `Jellyfish` | Regular | 3.329 | 0.98 | 0 |
| 23 | `Carnivorous invertebrates` | Regular | 3 | 12.95 | 0 |
| 24 | `2nd level benthos` | Regular | 2 | 143.1 | 0 |
| 25 | `Predatory zooplankton` | Regular | 3.208 | 86.79 | 0 |
| 26 | `Herbivorous zooplankton` | Regular | 2 | 197.5 | 0 |
| 27 | `Phytobenthos` | PP | 1 | 12.58 | 0 |
| 28 | `Phytoplankton` | PP | 1 | 160.9 | 0 |
| 29 | `Detritus` | DET | 1 | 1 | 0 |
| 30 | `diet_import` | Import | 1 | 1 | 0 |

`taxon_descr` carries membership for 29 of 30 groups — use it before the paper.
- `Baleen whales`: Baleen whales (Mysticeti); Table 1 supplies the group label, not a species list.
- `Toothed whales`: Toothed whales other than the separate sperm-whale compartment; species membership not documented in the available chapter.
- `Sperm whales`: Sperm whales; the common-name stock in Table 1, no binomial listed.
- `Pinnipeds`: Pinnipeds; species membership not documented in the available chapter.
- `Seabirds`: Seabirds; species membership not documented in the available chapter.
- `Walleye pollock`: Walleye pollock, adult/nonjuvenile compartment; Table 1 separates Juv. pollock. Scientific-name crosswalk Gadus chalcogrammus is a taxonomic interpretation.
- `Juv. pollock`: Juvenile walleye pollock; age/length boundary not documented in the available chapter.
- `Pacific herring`: Pacific herring; named stock in Table 1. Scientific-name crosswalk Clupea pallasii is a taxonomic interpretation.
- `Salmon`: Salmon; species membership not documented in the available chapter.
- `Capelin`: Capelin; named stock in Table 1. Scientific-name crosswalk Mallotus villosus is a taxonomic interpretation.
- `Pacific Sardine`: Pacific Sardine; binomial and regional synonym treatment not documented in the available chapter.
- `Other Gadidae`: Gadidae other than pollock (pollock has two separate life-stage groups); Table 1 taxonomic label.
- `Pleuronectidae`: Pleuronectidae; Table 1 family label, no species list.
- `Cottidae`: Cottidae; Table 1 family label, no species list.
- `Other bottom fishes`: Other bottom fishes; residual bottom-fish pool, species membership not documented in the available chapter.
- `Ammodytidae`: Ammodytidae; Table 1 family label, no species list.
- `Myctophidae`: Myctophidae; Table 1 family label, no species list.
- `Bathylagidae`: Bathylagidae; Table 1 family label, no species list.
- `Other mesopelagic fishes`: Other mesopelagic fishes, excluding the separately named Myctophidae and Bathylagidae; species list not documented.
- `Crabs and shrimps`: Crabs and shrimps; Table 1 taxonomic pool label, no species list.
- `Squids`: Squids; Table 1 taxonomic pool label, no species list.
- `Jellyfish`: Jellyfish; Table 1 pool label, no species list.
- `Carnivorous invertebrates`: Carnivorous invertebrates; Table 1 feeding-guild label, species membership not documented; Table 3 diet is second-level benthos.
- `2nd level benthos`: 2nd level benthos; Table 1 trophic-guild label, species membership not documented; Table 3 diet draws from phytoplankton, phytobenthos and detritus.
- `Predatory zooplankton`: Predatory zooplankton; species membership not documented.
- `Herbivorous zooplankton`: Herbivorous zooplankton; species membership not documented.
- `Phytobenthos`: Phytobenthos; benthic primary producers, species membership not documented.
- `Phytoplankton`: Phytoplankton; pelagic primary producers, species membership not documented.
- `Detritus`: Detritus; nonliving compartment, not a taxon.

## Model `52_2_Sea_of_Okhotsk_SD_(1980)`

10 groups, 20 SPPR methods. Group names below are verbatim and authoritative — copy them exactly.

| seq | group_name | type | TL | biomass | model catch |
| --- | --- | --- | --- | --- | --- |
| 1 | `Phytoplankton` | PP | 1 | 57.45 | 0 |
| 2 | `Herbivorous plankton` | Regular | 2 | 197.5 | 0 |
| 3 | `Predatory plankton` | Regular | 3.198 | 72.33 | 0 |
| 4 | `Necton` | Regular | 3.371 | 22.07 | 0 |
| 5 | `Non-predatory zoobenthos` | Regular | 2.299 | 131.2 | 0 |
| 6 | `Predatory zoobenthos` | Regular | 3.299 | 13.46 | 0 |
| 7 | `Nectobenthos` | Regular | 3.605 | 3.145 | 0 |
| 8 | `Mammals and birds` | Regular | 3.68 | 0.322 | 0 |
| 9 | `Detritus` | DET | 1 | 1 | 0 |
| 10 | `diet_import` | Import | 1 | 1 | 0 |

`taxon_descr` is empty for every group, so the paper and its supplements are the only source of membership. Record that limitation in the notes.

## Taxa, by tonnage

`coarse` marks a label above genus: it may legitimately span several groups, which is what the composite syntax is for.

| # | cum % | tonnes | taxon | rank | common name | SAU functional group | SAU commercial group | TL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 60.3 | 146,132,008 | `Gadus chalcogrammus` | species | Alaska pollock | Medium benthopelagics (30 - 89 cm) | Cod-likes | 3.57 |
| 2 | 68.0 | 18,753,776 | `Clupea pallasii` | species | Pacific herring | Medium pelagics (30 - 89 cm) | Herring-likes | 3.16 |
| 3 | 73.9 | 14,223,073 | `Marine fishes not identified` | **category** | Marine fishes nei | Medium demersals (30 - 89 cm) | Other fishes & inverts | 3.28 |
| 4 | 78.5 | 11,221,365 | `Oncorhynchus gorbuscha` | species | Pink salmon | Medium demersals (30 - 89 cm) | Salmon, smelts, etc | 4.49 |
| 5 | 81.2 | 6,361,028 | `Sardinops sagax` | species | South American pilchard | Medium pelagics (30 - 89 cm) | Herring-likes | 2.84 |
| 6 | 83.3 | 5,161,513 | `Gadus macrocephalus` | species | Pacific cod | Large demersals (>=90 cm) | Cod-likes | 4.16 |
| 7 | 84.8 | 3,616,523 | `Oncorhynchus` | genus | Salmons, trouts | Large benthopelagics (>=90 cm) | Salmon, smelts, etc | 3.95 |
| 8 | 86.1 | 3,266,940 | `Oncorhynchus keta` | species | Chum salmon | Large benthopelagics (>=90 cm) | Salmon, smelts, etc | 3.74 |
| 9 | 87.2 | 2,647,806 | `Pleuronectiformes` | **order** | Flatfishes | Small to medium flatfishes (<90 cm) | Flatfishes | 3.57 |
| 10 | 88.1 | 2,194,189 | `Paralithodes camtschaticus` | species | Red king crab | Lobsters, crabs | Crustaceans | 3.70 |
| 11 | 88.9 | 1,970,291 | `Pleurogrammus azonus` | species | Okhotsk atka mackerel | Medium demersals (30 - 89 cm) | Scorpionfishes | 3.60 |
| 12 | 89.7 | 1,716,358 | `Scomber` | genus | Chub mackerels | Medium pelagics (30 - 89 cm) | Perch-likes | 3.65 |
| 13 | 90.3 | 1,601,595 | `Teuthida` | genus | Squids | Cephalopods | Other fishes & inverts | 4.13 |
| 14 | 90.9 | 1,420,067 | `Eleginus gracilis` | species | Saffron cod | Medium demersals (30 - 89 cm) | Cod-likes | 4.10 |
| 15 | 91.5 | 1,413,152 | `Ammodytes personatus` | species | Pacific sandlance | Small demersals (<30 cm) | Perch-likes | 3.00 |
| 16 | 92.1 | 1,397,773 | `Todarodes pacificus` | species | Japanese flying squid | Cephalopods | Other fishes & inverts | 4.28 |
| 17 | 92.6 | 1,330,721 | `Mollusca` | genus | Clams, seasnails, squids, octopuses | Other demersal invertebrates | Molluscs | 2.10 |
| 18 | 93.1 | 1,247,074 | `Cololabis saira` | species | Pacific saury | Medium pelagics (30 - 89 cm) | Other fishes & inverts | 3.71 |
| 19 | 93.6 | 1,245,167 | `Pleurogrammus monopterygius` | species | Atka mackerel | Medium demersals (30 - 89 cm) | Scorpionfishes | 3.38 |
| 20 | 94.1 | 1,182,462 | `Oncorhynchus nerka` | species | Sockeye salmon | Medium pelagics (30 - 89 cm) | Salmon, smelts, etc | 3.54 |
| 21 | 94.6 | 1,084,819 | `Pleuronectidae` | **family** | Righteye flounders | Small to medium flatfishes (<90 cm) | Flatfishes | 3.49 |
| 22 | 95.0 | 1,077,371 | `Mallotus villosus` | species | Capelin | Small pelagics (<30 cm) | Salmon, smelts, etc | 3.15 |
| 23 | 95.4 | 935,887 | `Miscellaneous marine crustaceans` | **category** | Marine crabs, shrimps, lobsters nei | Shrimps | Crustaceans | 2.70 |
| 24 | 95.8 | 883,031 | `Scomber japonicus` | species | Pacific chub mackerel | Medium pelagics (30 - 89 cm) | Perch-likes | 3.38 |
| 25 | 96.1 | 730,793 | `Pectinidae` | **family** | Scallops | Other demersal invertebrates | Molluscs | 2.00 |
| 26 | 96.3 | 641,457 | `Moridae` | **family** | Codlings, moras | Medium benthopelagics (30 - 89 cm) | Cod-likes | 3.87 |
| 27 | 96.6 | 546,075 | `Engraulis japonicus` | species | Japanese anchovy | Small pelagics (<30 cm) | Anchovies | 3.14 |
| 28 | 96.8 | 535,524 | `Laemonema longipes` | species | Longfin codling | Medium benthopelagics (30 - 89 cm) | Cod-likes | 3.24 |
| 29 | 97.0 | 513,134 | `Chionoecetes` | genus | Tanner, snow crabs | Lobsters, crabs | Crustaceans | 2.30 |
| 30 | 97.2 | 418,738 | `Oncorhynchus kisutch` | species | Coho salmon | Large demersals (>=90 cm) | Salmon, smelts, etc | 4.22 |
| 31 | 97.3 | 409,348 | `Chionoecetes opilio` | species | Snow crab | Lobsters, crabs | Crustaceans | 3.54 |
| 32 | 97.5 | 391,149 | `Bivalvia` | genus | Clams | Other demersal invertebrates | Molluscs | 2.23 |
| 33 | 97.7 | 383,637 | `Atheresthes evermanni` | species | Kamchatka flounder | Large flatfishes (>=90 cm) | Flatfishes | 4.30 |
| 34 | 97.8 | 375,867 | `Batoidea` | **superfamily** | Batoids, skates, rays, sawfishes | Large rays (>=90 cm) | Sharks & rays | 3.72 |
| 35 | 97.9 | 340,195 | `Osmeridae` | **family** | Smelts | Small pelagics (<30 cm) | Salmon, smelts, etc | 3.46 |
| 36 | 98.0 | 238,735 | `Hippoglossus stenolepis` | species | Pacific halibut | Large flatfishes (>=90 cm) | Flatfishes | 4.14 |
| 37 | 98.1 | 237,688 | `Sebastidae` | **family** | Rockfishes, rockcods, thornyheads | Medium demersals (30 - 89 cm) | Scorpionfishes | 3.74 |
| 38 | 98.2 | 232,813 | `Decapoda` | genus | Crabs, lobsters, shrimps | Lobsters, crabs | Crustaceans | 3.43 |
| 39 | 98.3 | 231,063 | `Octopoda` | **class** | Octopuses, argonauts | Cephalopods | Other fishes & inverts | 3.58 |
| 40 | 98.4 | 222,419 | `Anoplopoma fimbria` | species | Sablefish | Large bathydemersals (>=90 cm) | Scorpionfishes | 3.84 |
| 41 | 98.5 | 222,111 | `Reinhardtius hippoglossoides` | species | Greenland halibut | Small to medium flatfishes (<90 cm) | Flatfishes | 4.38 |
| 42 | 98.6 | 217,486 | `Salmonidae` | **family** | Salmonids | Large benthopelagics (>=90 cm) | Salmon, smelts, etc | 3.30 |
| 43 | 98.7 | 204,057 | `Arctoscopus japonicus` | species | Japanese sandfish | Small bathydemersals (<30 cm) | Perch-likes | 3.51 |
| 44 | 98.8 | 195,817 | `Trichiurus lepturus` | species | Largehead hairtail | Large benthopelagics (>=90 cm) | Perch-likes | 4.42 |
| 45 | 98.9 | 191,958 | `Brachyura` | genus | Marine crabs | Lobsters, crabs | Crustaceans | 2.60 |
| 46 | 98.9 | 178,083 | `Pandalus borealis` | species | Northern prawn | Shrimps | Crustaceans | 3.07 |
| 47 | 99.0 | 165,448 | `Cephalopoda` | **class** | Squids, cuttlefishes, octopuses | Cephalopods | Other fishes & inverts | 3.81 |
| 48 | 99.1 | 160,436 | `Trachurus japonicus` | species | Japanese jack mackerel | Medium demersals (30 - 89 cm) | Perch-likes | 3.40 |
| 49 | 99.1 | 146,408 | `Mizuhopecten yessoensis` | species | Yesso scallop | Other demersal invertebrates | Molluscs | 2.10 |
| 50 | 99.2 | 145,261 | `Octopodidae` | **family** | Octopuses | Cephalopods | Other fishes & inverts | 3.59 |
| 51 | 99.2 | 115,313 | `Sciaenidae` | **family** | Drums, croakers | Medium demersals (30 - 89 cm) | Perch-likes | 3.76 |
| 52 | 99.3 | 113,523 | `Carangidae` | **family** | Jacks, pompanos | Medium pelagics (30 - 89 cm) | Perch-likes | 4.05 |
| 53 | 99.3 | 97,536 | `Sebastes` | genus | Redfishes | Large reef assoc. fish (>=90 cm) | Scorpionfishes | 3.79 |
| 54 | 99.4 | 94,821 | `Echinoidea` | **superfamily** | Sea urchins, sea hedgehogs | Other demersal invertebrates | Other fishes & inverts | 2.51 |
| 55 | 99.4 | 87,093 | `Seriola lalandi` | species | Yellowtail amberjack | Large benthopelagics (>=90 cm) | Perch-likes |  |
| 56 | 99.4 | 85,819 | `Mugil cephalus` | species | Flathead grey mullet | Large benthopelagics (>=90 cm) | Perch-likes | 2.14 |
| 57 | 99.5 | 84,065 | `Chondrichthyes` | genus | Sharks, rays, chimaeras | Large sharks (>=90 cm) | Sharks & rays | 4.00 |
| 58 | 99.5 | 81,111 | `Scombridae` | **family** | Mackerels, tunas, bonitos | Medium pelagics (30 - 89 cm) | Perch-likes | 4.26 |
| 59 | 99.5 | 78,934 | `Sebastes alutus` | species | Pacific ocean perch | Medium demersals (30 - 89 cm) | Scorpionfishes | 3.48 |
| 60 | 99.6 | 73,300 | `Oncorhynchus tshawytscha` | species | Chinook salmon | Large benthopelagics (>=90 cm) | Salmon, smelts, etc | 4.40 |
| 61 | 99.6 | 70,112 | `Salvelinus` | genus | Chars | Large benthopelagics (>=90 cm) | Salmon, smelts, etc | 4.10 |
| 62 | 99.6 | 68,505 | `Paralithodes platypus` | species | Blue king crab | Lobsters, crabs | Crustaceans | 3.79 |
| 63 | 99.6 | 67,591 | `Pentaceros wheeleri` | species | Slender armorhead | Medium pelagics (30 - 89 cm) | Perch-likes |  |
| 64 | 99.7 | 61,014 | `Limanda aspera` | species | Yellowfin sole | Small to medium flatfishes (<90 cm) | Flatfishes |  |
| 65 | 99.7 | 54,063 | `Bathylagidae` | **family** | Deepsea smelts | Small bathypelagics (<30 cm) | Salmon, smelts, etc | 3.10 |
| 66 | 99.7 | 51,867 | `Seriola` | genus | Amberjacks | Large benthopelagics (>=90 cm) | Perch-likes | 4.39 |
| 67 | 99.7 | 44,139 | `Thunnus alalunga` | species | Albacore | Large pelagics (>=90 cm) | Tuna & billfishes | 4.30 |
| 68 | 99.7 | 43,262 | `Loliginidae` | **family** | Common pencil squids | Cephalopods | Other fishes & inverts | 3.90 |
| 69 | 99.8 | 38,211 | `Hippoglossoides elassodon` | species | Flathead sole | Small to medium flatfishes (<90 cm) | Flatfishes |  |
| 70 | 99.8 | 37,945 | `Gadidae` | **family** | Cods, haddocks | Medium demersals (30 - 89 cm) | Cod-likes | 3.84 |
| 71 | 99.8 | 36,062 | `Gastropoda` | **class** | Sea snails | Other demersal invertebrates | Molluscs | 3.06 |
| 72 | 99.8 | 32,711 | `Berryteuthis magister` | species | Schoolmaster gonate squid | Cephalopods | Other fishes & inverts |  |
| 73 | 99.8 | 29,831 | `Lutjanidae` | **family** | Snappers | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.02 |
| 74 | 99.8 | 27,778 | `Clupeidae` | **family** | Herrings, sardines, menhadens | Small pelagics (<30 cm) | Herring-likes | 3.16 |
| 75 | 99.8 | 27,770 | `Holothuroidea` | **superfamily** | Sea cucumbers | Other demersal invertebrates | Other fishes & inverts | 2.00 |
| 76 | 99.9 | 26,931 | `Dendrobranchiata` | genus | Shrimps and prawns | Shrimps | Crustaceans | 3.24 |
| 77 | 99.9 | 21,987 | `Pandalus` | genus | Seabed shrimps | Shrimps | Crustaceans |  |
| 78 | 99.9 | 21,764 | `Tetraodontidae` | **family** | Puffers, tobies | Large reef assoc. fish (>=90 cm) | Other fishes & inverts | 3.50 |
| 79 | 99.9 | 21,403 | `Muraenesox cinereus` | species | Daggertooth pike conger | Large demersals (>=90 cm) | Other fishes & inverts | 4.38 |
| 80 | 99.9 | 21,142 | `Paralichthys olivaceus` | species | Bastard halibut | Large flatfishes (>=90 cm) | Flatfishes | 4.25 |
| 81 | 99.9 | 20,767 | `Salvelinus malma` | species | Dolly varden | Large benthopelagics (>=90 cm) | Salmon, smelts, etc | 4.40 |
| 82 | 99.9 | 20,332 | `Mactridae` | **family** | Mactra surf clams | Other demersal invertebrates | Molluscs | 2.00 |
| 83 | 99.9 | 19,289 | `Cyprinidae` | **family** | Carps, barbels, other cyprinids | Medium demersals (30 - 89 cm) | Other fishes & inverts | 2.80 |
| 84 | 99.9 | 17,042 | `Paralithodes` | genus | North Pacific king crabs | Lobsters, crabs | Crustaceans |  |
| 85 | 99.9 | 15,486 | `Scorpaeniformes` | **order** | Scorpionfishes, flatheads | Medium demersals (30 - 89 cm) | Scorpionfishes | 3.78 |
| 86 | 99.9 | 15,375 | `Pandalus goniurus` | species | Humpy shrimp | Shrimps | Crustaceans | 2.60 |
| 87 | 99.9 | 15,329 | `Clupeiformes` | **order** | Herrings, shads, anchovies | Small pelagics (<30 cm) | Other fishes & inverts | 3.24 |
| 88 | 99.9 | 14,163 | `Thunnus orientalis` | species | Pacific bluefin tuna | Large pelagics (>=90 cm) | Tuna & billfishes | 4.05 |
| 89 | 100.0 | 10,728 | `Chionoecetes japonicus` | species | Red snow crab | Lobsters, crabs | Crustaceans | 3.74 |
| 90 | 100.0 | 10,609 | `Ommastrephidae` | **family** | Arrow squids | Cephalopods | Other fishes & inverts | 4.09 |
| 91 | 100.0 | 10,296 | `Sebastolobus alascanus` | species | Shortspine thornyhead | Medium bathydemersals (30 - 89 cm) | Scorpionfishes | 3.62 |
| 92 | 100.0 | 9,518 | `Octopus` | genus | Octopuses, pikas | Cephalopods | Other fishes & inverts | 3.80 |
| 93 | 100.0 | 9,107 | `Pandalus hypsinotus` | species | Coonstriped shrimp | Shrimps | Crustaceans | 2.60 |
| 94 | 100.0 | 7,637 | `Squillidae` | **family** | Squilla mantis shrimps | Shrimps | Crustaceans | 3.50 |
| 95 | 100.0 | 7,581 | `Elasmobranchii` | genus | Sharks, rays, skates | Large sharks (>=90 cm) | Sharks & rays | 4.05 |
| 96 | 100.0 | 7,260 | `Trachurus` | genus | Jacks, horse mackerels | Medium pelagics (30 - 89 cm) | Perch-likes | 3.69 |
| 97 | 100.0 | 6,619 | `Haliotidae` | **family** | Abalones, ear shells | Other demersal invertebrates | Molluscs | 2.00 |
| 98 | 100.0 | 5,637 | `Corbicula japonica` | species | Japanese corbicula | Other demersal invertebrates | Molluscs | 2.05 |
| 99 | 100.0 | 5,635 | `Gadiformes` | **order** | Cods | Medium benthopelagics (30 - 89 cm) | Cod-likes |  |
| 100 | 100.0 | 3,136 | `Lycodes` | genus | Eelpouts | Medium bathydemersals (30 - 89 cm) | Perch-likes | 3.30 |
| 101 | 100.0 | 2,973 | `Actinopterygii` | genus | Ray-finned fishes | Medium demersals (30 - 89 cm) | Other fishes & inverts | 3.79 |
| 102 | 100.0 | 2,838 | `Miscellaneous aquatic invertebrates` | **category** | Aquatic invertebrates | Other demersal invertebrates | Other fishes & inverts | 2.43 |
| 103 | 100.0 | 2,478 | `Erimacrus isenbeckii` | species | Hair Crab | Lobsters, crabs | Crustaceans | 2.60 |
| 104 | 100.0 | 2,357 | `Mytilidae` | **family** | Sea mussels | Other demersal invertebrates | Molluscs | 2.00 |
| 105 | 100.0 | 2,182 | `Penaeus chinensis` | species | Fleshy prawn | Shrimps | Crustaceans | 2.00 |
| 106 | 100.0 | 2,038 | `Congridae` | **family** | Conger, garden eels | Large demersals (>=90 cm) | Other fishes & inverts | 4.18 |
| 107 | 100.0 | 2,017 | `Serranidae` | **family** | Basses, groupers, hinds | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.98 |
| 108 | 100.0 | 1,936 | `Synodontidae` | **family** | Lizardfishes, sauries | Medium demersals (30 - 89 cm) | Other fishes & inverts | 4.30 |
| 109 | 100.0 | 1,597 | `Perciformes` | **order** | Perch-likes | Medium demersals (30 - 89 cm) | Perch-likes | 3.53 |
| 110 | 100.0 | 1,468 | `Ommastrephes bartramii` | species | Neon flying squid | Cephalopods | Other fishes & inverts | 4.37 |
| 111 | 100.0 | 1,370 | `Sclerocrangon` | genus | Sculptured shrimps | Shrimps | Crustaceans | 2.20 |
| 112 | 100.0 | 1,186 | `Mugilidae` | **family** | Mullets, grey mullets | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 2.53 |
| 113 | 100.0 | 1,142 | `Hexagrammos otakii` | species | Fat grrenling | Small pelagics (<30 cm) | Scorpionfishes |  |
| 114 | 100.0 | 964 | `Hexagrammidae` | **family** | Greenlings | Medium demersals (30 - 89 cm) | Scorpionfishes | 3.72 |
| 115 | 100.0 | 743 | `Marine pelagic fishes not identified` | **category** | Pelagic fishes | Medium pelagics (30 - 89 cm) | Other fishes & inverts | 3.35 |
| 116 | 100.0 | 566 | `Beryx` | genus | Alfonsinos | Medium benthopelagics (30 - 89 cm) | Other fishes & inverts | 3.97 |
| 117 | 100.0 | 531 | `Apostichopus japonicus` | species | Japanese sea cucumber | Other demersal invertebrates | Other fishes & inverts | 2.30 |
| 118 | 100.0 | 518 | `Crassostrea` | genus | Cupped oysters | Other demersal invertebrates | Molluscs | 2.00 |
| 119 | 100.0 | 488 | `Stromateidae` | **family** | Butterfishes | Small benthopelagics (<30 cm) | Perch-likes | 3.62 |
| 120 | 100.0 | 463 | `Bramidae` | **family** | Pomfrets | Medium pelagics (30 - 89 cm) | Perch-likes | 4.14 |
| 121 | 100.0 | 384 | `Cephea` | genus | Cepheid jellyfishes | Jellyfish | Other fishes & inverts |  |
| 122 | 100.0 | 282 | `Scorpaenidae` | **family** | Scorpionfishes, rockfishes | Large reef assoc. fish (>=90 cm) | Scorpionfishes |  |
| 123 | 100.0 | 254 | `Scyphozoa` | **phylum** | True jellyfishes | Jellyfish | Other fishes & inverts | 3.46 |
| 124 | 100.0 | 239 | `Pandalopsis japonica` | species | Sidestripe shrimp | Shrimps | Crustaceans |  |
| 125 | 100.0 | 204 | `Pandalus kessleri` | species | Grass shrimp | Shrimps | Crustaceans | 2.60 |
| 126 | 100.0 | 151 | `Oncorhynchus masou` | species | Masu salmon | Medium benthopelagics (30 - 89 cm) | Salmon, smelts, etc | 3.60 |
| 127 | 100.0 | 116 | `Isurus` | genus | Mako sharks | Large sharks (>=90 cm) | Sharks & rays | 4.50 |
| 128 | 100.0 | 112 | `Paralithodes brevipes` | species | Spiny king crab | Lobsters, crabs | Crustaceans | 2.00 |
| 129 | 100.0 | 79 | `Metapenaeus` | genus | Indo-Pacific prawns | Shrimps | Crustaceans | 2.70 |
| 130 | 100.0 | 34 | `Mola mola` | species | Ocean sunfish | Large pelagics (>=90 cm) | Other fishes & inverts | 3.68 |
| 131 | 100.0 | 26 | `Magallana gigas` | species | Pacific cupped oyster | Other demersal invertebrates | Molluscs | 2.00 |
| 132 | 100.0 | 7 | `Xiphias gladius` | species | Swordfish | Large pelagics (>=90 cm) | Tuna & billfishes | 4.53 |
| 133 | 100.0 | 7 | `Decapterus` | genus | Scads | Medium pelagics (30 - 89 cm) | Perch-likes | 3.63 |
| 134 | 100.0 | 5 | `Scomberomorus niphonius` | species | Japanese Spanish mackerel | Large pelagics (>=90 cm) | Perch-likes | 4.50 |
| 135 | 100.0 | 5 | `Panulirus` | genus | Spiny lobsters | Lobsters, crabs | Crustaceans |  |
| 136 | 100.0 | 2 | `Rachycentron canadum` | species | Cobia | Large pelagics (>=90 cm) | Perch-likes | 3.96 |
| 137 | 100.0 | 2 | `Coregonus` | genus | Whitefishes | Medium pelagics (30 - 89 cm) | Salmon, smelts, etc |  |
| 138 | 100.0 | 1 | `Haliotis` | genus | Abalones | Other demersal invertebrates | Molluscs |  |
| 139 | 100.0 | 1 | `Seriola dumerili` | species | Greater amberjack | Large reef assoc. fish (>=90 cm) | Perch-likes | 4.50 |
| 140 | 100.0 | 1 | `Saurida` | genus | Lizardfishes | Medium demersals (30 - 89 cm) | Other fishes & inverts | 4.35 |
| 141 | 100.0 | 1 | `Prionace glauca` | species | Blue shark | Large sharks (>=90 cm) | Sharks & rays | 4.35 |
| 142 | 100.0 | 0 | `Echinozoa` | **phylum** | Sea urchins and sea cucumbers | Other demersal invertebrates | Other fishes & inverts |  |
| 143 | 100.0 | 0 | `Lates calcarifer` | species | Barramundi | Large demersals (>=90 cm) | Perch-likes | 4.35 |
| 144 | 100.0 | 0 | `Rhopilema hispidum` | species | Sand jellyfish | Jellyfish | Other fishes & inverts | 3.46 |
| 145 | 100.0 | 0 | `Scaridae` | **family** | Parrotfishes | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 2.00 |
| 146 | 100.0 | 0 | `Rachycentridae` | **family** | Cobias | Large pelagics (>=90 cm) | Perch-likes |  |
| 147 | 100.0 | 0 | `Chanos chanos` | species | Milkfish | Large benthopelagics (>=90 cm) | Other fishes & inverts | 2.03 |
| 148 | 100.0 | 0 | `Sphyraena barracuda` | species | Great barracuda | Large pelagics (>=90 cm) | Perch-likes | 4.49 |
| 149 | 100.0 | 0 | `Pinctada` | genus | Mother of pearl oysters | Other demersal invertebrates | Molluscs |  |
| 150 | 100.0 | 0 | `Scombroidei` | **suborder** | Tunas, bonitos, billfishes | Large pelagics (>=90 cm) | Tuna & billfishes |  |
| 151 | 100.0 | 0 | `Isurus oxyrinchus` | species | Shortfin mako | Large sharks (>=90 cm) | Sharks & rays |  |

## Where the difficulty is

50 of 151 labels sit above genus and together carry **22,778,185 tonnes (9.4 % of the catch)**.
Leaving these unresolved is what caps coverage near 78 %. Read `references/coarse-taxa-playbook.md` before deciding any of them.

The ten largest:

- `Marine fishes not identified` — 14,223,073 t (5.9 %), SAU: Medium demersals (30 - 89 cm) / Other fishes & inverts
- `Pleuronectiformes` — 2,647,806 t (1.1 %), SAU: Small to medium flatfishes (<90 cm) / Flatfishes
- `Pleuronectidae` — 1,084,819 t (0.4 %), SAU: Small to medium flatfishes (<90 cm) / Flatfishes
- `Miscellaneous marine crustaceans` — 935,887 t (0.4 %), SAU: Shrimps / Crustaceans
- `Pectinidae` — 730,793 t (0.3 %), SAU: Other demersal invertebrates / Molluscs
- `Moridae` — 641,457 t (0.3 %), SAU: Medium benthopelagics (30 - 89 cm) / Cod-likes
- `Batoidea` — 375,867 t (0.2 %), SAU: Large rays (>=90 cm) / Sharks & rays
- `Osmeridae` — 340,195 t (0.1 %), SAU: Small pelagics (<30 cm) / Salmon, smelts, etc
- `Sebastidae` — 237,688 t (0.1 %), SAU: Medium demersals (30 - 89 cm) / Scorpionfishes
- `Octopoda` — 231,063 t (0.1 %), SAU: Cephalopods / Other fishes & inverts
