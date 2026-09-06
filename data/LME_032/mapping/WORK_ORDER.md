# Mapping work order — LME_032

catch years        : 1950-2019
taxa to map        : 430
total catch        : 197,852,454 tonnes over the whole period
Ecopath models     : 1

## Model selection — check `usable` before mapping

| author | title | usable | notes |
| --- | --- | --- | --- |
| Mohamed K.S (2008) | A trophic model of the Arabian Sea Ecosystem off Karnataka | **yes** |  |

A model marked `no` must not be mapped. Say so and stop.

## Model `32_1_Arabian_Sea_off_Karnataka_(2000)`

25 groups, 20 SPPR methods. Group names below are verbatim and authoritative — copy them exactly.

| seq | group_name | type | TL | biomass | model catch |
| --- | --- | --- | --- | --- | --- |
| 1 | `Marine Mammals` | Regular | 4.061 | 0.019 | 0 |
| 2 | `Sharks` | Regular | 4.449 | 0.013 | 0.03 |
| 3 | `Skates & Rays` | Regular | 3.586 | 0.022 | 0.009 |
| 4 | `Large Pelagics` | Regular | 4.179 | 0.061 | 0.185 |
| 5 | `Tunas` | Regular | 4.143 | 0.032 | 0.113 |
| 6 | `Cephalopods` | Regular | 4.183 | 0.234 | 0.278 |
| 7 | `Large Benthopelagics` | Regular | 4.149 | 0.106 | 0.351 |
| 8 | `Large Benthic Carnivores` | Regular | 4.144 | 0.628 | 0.281 |
| 9 | `Med Benthic Carnivores` | Regular | 3.19 | 0.108 | 0.33 |
| 10 | `Small Benthic Carnivores` | Regular | 2.683 | 0.53 | 0.816 |
| 11 | `Small Benthopelagics` | Regular | 3.878 | 0.281 | 0.38 |
| 12 | `Mackerel` | Regular | 2 | 0.249 | 0.945 |
| 13 | `Clupeids` | Regular | 2.949 | 0.289 | 1.439 |
| 14 | `Anchovies` | Regular | 3.488 | 1.11 | 0.201 |
| 15 | `Crabs & Lobster` | Regular | 2.893 | 0.14 | 0.061 |
| 16 | `Shrimps` | Regular | 3.015 | 0.826 | 0.306 |
| 17 | `Benthic Omnivores` | Regular | 2.551 | 0.556 | 0.844 |
| 18 | `Heterotrophic Benthos` | Regular | 2.323 | 38 | 0 |
| 19 | `Meiobenthos` | Regular | 2.023 | 20 | 0 |
| 20 | `Micro Nekton` | Regular | 3.242 | 0.8 | 0 |
| 21 | `Large zooplankton` | Regular | 2.584 | 4 | 0 |
| 22 | `Micro Zooplankton` | Regular | 2 | 10 | 0 |
| 23 | `Phytoplankton` | PP | 1 | 58.5 | 0 |
| 24 | `Detritus` | DET | 1 | 9.3 | 0 |
| 25 | `diet_import` | Import | 1 | 1 | 0 |

`taxon_descr` is empty for every group, so the paper and its supplements are the only source of membership. Record that limitation in the notes.

## Taxa, by tonnage

`coarse` marks a label above genus: it may legitimately span several groups, which is what the composite syntax is for.

| # | cum % | tonnes | taxon | rank | common name | SAU functional group | SAU commercial group | TL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 12.5 | 24,743,762 | `Marine fishes not identified` | **category** | Marine fishes nei | Medium demersals (30 - 89 cm) | Other fishes & inverts | 3.28 |
| 2 | 23.6 | 21,859,960 | `Sardinella longiceps` | species | Indian oil sardine | Small pelagics (<30 cm) | Herring-likes | 2.41 |
| 3 | 28.1 | 8,918,687 | `Penaeidae` | **family** | Commercial shrimps and prawns | Shrimps | Crustaceans | 3.31 |
| 4 | 31.8 | 7,443,896 | `Rastrelliger kanagurta` | species | Indian mackerel | Medium pelagics (30 - 89 cm) | Perch-likes | 3.19 |
| 5 | 35.2 | 6,707,975 | `Sciaenidae` | **family** | Drums, croakers | Medium demersals (30 - 89 cm) | Perch-likes | 3.76 |
| 6 | 38.6 | 6,694,091 | `Decapoda` | genus | Crabs, lobsters, shrimps | Lobsters, crabs | Crustaceans | 3.43 |
| 7 | 41.8 | 6,251,571 | `Harpadon nehereus` | species | Bombay-duck | Medium benthopelagics (30 - 89 cm) | Other fishes & inverts | 4.20 |
| 8 | 44.3 | 5,102,723 | `Clupeiformes` | **order** | Herrings, shads, anchovies | Small pelagics (<30 cm) | Other fishes & inverts | 3.24 |
| 9 | 46.4 | 4,009,328 | `Nemipteridae` | **family** | Threadfins, whiptail breams | Small demersals (<30 cm) | Perch-likes | 3.51 |
| 10 | 48.3 | 3,854,520 | `Clupeidae` | **family** | Herrings, sardines, menhadens | Small pelagics (<30 cm) | Herring-likes | 3.16 |
| 11 | 50.0 | 3,372,977 | `Bivalvia` | genus | Clams | Other demersal invertebrates | Molluscs | 2.23 |
| 12 | 51.6 | 3,111,578 | `Carangidae` | **family** | Jacks, pompanos | Medium pelagics (30 - 89 cm) | Perch-likes | 4.05 |
| 13 | 53.2 | 3,089,128 | `Scomberomorus commerson` | species | Narrow-barred Spanish mackerel | Large pelagics (>=90 cm) | Perch-likes | 4.50 |
| 14 | 54.7 | 3,034,890 | `Thunnus albacares` | species | Yellowfin tuna | Large pelagics (>=90 cm) | Tuna & billfishes | 4.41 |
| 15 | 56.2 | 2,956,883 | `Carcharhinidae` | **family** | Requiem sharks | Large sharks (>=90 cm) | Sharks & rays | 4.24 |
| 16 | 57.6 | 2,892,969 | `Ariidae` | **family** | Sea catfishes, coblers | Medium demersals (30 - 89 cm) | Other fishes & inverts | 3.48 |
| 17 | 58.9 | 2,495,476 | `Elasmobranchii` | genus | Sharks, rays, skates | Large sharks (>=90 cm) | Sharks & rays | 4.05 |
| 18 | 60.1 | 2,341,898 | `Siluriformes` | **order** | Catfishes | Medium demersals (30 - 89 cm) | Other fishes & inverts | 3.48 |
| 19 | 61.2 | 2,158,952 | `Netuma thalassina` | species | Giant catfish | Large demersals (>=90 cm) | Other fishes & inverts | 3.54 |
| 20 | 62.2 | 2,081,456 | `Leiognathidae` | **family** | Slipmouths, ponyfishes | Small benthopelagics (<30 cm) | Perch-likes | 3.24 |
| 21 | 63.3 | 2,074,947 | `Decapterus` | genus | Scads | Medium pelagics (30 - 89 cm) | Perch-likes | 3.63 |
| 22 | 64.3 | 2,035,289 | `Engraulidae` | **family** | Anchovies, round herrings | Small pelagics (<30 cm) | Anchovies | 3.20 |
| 23 | 65.3 | 2,019,039 | `Rastrelliger` | genus | Indian mackerels | Medium pelagics (30 - 89 cm) | Perch-likes | 3.10 |
| 24 | 66.2 | 1,815,616 | `Perciformes` | **order** | Perch-likes | Medium demersals (30 - 89 cm) | Perch-likes | 3.53 |
| 25 | 67.1 | 1,764,086 | `Soleidae` | **family** | Soles | Small to medium flatfishes (<90 cm) | Flatfishes | 3.15 |
| 26 | 68.0 | 1,669,326 | `Cephalopoda` | **class** | Squids, cuttlefishes, octopuses | Cephalopods | Other fishes & inverts | 3.81 |
| 27 | 68.8 | 1,654,746 | `Stolephorus` | genus | Garment anchovies | Small pelagics (<30 cm) | Anchovies | 3.44 |
| 28 | 69.6 | 1,621,588 | `Penaeus semisulcatus` | species | Green tiger prawn | Shrimps | Crustaceans | 2.00 |
| 29 | 70.3 | 1,406,593 | `Trichiurus lepturus` | species | Largehead hairtail | Large benthopelagics (>=90 cm) | Perch-likes | 4.42 |
| 30 | 71.1 | 1,403,252 | `Sepiidae` | **family** | Cuttlefishes | Cephalopods | Other fishes & inverts | 3.60 |
| 31 | 71.8 | 1,394,181 | `Serranidae` | **family** | Basses, groupers, hinds | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.98 |
| 32 | 72.4 | 1,295,404 | `Thryssa` | genus | Thryssas | Small pelagics (<30 cm) | Anchovies | 3.34 |
| 33 | 73.1 | 1,268,944 | `Katsuwonus pelamis` | species | Skipjack tuna | Large pelagics (>=90 cm) | Tuna & billfishes | 4.43 |
| 34 | 73.7 | 1,259,868 | `Synodontidae` | **family** | Lizardfishes, sauries | Medium demersals (30 - 89 cm) | Other fishes & inverts | 4.30 |
| 35 | 74.3 | 1,220,451 | `Otolithes ruber` | species | Tigertooth croaker | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.60 |
| 36 | 74.9 | 1,166,516 | `Thunnus tonggol` | species | Longtail tuna | Large pelagics (>=90 cm) | Tuna & billfishes | 4.50 |
| 37 | 75.5 | 1,098,891 | `Scombridae` | **family** | Mackerels, tunas, bonitos | Medium pelagics (30 - 89 cm) | Perch-likes | 4.26 |
| 38 | 76.0 | 1,031,415 | `Teuthida` | genus | Squids | Cephalopods | Other fishes & inverts | 4.13 |
| 39 | 76.5 | 996,585 | `Portunus pelagicus` | species | Blue swimming crab | Lobsters, crabs | Crustaceans | 2.48 |
| 40 | 77.0 | 985,215 | `Coryphaena hippurus` | species | Common dolphinfish | Large pelagics (>=90 cm) | Perch-likes | 4.37 |
| 41 | 77.5 | 959,509 | `Mugilidae` | **family** | Mullets, grey mullets | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 2.53 |
| 42 | 77.9 | 940,847 | `Tenualosa ilisha` | species | Hilsa shad | Medium pelagics (30 - 89 cm) | Herring-likes | 2.20 |
| 43 | 78.4 | 906,175 | `Platycaranx chrysophrys` | species | Longnose trevally | Small pelagics (<30 cm) | Perch-likes | 4.30 |
| 44 | 78.8 | 891,125 | `Alopias superciliosus` | species | Bigeye thresher | Large sharks (>=90 cm) | Sharks & rays | 4.51 |
| 45 | 79.3 | 881,596 | `Parastromateus niger` | species | Black pomfret | Medium benthopelagics (30 - 89 cm) | Perch-likes | 2.93 |
| 46 | 79.7 | 876,508 | `Isurus oxyrinchus` | species | Shortfin mako | Large sharks (>=90 cm) | Sharks & rays | 4.50 |
| 47 | 80.2 | 866,451 | `Scomberomorus guttatus` | species | Indo-Pacific king mackerel | Medium pelagics (30 - 89 cm) | Perch-likes | 4.28 |
| 48 | 80.6 | 808,579 | `Lactarius lactarius` | species | False trevally | Medium pelagics (30 - 89 cm) | Perch-likes | 3.97 |
| 49 | 81.0 | 771,545 | `Sparidae` | **family** | Porgies, seabreams | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.31 |
| 50 | 81.3 | 740,452 | `Scomberoides commersonnianus` | species | Talang queenfish | Large reef assoc. fish (>=90 cm) | Perch-likes | 4.48 |
| 51 | 81.7 | 738,911 | `Sphyraena barracuda` | species | Great barracuda | Large pelagics (>=90 cm) | Perch-likes | 4.49 |
| 52 | 82.1 | 736,193 | `Lethrinus nebulosus` | species | Spangled emperor | Medium demersals (30 - 89 cm) | Perch-likes | 3.76 |
| 53 | 82.5 | 735,234 | `Lethrinidae` | **family** | Emperors, scavengers | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.59 |
| 54 | 82.8 | 727,113 | `Sardinella sindensis` | species | Sind sardinella | Small pelagics (<30 cm) | Herring-likes | 2.90 |
| 55 | 83.2 | 717,138 | `Sphyraena` | genus | Barracudas, sennets | Large pelagics (>=90 cm) | Perch-likes | 4.40 |
| 56 | 83.6 | 712,149 | `Scyphozoa` | **phylum** | True jellyfishes | Jellyfish | Other fishes & inverts | 3.46 |
| 57 | 83.9 | 710,556 | `Euthynnus affinis` | species | Kawakawa | Large pelagics (>=90 cm) | Tuna & billfishes | 4.50 |
| 58 | 84.3 | 684,063 | `Dendrobranchiata` | genus | Shrimps and prawns | Shrimps | Crustaceans | 3.24 |
| 59 | 84.6 | 682,440 | `Marine pelagic fishes not identified` | **category** | Pelagic fishes | Medium pelagics (30 - 89 cm) | Other fishes & inverts | 3.35 |
| 60 | 84.9 | 655,231 | `Pampus` | genus | Silver pomfrets | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.41 |
| 61 | 85.3 | 639,450 | `Bramidae` | **family** | Pomfrets | Medium pelagics (30 - 89 cm) | Perch-likes | 4.14 |
| 62 | 85.6 | 630,038 | `Scomberoides lysan` | species | Doublespotted queenfish | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.38 |
| 63 | 85.9 | 614,306 | `Nemipterus japonicus` | species | Japanese threadfin bream | Small demersals (<30 cm) | Perch-likes | 3.77 |
| 64 | 86.2 | 609,226 | `Thryssa dussumieri` | species | Dussumier's thryssa | Small pelagics (<30 cm) | Anchovies | 2.82 |
| 65 | 86.5 | 604,225 | `Pomadasys stridens` | species | Striped piggy | Small reef assoc. fish (<30 cm) | Perch-likes | 4.02 |
| 66 | 86.8 | 602,770 | `Epinephelus` | genus | Seabasses, hinds | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.84 |
| 67 | 87.1 | 599,406 | `Mullidae` | **family** | Goatfishes | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.46 |
| 68 | 87.4 | 588,654 | `Siganidae` | **family** | Rabbitfishes | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 2.11 |
| 69 | 87.7 | 581,595 | `Nematalosa nasus` | species | Bloch's gizzard shad | Small pelagics (<30 cm) | Herring-likes | 2.67 |
| 70 | 88.0 | 554,264 | `Scomberoides` | genus | Queenfishes | Medium pelagics (30 - 89 cm) | Perch-likes | 4.47 |
| 71 | 88.2 | 491,361 | `Sepia` | genus | Sepia cuttlefishes | Cephalopods | Other fishes & inverts | 3.69 |
| 72 | 88.5 | 473,954 | `Chirocentrus` | genus | Wolf herrings | Large pelagics (>=90 cm) | Herring-likes | 4.30 |
| 73 | 88.7 | 459,844 | `Myliobatidae` | **family** | Eagle/manta rays | Large rays (>=90 cm) | Sharks & rays | 3.36 |
| 74 | 88.9 | 424,932 | `Sepia pharaonis` | species | Pharaoh cuttlefish | Cephalopods | Other fishes & inverts | 3.80 |
| 75 | 89.1 | 394,600 | `Polynemidae` | **family** | Threadfins | Small demersals (<30 cm) | Perch-likes | 3.62 |
| 76 | 89.3 | 389,450 | `Anguilliformes` | **order** | Eels, morays | Large demersals (>=90 cm) | Other fishes & inverts | 3.89 |
| 77 | 89.5 | 389,277 | `Pampus argenteus` | species | Silver pomfret | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.30 |
| 78 | 89.7 | 388,192 | `Photopectoralis bindus` | species | Orangefin ponyfish | Large reef assoc. fish (>=90 cm) | Perch-likes | 2.93 |
| 79 | 89.9 | 385,147 | `Mugil cephalus` | species | Flathead grey mullet | Large benthopelagics (>=90 cm) | Perch-likes | 2.14 |
| 80 | 90.1 | 382,140 | `Batoidea` | **superfamily** | Batoids, skates, rays, sawfishes | Large rays (>=90 cm) | Sharks & rays | 3.72 |
| 81 | 90.3 | 372,309 | `Rhinobatidae` | **family** | Guitarfishes, fanrays | Large rays (>=90 cm) | Sharks & rays | 3.70 |
| 82 | 90.5 | 368,121 | `Psettodes erumei` | species | Indian halibut | Small to medium flatfishes (<90 cm) | Flatfishes | 4.39 |
| 83 | 90.6 | 347,682 | `Saurida tumbil` | species | Greater lizardfish | Medium demersals (30 - 89 cm) | Other fishes & inverts | 4.40 |
| 84 | 90.8 | 336,710 | `Anodontostoma chacunda` | species | Chacunda gizzard shad | Small pelagics (<30 cm) | Herring-likes | 2.84 |
| 85 | 91.0 | 333,218 | `Mytilidae` | **family** | Sea mussels | Other demersal invertebrates | Molluscs | 2.00 |
| 86 | 91.1 | 332,436 | `Caranx ignobilis` | species | Giant trevally | Large reef assoc. fish (>=90 cm) | Perch-likes | 4.22 |
| 87 | 91.3 | 330,623 | `Portunidae` | **family** | Swimming crabs | Lobsters, crabs | Crustaceans | 3.56 |
| 88 | 91.5 | 323,337 | `Chirocentrus nudus` | species | Whitefin wolf-herring | Large pelagics (>=90 cm) | Herring-likes | 4.19 |
| 89 | 91.6 | 322,976 | `Carcharhinus sorrah` | species | Spottail shark | Large sharks (>=90 cm) | Sharks & rays | 4.15 |
| 90 | 91.8 | 314,256 | `Lutjanidae` | **family** | Snappers | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.02 |
| 91 | 92.0 | 314,134 | `Sardinella gibbosa` | species | Goldstripe sardinella | Small pelagics (<30 cm) | Herring-likes | 2.85 |
| 92 | 92.1 | 313,757 | `Sillago sihama` | species | Silver sillago | Medium demersals (30 - 89 cm) | Perch-likes | 3.33 |
| 93 | 92.3 | 308,504 | `Rachycentron canadum` | species | Cobia | Large pelagics (>=90 cm) | Perch-likes | 3.96 |
| 94 | 92.4 | 307,603 | `Pleuronectiformes` | **order** | Flatfishes | Small to medium flatfishes (<90 cm) | Flatfishes | 3.57 |
| 95 | 92.6 | 304,241 | `Upeneus vittatus` | species | Yellowstriped goatfish | Small reef assoc. fish (<30 cm) | Perch-likes | 3.62 |
| 96 | 92.7 | 298,082 | `Pomadasys kaakan` | species | Javelin grunter | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.46 |
| 97 | 92.9 | 297,742 | `Haemulidae` | **family** | Grunts, sweetlips, bonnetmouths | Medium demersals (30 - 89 cm) | Perch-likes | 3.36 |
| 98 | 93.0 | 286,828 | `Dussumieria acuta` | species | Rainbow sardine | Small pelagics (<30 cm) | Herring-likes | 3.40 |
| 99 | 93.2 | 273,611 | `Terapon jarbua` | species | Jarbua terapon | Medium demersals (30 - 89 cm) | Perch-likes | 3.93 |
| 100 | 93.3 | 272,238 | `Auxis` | genus | Bullet and frigate tunas | Medium pelagics (30 - 89 cm) | Tuna & billfishes | 4.24 |
| 101 | 93.4 | 267,299 | `Epinephelus coioides` | species | Orange-spotted grouper | Large reef assoc. fish (>=90 cm) | Perch-likes | 4.00 |
| 102 | 93.6 | 264,488 | `Platycephalus indicus` | species | Bartail flathead | Medium demersals (30 - 89 cm) | Scorpionfishes | 3.60 |
| 103 | 93.7 | 252,689 | `Pomadasys` | genus | Grunters | Medium demersals (30 - 89 cm) | Perch-likes | 3.59 |
| 104 | 93.8 | 244,003 | `Argyrops spinifer` | species | King soldier bream | Medium demersals (30 - 89 cm) | Perch-likes | 4.49 |
| 105 | 93.9 | 242,711 | `Chirocentrus dorab` | species | Dorab wolf-herring | Large benthopelagics (>=90 cm) | Herring-likes | 4.20 |
| 106 | 94.1 | 238,933 | `Lethrinus` | genus | Emperors | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.75 |
| 107 | 94.2 | 237,802 | `Lutjanus johnii` | species | John's snapper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.20 |
| 108 | 94.3 | 231,004 | `Sardinella albella` | species | White sardinella | Small reef assoc. fish (<30 cm) | Herring-likes | 2.68 |
| 109 | 94.4 | 229,435 | `Glaucostegus granulatus` | species | Granulated guitarfish | Large rays (>=90 cm) | Sharks & rays | 3.50 |
| 110 | 94.5 | 227,653 | `Monacanthidae` | **family** | Filefishes | Medium reef assoc. fish (30 - 89 cm) | Other fishes & inverts | 3.00 |
| 111 | 94.7 | 227,216 | `Lutjanus argentimaculatus` | species | Mangrove red snapper | Large reef assoc. fish (>=90 cm) | Perch-likes | 3.58 |
| 112 | 94.8 | 226,034 | `Chiloscyllium arabicum` | species | Arabian carpetshark | Small to medium sharks (<90 cm) | Sharks & rays | 4.06 |
| 113 | 94.9 | 219,971 | `Trichiuridae` | **family** | Cutlassfishes | Large benthopelagics (>=90 cm) | Perch-likes | 4.15 |
| 114 | 95.0 | 219,473 | `Himantura uarnak` | species | Honeycomb stingray | Large rays (>=90 cm) | Sharks & rays | 3.60 |
| 115 | 95.1 | 216,227 | `Saurida` | genus | Lizardfishes | Medium demersals (30 - 89 cm) | Other fishes & inverts | 4.35 |
| 116 | 95.2 | 204,391 | `Planiliza klunzingeri` | species | Klunzinger's mullet | Small demersals (<30 cm) | Perch-likes | 2.63 |
| 117 | 95.3 | 197,932 | `Scomberomorus` | genus | Spanish mackerels | Large pelagics (>=90 cm) | Perch-likes | 4.35 |
| 118 | 95.4 | 196,435 | `Istiophorus platypterus` | species | Indo-Pacific sailfish | Large pelagics (>=90 cm) | Tuna & billfishes | 4.50 |
| 119 | 95.5 | 194,006 | `Megalaspis cordyla` | species | Torpedo scad | Medium pelagics (30 - 89 cm) | Perch-likes | 4.24 |
| 120 | 95.6 | 192,426 | `Placuna placenta` | species | Windowpane oyster | Other demersal invertebrates | Molluscs | 2.41 |
| 121 | 95.7 | 184,886 | `Lutjanus` | genus | Snappers | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.02 |
| 122 | 95.8 | 182,866 | `Metapenaeus affinis` | species | Jinga shrimp | Shrimps | Crustaceans | 3.44 |
| 123 | 95.9 | 182,171 | `Muraenesox cinereus` | species | Daggertooth pike conger | Large demersals (>=90 cm) | Other fishes & inverts | 4.38 |
| 124 | 96.0 | 177,376 | `Muraenesocidae` | **family** | Pike congers | Large demersals (>=90 cm) | Other fishes & inverts | 3.90 |
| 125 | 96.0 | 158,185 | `Auxis thazard` | species | Frigate tuna | Medium pelagics (30 - 89 cm) | Tuna & billfishes | 4.37 |
| 126 | 96.1 | 156,925 | `Lutjanus malabaricus` | species | Malabar blood snapper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.48 |
| 127 | 96.2 | 155,152 | `Congresox talabonoides` | species | Indian pike conger | Large demersals (>=90 cm) | Other fishes & inverts | 4.30 |
| 128 | 96.3 | 151,936 | `Lethrinus lentjan` | species | Pink ear emperor | Medium demersals (30 - 89 cm) | Perch-likes | 3.94 |
| 129 | 96.4 | 150,093 | `Parapenaeopsis stylifera` | species | Kiddi shrimp | Shrimps | Crustaceans | 2.66 |
| 130 | 96.4 | 144,069 | `Aetobatus narinari` | species | Spotted eagle ray | Large rays (>=90 cm) | Sharks & rays | 4.17 |
| 131 | 96.5 | 138,038 | `Pastinachus sephen` | species | Cowtail stingray | Large rays (>=90 cm) | Sharks & rays | 3.71 |
| 132 | 96.6 | 137,700 | `Aetomylaeus nichofii` | species | Banded eagle ray | Small to medium rays (<90 cm) | Sharks & rays | 3.76 |
| 133 | 96.6 | 136,913 | `Aetomylaeus maculatus` | species | Mottled eagle ray | Large rays (>=90 cm) | Sharks & rays | 3.80 |
| 134 | 96.7 | 135,616 | `Argyrosomus heinii` | species | Arabian sea meagre | Medium benthopelagics (30 - 89 cm) | Perch-likes | 4.04 |
| 135 | 96.8 | 133,399 | `Protonibea diacanthus` | species | Blackspotted croaker | Small pelagics (<30 cm) | Perch-likes | 3.50 |
| 136 | 96.8 | 130,773 | `Bregmaceros mcclellandi` | species | Unicorn cod | Small pelagics (<30 cm) | Cod-likes | 3.30 |
| 137 | 96.9 | 129,833 | `Acanthopagrus bifasciatus` | species | Twobar seabream | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.39 |
| 138 | 97.0 | 128,247 | `Upeneus sulphureus` | species | Sulphur goatfish | Small demersals (<30 cm) | Perch-likes | 3.08 |
| 139 | 97.0 | 128,203 | `Auxis rochei` | species | Bullet tuna | Medium pelagics (30 - 89 cm) | Tuna & billfishes | 4.13 |
| 140 | 97.1 | 124,640 | `Grammoplites suppositus` | species | Spotfin flathead | Small demersals (<30 cm) | Scorpionfishes | 3.84 |
| 141 | 97.2 | 123,483 | `Scolopsis taeniata` | species | Black-streaked monocle bream | Small reef assoc. fish (<30 cm) | Perch-likes | 3.51 |
| 142 | 97.2 | 115,717 | `Sparidentex hasta` | species | Sobaity seabream | Medium demersals (30 - 89 cm) | Perch-likes | 3.38 |
| 143 | 97.3 | 114,651 | `Loliginidae` | **family** | Common pencil squids | Cephalopods | Other fishes & inverts | 3.90 |
| 144 | 97.3 | 114,147 | `Plectorhinchus` | genus | Sweetlips | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.43 |
| 145 | 97.4 | 112,929 | `Gerres oyena` | species | Common silver-biddy | Small demersals (<30 cm) | Perch-likes | 3.07 |
| 146 | 97.4 | 112,144 | `Caranx` | genus | Jacks | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.12 |
| 147 | 97.5 | 112,019 | `Siganus` | genus | Spinefoots | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 2.11 |
| 148 | 97.6 | 110,457 | `Sphyraenidae` | **family** | Barracudas | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.40 |
| 149 | 97.6 | 107,986 | `Argyrosomus japonicus` | species | Japanese meagre | Large benthopelagics (>=90 cm) | Perch-likes | 4.48 |
| 150 | 97.7 | 107,531 | `Pteriomorphia` | genus | Clams, cockles, arkshells | Other demersal invertebrates | Molluscs | 2.27 |
| 151 | 97.7 | 105,351 | `Thunnus obesus` | species | Bigeye tuna | Large pelagics (>=90 cm) | Tuna & billfishes | 4.49 |
| 152 | 97.8 | 104,198 | `Pampus chinensis` | species | Chinese silver pomfret | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.60 |
| 153 | 97.8 | 102,451 | `Istiophoridae` | **family** | Billfishes | Large pelagics (>=90 cm) | Tuna & billfishes | 4.48 |
| 154 | 97.9 | 101,616 | `Gerreidae` | **family** | Mojarras, silverbellies | Small benthopelagics (<30 cm) | Perch-likes | 3.03 |
| 155 | 97.9 | 101,348 | `Acanthopagrus berda` | species | Goldsilk seabream | Medium demersals (30 - 89 cm) | Perch-likes | 3.48 |
| 156 | 98.0 | 100,414 | `Pelates quadrilineatus` | species | Fourlined terapon | Small pelagics (<30 cm) | Perch-likes | 3.50 |
| 157 | 98.0 | 96,058 | `Rhabdosargus sarba` | species | Goldlined seabream | Medium demersals (30 - 89 cm) | Perch-likes | 3.37 |
| 158 | 98.1 | 94,124 | `Rhizostomeae` | genus | Oral arm jellyfishes | Jellyfish | Other fishes & inverts | 3.46 |
| 159 | 98.1 | 92,213 | `Hemiramphus` | genus | Halfbeaks | Medium pelagics (30 - 89 cm) | Other fishes & inverts | 3.05 |
| 160 | 98.2 | 91,555 | `Terapon` | genus | Terapons | Medium demersals (30 - 89 cm) | Perch-likes | 3.50 |
| 161 | 98.2 | 91,091 | `Pterotolithus maculatus` | species | Blotched tiger-toothed croaker | Small pelagics (<30 cm) | Perch-likes | 3.70 |
| 162 | 98.3 | 90,584 | `Flavocaranx bajad` | species | Orangespotted trevally | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.30 |
| 163 | 98.3 | 90,157 | `Selar crumenophthalmus` | species | Bigeye scad | Medium pelagics (30 - 89 cm) | Perch-likes | 3.81 |
| 164 | 98.3 | 85,337 | `Chanos chanos` | species | Milkfish | Large benthopelagics (>=90 cm) | Other fishes & inverts | 2.03 |
| 165 | 98.4 | 82,308 | `Palinuridae` | **family** | Spiny lobsters | Lobsters, crabs | Crustaceans | 3.14 |
| 166 | 98.4 | 78,171 | `Sardinella` | genus | Sardinellas | Small pelagics (<30 cm) | Herring-likes | 2.77 |
| 167 | 98.5 | 77,027 | `Octopus` | genus | Octopuses, pikas | Cephalopods | Other fishes & inverts | 3.80 |
| 168 | 98.5 | 76,430 | `Eleutheronema tetradactylum` | species | Fourfinger threadfin | Large demersals (>=90 cm) | Perch-likes | 4.06 |
| 169 | 98.5 | 75,750 | `Panulirus homarus` | species | Scalloped spiny lobster | Lobsters, crabs | Crustaceans | 3.33 |
| 170 | 98.6 | 73,347 | `Drepane punctata` | species | Spotted sicklefish | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.32 |
| 171 | 98.6 | 69,936 | `Lates calcarifer` | species | Barramundi | Large demersals (>=90 cm) | Perch-likes | 4.35 |
| 172 | 98.7 | 66,906 | `Epinephelus malabaricus` | species | Malabar grouper | Large reef assoc. fish (>=90 cm) | Perch-likes | 4.16 |
| 173 | 98.7 | 66,203 | `Istiompax indica` | species | Black marlin | Large pelagics (>=90 cm) | Tuna & billfishes | 4.50 |
| 174 | 98.7 | 66,028 | `Leiognathus` | genus | Ponyfishes | Small benthopelagics (<30 cm) | Perch-likes | 3.22 |
| 175 | 98.8 | 65,506 | `Alepes` | genus | Crevalles | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.32 |
| 176 | 98.8 | 63,170 | `Chondrichthyes` | genus | Sharks, rays, chimaeras | Large sharks (>=90 cm) | Sharks & rays | 4.00 |
| 177 | 98.8 | 59,620 | `Leiognathus equula` | species | Common ponyfish | Small benthopelagics (<30 cm) | Perch-likes | 2.95 |
| 178 | 98.8 | 57,691 | `Epinephelus tauvina` | species | Greasy grouper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.13 |
| 179 | 98.9 | 57,459 | `Gastropoda` | **class** | Sea snails | Other demersal invertebrates | Molluscs | 3.06 |
| 180 | 98.9 | 54,884 | `Catostylus perezi` | species | Banana jellyfish | Jellyfish | Other fishes & inverts | 3.46 |
| 181 | 98.9 | 54,682 | `Gnathanodon speciosus` | species | Golden trevally | Large reef assoc. fish (>=90 cm) | Perch-likes | 3.84 |
| 182 | 99.0 | 53,466 | `Carcharhinus melanopterus` | species | Blacktip reef shark | Large sharks (>=90 cm) | Sharks & rays | 3.94 |
| 183 | 99.0 | 53,203 | `Tetraodontidae` | **family** | Puffers, tobies | Large reef assoc. fish (>=90 cm) | Other fishes & inverts | 3.50 |
| 184 | 99.0 | 52,421 | `Rhabdosargus haffara` | species | Haffara seabream | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.50 |
| 185 | 99.0 | 47,891 | `Gerres` | genus | Silver biddies | Small benthopelagics (<30 cm) | Perch-likes | 3.27 |
| 186 | 99.1 | 47,704 | `Platycephalidae` | **family** | Flatheads | Medium demersals (30 - 89 cm) | Scorpionfishes | 3.90 |
| 187 | 99.1 | 45,451 | `Cephea` | genus | Cepheid jellyfishes | Jellyfish | Other fishes & inverts | 3.46 |
| 188 | 99.1 | 42,337 | `Panulirus polyphagus` | species | Mud spiny lobster | Lobsters, crabs | Crustaceans | 2.94 |
| 189 | 99.1 | 42,325 | `Decapterus russelli` | species | Indian scad | Medium pelagics (30 - 89 cm) | Perch-likes | 3.68 |
| 190 | 99.1 | 42,093 | `Pristipomoides filamentosus` | species | Crimson jobfish | Medium demersals (30 - 89 cm) | Perch-likes | 4.19 |
| 191 | 99.2 | 39,278 | `Lamnidae` | **family** | Mackerel/white sharks | Large sharks (>=90 cm) | Sharks & rays | 4.50 |
| 192 | 99.2 | 38,876 | `Sphyrnidae` | **family** | Hammer, bonnet, scoophead sharks | Large sharks (>=90 cm) | Sharks & rays | 4.19 |
| 193 | 99.2 | 36,489 | `Saccostrea cuccullata` | species | Hooded oyster | Other demersal invertebrates | Molluscs | 2.00 |
| 194 | 99.2 | 35,925 | `Xiphias gladius` | species | Swordfish | Large pelagics (>=90 cm) | Tuna & billfishes | 4.53 |
| 195 | 99.2 | 35,901 | `Hilsa kelee` | species | Kelee shad | Small pelagics (<30 cm) | Herring-likes | 3.25 |
| 196 | 99.3 | 35,430 | `Sphyraena obtusata` | species | Obtuse barracuda | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.50 |
| 197 | 99.3 | 35,185 | `Platycaranx malabaricus` | species | Malabar trevally | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.88 |
| 198 | 99.3 | 35,048 | `Moolgarda seheli` | species | Bluespot mullet | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 2.32 |
| 199 | 99.3 | 33,346 | `Epinephelus areolatus` | species | Areolate grouper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.74 |
| 200 | 99.3 | 33,186 | `Carcharhinus limbatus` | species | Blacktip shark | Large sharks (>=90 cm) | Sharks & rays | 4.37 |
| 201 | 99.3 | 32,443 | `Siganus canaliculatus` | species | White-spotted spinefoot | Small reef assoc. fish (<30 cm) | Perch-likes | 2.76 |
| 202 | 99.4 | 32,304 | `Panulirus` | genus | Spiny lobsters | Lobsters, crabs | Crustaceans | 2.60 |
| 203 | 99.4 | 30,227 | `Rhynchobatus djiddensis` | species | Giant guitarfish | Large rays (>=90 cm) | Sharks & rays | 3.60 |
| 204 | 99.4 | 30,163 | `Isurus paucus` | species | Longfin mako | Large sharks (>=90 cm) | Sharks & rays | 4.51 |
| 205 | 99.4 | 30,085 | `Diagramma pictum` | species | Painted sweetlips | Large reef assoc. fish (>=90 cm) | Perch-likes | 3.70 |
| 206 | 99.4 | 29,822 | `Alopias vulpinus` | species | Thresher | Large sharks (>=90 cm) | Sharks & rays | 4.50 |
| 207 | 99.4 | 29,489 | `Sphyraena forsteri` | species | Bigeye barracuda | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.42 |
| 208 | 99.4 | 27,484 | `Lethrinus olivaceus` | species | Longface emperor | Medium demersals (30 - 89 cm) | Perch-likes | 3.95 |
| 209 | 99.5 | 26,785 | `Lethrinus borbonicus` | species | Snubnose emperor | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.47 |
| 210 | 99.5 | 26,195 | `Sphyraena jello` | species | Pickhandle barracuda | Large reef assoc. fish (>=90 cm) | Perch-likes | 4.50 |
| 211 | 99.5 | 25,524 | `Acanthocybium solandri` | species | Wahoo | Large pelagics (>=90 cm) | Perch-likes | 4.26 |
| 212 | 99.5 | 25,504 | `Rhizoprionodon acutus` | species | Milk shark | Large sharks (>=90 cm) | Sharks & rays | 4.25 |
| 213 | 99.5 | 25,061 | `Atule mate` | species | Yellowtail scad | Small pelagics (<30 cm) | Perch-likes | 4.22 |
| 214 | 99.5 | 23,655 | `Selaroides leptolepis` | species | Yellowstripe scad | Small pelagics (<30 cm) | Perch-likes | 3.84 |
| 215 | 99.5 | 22,908 | `Sarda orientalis` | species | Striped bonito | Large pelagics (>=90 cm) | Tuna & billfishes | 4.21 |
| 216 | 99.5 | 22,698 | `Marine groundfishes not identified` | **category** | Groundfishes | Medium demersals (30 - 89 cm) | Other fishes & inverts | 3.22 |
| 217 | 99.6 | 21,995 | `Epinephelus polylepis` | species | Smallscaled grouper | Medium demersals (30 - 89 cm) | Perch-likes | 3.80 |
| 218 | 99.6 | 21,887 | `Sphyrna` | genus | Hammerhead sharks | Large sharks (>=90 cm) | Sharks & rays | 4.20 |
| 219 | 99.6 | 21,612 | `Pomadasys olivaceus` | species | Olive grunt | Medium reef assoc. fish (30 - 89 cm) | Perch-likes |  |
| 220 | 99.6 | 21,025 | `Equulites klunzingeri` | species | Klunzinger's ponyfish | Small demersals (<30 cm) | Perch-likes | 3.50 |
| 221 | 99.6 | 20,714 | `Carcharhinus dussumieri` | species | Whitecheek shark | Small to medium sharks (<90 cm) | Sharks & rays | 3.90 |
| 222 | 99.6 | 19,856 | `Alepes djedaba` | species | Shrimp scad | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.32 |
| 223 | 99.6 | 19,236 | `Carcharhinus amblyrhynchos` | species | Blacktail reef shark | Large sharks (>=90 cm) | Sharks & rays | 4.11 |
| 224 | 99.6 | 18,415 | `Triakidae` | **family** | Houndsharks | Large sharks (>=90 cm) | Sharks & rays | 3.82 |
| 225 | 99.6 | 17,571 | `Scyris indica` | species | Indian threadfish | Large reef assoc. fish (>=90 cm) | Perch-likes | 4.09 |
| 226 | 99.6 | 17,485 | `Echinoidea` | **superfamily** | Sea urchins, sea hedgehogs | Other demersal invertebrates | Other fishes & inverts | 2.51 |
| 227 | 99.7 | 17,278 | `Carcharhinus falciformis` | species | Silky shark | Large sharks (>=90 cm) | Sharks & rays | 4.51 |
| 228 | 99.7 | 16,713 | `Atropus armatus` | species | Longfin trevally | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.15 |
| 229 | 99.7 | 16,241 | `Scaridae` | **family** | Parrotfishes | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 2.00 |
| 230 | 99.7 | 16,132 | `Siganus sutor` | species | Shoemaker spinefoot | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 2.00 |
| 231 | 99.7 | 15,909 | `Coryphaena` | genus | Dolphinfishes | Large pelagics (>=90 cm) | Perch-likes | 4.49 |
| 232 | 99.7 | 15,756 | `Kajikia audax` | species | Striped marlin | Large pelagics (>=90 cm) | Tuna & billfishes | 4.58 |
| 233 | 99.7 | 15,236 | `Leptomelanosoma indicum` | species | Indian threadfin | Large demersals (>=90 cm) | Perch-likes | 3.86 |
| 234 | 99.7 | 15,211 | `Gobiidae` | **family** | Gobies | Small reef assoc. fish (<30 cm) | Perch-likes | 3.11 |
| 235 | 99.7 | 14,881 | `Epinephelus diacanthus` | species | Spinycheek grouper | Large reef assoc. fish (>=90 cm) | Perch-likes | 3.80 |
| 236 | 99.7 | 14,672 | `Cnidaria` | genus | Cnidarians, coelenterates | Jellyfish | Other fishes & inverts | 2.50 |
| 237 | 99.7 | 14,261 | `Drepane` | genus | Sicklefishes | Medium benthopelagics (30 - 89 cm) | Perch-likes | 3.32 |
| 238 | 99.7 | 14,044 | `Alopias pelagicus` | species | Pelagic thresher | Large sharks (>=90 cm) | Sharks & rays | 4.50 |
| 239 | 99.7 | 13,645 | `Brama brama` | species | Atlantic pomfret | Medium bathypelagics (30 - 89 cm) | Perch-likes | 4.08 |
| 240 | 99.8 | 13,188 | `Aprion virescens` | species | Green jobfish | Large reef assoc. fish (>=90 cm) | Perch-likes | 4.28 |
| 241 | 99.8 | 12,342 | `Thunnus alalunga` | species | Albacore | Large pelagics (>=90 cm) | Tuna & billfishes | 4.30 |
| 242 | 99.8 | 11,466 | `Epinephelus chlorostigma` | species | Brownspotted grouper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.99 |
| 243 | 99.8 | 11,234 | `Ophichthidae` | **family** | Snake eels | Medium demersals (30 - 89 cm) | Other fishes & inverts | 3.64 |
| 244 | 99.8 | 11,224 | `Mollusca` | genus | Clams, seasnails, squids, octopuses | Other demersal invertebrates | Molluscs | 2.10 |
| 245 | 99.8 | 11,124 | `Lethrinus microdon` | species | Smalltooth emperor | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.79 |
| 246 | 99.8 | 10,993 | `Lutjanus gibbus` | species | Humpback red snapper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.12 |
| 247 | 99.8 | 10,860 | `Caesionidae` | **family** | Fusiliers | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.39 |
| 248 | 99.8 | 10,706 | `Pomacanthus maculosus` | species | Yellowbar angelfish | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 2.67 |
| 249 | 99.8 | 10,223 | `Epinephelus multinotatus` | species | White-blotched grouper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.86 |
| 250 | 99.8 | 10,211 | `Mene maculata` | species | Moonfish | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.45 |
| 251 | 99.8 | 9,813 | `Nemipterus` | genus | Threadfin breams | Small demersals (<30 cm) | Perch-likes | 3.72 |
| 252 | 99.8 | 9,323 | `Pomadasys argenteus` | species | Silver grunt | Medium demersals (30 - 89 cm) | Perch-likes | 3.47 |
| 253 | 99.8 | 9,285 | `Lethrinus obsoletus` | species | Orange-striped emperor | Medium demersals (30 - 89 cm) | Perch-likes | 3.89 |
| 254 | 99.8 | 9,240 | `Scomberoides tol` | species | Needlescaled queenfish | Medium pelagics (30 - 89 cm) | Perch-likes | 4.11 |
| 255 | 99.8 | 8,854 | `Penaeus monodon` | species | Giant tiger prawn | Shrimps | Crustaceans | 2.60 |
| 256 | 99.8 | 8,823 | `Sphyrna lewini` | species | Scalloped hammerhead | Large sharks (>=90 cm) | Sharks & rays | 4.08 |
| 257 | 99.8 | 8,403 | `Alectis ciliaris` | species | African pompano | Large pelagics (>=90 cm) | Perch-likes | 3.95 |
| 258 | 99.8 | 8,218 | `Gerres longirostris` | species | Strongspine silver-biddy | Medium demersals (30 - 89 cm) | Perch-likes | 3.50 |
| 259 | 99.9 | 8,179 | `Trachinotus mookalee` | species | Indian pompano | Medium demersals (30 - 89 cm) | Perch-likes | 3.78 |
| 260 | 99.9 | 8,001 | `Carcharhinus albimarginatus` | species | Silvertip shark | Large sharks (>=90 cm) | Sharks & rays | 4.21 |
| 261 | 99.9 | 7,997 | `Lutjanus bohar` | species | Two-spot red snapper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.27 |
| 262 | 99.9 | 7,619 | `Rachycentridae` | **family** | Cobias | Large pelagics (>=90 cm) | Perch-likes | 3.96 |
| 263 | 99.9 | 7,572 | `Penaeus` | genus | Tiger prawns | Shrimps | Crustaceans | 2.70 |
| 264 | 99.9 | 7,496 | `Plectorhinchus gaterinus` | species | Blackspotted rubberlip | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.99 |
| 265 | 99.9 | 6,950 | `Variola louti` | species | Yellow-edged lyretail | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.33 |
| 266 | 99.9 | 6,630 | `Lutjanus russellii` | species | Russell's snapper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.10 |
| 267 | 99.9 | 6,471 | `Etelis` | genus | Snappers | Medium bathydemersals (30 - 89 cm) | Perch-likes | 4.36 |
| 268 | 99.9 | 6,453 | `Spratelloides gracilis` | species | Silver-stripe round herring | Small pelagics (<30 cm) | Herring-likes | 3.06 |
| 269 | 99.9 | 6,304 | `Plectropomus areolatus` | species | Squaretail coralgrouper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.50 |
| 270 | 99.9 | 6,055 | `Plectropomus pessuliferus` | species | Roving coralgrouper | Large reef assoc. fish (>=90 cm) | Perch-likes | 4.28 |
| 271 | 99.9 | 5,871 | `Xiphiidae` | **family** | Swordfishes | Large pelagics (>=90 cm) | Tuna & billfishes | 4.50 |
| 272 | 99.9 | 5,854 | `Carcharhinus plumbeus` | species | Sandbar shark | Large sharks (>=90 cm) | Sharks & rays | 4.49 |
| 273 | 99.9 | 5,521 | `Turrum fulvoguttatum` | species | Yellowspotted trevally | Large reef assoc. fish (>=90 cm) | Perch-likes | 4.43 |
| 274 | 99.9 | 5,431 | `Thenus orientalis` | species | Flathead lobster | Lobsters, crabs | Crustaceans | 2.50 |
| 275 | 99.9 | 5,429 | `Lutjanus quinquelineatus` | species | Five-lined snapper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.68 |
| 276 | 99.9 | 5,245 | `Metapenaeus` | genus | Indo-Pacific prawns | Shrimps | Crustaceans | 2.70 |
| 277 | 99.9 | 4,959 | `Galeocerdo cuvier` | species | Tiger shark | Large sharks (>=90 cm) | Sharks & rays | 4.54 |
| 278 | 99.9 | 4,954 | `Carcharhinus` | genus | Sharp-nosed sharks | Large sharks (>=90 cm) | Sharks & rays | 4.26 |
| 279 | 99.9 | 4,914 | `Uroteuthis duvaucelii` | species | Indian squid | Cephalopods | Other fishes & inverts | 3.77 |
| 280 | 99.9 | 4,875 | `Carcharhinus amblyrhynchoides` | species | Graceful shark | Large sharks (>=90 cm) | Sharks & rays | 4.22 |
| 281 | 99.9 | 4,725 | `Scarus persicus` | species | Gulf parrotfish | Medium benthopelagics (30 - 89 cm) | Perch-likes | 2.00 |
| 282 | 99.9 | 4,521 | `Lutjanus fulviflamma` | species | Dory snapper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.79 |
| 283 | 99.9 | 4,491 | `Pomadasys argyreus` | species | Bluecheek silver grunt | Small pelagics (<30 cm) | Perch-likes |  |
| 284 | 99.9 | 4,428 | `Miscellaneous marine crustaceans` | **category** | Marine crabs, shrimps, lobsters nei | Shrimps | Crustaceans | 2.70 |
| 285 | 99.9 | 4,195 | `Cephalopholis hemistiktos` | species | Yellowfin hind | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.14 |
| 286 | 99.9 | 4,088 | `Platax orbicularis` | species | Orbicular batfish | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.33 |
| 287 | 99.9 | 4,054 | `Crenidens crenidens` | species | Karanteen seabream | Small demersals (<30 cm) | Perch-likes | 2.80 |
| 288 | 99.9 | 3,892 | `Hemiramphidae` | **family** | Halfbeaks, garfishes | Medium pelagics (30 - 89 cm) | Other fishes & inverts | 2.82 |
| 289 | 99.9 | 3,838 | `Plectorhinchus schotaf` | species | Minstrel sweetlips | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.82 |
| 290 | 99.9 | 3,802 | `Acanthurus dussumieri` | species | Eyestripe surgeonfish | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 2.02 |
| 291 | 99.9 | 3,725 | `Rajiformes` | **order** | Skates and rays | Large rays (>=90 cm) | Sharks & rays | 3.61 |
| 292 | 99.9 | 3,719 | `Caranx sexfasciatus` | species | Bigeye trevally | Large reef assoc. fish (>=90 cm) | Perch-likes | 4.50 |
| 293 | 99.9 | 3,329 | `Lethrinus mahsena` | species | Sky emperor | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.43 |
| 294 | 99.9 | 3,298 | `Nebrius ferrugineus` | species | Tawny nurse shark | Large sharks (>=90 cm) | Sharks & rays | 4.10 |
| 295 | 99.9 | 3,090 | `Solenidae` | **family** | Razor, knife clams | Other demersal invertebrates | Molluscs | 2.00 |
| 296 | 99.9 | 3,016 | `Synanceiidae` | **family** | Stonefishes | Medium demersals (30 - 89 cm) | Scorpionfishes | 4.20 |
| 297 | 99.9 | 2,999 | `Istiophorus` | genus | Sailfishes | Large pelagics (>=90 cm) | Tuna & billfishes | 4.50 |
| 298 | 100.0 | 2,723 | `Sepioteuthis lessoniana` | species | Bigfin reef squid | Cephalopods | Other fishes & inverts | 3.98 |
| 299 | 100.0 | 2,667 | `Ariomma indica` | species | Indian driftfish | Small benthopelagics (<30 cm) | Perch-likes | 3.63 |
| 300 | 100.0 | 2,666 | `Seriolina nigrofasciata` | species | Blackbanded trevally | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.17 |
| 301 | 100.0 | 2,657 | `Bolbometopon muricatum` | species | Green humphead parrotfish | Large reef assoc. fish (>=90 cm) | Perch-likes | 2.67 |
| 302 | 100.0 | 2,545 | `Scombroidei` | **suborder** | Tunas, bonitos, billfishes | Large pelagics (>=90 cm) | Tuna & billfishes | 4.20 |
| 303 | 100.0 | 2,518 | `Pristidae` | **family** | Sawfishes | Large rays (>=90 cm) | Sharks & rays | 4.24 |
| 304 | 100.0 | 2,311 | `Haliotis` | genus | Abalones | Other demersal invertebrates | Molluscs | 2.00 |
| 305 | 100.0 | 2,303 | `Cheimerius nufar` | species | Santer seabream | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.54 |
| 306 | 100.0 | 2,258 | `Sillaginidae` | **family** | Smelt-whitings | Medium demersals (30 - 89 cm) | Perch-likes | 3.25 |
| 307 | 100.0 | 2,237 | `Lutjanus kasmira` | species | Common bluestripe snapper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.87 |
| 308 | 100.0 | 2,236 | `Carcharhiniformes` | **order** | Ground sharks | Large sharks (>=90 cm) | Sharks & rays | 4.08 |
| 309 | 100.0 | 2,226 | `Monotaxis grandoculis` | species | Humpnose big-eye bream | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.37 |
| 310 | 100.0 | 2,216 | `Caranx melampygus` | species | Bluefin trevally | Large reef assoc. fish (>=90 cm) | Perch-likes | 4.49 |
| 311 | 100.0 | 2,154 | `Balistidae` | **family** | Triggerfishes | Medium reef assoc. fish (30 - 89 cm) | Other fishes & inverts | 3.25 |
| 312 | 100.0 | 2,126 | `Carcharhinus longimanus` | species | Oceanic whitetip shark | Large sharks (>=90 cm) | Sharks & rays | 4.16 |
| 313 | 100.0 | 2,072 | `Congridae` | **family** | Conger, garden eels | Large demersals (>=90 cm) | Other fishes & inverts |  |
| 314 | 100.0 | 2,031 | `Bothus pantherinus` | species | Leopard flounder | Small to medium flatfishes (<90 cm) | Flatfishes | 3.50 |
| 315 | 100.0 | 1,936 | `Parupeneus indicus` | species | Indian goatfish | Medium reef assoc. fish (30 - 89 cm) | Perch-likes |  |
| 316 | 100.0 | 1,897 | `Sphyraena putnamae` | species | Sawtooth barracuda | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.50 |
| 317 | 100.0 | 1,857 | `Turrum coeruleopinnatum` | species | Coastal trevally | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.44 |
| 318 | 100.0 | 1,822 | `Carangoides` | genus | Trevallies | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.34 |
| 319 | 100.0 | 1,653 | `Seriola rivoliana` | species | Longfin yellowtail | Large benthopelagics (>=90 cm) | Perch-likes | 4.45 |
| 320 | 100.0 | 1,650 | `Encrasicholina heteroloba` | species | Shorthead anchovy | Small pelagics (<30 cm) | Anchovies | 3.27 |
| 321 | 100.0 | 1,642 | `Lethrinus xanthochilus` | species | Yellowlip emperor | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.78 |
| 322 | 100.0 | 1,639 | `Prionace glauca` | species | Blue shark | Large sharks (>=90 cm) | Sharks & rays | 4.35 |
| 323 | 100.0 | 1,622 | `Stromateidae` | **family** | Butterfishes | Small benthopelagics (<30 cm) | Perch-likes | 3.62 |
| 324 | 100.0 | 1,609 | `Zeus faber` | species | John dory | Medium benthopelagics (30 - 89 cm) | Other fishes & inverts |  |
| 325 | 100.0 | 1,585 | `Terapontidae` | **family** | Grunters, tigerperches | Medium demersals (30 - 89 cm) | Perch-likes | 3.64 |
| 326 | 100.0 | 1,583 | `Caesio caerulaurea` | species | Blue and gold fusilier | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.40 |
| 327 | 100.0 | 1,562 | `Caesio lunaris` | species | Lunar fusilier | Medium reef assoc. fish (30 - 89 cm) | Perch-likes |  |
| 328 | 100.0 | 1,483 | `Aphareus furca` | species | Small toothed jobfish | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.14 |
| 329 | 100.0 | 1,471 | `Plectorhinchus pictus` | species | Trout sweetlips | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.85 |
| 330 | 100.0 | 1,365 | `Centrolophidae` | **family** | Medusafishes | Medium benthopelagics (30 - 89 cm) | Perch-likes |  |
| 331 | 100.0 | 1,213 | `Lethrinus harak` | species | Thumbprint emperor | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.59 |
| 332 | 100.0 | 1,171 | `Inermiidae` | **family** | Bonnetmouths | Small pelagics (<30 cm) | Perch-likes |  |
| 333 | 100.0 | 1,143 | `Epinephelus fuscoguttatus` | species | Brown-marbled grouper | Large reef assoc. fish (>=90 cm) | Perch-likes | 4.14 |
| 334 | 100.0 | 1,121 | `Octopodidae` | **family** | Octopuses | Cephalopods | Other fishes & inverts | 3.59 |
| 335 | 100.0 | 1,098 | `Ferdauia orthogrammus` | species | Island trevally | Medium pelagics (30 - 89 cm) | Perch-likes | 4.48 |
| 336 | 100.0 | 1,056 | `Makaira` | genus | Blue marlins | Large pelagics (>=90 cm) | Tuna & billfishes | 4.47 |
| 337 | 100.0 | 1,017 | `Ephippidae` | **family** | Spade-, batfishes, scats | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.57 |
| 338 | 100.0 | 978 | `Cephalopholis miniata` | species | Coral hind | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.29 |
| 339 | 100.0 | 958 | `Epinephelus fasciatus` | species | Blacktip grouper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.72 |
| 340 | 100.0 | 958 | `Cephalopholis` | genus | Hinds | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.13 |
| 341 | 100.0 | 948 | `Ablennes hians` | species | Flat needlefish | Large pelagics (>=90 cm) | Other fishes & inverts | 4.50 |
| 342 | 100.0 | 937 | `Seriola` | genus | Amberjacks | Large benthopelagics (>=90 cm) | Perch-likes | 4.39 |
| 343 | 100.0 | 920 | `Octopoda` | **class** | Octopuses, argonauts | Cephalopods | Other fishes & inverts | 3.58 |
| 344 | 100.0 | 860 | `Scomberomorus lineolatus` | species | Streaked seerfish | Large pelagics (>=90 cm) | Perch-likes | 4.50 |
| 345 | 100.0 | 860 | `Gymnosarda unicolor` | species | Dogtooth tuna | Large reef assoc. fish (>=90 cm) | Tuna & billfishes | 4.50 |
| 346 | 100.0 | 851 | `Scolopsis` | genus | Monocle breams | Small reef assoc. fish (<30 cm) | Perch-likes | 3.30 |
| 347 | 100.0 | 851 | `Berycidae` | **family** | Alfonsinos, redfishes | Medium benthopelagics (30 - 89 cm) | Other fishes & inverts |  |
| 348 | 100.0 | 816 | `Aluterus monoceros` | species | Unicorn leatherjacket filefish | Medium reef assoc. fish (30 - 89 cm) | Other fishes & inverts | 3.84 |
| 349 | 100.0 | 763 | `Caranx lugubris` | species | Black jack | Large benthopelagics (>=90 cm) | Perch-likes | 4.50 |
| 350 | 100.0 | 740 | `Aphareus rutilans` | species | Rusty jobfish | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.11 |
| 351 | 100.0 | 725 | `Macolor niger` | species | Black and white snapper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.01 |
| 352 | 100.0 | 666 | `Macolor macularis` | species | Midnight snapper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes |  |
| 353 | 100.0 | 645 | `Sillago` | genus | Smelt-whitings | Medium demersals (30 - 89 cm) | Perch-likes | 3.33 |
| 354 | 100.0 | 616 | `Rhincodon typus` | species | Whale shark | Large sharks (>=90 cm) | Sharks & rays | 3.55 |
| 355 | 100.0 | 581 | `Penaeus indicus` | species | Indian white prawn | Shrimps | Crustaceans |  |
| 356 | 100.0 | 524 | `Nemipterus randalli` | species | Randall's threadfin bream | Small demersals (<30 cm) | Perch-likes |  |
| 357 | 100.0 | 521 | `Aethaloperca rogaa` | species | Redmouth grouper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.20 |
| 358 | 100.0 | 507 | `Plotosidae` | **family** | Eeltail catfishes | Medium reef assoc. fish (30 - 89 cm) | Other fishes & inverts | 3.49 |
| 359 | 100.0 | 501 | `Elagatis bipinnulata` | species | Rainbow runner | Large pelagics (>=90 cm) | Perch-likes | 4.27 |
| 360 | 100.0 | 485 | `Malacostraca` | genus | Lobsters, crabs, shrimps, krill | Shrimps | Crustaceans |  |
| 361 | 100.0 | 485 | `Veneridae` | **family** | Venus clams | Other demersal invertebrates | Molluscs | 2.00 |
| 362 | 100.0 | 478 | `Haliotidae` | **family** | Abalones, ear shells | Other demersal invertebrates | Molluscs | 2.00 |
| 363 | 100.0 | 423 | `Spratelloides delicatulus` | species | Delicate round herring | Small reef assoc. fish (<30 cm) | Herring-likes |  |
| 364 | 100.0 | 381 | `Sphyrna zygaena` | species | Smooth hammerhead | Large sharks (>=90 cm) | Sharks & rays | 4.94 |
| 365 | 100.0 | 363 | `Plectorhinchus sordidus` | species | Sordid rubberlip | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.99 |
| 366 | 100.0 | 355 | `Holothuroidea` | **superfamily** | Sea cucumbers | Other demersal invertebrates | Other fishes & inverts | 2.00 |
| 367 | 100.0 | 352 | `Hemiramphus archipelagicus` | species | Jumping halfbeak | Medium pelagics (30 - 89 cm) | Other fishes & inverts | 3.25 |
| 368 | 100.0 | 352 | `Scorpaenidae` | **family** | Scorpionfishes, rockfishes | Large reef assoc. fish (>=90 cm) | Scorpionfishes | 3.92 |
| 369 | 100.0 | 352 | `Chaetodontidae` | **family** | Butterflyfishes | Small reef assoc. fish (<30 cm) | Perch-likes | 3.24 |
| 370 | 100.0 | 312 | `Beryx` | genus | Alfonsinos | Medium benthopelagics (30 - 89 cm) | Other fishes & inverts |  |
| 371 | 100.0 | 287 | `Scylla serrata` | species | Indo-Pacific swamp crab | Lobsters, crabs | Crustaceans | 3.17 |
| 372 | 100.0 | 282 | `Pomatomus saltatrix` | species | Bluefish | Large pelagics (>=90 cm) | Perch-likes |  |
| 373 | 100.0 | 279 | `Gadiformes` | **order** | Cods | Medium benthopelagics (30 - 89 cm) | Cod-likes |  |
| 374 | 100.0 | 255 | `Triaenodon obesus` | species | Whitetip reef shark | Large sharks (>=90 cm) | Sharks & rays |  |
| 375 | 100.0 | 242 | `Lethrinus rubrioperculatus` | species | Spotcheek emperor | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.75 |
| 376 | 100.0 | 230 | `Caesio` | genus | Caesios | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.40 |
| 377 | 100.0 | 230 | `Isurus` | genus | Mako sharks | Large sharks (>=90 cm) | Sharks & rays | 4.50 |
| 378 | 100.0 | 211 | `Seriola dumerili` | species | Greater amberjack | Large reef assoc. fish (>=90 cm) | Perch-likes | 4.50 |
| 379 | 100.0 | 209 | `Modiolus` | genus | Horse mussels | Other demersal invertebrates | Molluscs |  |
| 380 | 100.0 | 190 | `Miscellaneous aquatic invertebrates` | **category** | Aquatic invertebrates | Other demersal invertebrates | Other fishes & inverts | 2.43 |
| 381 | 100.0 | 185 | `Holothuria atra` | species | Lollyfish | Other demersal invertebrates | Other fishes & inverts | 2.00 |
| 382 | 100.0 | 165 | `Gempylidae` | **family** | Snake mackerels | Large benthopelagics (>=90 cm) | Perch-likes |  |
| 383 | 100.0 | 135 | `Macolor` | genus | Snappers | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.99 |
| 384 | 100.0 | 123 | `Gerres oblongus` | species | Slender silver-biddy | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.50 |
| 385 | 100.0 | 114 | `Zeidae` | **family** | Dories | Medium bathydemersals (30 - 89 cm) | Other fishes & inverts |  |
| 386 | 100.0 | 112 | `Holothuriidae` | **family** | Fleshy sea cucumbers | Other demersal invertebrates | Other fishes & inverts | 2.00 |
| 387 | 100.0 | 110 | `Pomacentridae` | **family** | Damselfishes | Small reef assoc. fish (<30 cm) | Perch-likes | 2.57 |
| 388 | 100.0 | 107 | `Platycaranx talamparoides` | species | Imposter trevally | Medium pelagics (30 - 89 cm) | Perch-likes | 4.40 |
| 389 | 100.0 | 90 | `Tetrapturus angustirostris` | species | Shortbill spearfish | Large pelagics (>=90 cm) | Tuna & billfishes | 4.50 |
| 390 | 100.0 | 88 | `Maculabatis gerrardi` | species | Sharpnose stingray | Large rays (>=90 cm) | Sharks & rays | 3.73 |
| 391 | 100.0 | 83 | `Decapterus macarellus` | species | Mackerel scad | Medium pelagics (30 - 89 cm) | Perch-likes | 3.96 |
| 392 | 100.0 | 81 | `Epinephelus polyphekadion` | species | Camouflage grouper | Large reef assoc. fish (>=90 cm) | Perch-likes | 3.99 |
| 393 | 100.0 | 74 | `Holothuria fuscogilva` | species | White teatfish | Other demersal invertebrates | Other fishes & inverts | 2.00 |
| 394 | 100.0 | 72 | `Thunnus` | genus | Tunas | Large pelagics (>=90 cm) | Tuna & billfishes |  |
| 395 | 100.0 | 57 | `Myctophidae` | **family** | Lanternfishes | Small pelagics (<30 cm) | Other fishes & inverts |  |
| 396 | 100.0 | 48 | `Pristipomoides` | genus | Jobfishes | Medium demersals (30 - 89 cm) | Perch-likes | 3.91 |
| 397 | 100.0 | 42 | `Bothidae` | **family** | Lefteye flounders | Small to medium flatfishes (<90 cm) | Flatfishes | 3.77 |
| 398 | 100.0 | 41 | `Holothuria edulis` | species | Pinkfish | Other demersal invertebrates | Other fishes & inverts | 2.00 |
| 399 | 100.0 | 41 | `Holothuria fuscopunctata` | species | Elephant trunkfish | Other demersal invertebrates | Other fishes & inverts | 2.00 |
| 400 | 100.0 | 41 | `Holothuria leucospilota` | species | White threads fish | Other demersal invertebrates | Other fishes & inverts | 2.00 |
| 401 | 100.0 | 39 | `Hexanchus griseus` | species | Bluntnose sixgill shark | Large sharks (>=90 cm) | Sharks & rays |  |
| 402 | 100.0 | 36 | `Scomber` | genus | Chub mackerels | Medium pelagics (30 - 89 cm) | Perch-likes |  |
| 403 | 100.0 | 34 | `Carcharhinus obscurus` | species | Dusky shark | Large sharks (>=90 cm) | Sharks & rays |  |
| 404 | 100.0 | 34 | `Panulirus versicolor` | species | Painted spiny lobster | Lobsters, crabs | Crustaceans | 3.57 |
| 405 | 100.0 | 26 | `Penaeus latisulcatus` | species | Western king prawn | Shrimps | Crustaceans | 2.70 |
| 406 | 100.0 | 24 | `Alopias` | genus | Thresher sharks | Large sharks (>=90 cm) | Sharks & rays |  |
| 407 | 100.0 | 22 | `Platax` | genus | Spadefishes | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.53 |
| 408 | 100.0 | 15 | `Plectropomus laevis` | species | Blacksaddled coralgrouper | Large reef assoc. fish (>=90 cm) | Perch-likes |  |
| 409 | 100.0 | 15 | `Cephalopholis argus` | species | Peacock hind | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 4.48 |
| 410 | 100.0 | 11 | `Panulirus penicillatus` | species | Pronghorn spiny lobster | Lobsters, crabs | Crustaceans | 3.57 |
| 411 | 100.0 | 9 | `Loligo` | genus | Common squids | Cephalopods | Other fishes & inverts |  |
| 412 | 100.0 | 4 | `Priacanthidae` | **family** | Bigeyes, catalufas | Medium reef assoc. fish (30 - 89 cm) | Perch-likes |  |
| 413 | 100.0 | 2 | `Scarus ghobban` | species | Blue-barred parrotfish | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 2.00 |
| 414 | 100.0 | 1 | `Trichiurus` | genus | Hairtails | Large benthopelagics (>=90 cm) | Perch-likes | 4.42 |
| 415 | 100.0 | 1 | `Epinephelus coeruleopunctatus` | species | Whitespotted grouper | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.72 |
| 416 | 100.0 | 1 | `Lamniformes` | **order** | Mackerel sharks | Large sharks (>=90 cm) | Sharks & rays |  |
| 417 | 100.0 | 1 | `Lophiidae` | **family** | Goosefishes | Medium bathydemersals (30 - 89 cm) | Other fishes & inverts |  |
| 418 | 100.0 | 1 | `Pristipomoides multidens` | species | Goldbanded jobfish | Medium demersals (30 - 89 cm) | Perch-likes | 3.84 |
| 419 | 100.0 | 1 | `Ruvettus pretiosus` | species | Oilfish | Large benthopelagics (>=90 cm) | Perch-likes |  |
| 420 | 100.0 | 0 | `Lepturacanthus savala` | species | Savalai hairtail | Large benthopelagics (>=90 cm) | Perch-likes | 4.31 |
| 421 | 100.0 | 0 | `Mobula birostris` | species | Giant manta | Large rays (>=90 cm) | Sharks & rays | 3.46 |
| 422 | 100.0 | 0 | `Gymnocranius grandoculis` | species | Blue-lined large-eye bream | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.76 |
| 423 | 100.0 | 0 | `Lepidocybium flavobrunneum` | species | Escolar | Large bathypelagics (>=90 cm) | Perch-likes |  |
| 424 | 100.0 | 0 | `Plotosus lineatus` | species | Striped eel catfish | Medium reef assoc. fish (30 - 89 cm) | Other fishes & inverts |  |
| 425 | 100.0 | 0 | `Lampris guttatus` | species | Opah | Large bathypelagics (>=90 cm) | Other fishes & inverts |  |
| 426 | 100.0 | 0 | `Pomacanthidae` | **family** | Angelfishes | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 2.86 |
| 427 | 100.0 | 0 | `Carcharhinus macloti` | species | Hardnose shark | Small to medium sharks (<90 cm) | Sharks & rays |  |
| 428 | 100.0 | 0 | `Labridae` | **family** | Wrasses, gropers, tuskfishes | Medium reef assoc. fish (30 - 89 cm) | Perch-likes | 3.46 |
| 429 | 100.0 | 0 | `Portunus` | genus | Swimmer crabs | Lobsters, crabs | Crustaceans | 3.26 |
| 430 | 100.0 | 0 | `Acanthuridae` | **family** | Surgeons, tangs, unicornfishes | Small reef assoc. fish (<30 cm) | Perch-likes | 2.28 |

## Where the difficulty is

98 of 430 labels sit above genus and together carry **89,976,286 tonnes (45.5 % of the catch)**.
Leaving these unresolved is what caps coverage near 78 %. Read `references/coarse-taxa-playbook.md` before deciding any of them.

The ten largest:

- `Marine fishes not identified` — 24,743,762 t (12.5 %), SAU: Medium demersals (30 - 89 cm) / Other fishes & inverts
- `Penaeidae` — 8,918,687 t (4.5 %), SAU: Shrimps / Crustaceans
- `Sciaenidae` — 6,707,975 t (3.4 %), SAU: Medium demersals (30 - 89 cm) / Perch-likes
- `Clupeiformes` — 5,102,723 t (2.6 %), SAU: Small pelagics (<30 cm) / Other fishes & inverts
- `Nemipteridae` — 4,009,328 t (2.0 %), SAU: Small demersals (<30 cm) / Perch-likes
- `Clupeidae` — 3,854,520 t (1.9 %), SAU: Small pelagics (<30 cm) / Herring-likes
- `Carangidae` — 3,111,578 t (1.6 %), SAU: Medium pelagics (30 - 89 cm) / Perch-likes
- `Carcharhinidae` — 2,956,883 t (1.5 %), SAU: Large sharks (>=90 cm) / Sharks & rays
- `Ariidae` — 2,892,969 t (1.5 %), SAU: Medium demersals (30 - 89 cm) / Other fishes & inverts
- `Siluriformes` — 2,341,898 t (1.2 %), SAU: Medium demersals (30 - 89 cm) / Other fishes & inverts
