# Mapping work order — LME_047

catch years        : 1950-2019
taxa to map        : 276
total catch        : 282,784,028 tonnes over the whole period
Ecopath models     : 2

## Model selection — check `usable` before mapping

| author | title | usable | notes |
| --- | --- | --- | --- |
| Xu L, Song P, Wang Y, Xie B, Huang L, Li | Estimating the Impact of a Seasonal Fishing Moratorium | **yes** | used the 2018 model |

A model marked `no` must not be mapped. Say so and stop.

## Model `47_1_East_China_Sea_(1997)`

25 groups, 20 SPPR methods. Group names below are verbatim and authoritative — copy them exactly.

| seq | group_name | type | TL | biomass | model catch |
| --- | --- | --- | --- | --- | --- |
| 1 | `Phytoplankton` | PP | 1 | 16.52 | 0 |
| 2 | `Zooplankton` | Regular | 2 | 4.703 | 0 |
| 3 | `Polychaetes` | Regular | 2 | 3.13 | 0 |
| 4 | `Mollusks` | Regular | 2.169 | 9.51 | 0 |
| 5 | `Benthic Crustaceans` | Regular | 2.161 | 1.6 | 0 |
| 6 | `Echinoderms` | Regular | 2.22 | 3.46 | 0 |
| 7 | `Other invertebrates` | Regular | 2 | 3.16 | 0 |
| 8 | `Crabs` | Regular | 2.322 | 0.143 | 0 |
| 9 | `Shrimps` | Regular | 2.314 | 0.161 | 0 |
| 10 | `Cephalopods` | Regular | 2.819 | 0.549 | 0 |
| 11 | `Planktivores` | Regular | 3.007 | 0.71 | 0 |
| 12 | `Benthivores` | Regular | 2.847 | 0.0397 | 0 |
| 13 | `Piscivores` | Regular | 3.509 | 0.348 | 0 |
| 14 | `Hairtails` | Regular | 3.207 | 1.336 | 0 |
| 15 | `Bombay duck` | Regular | 3.773 | 0.11 | 0 |
| 16 | `Planktivores/Benthivores` | Regular | 2.958 | 0.609 | 0 |
| 17 | `Planktivores/piscivores` | Regular | 3.099 | 2.588 | 0 |
| 18 | `Benthivores/piscivores` | Regular | 3.139 | 0.534 | 0 |
| 19 | `Omnivores` | Regular | 3.139 | 0.136 | 0 |
| 20 | `Large yellow croakers` | Regular | 3.39 | 0.00107 | 0 |
| 21 | `Small yellow croakers` | Regular | 3.147 | 0.356 | 0 |
| 22 | `Sharks` | Regular | 4.081 | 0.00889 | 0 |
| 23 | `Marine mammals` | Regular | 3.814 | 0.00404 | 0 |
| 24 | `Detritus` | DET | 1 | 100 | 0 |
| 25 | `diet_import` | Import | 1 | 1 | 0 |

`taxon_descr` is empty for every group, so the paper and its supplements are the only source of membership. Record that limitation in the notes.

## Model `47_2_East_China_Sea_(2018)`

25 groups, 20 SPPR methods. Group names below are verbatim and authoritative — copy them exactly.

| seq | group_name | type | TL | biomass | model catch |
| --- | --- | --- | --- | --- | --- |
| 1 | `Phytoplankton` | PP | 1 | 43.2 | 0 |
| 2 | `Zooplankton` | Regular | 2 | 12.82 | 0 |
| 3 | `Polychaetes` | Regular | 2 | 1.841 | 0 |
| 4 | `Mollusks` | Regular | 2.169 | 0.343 | 0 |
| 5 | `Benthic Crustaceans` | Regular | 2.151 | 1.53 | 0 |
| 6 | `Echinoderms` | Regular | 2.212 | 6.427 | 0 |
| 7 | `Other invertebrates` | Regular | 2 | 1.359 | 0 |
| 8 | `Crabs` | Regular | 2.334 | 0.0534 | 0 |
| 9 | `Shrimps` | Regular | 2.314 | 0.288 | 0 |
| 10 | `Cephalopods` | Regular | 2.955 | 0.894 | 0 |
| 11 | `Planktivores` | Regular | 2.919 | 4.701 | 0 |
| 12 | `Benthivores` | Regular | 2.875 | 0.278 | 0 |
| 13 | `Piscivores` | Regular | 3.94 | 0.275 | 0 |
| 14 | `Hairtails` | Regular | 3.368 | 3.369 | 0 |
| 15 | `Bombay duck` | Regular | 3.419 | 1.497 | 0 |
| 16 | `Planktivores/Benthivores` | Regular | 2.964 | 2.103 | 0 |
| 17 | `Planktivores/piscivores` | Regular | 3.522 | 1.294 | 0 |
| 18 | `Benthivores/piscivores` | Regular | 3.459 | 0.349 | 0 |
| 19 | `Omnivores` | Regular | 3.435 | 0.439 | 0 |
| 20 | `Large yellow croakers` | Regular | 3.498 | 0.0339 | 0 |
| 21 | `Small yellow croakers` | Regular | 3.206 | 0.0832 | 0 |
| 22 | `Sharks` | Regular | 4.236 | 0.00935 | 0 |
| 23 | `Marine mammals` | Regular | 3.939 | 0.00404 | 0 |
| 24 | `Detritus` | DET | 1 | 100 | 0 |
| 25 | `diet_import` | Import | 1 | 1 | 0 |

`taxon_descr` is empty for every group, so the paper and its supplements are the only source of membership. Record that limitation in the notes.

## Taxa, by tonnage

`coarse` marks a label above genus: it may legitimately span several groups, which is what the composite syntax is for.

| # | cum % | tonnes | taxon | rank | common name | SAU functional group | SAU commercial group | TL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 12.9 | 36,591,787 | `Marine fishes not identified` | **category** | Marine fishes nei | Medium demersals (30 - 89 cm) | Other fishes & inverts | 3.28 |
| 2 | 22.1 | 25,918,314 | `Sardinops sagax` | species | South American pilchard | Medium pelagics (30 - 89 cm) | Herring-likes | 2.84 |
| 3 | 28.8 | 18,967,269 | `Trichiurus lepturus` | species | Largehead hairtail | Large benthopelagics (>=90 cm) | Perch-likes | 4.42 |
| 4 | 34.8 | 16,805,259 | `Engraulis japonicus` | species | Japanese anchovy | Small pelagics (<30 cm) | Anchovies | 3.14 |
| 5 | 39.2 | 12,477,396 | `Scomber japonicus` | species | Pacific chub mackerel | Medium pelagics (30 - 89 cm) | Perch-likes | 3.38 |
| 6 | 42.5 | 9,556,263 | `Scomber` | genus | Chub mackerels | Medium pelagics (30 - 89 cm) | Perch-likes | 3.65 |
| 7 | 45.5 | 8,328,661 | `Cololabis saira` | species | Pacific saury | Medium pelagics (30 - 89 cm) | Other fishes & inverts | 3.71 |
| 8 | 48.1 | 7,501,648 | `Mollusca` | genus | Clams, seasnails, squids, octopuses | Other demersal invertebrates | Molluscs | 2.10 |
| 9 | 50.5 | 6,656,949 | `Miscellaneous marine crustaceans` | **category** | Marine crabs, shrimps, lobsters nei | Shrimps | Crustaceans | 2.70 |
| 10 | 52.8 | 6,448,339 | `Larimichthys polyactis` | species | Yellow croaker | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.64 |
| 11 | 54.7 | 5,391,928 | `Acetes japonicus` | species | Akiami paste shrimp | Shrimps | Crustaceans | 2.54 |
| 12 | 56.5 | 5,085,315 | `Todarodes pacificus` | species | Japanese flying squid | Cephalopods | Other fishes & inverts | 4.28 |
| 13 | 58.3 | 5,013,099 | `Sciaenidae` | **family** | Drums, croakers | Medium demersals (30 - 89 cm) | Perch-likes | 3.76 |
| 14 | 60.0 | 4,888,905 | `Stephanolepis cirrhifer` | species | Threadsail filefish | Small demersals (<30 cm) | Other fishes & inverts | 2.84 |
| 15 | 61.6 | 4,644,809 | `Pectinidae` | **family** | Scallops | Other demersal invertebrates | Molluscs | 2.00 |
| 16 | 63.2 | 4,334,965 | `Scyphozoa` | **phylum** | True jellyfishes | Jellyfish | Other fishes & inverts | 3.46 |
| 17 | 64.5 | 3,661,117 | `Pleuronectidae` | **family** | Righteye flounders | Small to medium flatfishes (<90 cm) | Flatfishes | 3.49 |
| 18 | 65.7 | 3,486,912 | `Muraenesox cinereus` | species | Daggertooth pike conger | Large demersals (>=90 cm) | Other fishes & inverts | 4.38 |
| 19 | 66.9 | 3,365,329 | `Pennahia argentata` | species | Silver croaker | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.47 |
| 20 | 68.0 | 3,276,610 | `Gadus macrocephalus` | species | Pacific cod | Large demersals (>=90 cm) | Cod-likes | 4.16 |
| 21 | 69.1 | 3,089,551 | `Monacanthidae` | **family** | Filefishes | Medium reef assoc. fish (30 - 89 cm) | Other fishes & inverts | 3.00 |
| 22 | 70.2 | 2,910,778 | `Pampus` | genus | Silver pomfrets | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.41 |
| 23 | 71.2 | 2,883,416 | `Bivalvia` | genus | Clams | Other demersal invertebrates | Molluscs | 2.23 |
| 24 | 72.2 | 2,850,108 | `Trachysalambria curvirostris` | species | Southern rough shrimp | Shrimps | Crustaceans | 2.70 |
| 25 | 73.2 | 2,808,444 | `Nemipterus` | genus | Threadfin breams | Small demersals (<30 cm) | Perch-likes | 3.72 |
| 26 | 74.2 | 2,797,567 | `Scomberomorus` | genus | Spanish mackerels | Large pelagics (>=90 cm) | Perch-likes | 4.35 |
| 27 | 75.1 | 2,665,672 | `Portunus trituberculatus` | species | Gazami crab | Lobsters, crabs | Crustaceans | 3.73 |
| 28 | 76.0 | 2,576,878 | `Octopoda` | **class** | Octopuses, argonauts | Cephalopods | Other fishes & inverts | 3.58 |
| 29 | 76.8 | 2,151,524 | `Sepiida` | genus | Cuttlefishes, bobtail squids | Cephalopods | Other fishes & inverts | 3.70 |
| 30 | 77.5 | 2,056,876 | `Larimichthys crocea` | species | Large yellow croaker | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.72 |
| 31 | 78.2 | 2,034,326 | `Scomberomorus niphonius` | species | Japanese Spanish mackerel | Large pelagics (>=90 cm) | Perch-likes | 4.50 |
| 32 | 78.9 | 1,954,164 | `Planiliza haematocheilus` | species | So-iny mullet | Medium demersals (30 - 89 cm) | Perch-likes | 2.50 |
| 33 | 79.6 | 1,877,838 | `Teuthida` | genus | Squids | Cephalopods | Other fishes & inverts | 4.13 |
| 34 | 80.2 | 1,839,740 | `Penaeus chinensis` | species | Fleshy prawn | Shrimps | Crustaceans | 2.00 |
| 35 | 80.9 | 1,837,237 | `Oncorhynchus` | genus | Salmons, trouts | Large benthopelagics (>=90 cm) | Salmon, smelts, etc | 3.95 |
| 36 | 81.5 | 1,801,294 | `Carangidae` | **family** | Jacks, pompanos | Medium pelagics (30 - 89 cm) | Perch-likes | 4.05 |
| 37 | 82.1 | 1,596,611 | `Psenopsis anomala` | species | Pacific rudderfish | Small benthopelagics (<30 cm) | Perch-likes | 4.00 |
| 38 | 82.6 | 1,512,499 | `Squillidae` | **family** | Squilla mantis shrimps | Shrimps | Crustaceans | 3.50 |
| 39 | 83.2 | 1,497,432 | `Sparidae` | **family** | Porgies, seabreams | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.31 |
| 40 | 83.7 | 1,439,693 | `Alepes` | genus | Crevalles | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.32 |
| 41 | 84.2 | 1,391,721 | `Sepiidae` | **family** | Cuttlefishes | Cephalopods | Other fishes & inverts | 3.60 |
| 42 | 84.6 | 1,326,613 | `Harpadon nehereus` | species | Bombay-duck | Medium benthopelagics (30 - 89 cm) | Other fishes & inverts | 4.20 |
| 43 | 85.1 | 1,251,232 | `Katsuwonus pelamis` | species | Skipjack tuna | Large pelagics (>=90 cm) | Tuna & billfishes | 4.43 |
| 44 | 85.5 | 1,145,374 | `Cephalopoda` | **class** | Squids, cuttlefishes, octopuses | Cephalopods | Other fishes & inverts | 3.81 |
| 45 | 85.9 | 1,145,241 | `Nemipteridae` | **family** | Threadfins, whiptail breams | Small demersals (<30 cm) | Perch-likes | 3.51 |
| 46 | 86.3 | 1,087,502 | `Thunnus albacares` | species | Yellowfin tuna | Large pelagics (>=90 cm) | Tuna & billfishes | 4.41 |
| 47 | 86.6 | 1,072,383 | `Trachurus japonicus` | species | Japanese jack mackerel | Medium demersals (30 - 89 cm) | Perch-likes | 3.40 |
| 48 | 87.0 | 1,043,660 | `Rhopilema esculentum` | species | Flame jellyfish | Jellyfish | Other fishes & inverts | 3.01 |
| 49 | 87.4 | 1,024,425 | `Mugil cephalus` | species | Flathead grey mullet | Large benthopelagics (>=90 cm) | Perch-likes | 2.14 |
| 50 | 87.7 | 969,826 | `Dendrobranchiata` | genus | Shrimps and prawns | Shrimps | Crustaceans | 3.24 |
| 51 | 88.1 | 969,705 | `Pagrus major` | species | Japanese seabream | Large demersals (>=90 cm) | Perch-likes | 3.70 |
| 52 | 88.4 | 964,340 | `Decapoda` | genus | Crabs, lobsters, shrimps | Lobsters, crabs | Crustaceans | 3.43 |
| 53 | 88.7 | 919,190 | `Turbo cornutus` | species | Horned turban | Other demersal invertebrates | Molluscs | 2.00 |
| 54 | 89.0 | 918,502 | `Conger myriaster` | species | Whitespotted conger | Medium demersals (30 - 89 cm) | Other fishes & inverts | 3.98 |
| 55 | 89.3 | 830,914 | `Congridae` | **family** | Conger, garden eels | Large demersals (>=90 cm) | Other fishes & inverts | 4.18 |
| 56 | 89.6 | 813,532 | `Seriola` | genus | Amberjacks | Large benthopelagics (>=90 cm) | Perch-likes | 4.39 |
| 57 | 89.9 | 778,974 | `Ilisha elongata` | species | Elongate ilisha | Medium pelagics (30 - 89 cm) | Herring-likes | 3.79 |
| 58 | 90.2 | 733,122 | `Sebastes` | genus | Redfishes | Large reef assoc. fish (>=90 cm) | Scorpionfishes | 3.79 |
| 59 | 90.4 | 716,636 | `Epinephelus` | genus | Seabasses, hinds | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.84 |
| 60 | 90.7 | 714,004 | `Loliginidae` | **family** | Common pencil squids | Cephalopods | Other fishes & inverts | 3.90 |
| 61 | 90.9 | 672,628 | `Stromateidae` | **family** | Butterfishes | Small benthopelagics (<30 cm) | Perch-likes | 3.62 |
| 62 | 91.1 | 602,209 | `Brachyura` | genus | Marine crabs | Lobsters, crabs | Crustaceans | 2.60 |
| 63 | 91.3 | 584,332 | `Octopodidae` | **family** | Octopuses | Cephalopods | Other fishes & inverts | 3.59 |
| 64 | 91.5 | 578,418 | `Clupeidae` | **family** | Herrings, sardines, menhadens | Small pelagics (<30 cm) | Herring-likes | 3.16 |
| 65 | 91.7 | 553,050 | `Ammodytes personatus` | species | Pacific sandlance | Small demersals (<30 cm) | Perch-likes | 3.00 |
| 66 | 91.9 | 531,011 | `Ruditapes philippinarum` | species | Japanese carpet shell | Other demersal invertebrates | Molluscs | 2.00 |
| 67 | 92.1 | 516,794 | `Dussumieria` | genus | Rainbow sardines | Small pelagics (<30 cm) | Herring-likes | 3.40 |
| 68 | 92.3 | 513,751 | `Scombridae` | **family** | Mackerels, tunas, bonitos | Medium pelagics (30 - 89 cm) | Perch-likes | 4.26 |
| 69 | 92.5 | 496,055 | `Paralichthyidae` | **family** | Largetooth flounders | Small to medium flatfishes (<90 cm) | Flatfishes | 4.06 |
| 70 | 92.6 | 494,813 | `Elasmobranchii` | genus | Sharks, rays, skates | Large sharks (>=90 cm) | Sharks & rays | 4.05 |
| 71 | 92.8 | 491,695 | `Konosirus punctatus` | species | Dotted gizzard shad | Small pelagics (<30 cm) | Herring-likes | 2.87 |
| 72 | 93.0 | 458,399 | `Auxis` | genus | Bullet and frigate tunas | Medium pelagics (30 - 89 cm) | Tuna & billfishes | 4.24 |
| 73 | 93.1 | 457,803 | `Tetraodontidae` | **family** | Puffers, tobies | Large reef assoc. fish (>=90 cm) | Other fishes & inverts | 3.50 |
| 74 | 93.3 | 437,631 | `Pampus argenteus` | species | Silver pomfret | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.30 |
| 75 | 93.4 | 417,477 | `Priacanthus` | genus | Bigeyes | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.81 |
| 76 | 93.6 | 414,545 | `Synodontidae` | **family** | Lizardfishes, sauries | Medium demersals (30 - 89 cm) | Other fishes & inverts | 4.30 |
| 77 | 93.7 | 394,575 | `Paralichthys olivaceus` | species | Bastard halibut | Large flatfishes (>=90 cm) | Flatfishes | 4.25 |
| 78 | 93.9 | 387,972 | `Coryphaena hippurus` | species | Common dolphinfish | Large pelagics (>=90 cm) | Perch-likes | 4.37 |
| 79 | 94.0 | 380,780 | `Nemipterus virgatus` | species | Golden threadfin bream | Medium demersals (30 - 89 cm) | Perch-likes | 3.99 |
| 80 | 94.1 | 378,083 | `Salmonidae` | **family** | Salmonids | Large benthopelagics (>=90 cm) | Salmon, smelts, etc | 3.30 |
| 81 | 94.3 | 376,985 | `Portunus pelagicus` | species | Blue swimming crab | Lobsters, crabs | Crustaceans | 2.48 |
| 82 | 94.4 | 376,346 | `Sardinella zunasi` | species | Japanese sardinella | Small pelagics (<30 cm) | Herring-likes | 3.12 |
| 83 | 94.5 | 363,494 | `Charybdis` | genus | Whirlpool swimming crabs | Lobsters, crabs | Crustaceans | 2.70 |
| 84 | 94.6 | 355,324 | `Magallana gigas` | species | Pacific cupped oyster | Other demersal invertebrates | Molluscs | 2.00 |
| 85 | 94.8 | 350,946 | `Anadara` | genus | Arks, blood cockles | Other demersal invertebrates | Molluscs | 2.00 |
| 86 | 94.9 | 330,266 | `Echinoidea` | **superfamily** | Sea urchins, sea hedgehogs | Other demersal invertebrates | Other fishes & inverts | 2.51 |
| 87 | 95.0 | 326,945 | `Decapterus maruadsi` | species | Japanese scad | Small pelagics (<30 cm) | Perch-likes | 3.40 |
| 88 | 95.1 | 318,824 | `Lateolabrax japonicus` | species | Japanese seabass | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.36 |
| 89 | 95.2 | 316,782 | `Priacanthus macracanthus` | species | Red bigeye | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.11 |
| 90 | 95.3 | 312,294 | `Exocoetidae` | **family** | Flyingfishes | Small pelagics (<30 cm) | Other fishes & inverts | 3.57 |
| 91 | 95.4 | 302,878 | `Scomber australasicus` | species | Blue mackerel | Medium pelagics (30 - 89 cm) | Perch-likes | 4.23 |
| 92 | 95.5 | 301,798 | `Mytilus coruscus` | species | Korean mussel | Other demersal invertebrates | Molluscs | 2.00 |
| 93 | 95.7 | 295,123 | `Atrobucca nibe` | species | Blackmouth croaker | Medium demersals (30 - 89 cm) | Perch-likes | 3.03 |
| 94 | 95.8 | 292,062 | `Spratelloides gracilis` | species | Silver-stripe round herring | Small pelagics (<30 cm) | Herring-likes | 3.06 |
| 95 | 95.9 | 269,538 | `Ruvettus pretiosus` | species | Oilfish | Large benthopelagics (>=90 cm) | Perch-likes | 4.18 |
| 96 | 95.9 | 266,462 | `Lutjanidae` | **family** | Snappers | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.02 |
| 97 | 96.0 | 266,427 | `Sebastidae` | **family** | Rockfishes, rockcods, thornyheads | Medium demersals (30 - 89 cm) | Scorpionfishes | 3.74 |
| 98 | 96.1 | 262,931 | `Pleurogrammus azonus` | species | Okhotsk atka mackerel | Medium demersals (30 - 89 cm) | Scorpionfishes | 3.60 |
| 99 | 96.2 | 262,293 | `Bathylagidae` | **family** | Deepsea smelts | Small bathypelagics (<30 cm) | Salmon, smelts, etc | 3.10 |
| 100 | 96.3 | 260,655 | `Clupeiformes` | **order** | Herrings, shads, anchovies | Small pelagics (<30 cm) | Other fishes & inverts | 3.24 |
| 101 | 96.4 | 259,641 | `Mullidae` | **family** | Goatfishes | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.46 |
| 102 | 96.5 | 252,888 | `Chelidonichthys kumu` | species | Bluefin gurnard | Medium demersals (30 - 89 cm) | Scorpionfishes | 3.68 |
| 103 | 96.6 | 251,483 | `Nibea mitsukurii` | species | Honnibe croaker | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.50 |
| 104 | 96.7 | 251,452 | `Saurida tumbil` | species | Greater lizardfish | Medium demersals (30 - 89 cm) | Other fishes & inverts | 4.40 |
| 105 | 96.8 | 244,737 | `Mugilidae` | **family** | Mullets, grey mullets | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 2.53 |
| 106 | 96.8 | 244,327 | `Coryphaena` | genus | Dolphinfishes | Large pelagics (>=90 cm) | Perch-likes | 4.49 |
| 107 | 96.9 | 243,979 | `Thunnus alalunga` | species | Albacore | Large pelagics (>=90 cm) | Tuna & billfishes | 4.30 |
| 108 | 97.0 | 241,390 | `Platycephalus indicus` | species | Bartail flathead | Medium demersals (30 - 89 cm) | Scorpionfishes | 3.60 |
| 109 | 97.1 | 233,447 | `Mactridae` | **family** | Mactra surf clams | Other demersal invertebrates | Molluscs | 2.00 |
| 110 | 97.2 | 225,279 | `Muraenesocidae` | **family** | Pike congers | Large demersals (>=90 cm) | Other fishes & inverts | 3.90 |
| 111 | 97.3 | 207,964 | `Squalidae` | **family** | Dogfish sharks | Large sharks (>=90 cm) | Sharks & rays |  |
| 112 | 97.3 | 202,009 | `Seriola lalandi` | species | Yellowtail amberjack | Large benthopelagics (>=90 cm) | Perch-likes |  |
| 113 | 97.4 | 194,475 | `Portunidae` | **family** | Swimming crabs | Lobsters, crabs | Crustaceans | 3.56 |
| 114 | 97.5 | 194,147 | `Pagrus auratus` | species | Silver seabream | Large demersals (>=90 cm) | Perch-likes | 3.59 |
| 115 | 97.5 | 181,261 | `Thunnus obesus` | species | Bigeye tuna | Large pelagics (>=90 cm) | Tuna & billfishes | 4.49 |
| 116 | 97.6 | 178,843 | `Haemulidae` | **family** | Grunts, sweetlips, bonnetmouths | Medium demersals (30 - 89 cm) | Perch-likes | 3.36 |
| 117 | 97.7 | 172,423 | `Gastropoda` | **class** | Sea snails | Other demersal invertebrates | Molluscs | 3.06 |
| 118 | 97.7 | 170,770 | `Holothuroidea` | **superfamily** | Sea cucumbers | Other demersal invertebrates | Other fishes & inverts | 2.00 |
| 119 | 97.8 | 170,438 | `Penaeus japonicus` | species | Kuruma prawn | Shrimps | Crustaceans | 2.70 |
| 120 | 97.8 | 169,862 | `Mytilidae` | **family** | Sea mussels | Other demersal invertebrates | Molluscs | 2.00 |
| 121 | 97.9 | 162,120 | `Penaeidae` | **family** | Commercial shrimps and prawns | Shrimps | Crustaceans | 3.31 |
| 122 | 97.9 | 161,385 | `Trichiuridae` | **family** | Cutlassfishes | Large benthopelagics (>=90 cm) | Perch-likes | 4.15 |
| 123 | 98.0 | 151,612 | `Parastromateus niger` | species | Black pomfret | Medium benthopelagics (30 - 89 cm) | Perch-likes | 2.93 |
| 124 | 98.1 | 148,894 | `Miichthys miiuy` | species | Mi-iuy croaker | Medium demersals (30 - 89 cm) | Perch-likes | 3.50 |
| 125 | 98.1 | 148,352 | `Nemopilema nomurai` | species | Nomura jelly | Jellyfish | Other fishes & inverts | 3.57 |
| 126 | 98.2 | 144,964 | `Decapterus` | genus | Scads | Medium pelagics (30 - 89 cm) | Perch-likes | 3.63 |
| 127 | 98.2 | 136,909 | `Gadus chalcogrammus` | species | Alaska pollock | Medium benthopelagics (30 - 89 cm) | Cod-likes | 3.57 |
| 128 | 98.3 | 131,986 | `Branchiostegus japonicus` | species | Horsehead tilefish | Medium demersals (30 - 89 cm) | Perch-likes |  |
| 129 | 98.3 | 127,413 | `Meretrix lusoria` | species | Japanese hard clam | Other demersal invertebrates | Molluscs | 2.00 |
| 130 | 98.3 | 127,154 | `Gadidae` | **family** | Cods, haddocks | Medium demersals (30 - 89 cm) | Cod-likes | 3.84 |
| 131 | 98.4 | 126,542 | `Scomberomorus guttatus` | species | Indo-Pacific king mackerel | Medium pelagics (30 - 89 cm) | Perch-likes | 4.28 |
| 132 | 98.4 | 118,930 | `Tegillarca granosa` | species | Granular ark | Other demersal invertebrates | Molluscs | 2.00 |
| 133 | 98.5 | 118,393 | `Menidae` | **family** | Moonfishes | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.45 |
| 134 | 98.5 | 117,945 | `Scorpaenidae` | **family** | Scorpionfishes, rockfishes | Large reef assoc. fish (>=90 cm) | Scorpionfishes | 3.92 |
| 135 | 98.6 | 115,550 | `Ommastrephidae` | **family** | Arrow squids | Cephalopods | Other fishes & inverts | 4.09 |
| 136 | 98.6 | 114,419 | `Veneridae` | **family** | Venus clams | Other demersal invertebrates | Molluscs | 2.00 |
| 137 | 98.6 | 112,459 | `Meretrix` | genus | Hard clams | Other demersal invertebrates | Molluscs |  |
| 138 | 98.7 | 111,019 | `Miscellaneous aquatic invertebrates` | **category** | Aquatic invertebrates | Other demersal invertebrates | Other fishes & inverts | 2.43 |
| 139 | 98.7 | 110,356 | `Ariidae` | **family** | Sea catfishes, coblers | Medium demersals (30 - 89 cm) | Other fishes & inverts | 3.48 |
| 140 | 98.8 | 110,211 | `Mene maculata` | species | Moonfish | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.45 |
| 141 | 98.8 | 109,533 | `Acanthopagrus schlegelii` | species | Blackhead seabream | Medium demersals (30 - 89 cm) | Perch-likes | 3.24 |
| 142 | 98.8 | 109,132 | `Octopus` | genus | Octopuses, pikas | Cephalopods | Other fishes & inverts | 3.80 |
| 143 | 98.9 | 108,959 | `Apostichopus japonicus` | species | Japanese sea cucumber | Other demersal invertebrates | Other fishes & inverts | 2.30 |
| 144 | 98.9 | 106,953 | `Arctoscopus japonicus` | species | Japanese sandfish | Small bathydemersals (<30 cm) | Perch-likes | 3.51 |
| 145 | 98.9 | 104,739 | `Batoidea` | **superfamily** | Batoids, skates, rays, sawfishes | Large rays (>=90 cm) | Sharks & rays | 3.72 |
| 146 | 99.0 | 101,912 | `Perciformes` | **order** | Perch-likes | Medium demersals (30 - 89 cm) | Perch-likes | 3.53 |
| 147 | 99.0 | 101,829 | `Ostreidae` | **family** | True oysters | Other demersal invertebrates | Molluscs | 2.00 |
| 148 | 99.1 | 100,251 | `Portunus` | genus | Swimmer crabs | Lobsters, crabs | Crustaceans | 3.26 |
| 149 | 99.1 | 94,937 | `Penaeus penicillatus` | species | Redtail prawn | Shrimps | Crustaceans | 2.70 |
| 150 | 99.1 | 94,827 | `Thunnus orientalis` | species | Pacific bluefin tuna | Large pelagics (>=90 cm) | Tuna & billfishes | 4.05 |
| 151 | 99.2 | 93,743 | `Liparis tanakae` | species | Tanaka's snailfish | Medium demersals (30 - 89 cm) | Scorpionfishes | 3.42 |
| 152 | 99.2 | 89,561 | `Trachurus` | genus | Jacks, horse mackerels | Medium pelagics (30 - 89 cm) | Perch-likes | 3.69 |
| 153 | 99.2 | 88,946 | `Hyporhamphus sajori` | species | Japanese halfbeak | Medium pelagics (30 - 89 cm) | Other fishes & inverts | 3.40 |
| 154 | 99.2 | 86,015 | `Kajikia audax` | species | Striped marlin | Large pelagics (>=90 cm) | Tuna & billfishes | 4.58 |
| 155 | 99.3 | 81,964 | `Clupea pallasii` | species | Pacific herring | Medium pelagics (30 - 89 cm) | Herring-likes | 3.16 |
| 156 | 99.3 | 81,443 | `Sepia` | genus | Sepia cuttlefishes | Cephalopods | Other fishes & inverts | 3.69 |
| 157 | 99.3 | 80,340 | `Haliotidae` | **family** | Abalones, ear shells | Other demersal invertebrates | Molluscs | 2.00 |
| 158 | 99.4 | 77,932 | `Metapenaeus` | genus | Indo-Pacific prawns | Shrimps | Crustaceans | 2.70 |
| 159 | 99.4 | 76,180 | `Serranidae` | **family** | Basses, groupers, hinds | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.98 |
| 160 | 99.4 | 75,649 | `Pleuronectiformes` | **order** | Flatfishes | Small to medium flatfishes (<90 cm) | Flatfishes | 3.57 |
| 161 | 99.4 | 75,389 | `Scomberomorus commerson` | species | Narrow-barred Spanish mackerel | Large pelagics (>=90 cm) | Perch-likes | 4.50 |
| 162 | 99.5 | 71,627 | `Engraulidae` | **family** | Anchovies, round herrings | Small pelagics (<30 cm) | Anchovies | 3.20 |
| 163 | 99.5 | 69,690 | `Metapenaeus joyneri` | species | Shiba shrimp | Shrimps | Crustaceans | 3.20 |
| 164 | 99.5 | 68,433 | `Kyphosidae` | **family** | Sea chubs, knifefishes, niblers | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 2.19 |
| 165 | 99.5 | 64,133 | `Marine finfishes not identified` | **category** | Finfishes | Medium demersals (30 - 89 cm) | Other fishes & inverts | 3.23 |
| 166 | 99.6 | 63,755 | `Oplegnathus fasciatus` | species | Barred knifejaw | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.55 |
| 167 | 99.6 | 63,369 | `Cardiidae` | **family** | Cockles | Other demersal invertebrates | Molluscs | 2.00 |
| 168 | 99.6 | 62,950 | `Lethrinidae` | **family** | Emperors, scavengers | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.59 |
| 169 | 99.6 | 60,256 | `Chondrichthyes` | genus | Sharks, rays, chimaeras | Large sharks (>=90 cm) | Sharks & rays | 4.00 |
| 170 | 99.6 | 50,735 | `Parapristipoma trilineatum` | species | Chicken grunt | Small pelagics (<30 cm) | Perch-likes |  |
| 171 | 99.7 | 42,288 | `Evynnis tumifrons` | species | Yellowback seabream | Medium demersals (30 - 89 cm) | Perch-likes | 3.97 |
| 172 | 99.7 | 40,681 | `Scyllaridae` | **family** | Slipper lobsters | Lobsters, crabs | Crustaceans | 2.87 |
| 173 | 99.7 | 35,797 | `Xiphias gladius` | species | Swordfish | Large pelagics (>=90 cm) | Tuna & billfishes | 4.53 |
| 174 | 99.7 | 35,633 | `Epinephelus coioides` | species | Orange-spotted grouper | Large reef assoc. fish (>=90 cm) | Perch-likes | 4.00 |
| 175 | 99.7 | 33,882 | `Gobiidae` | **family** | Gobies | Small reef assoc. fish (<30 cm) | Perch-likes | 3.11 |
| 176 | 99.7 | 31,522 | `Ariomma indica` | species | Indian driftfish | Small benthopelagics (<30 cm) | Perch-likes | 3.63 |
| 177 | 99.7 | 29,929 | `Platycaranx talamparoides` | species | Imposter trevally | Medium pelagics (30 - 89 cm) | Perch-likes | 4.40 |
| 178 | 99.7 | 29,675 | `Decapterus russelli` | species | Indian scad | Medium pelagics (30 - 89 cm) | Perch-likes | 3.68 |
| 179 | 99.8 | 29,278 | `Panulirus` | genus | Spiny lobsters | Lobsters, crabs | Crustaceans |  |
| 180 | 99.8 | 28,913 | `Niphon spinosus` | species | Ara | Medium demersals (30 - 89 cm) | Perch-likes | 4.50 |
| 181 | 99.8 | 28,555 | `Chanos chanos` | species | Milkfish | Large benthopelagics (>=90 cm) | Other fishes & inverts | 2.03 |
| 182 | 99.8 | 28,314 | `Istiompax indica` | species | Black marlin | Large pelagics (>=90 cm) | Tuna & billfishes | 4.50 |
| 183 | 99.8 | 28,085 | `Panulirus longipes` | species | Longlegged spiny lobster | Lobsters, crabs | Crustaceans | 2.60 |
| 184 | 99.8 | 26,808 | `Sillaginidae` | **family** | Smelt-whitings | Medium demersals (30 - 89 cm) | Perch-likes | 3.25 |
| 185 | 99.8 | 26,536 | `Lateolabracidae` | **family** | Asian seaperches | Large demersals (>=90 cm) | Perch-likes | 3.78 |
| 186 | 99.8 | 24,879 | `Ammodytes` | genus | Sand eels | Large reef assoc. fish (>=90 cm) | Perch-likes | 3.11 |
| 187 | 99.8 | 24,833 | `Cypselurus` | genus | Cypselurid flyingfishes | Small pelagics (<30 cm) | Other fishes & inverts | 3.40 |
| 188 | 99.8 | 23,372 | `Gymnocranius` | genus | Largeeye breams | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.40 |
| 189 | 99.8 | 21,850 | `Muraenidae` | **family** | Moray eels | Large reef assoc. fish (>=90 cm) | Other fishes & inverts | 4.07 |
| 190 | 99.9 | 21,361 | `Ibacus ciliatus` | species | Sand Crayfish | Lobsters, crabs | Crustaceans | 2.60 |
| 191 | 99.9 | 21,010 | `Scylla serrata` | species | Indo-Pacific swamp crab | Lobsters, crabs | Crustaceans | 3.17 |
| 192 | 99.9 | 20,761 | `Istiophoridae` | **family** | Billfishes | Large pelagics (>=90 cm) | Tuna & billfishes | 4.48 |
| 193 | 99.9 | 20,591 | `Megalaspis cordyla` | species | Torpedo scad | Medium pelagics (30 - 89 cm) | Perch-likes | 4.24 |
| 194 | 99.9 | 16,984 | `Hexagrammos otakii` | species | Fat grrenling | Small pelagics (<30 cm) | Scorpionfishes |  |
| 195 | 99.9 | 16,064 | `Mizuhopecten yessoensis` | species | Yesso scallop | Other demersal invertebrates | Molluscs | 2.10 |
| 196 | 99.9 | 15,902 | `Platycaranx malabaricus` | species | Malabar trevally | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.88 |
| 197 | 99.9 | 15,659 | `Rachycentridae` | **family** | Cobias | Large pelagics (>=90 cm) | Perch-likes | 3.96 |
| 198 | 99.9 | 15,436 | `Haliotis` | genus | Abalones | Other demersal invertebrates | Molluscs | 2.00 |
| 199 | 99.9 | 15,411 | `Sillago` | genus | Smelt-whitings | Medium demersals (30 - 89 cm) | Perch-likes | 3.33 |
| 200 | 99.9 | 15,352 | `Hemiramphidae` | **family** | Halfbeaks, garfishes | Medium pelagics (30 - 89 cm) | Other fishes & inverts | 2.82 |
| 201 | 99.9 | 15,309 | `Hypoptychus dybowskii` | species | Korean sandlance | Small benthopelagics (<30 cm) | Other fishes & inverts |  |
| 202 | 99.9 | 15,194 | `Bramidae` | **family** | Pomfrets | Medium pelagics (30 - 89 cm) | Perch-likes | 4.14 |
| 203 | 99.9 | 15,082 | `Penaeus monodon` | species | Giant tiger prawn | Shrimps | Crustaceans | 2.60 |
| 204 | 99.9 | 14,481 | `Acanthocybium solandri` | species | Wahoo | Large pelagics (>=90 cm) | Perch-likes | 4.26 |
| 205 | 99.9 | 12,814 | `Saurida undosquamis` | species | Brushtooth lizardfish | Medium demersals (30 - 89 cm) | Other fishes & inverts | 4.46 |
| 206 | 99.9 | 12,628 | `Beryx splendens` | species | Splendid alfonsino | Medium benthopelagics (30 - 89 cm) | Other fishes & inverts | 4.27 |
| 207 | 99.9 | 12,020 | `Auxis rochei` | species | Bullet tuna | Medium pelagics (30 - 89 cm) | Tuna & billfishes | 4.13 |
| 208 | 100.0 | 11,759 | `Scorpaeniformes` | **order** | Scorpionfishes, flatheads | Medium demersals (30 - 89 cm) | Scorpionfishes | 3.78 |
| 209 | 100.0 | 11,558 | `Epinephelus maculatus` | species | Highfin grouper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.98 |
| 210 | 100.0 | 10,808 | `Isurus` | genus | Mako sharks | Large sharks (>=90 cm) | Sharks & rays | 4.50 |
| 211 | 100.0 | 10,193 | `Dussumieria elopsoides` | species | Slender rainbow sardine | Small pelagics (<30 cm) | Herring-likes | 3.40 |
| 212 | 100.0 | 10,072 | `Chirocentrus dorab` | species | Dorab wolf-herring | Large benthopelagics (>=90 cm) | Herring-likes |  |
| 213 | 100.0 | 7,656 | `Oratosquilla oratoria` | species | Japanese squillid mantis shrimp | Shrimps | Crustaceans | 3.27 |
| 214 | 100.0 | 7,507 | `Saurida` | genus | Lizardfishes | Medium demersals (30 - 89 cm) | Other fishes & inverts | 4.35 |
| 215 | 100.0 | 6,797 | `Stolephorus` | genus | Garment anchovies | Small pelagics (<30 cm) | Anchovies |  |
| 216 | 100.0 | 4,859 | `Sphyraena` | genus | Barracudas, sennets | Large pelagics (>=90 cm) | Perch-likes | 4.40 |
| 217 | 100.0 | 4,839 | `Rapana` | genus | Rapa whelks | Other demersal invertebrates | Molluscs | 3.00 |
| 218 | 100.0 | 4,739 | `Sphyraenidae` | **family** | Barracudas | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.40 |
| 219 | 100.0 | 4,450 | `Pseudopleuronectes herzensteini` | species | Yellow striped flounder | Small to medium flatfishes (<90 cm) | Flatfishes | 3.15 |
| 220 | 100.0 | 4,446 | `Hemitriakis japanica` | species | Japanese topeshark | Large sharks (>=90 cm) | Sharks & rays |  |
| 221 | 100.0 | 4,319 | `Makaira mazara` | species | Indo-Pacific blue marlin | Large pelagics (>=90 cm) | Tuna & billfishes | 4.46 |
| 222 | 100.0 | 3,605 | `Marine pelagic fishes not identified` | **category** | Pelagic fishes | Medium pelagics (30 - 89 cm) | Other fishes & inverts | 3.35 |
| 223 | 100.0 | 3,466 | `Mierspenaeopsis hardwickii` | species | Spear shrimp | Shrimps | Crustaceans | 2.71 |
| 224 | 100.0 | 2,998 | `Beryx` | genus | Alfonsinos | Medium benthopelagics (30 - 89 cm) | Other fishes & inverts | 3.97 |
| 225 | 100.0 | 2,330 | `Auxis thazard` | species | Frigate tuna | Medium pelagics (30 - 89 cm) | Tuna & billfishes | 4.37 |
| 226 | 100.0 | 2,144 | `Polydactylus sexfilis` | species | Sixfinger threadfin | Medium demersals (30 - 89 cm) | Perch-likes | 3.43 |
| 227 | 100.0 | 2,118 | `Seriola dumerili` | species | Greater amberjack | Large reef assoc. fish (>=90 cm) | Perch-likes | 4.50 |
| 228 | 100.0 | 2,089 | `Cheilopogon unicolor` | species | Limpidwing flyingfish | Medium pelagics (30 - 89 cm) | Other fishes & inverts | 3.70 |
| 229 | 100.0 | 1,967 | `Lates calcarifer` | species | Barramundi | Large demersals (>=90 cm) | Perch-likes | 4.35 |
| 230 | 100.0 | 1,671 | `Hexagrammidae` | **family** | Greenlings | Medium demersals (30 - 89 cm) | Scorpionfishes | 3.72 |
| 231 | 100.0 | 1,621 | `Clupanodon thrissa` | species | Chinese gizzard shad | Small pelagics (<30 cm) | Herring-likes | 3.01 |
| 232 | 100.0 | 1,514 | `Ommastrephes bartramii` | species | Neon flying squid | Cephalopods | Other fishes & inverts | 4.37 |
| 233 | 100.0 | 1,457 | `Mola mola` | species | Ocean sunfish | Large pelagics (>=90 cm) | Other fishes & inverts | 3.68 |
| 234 | 100.0 | 1,393 | `Scaridae` | **family** | Parrotfishes | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 2.00 |
| 235 | 100.0 | 1,323 | `Aluterus` | genus | Aluterid filefishes | Large reef assoc. fish (>=90 cm) | Other fishes & inverts | 2.81 |
| 236 | 100.0 | 1,217 | `Chionoecetes` | genus | Tanner, snow crabs | Lobsters, crabs | Crustaceans |  |
| 237 | 100.0 | 1,203 | `Prionace glauca` | species | Blue shark | Large sharks (>=90 cm) | Sharks & rays | 4.35 |
| 238 | 100.0 | 1,157 | `Scylla` | genus | Mud crabs | Lobsters, crabs | Crustaceans | 3.17 |
| 239 | 100.0 | 1,107 | `Gadiformes` | **order** | Cods | Medium benthopelagics (30 - 89 cm) | Cod-likes |  |
| 240 | 100.0 | 1,056 | `Encrasicholina punctifer` | species | Buccaneer anchovy | Small pelagics (<30 cm) | Anchovies | 3.25 |
| 241 | 100.0 | 1,044 | `Nibea albiflora` | species | Yellow drum | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.50 |
| 242 | 100.0 | 979 | `Carcharhinus falciformis` | species | Silky shark | Large sharks (>=90 cm) | Sharks & rays | 4.51 |
| 243 | 100.0 | 847 | `Parupeneus barberinus` | species | Dash-and-dot goatfish | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.22 |
| 244 | 100.0 | 777 | `Epinephelus malabaricus` | species | Malabar grouper | Large reef assoc. fish (>=90 cm) | Perch-likes | 4.16 |
| 245 | 100.0 | 758 | `Ranina ranina` | species | Kona crab  | Lobsters, crabs | Crustaceans |  |
| 246 | 100.0 | 740 | `Metapenaeus ensis` | species | Greasyback shrimp | Shrimps | Crustaceans | 2.70 |
| 247 | 100.0 | 575 | `Rachycentron canadum` | species | Cobia | Large pelagics (>=90 cm) | Perch-likes | 3.96 |
| 248 | 100.0 | 571 | `Sphyraena barracuda` | species | Great barracuda | Large pelagics (>=90 cm) | Perch-likes | 4.49 |
| 249 | 100.0 | 405 | `Berycidae` | **family** | Alfonsinos, redfishes | Medium benthopelagics (30 - 89 cm) | Other fishes & inverts | 3.99 |
| 250 | 100.0 | 341 | `Psettodes erumei` | species | Indian halibut | Small to medium flatfishes (<90 cm) | Flatfishes | 4.39 |
| 251 | 100.0 | 303 | `Paralithodes` | genus | North Pacific king crabs | Lobsters, crabs | Crustaceans |  |
| 252 | 100.0 | 288 | `Hemitrygon akajei` | species | Whip stingray | Large rays (>=90 cm) | Sharks & rays | 3.84 |
| 253 | 100.0 | 231 | `Chionoecetes opilio` | species | Snow crab | Lobsters, crabs | Crustaceans | 3.54 |
| 254 | 100.0 | 217 | `Sillago sihama` | species | Silver sillago | Medium demersals (30 - 89 cm) | Perch-likes | 3.33 |
| 255 | 100.0 | 201 | `Lethrinus miniatus` | species | Trumpet emperor | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.19 |
| 256 | 100.0 | 139 | `Istiophorus platypterus` | species | Indo-Pacific sailfish | Large pelagics (>=90 cm) | Tuna & billfishes | 4.50 |
| 257 | 100.0 | 137 | `Lutjanus bohar` | species | Two-spot red snapper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.27 |
| 258 | 100.0 | 134 | `Rhincodon typus` | species | Whale shark | Large sharks (>=90 cm) | Sharks & rays |  |
| 259 | 100.0 | 129 | `Sergestidae` | **family** | Sergestid shrimp | Shrimps | Crustaceans | 2.93 |
| 260 | 100.0 | 115 | `Lepidocybium flavobrunneum` | species | Escolar | Large bathypelagics (>=90 cm) | Perch-likes |  |
| 261 | 100.0 | 105 | `Acetes` | genus | Acetes shrimps | Shrimps | Crustaceans | 2.70 |
| 262 | 100.0 | 79 | `Zenopsis nebulosa` | species | Mirror dory | Medium bathydemersals (30 - 89 cm) | Other fishes & inverts | 3.98 |
| 263 | 100.0 | 66 | `Carcharhinus longimanus` | species | Oceanic whitetip shark | Large sharks (>=90 cm) | Sharks & rays | 4.16 |
| 264 | 100.0 | 31 | `Lutjanus` | genus | Snappers | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.02 |
| 265 | 100.0 | 17 | `Alopias` | genus | Thresher sharks | Large sharks (>=90 cm) | Sharks & rays | 4.50 |
| 266 | 100.0 | 13 | `Holothuriidae` | **family** | Fleshy sea cucumbers | Other demersal invertebrates | Other fishes & inverts | 2.00 |
| 267 | 100.0 | 12 | `Tripneustes gratilla` | species | Shortspine urchin | Other demersal invertebrates | Other fishes & inverts | 2.00 |
| 268 | 100.0 | 10 | `Chionoecetes japonicus` | species | Red snow crab | Lobsters, crabs | Crustaceans | 3.74 |
| 269 | 100.0 | 7 | `Upeneus` | genus | Upeneid goatfishes | Small reef assoc. fish (<30 cm) | Perch-likes |  |
| 270 | 100.0 | 4 | `Echinozoa` | **phylum** | Sea urchins and sea cucumbers | Other demersal invertebrates | Other fishes & inverts |  |
| 271 | 100.0 | 2 | `Rhopilema hispidum` | species | Sand jellyfish | Jellyfish | Other fishes & inverts | 3.46 |
| 272 | 100.0 | 1 | `Sphyrna` | genus | Hammerhead sharks | Large sharks (>=90 cm) | Sharks & rays | 4.20 |
| 273 | 100.0 | 1 | `Isurus oxyrinchus` | species | Shortfin mako | Large sharks (>=90 cm) | Sharks & rays | 4.50 |
| 274 | 100.0 | 0 | `Pinctada` | genus | Mother of pearl oysters | Other demersal invertebrates | Molluscs |  |
| 275 | 100.0 | 0 | `Scombroidei` | **suborder** | Tunas, bonitos, billfishes | Large pelagics (>=90 cm) | Tuna & billfishes |  |
| 276 | 100.0 | 0 | `Caranx` | genus | Jacks | Medium reef assoc. fish (30 - 89 cm) | Perch-likes |  |

## Where the difficulty is

80 of 276 labels sit above genus and together carry **86,710,138 tonnes (30.7 % of the catch)**.
Leaving these unresolved is what caps coverage near 78 %. Read `references/coarse-taxa-playbook.md` before deciding any of them.

The ten largest:

- `Marine fishes not identified` — 36,591,787 t (12.9 %), SAU: Medium demersals (30 - 89 cm) / Other fishes & inverts
- `Miscellaneous marine crustaceans` — 6,656,949 t (2.4 %), SAU: Shrimps / Crustaceans
- `Sciaenidae` — 5,013,099 t (1.8 %), SAU: Medium demersals (30 - 89 cm) / Perch-likes
- `Pectinidae` — 4,644,809 t (1.6 %), SAU: Other demersal invertebrates / Molluscs
- `Scyphozoa` — 4,334,965 t (1.5 %), SAU: Jellyfish / Other fishes & inverts
- `Pleuronectidae` — 3,661,117 t (1.3 %), SAU: Small to medium flatfishes (<90 cm) / Flatfishes
- `Monacanthidae` — 3,089,551 t (1.1 %), SAU: Medium reef assoc. fish (30 - 89 cm) / Other fishes & inverts
- `Octopoda` — 2,576,878 t (0.9 %), SAU: Cephalopods / Other fishes & inverts
- `Carangidae` — 1,801,294 t (0.6 %), SAU: Medium pelagics (30 - 89 cm) / Perch-likes
- `Squillidae` — 1,512,499 t (0.5 %), SAU: Shrimps / Crustaceans
